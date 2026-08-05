"""Whole-repo cold-start diagnostic: is this board actually ready to run?

`check` answers "is the board valid"; doctor answers "is this installation
wired up". They are deliberately separate, and a freshly scaffolded repo is
the case that proves it: `boardkit init` leaves placeholders on purpose, so
a fresh repo passes `check` and fails doctor on unfilled roles.

Three rules shape this module. Doctor never raises: a config that fails to
load becomes a finding, because "the config is broken" is a quadrant the
user needs named, not a traceback. Doctor never executes anything a repo
told it to run - `preflight` strings are printed by the caller, never here,
since a diagnostic that shells out to repo config is a code-execution
surface. And doctor never stays silent: a check that could not run is
reported as a skip, because silence reads as success.

The one quadrant doctor cannot cover is its own absence. That belongs to
the board-hygiene skill's fail-closed first step: run `boardkit doctor`, and
if the command is not found, stop and tell the user.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import tomllib
from dataclasses import dataclass
from enum import StrEnum
from fnmatch import fnmatch
from pathlib import Path

import yaml

from boardkit.board import BoardError, build_board, view_drift
from boardkit.brief import GATE_BULLET_RE, GATES_SECTION, gate_tokens
from boardkit.config import CONFIG_FILENAME, Config, find_config, load_config
from boardkit.contract import (
    BOARDKIT_HOME_VAR,
    CONTRACT_DOCS,
    DATA_DIR,
    ENTRY_SHIMS,
    JOB_WORKTREE_GLOB,
    SUPPORTED_CONTRACT_VERSIONS,
    TEMPLATES_DIR,
    ContractConfig,
    contract_digest,
    missing_pin_sources,
    placeholders,
    read_stamp,
    read_text_or_none,
    route_placeholders,
    sections,
)

CONTRACT_DOC_DESTS = dict(CONTRACT_DOCS)
ENTRY_SHIM_DESTS = dict(ENTRY_SHIMS)
REVIEW_TOOLING_TEMPLATE = "REVIEW-TOOLING.md.template"
AGENTS_TEMPLATE = "AGENTS.md.template"

# The two sections of REVIEW-TOOLING.md a consumer must write themselves.
# Everything else in that file ships usable; these ship as prompts.
REQUIRED_FILL_SECTIONS = ("Tools, in order of preference", "Harness bindings")

BOARD_SKILLS = ("board-hygiene", "delegating-work")
SKILL_METADATA_KEY = "boardkit-contract"
SKILL_SEARCH_PATTERNS = (
    "{repo}/.claude/skills/{name}/SKILL.md",
    "~/.claude/skills/{name}/SKILL.md",
    "~/.agents/skills/{name}/SKILL.md",
    "~/.claude/plugins/**/skills/{name}/SKILL.md",
)

# The bootstrap in the AGENTS template; doctor warns when it would resolve
# somewhere other than the boardkit that is actually running.
DEFAULT_HOME = "../boardkit"
# <checkout>/src/boardkit/data -> <checkout>. boardkit is not published to an
# index; it runs from a checkout, and that checkout is what BOARDKIT_HOME names.
INSTALL_ROOT = DATA_DIR.parent.parent.parent

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$", re.MULTILINE)
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)

# Every check doctor knows how to run, in report order. Any id not recorded
# by the end of a run is reported as skipped, so no check can go silent.
ALL_CHECKS = (
    "config.present",
    "config.repo-root",
    "contract.version-known",
    "config.loads",
    "docs.present",
    "contract.docs-stamped",
    "contract.skills-declared",
    "review-tooling.filled",
    "review-tooling.placeholders",
    "roles.filled",
    "routes.pin-source",
    "board.parses",
    "board.gate-vocabulary",
    "views.current",
    "env.boardkit-home",
    "skills.installed",
    "worktrees.stray",
    "entry.agents-stamp",
)


class Severity(StrEnum):
    ERROR = "error"
    WARN = "warn"


@dataclass(frozen=True)
class Finding:
    check: str
    severity: Severity
    message: str
    remedy: str


@dataclass(frozen=True)
class Skip:
    check: str
    reason: str


@dataclass(frozen=True)
class DoctorReport:
    config_path: Path | None
    contract_version: int | None
    digest: str | None
    findings: tuple[Finding, ...]
    skipped: tuple[Skip, ...]
    passed: tuple[str, ...]

    @property
    def errors(self) -> tuple[Finding, ...]:
        return tuple(f for f in self.findings if f.severity is Severity.ERROR)

    @property
    def warnings(self) -> tuple[Finding, ...]:
        return tuple(f for f in self.findings if f.severity is Severity.WARN)


def _normalize(text: str) -> str:
    return " ".join(text.split())


def unfilled_sections(
    current: str, shipped: str, headings: tuple[str, ...] = REQUIRED_FILL_SECTIONS
) -> list[str]:
    """Required sections the consumer has not written yet.

    Unfilled means missing, or still identical to the shipped template's own
    text. Comparison is whitespace-normalized, so re-wrapping a paragraph
    does not read as filling it in - the words have to change.
    """
    current_sections = sections(current)
    shipped_sections = sections(shipped)
    unfilled = []
    for heading in headings:
        body = current_sections.get(heading)
        if body is None or _normalize(body) == _normalize(shipped_sections[heading]):
            unfilled.append(heading)
    return unfilled


def section_placeholders(
    text: str, headings: tuple[str, ...] = REQUIRED_FILL_SECTIONS
) -> dict[str, list[str]]:
    """Placeholder tokens left inside the required fill-in sections.

    Scoped to those sections on purpose: elsewhere the document uses angle
    brackets as legitimate prose (`timeout <seconds>`), and a whole-file scan
    would report those as unfilled. HTML comments are stripped first, because
    a commented-out example row is guidance, not content awaiting a value.
    """
    bodies = sections(text)
    found = {}
    for heading in headings:
        if heading not in bodies:
            continue
        tokens = placeholders(HTML_COMMENT_RE.sub("", bodies[heading]))
        if tokens:
            found[heading] = tokens
    return found


def unfilled_routes(contract: ContractConfig) -> dict[str, list[str]]:
    """Route name -> the placeholder tokens still sitting in its values."""
    found = {}
    for name, route in contract.routes.items():
        tokens = route_placeholders(route)
        if tokens:
            found[name] = tokens
    return found


def stray_job_worktrees(porcelain: str) -> list[str]:
    """Delegation worktrees left registered, from `git worktree list --porcelain`.

    Takes the captured text rather than running git, so the parser is testable
    against a recorded incident without a repo to reproduce it in.
    """
    return [
        line.split(" ", 1)[1]
        for line in porcelain.splitlines()
        if line.startswith("worktree ") and fnmatch(line.split(" ", 1)[1], f"*{JOB_WORKTREE_GLOB}")
    ]


def boardkit_home_finding(env: str | None, install_root: Path, repo_root: Path) -> Finding | None:
    """Warn when the bootstrap would reach a different boardkit than this one.

    The recorded failure is silent: a same-line `BOARDKIT_HOME=... uv run`
    prefix expands the default before the assignment lands, so the command
    targets `../boardkit` while the operator believes it targeted their path.
    Naming both paths is what makes that visible.
    """
    remedy = f"export {BOARDKIT_HOME_VAR}={install_root} on its own line, before the `uv run` line"
    if env is not None:
        if Path(env).expanduser().resolve() == install_root:
            return None
        return Finding(
            "env.boardkit-home",
            Severity.WARN,
            f"{BOARDKIT_HOME_VAR}={env}, but this boardkit runs from {install_root}",
            remedy,
        )
    default = (repo_root / DEFAULT_HOME).resolve()
    if default == install_root:
        return None
    return Finding(
        "env.boardkit-home",
        Severity.WARN,
        f"{BOARDKIT_HOME_VAR} is unset, so the bootstrap resolves `{DEFAULT_HOME}` to "
        f"{default}, but this boardkit runs from {install_root}",
        remedy,
    )


def skill_paths(name: str, home: Path, repo_root: Path) -> list[Path]:
    """Every place a board-bound skill may be installed, in search order.

    Project scope comes first: a repo that ships its own copy of a board skill
    is pinning that copy deliberately, and a user-level install must not mask it.
    """
    return [
        repo_root / ".claude" / "skills" / name / "SKILL.md",
        home / ".claude" / "skills" / name / "SKILL.md",
        home / ".agents" / "skills" / name / "SKILL.md",
        *sorted((home / ".claude" / "plugins").glob(f"**/skills/{name}/SKILL.md")),
    ]


def skill_contract_version(text: str) -> int | None:
    """The contract version a skill's frontmatter declares, or None."""
    frontmatter = FRONTMATTER_RE.match(text)
    if frontmatter is None:
        return None
    try:
        data = yaml.safe_load(frontmatter.group(1))
    except yaml.YAMLError:
        return None
    metadata = data.get("metadata") if isinstance(data, dict) else None
    declared = metadata.get(SKILL_METADATA_KEY) if isinstance(metadata, dict) else None
    return declared if isinstance(declared, int) and not isinstance(declared, bool) else None


def _git_text(cwd: Path, *args: str) -> str | None:
    """Captured git output, or None when git is absent or this is not a repo."""
    try:
        result = subprocess.run(
            ["git", "-C", str(cwd), *args],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None
    return result.stdout if result.returncode == 0 else None


class _Checks:
    """Accumulator for one doctor run."""

    def __init__(self) -> None:
        self.findings: list[Finding] = []
        self.skipped: list[Skip] = []
        self.passed: list[str] = []

    def error(self, check: str, message: str, remedy: str) -> None:
        self.findings.append(Finding(check, Severity.ERROR, message, remedy))

    def warn(self, check: str, message: str, remedy: str) -> None:
        self.findings.append(Finding(check, Severity.WARN, message, remedy))

    def add(self, finding: Finding) -> None:
        self.findings.append(finding)

    def skip(self, check: str, reason: str) -> None:
        self.skipped.append(Skip(check, reason))

    def ok(self, check: str) -> None:
        self.passed.append(check)

    def recorded(self) -> set[str]:
        return {f.check for f in self.findings} | {s.check for s in self.skipped} | set(self.passed)

    def skip_remaining(self, reason: str) -> None:
        for check in ALL_CHECKS:
            if check not in self.recorded():
                self.skip(check, reason)

    def report(
        self, config_path: Path | None, version: int | None, digest: str | None = None
    ) -> DoctorReport:
        order = {check: index for index, check in enumerate(ALL_CHECKS)}
        return DoctorReport(
            config_path=config_path,
            contract_version=version,
            digest=digest,
            findings=tuple(sorted(self.findings, key=lambda f: order[f.check])),
            skipped=tuple(sorted(self.skipped, key=lambda s: order[s.check])),
            passed=tuple(sorted(self.passed, key=lambda c: order[c])),
        )


def _check_config_present(checks: _Checks, config_arg: str | None, cwd: Path) -> Path | None:
    remedy = f"run `boardkit init` in the repo root to scaffold {CONFIG_FILENAME}"
    if config_arg is not None:
        path = Path(config_arg).resolve()
        if not path.is_file():
            checks.error("config.present", f"no config file at {path}", remedy)
            return None
        checks.ok("config.present")
        return path
    try:
        path = find_config(cwd)
    except FileNotFoundError as exc:
        checks.error("config.present", str(exc), remedy)
        return None
    checks.ok("config.present")
    return path


def _check_repo_root(checks: _Checks, config_path: Path, cwd: Path) -> None:
    toplevel = _git_text(cwd, "rev-parse", "--show-toplevel")
    if toplevel is None:
        checks.skip("config.repo-root", "git is unavailable or this is not a git repository")
        return
    repo_root = Path(toplevel.strip()).resolve()
    if repo_root != config_path.parent:
        checks.warn(
            "config.repo-root",
            f"the config found is {config_path}, outside this repository ({repo_root}); "
            "the walk-up reached a parent repository's board",
            f"run from the board's own repo, or pass --config {repo_root}/{CONFIG_FILENAME}",
        )
        return
    checks.ok("config.repo-root")


def _check_version_known(checks: _Checks, config_path: Path) -> bool:
    """False when the config declares a version this kit does not know.

    Read from the raw TOML rather than the loaded Config, because a version
    skew is exactly the case where loading fails - and naming the skew is
    more useful than reporting that the loader refused.
    """
    try:
        with config_path.open("rb") as f:
            raw = tomllib.load(f)
    except (OSError, tomllib.TOMLDecodeError):
        checks.skip("contract.version-known", "the config is not readable TOML; see config.loads")
        return True
    contract = raw.get("contract")
    declared = contract.get("version") if isinstance(contract, dict) else None
    if not isinstance(declared, int) or isinstance(declared, bool):
        checks.skip(
            "contract.version-known",
            "the config declares no integer [contract] version; see config.loads",
        )
        return True
    if declared not in SUPPORTED_CONTRACT_VERSIONS:
        if declared == 1:
            # An older config, not a newer kit: name the exact migration.
            remedy = (
                'add `staging = "working-dir"` or `staging = "repo-native"` to every '
                "[routes.<name>] table (which read contract the transport honors), "
                "then set [contract] version = 2"
            )
        else:
            remedy = "upgrade boardkit to a version that knows this contract"
        checks.error(
            "contract.version-known",
            f"the config declares contract version {declared}; this boardkit supports "
            f"{sorted(SUPPORTED_CONTRACT_VERSIONS)}",
            remedy,
        )
        return False
    checks.ok("contract.version-known")
    return True


def _check_config_loads(checks: _Checks, config_path: Path, version_known: bool) -> Config | None:
    if not version_known:
        checks.skip("config.loads", "the declared contract version is unknown to this boardkit")
        return None
    try:
        config = load_config(config_path)
    except (FileNotFoundError, ValueError) as exc:
        checks.error(
            "config.loads",
            f"{type(exc).__name__}: {exc}",
            "fix the config against the schema in the boardkit README, then re-run doctor",
        )
        return None
    checks.ok("config.loads")
    return config


def _check_docs_present(checks: _Checks, root: Path) -> list[Path]:
    missing = [dest for _name, dest in CONTRACT_DOCS if not (root / dest).is_file()]
    if missing:
        checks.error(
            "docs.present",
            "missing board docs: " + ", ".join(str(p) for p in missing),
            "copy them from the kit's templates, or re-run `boardkit init` in a clean directory",
        )
    else:
        checks.ok("docs.present")
    return [root / dest for _name, dest in CONTRACT_DOCS if (root / dest).is_file()]


def _check_docs_stamped(checks: _Checks, root: Path, version: int) -> None:
    problems = []
    for _name, dest in CONTRACT_DOCS:
        text = read_text_or_none(root / dest)
        if text is None:
            continue  # docs.present already named it
        stamp = read_stamp(text)
        if stamp is None:
            problems.append(f"{dest} carries no contract stamp")
        elif stamp != version:
            problems.append(f"{dest} is stamped v{stamp}, config declares v{version}")
    if problems:
        checks.error(
            "contract.docs-stamped",
            "; ".join(problems),
            "re-copy the docs from a boardkit at this contract version",
        )
        return
    checks.ok("contract.docs-stamped")


def _check_skills(checks: _Checks, home: Path, repo_root: Path, version: int) -> None:
    installed: dict[str, Path] = {}
    absent = []
    for name in BOARD_SKILLS:
        found = next((p for p in skill_paths(name, home, repo_root) if p.is_file()), None)
        if found is None:
            absent.append(name)
        else:
            installed[name] = found

    if absent:
        searched = "; ".join(
            pattern.format(name=name, repo=repo_root)
            for name in absent
            for pattern in SKILL_SEARCH_PATTERNS
        )
        checks.warn(
            "skills.installed",
            f"board skills not installed: {', '.join(absent)} (searched {searched})",
            "install the board plugin, or dispatch the board's gates by hand",
        )
    else:
        checks.ok("skills.installed")

    if not installed:
        checks.skip(
            "contract.skills-declared", "no board skills are installed; see skills.installed"
        )
        return
    problems = []
    for name, path in sorted(installed.items()):
        text = read_text_or_none(path)
        declared = skill_contract_version(text) if text is not None else None
        if declared is None:
            problems.append(f"{name} ({path}) declares no `metadata.{SKILL_METADATA_KEY}`")
        elif declared != version:
            problems.append(f"{name} declares contract v{declared}, config declares v{version}")
    if problems:
        checks.error(
            "contract.skills-declared",
            "; ".join(problems),
            f"update the skill's frontmatter to `metadata: {{{SKILL_METADATA_KEY}: {version}}}`",
        )
        return
    checks.ok("contract.skills-declared")


def _check_review_tooling(checks: _Checks, root: Path) -> None:
    dest = CONTRACT_DOC_DESTS[REVIEW_TOOLING_TEMPLATE]
    current = read_text_or_none(root / dest)
    shipped = read_text_or_none(TEMPLATES_DIR / REVIEW_TOOLING_TEMPLATE)
    if current is None or shipped is None:
        reason = f"{dest} is not readable; see docs.present"
        checks.skip("review-tooling.filled", reason)
        checks.skip("review-tooling.placeholders", reason)
        return

    unfilled = unfilled_sections(current, shipped)
    if unfilled:
        present = sections(current)
        described = [
            f"'{h}' is unchanged from the shipped template" if h in present else f"'{h}' is missing"
            for h in unfilled
        ]
        checks.error(
            "review-tooling.filled",
            f"{dest}: " + "; ".join(described),
            "write the repo's actual tools and harness bindings into those sections",
        )
    else:
        checks.ok("review-tooling.filled")

    left = section_placeholders(current)
    if left:
        described = [f"'{h}': {', '.join(tokens)}" for h, tokens in left.items()]
        checks.error(
            "review-tooling.placeholders",
            f"{dest} still carries template placeholders: " + "; ".join(described),
            "replace each angle-bracket placeholder with the real value",
        )
        return
    checks.ok("review-tooling.placeholders")


def _check_roles_filled(checks: _Checks, config: Config) -> None:
    unfilled = unfilled_routes(config.contract)
    problems = [
        f"role `{role}` routes to `{route}`, which still carries {', '.join(unfilled[route])}"
        for role, route_names in config.contract.roles.items()
        for route in route_names
        if route in unfilled
    ]
    if problems:
        checks.error(
            "roles.filled",
            "; ".join(problems),
            "fill the placeholder values in the [routes.*] tables of boardkit.toml",
        )
        return
    checks.ok("roles.filled")


def _check_pin_sources(checks: _Checks, config: Config) -> None:
    problems = missing_pin_sources(config.contract, config.root)
    if problems:
        checks.error(
            "routes.pin-source",
            "; ".join(f"[routes.{name}]: {reason}" for name, reason in problems),
            "point `pin_source` at a heading that exists, where live model pins are recorded",
        )
        return
    checks.ok("routes.pin-source")


def undefined_gate_tokens(cards: list[dict], process_text: str) -> dict[str, list[str]]:
    """Card id -> gate letters its `gates` string declares but the Gates section never defines."""
    gates_body = sections(process_text).get(GATES_SECTION)
    if gates_body is None:
        return {}
    defined = {match.group(1) for match in GATE_BULLET_RE.finditer(gates_body)}
    missing: dict[str, list[str]] = {}
    for card in cards:
        undefined = [t for t in gate_tokens(card.get("gates", "")) if t not in defined]
        if undefined:
            missing[card["id"]] = undefined
    return missing


def _check_gate_vocabulary(checks: _Checks, config: Config, cards: list[dict]) -> None:
    process_text = read_text_or_none(config.root / CONTRACT_DOC_DESTS["PROCESS.md"])
    if process_text is None:
        checks.skip("board.gate-vocabulary", "PROCESS.md is missing; see docs.present")
        return
    if sections(process_text).get(GATES_SECTION) is None:
        checks.skip("board.gate-vocabulary", "PROCESS.md has no Gates section")
        return
    missing = undefined_gate_tokens(cards, process_text)
    if missing:
        detail = "; ".join(
            f"{card_id} declares Gate {', Gate '.join(tokens)}"
            for card_id, tokens in sorted(missing.items())
        )
        checks.warn(
            "board.gate-vocabulary",
            f"gate letters no `- Gate <X>` bullet in PROCESS.md's Gates section defines: {detail}",
            "define each letter in the Gates section or correct the card's `gates` string; "
            "`boardkit dispatch-brief` refuses undefined letters at dispatch time",
        )
        return
    checks.ok("board.gate-vocabulary")


def _check_board(checks: _Checks, config: Config) -> None:
    try:
        result = build_board(config)
    except BoardError as exc:
        checks.error(
            "board.parses",
            "; ".join(exc.errors),
            "fix the cards named above, then run `boardkit check`",
        )
        checks.skip("board.gate-vocabulary", "the board does not parse; see board.parses")
        checks.skip("views.current", "the board does not parse; see board.parses")
        return
    checks.ok("board.parses")

    _check_gate_vocabulary(checks, config, result.cards)

    drift = view_drift(config, result.views)
    if drift:
        checks.error("views.current", "; ".join(drift), "run `boardkit render`")
        return
    checks.ok("views.current")


def _check_worktrees(checks: _Checks, cwd: Path) -> None:
    porcelain = _git_text(cwd, "worktree", "list", "--porcelain")
    if porcelain is None:
        checks.skip("worktrees.stray", "git is unavailable or this is not a git repository")
        return
    stray = stray_job_worktrees(porcelain)
    if stray:
        checks.warn(
            "worktrees.stray",
            f"{len(stray)} delegation worktree(s) still registered: " + ", ".join(stray),
            "remove each with `git worktree remove`, per the REVIEW-TOOLING transport rule",
        )
        return
    checks.ok("worktrees.stray")


def _check_agents_stamp(checks: _Checks, root: Path, version: int) -> None:
    dest = ENTRY_SHIM_DESTS[AGENTS_TEMPLATE]
    text = read_text_or_none(root / dest)
    if text is None:
        checks.warn(
            "entry.agents-stamp",
            f"{dest} is missing; agents have no canonical entry point",
            f"copy {AGENTS_TEMPLATE} from the kit, or merge its read order into your own",
        )
        return
    stamp = read_stamp(text)
    if stamp != version:
        found = "no stamp" if stamp is None else f"v{stamp}"
        checks.warn(
            "entry.agents-stamp",
            f"{dest} carries {found}, config declares v{version}; init leaves an existing "
            "entry file untouched, so this one may predate the contract",
            f"merge the current {AGENTS_TEMPLATE} into it and carry the stamp across",
        )
        return
    checks.ok("entry.agents-stamp")


def run_doctor(config_arg: str | None, cwd: Path, home: Path | None = None) -> DoctorReport:
    """Diagnose the whole installation. Reports failures; never raises them.

    `home` is a parameter so the skills quadrant is testable end to end; it
    defaults to the real home directory, which is what the CLI passes.
    """
    checks = _Checks()
    home = Path.home() if home is None else home

    config_path = _check_config_present(checks, config_arg, cwd)
    if config_path is None:
        checks.skip_remaining("no config file was found")
        return checks.report(None, None)

    _check_repo_root(checks, config_path, cwd)
    version_known = _check_version_known(checks, config_path)
    config = _check_config_loads(checks, config_path, version_known)
    if config is None:
        checks.skip_remaining("the config could not be loaded")
        return checks.report(config_path, None)

    version = config.contract.version
    root = config.root
    _check_docs_present(checks, root)
    _check_docs_stamped(checks, root, version)
    _check_skills(checks, home, root, version)
    _check_review_tooling(checks, root)
    _check_roles_filled(checks, config)
    _check_pin_sources(checks, config)
    _check_board(checks, config)
    home_finding = boardkit_home_finding(os.environ.get(BOARDKIT_HOME_VAR), INSTALL_ROOT, root)
    if home_finding is None:
        checks.ok("env.boardkit-home")
    else:
        checks.add(home_finding)
    _check_worktrees(checks, cwd)
    _check_agents_stamp(checks, root, version)

    checks.skip_remaining("not reached")
    return checks.report(config_path, version, contract_digest(config))


def render_text(report: DoctorReport) -> str:
    lines = [
        f"boardkit doctor: {report.config_path}"
        if report.config_path is not None
        else f"boardkit doctor: no {CONFIG_FILENAME} found"
    ]
    if report.contract_version is not None:
        lines.append(f"contract: v{report.contract_version}")
    if report.digest is not None:
        lines.append(f"digest: {report.digest}")
    lines.append("")
    for finding in report.findings:
        lines.append(f"{finding.severity.upper()}: {finding.check}: {finding.message}")
        lines.append(f"  fix: {finding.remedy}")
    for skip in report.skipped:
        lines.append(f"SKIP: {skip.check}: {skip.reason}")
    if report.findings or report.skipped:
        lines.append("")

    counts = (
        f"{len(report.passed)} passed, {len(report.errors)} error(s), "
        f"{len(report.warnings)} warning(s), {len(report.skipped)} skipped"
    )
    lines.append(f"{'FAIL' if report.errors else 'OK'}: {counts}")
    return "\n".join(lines) + "\n"


def render_json(report: DoctorReport) -> str:
    payload = {
        "config_path": str(report.config_path) if report.config_path is not None else None,
        "contract_version": report.contract_version,
        "digest": report.digest,
        "ok": not report.errors,
        "findings": [
            {
                "check": f.check,
                "severity": str(f.severity),
                "message": f.message,
                "remedy": f.remedy,
            }
            for f in report.findings
        ],
        "skipped": [{"check": s.check, "reason": s.reason} for s in report.skipped],
        "passed": list(report.passed),
    }
    return json.dumps(payload, indent=2) + "\n"
