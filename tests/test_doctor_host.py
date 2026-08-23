"""Tests for the R6 host-repo hazard checks and the R7 parity check (S24,
with the shim convention S29 settled on).

Real git repos, tiny and local: the checks under test exist because of
real hosts (a board on a feature branch, a dirty wiki with unpushed
commits), so the fixtures reproduce those shapes rather than mocking git.
"""

import subprocess
from pathlib import Path

from conftest import config_text

from boardkit.config import load_config
from boardkit.contract import TEMPLATES_DIR
from boardkit.doctor import SHIM_TEMPLATES, _check_entry_parity, _check_host, _Checks

IDENTITY = ["-c", "user.email=t@t", "-c", "user.name=t"]

# The convention S29 settled on: doctor compares a shim against the text
# `boardkit init` scaffolds, so the fixtures scaffold it the same way.
SHIM = "Read `AGENTS.md` first; it is the stable agent handoff for this repo.\n"


def _git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(cwd), *IDENTITY, *args], check=True, capture_output=True)


def _repo(tmp_path: Path, base_branch: str | None = None) -> Path:
    tmp_path.mkdir(exist_ok=True)
    extra = f'base_branch = "{base_branch}"\n' if base_branch else ""
    config = config_text().replace("[review]", extra + "[review]", 1)
    (tmp_path / "boardkit.toml").write_text(config, encoding="utf-8")
    (tmp_path / "cards").mkdir(exist_ok=True)
    subprocess.run(["git", "init", "-q", "-b", "main", str(tmp_path)], check=True)
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "seed")
    return tmp_path


def _findings(checks: _Checks) -> dict[str, str]:
    return {f.check: f.message for f in checks.findings}


def test_base_branch_mismatch_warns(tmp_path: Path) -> None:
    repo = _repo(tmp_path, base_branch="main")
    _git(repo, "checkout", "-q", "-b", "feature/side")
    checks = _Checks()
    _check_host(checks, load_config(repo / "boardkit.toml"))
    assert "not the declared base 'main'" in _findings(checks)["host.base-branch"]


def test_base_branch_undeclared_is_a_skip_not_a_pass(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    checks = _Checks()
    _check_host(checks, load_config(repo / "boardkit.toml"))
    assert any(s.check == "host.base-branch" for s in checks.skipped)
    assert "host.base-branch" not in checks.passed


def test_dirty_tree_and_missing_upstream_warn(tmp_path: Path) -> None:
    # A clean repo with no upstream is still local-only state (S24 Gate A):
    # the branch - and the board on it - exists on this machine alone.
    repo = _repo(tmp_path, base_branch="main")
    checks = _Checks()
    _check_host(checks, load_config(repo / "boardkit.toml"))
    assert "no upstream" in _findings(checks)["host.tree-state"]
    (repo / "scratch.txt").write_text("x", encoding="utf-8")
    checks = _Checks()
    _check_host(checks, load_config(repo / "boardkit.toml"))
    assert "dirty tree" in _findings(checks)["host.tree-state"]


def test_unpushed_commits_warn_and_pushed_clean_passes(tmp_path: Path) -> None:
    origin = tmp_path / "origin.git"
    subprocess.run(["git", "init", "-q", "--bare", str(origin)], check=True)
    repo = _repo(tmp_path / "work")
    _git(repo, "remote", "add", "origin", str(origin))
    _git(repo, "push", "-q", "-u", "origin", "main")
    checks = _Checks()
    _check_host(checks, load_config(repo / "boardkit.toml"))
    assert "host.tree-state" in checks.passed
    _git(repo, "commit", "-q", "--allow-empty", "-m", "local only")
    checks = _Checks()
    _check_host(checks, load_config(repo / "boardkit.toml"))
    assert "1 unpushed commit(s)" in _findings(checks)["host.tree-state"]


def test_parity_shim_layout_passes(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text("# Agent instructions\n", encoding="utf-8")
    (tmp_path / "CLAUDE.md").write_text(SHIM, encoding="utf-8")
    checks = _Checks()
    _check_entry_parity(checks, tmp_path)
    assert "entry.parity" in checks.passed


def test_parity_accepts_the_shims_init_scaffolds(tmp_path: Path) -> None:
    """S29 acceptance: the convention is whatever `boardkit init` writes, so
    the shipped templates verbatim are the case that must pass."""
    (tmp_path / "AGENTS.md").write_text("# Agent instructions\n", encoding="utf-8")
    for name, template in SHIM_TEMPLATES.items():
        (tmp_path / name).write_text(
            (TEMPLATES_DIR / template).read_text(encoding="utf-8"), encoding="utf-8"
        )
    checks = _Checks()
    _check_entry_parity(checks, tmp_path)
    assert "entry.parity" in checks.passed


def test_parity_divergent_full_text_warns(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text("# Agent instructions\n", encoding="utf-8")
    (tmp_path / "CLAUDE.md").write_text("# Totally different rules\n", encoding="utf-8")
    checks = _Checks()
    _check_entry_parity(checks, tmp_path)
    assert "follow different rules" in _findings(checks)["entry.parity"]


def test_parity_absent_agents_and_absent_everything_warn(tmp_path: Path) -> None:
    checks = _Checks()
    _check_entry_parity(checks, tmp_path)
    assert "every harness runs blind" in _findings(checks)["entry.parity"]
    (tmp_path / "CLAUDE.md").write_text("# Rules\n", encoding="utf-8")
    checks = _Checks()
    _check_entry_parity(checks, tmp_path)
    assert "AGENTS.md does not" in _findings(checks)["entry.parity"]


def test_parity_agents_with_no_shims_warns(tmp_path: Path) -> None:
    """S24 Gate A: an AGENTS.md nothing points at leaves single-entry-file
    harnesses blind, which is not parity."""
    (tmp_path / "AGENTS.md").write_text("# Agent instructions\n", encoding="utf-8")
    checks = _Checks()
    _check_entry_parity(checks, tmp_path)
    assert "no shim points at it" in _findings(checks)["entry.parity"]
    # A repo with no shims is being told to write one, so this branch owes
    # the text itself, not only a pointer at where the text is stated: an
    # AGENTS.md that predates the convention has no section to point at.
    remedy = next(f for f in checks.findings if f.check == "entry.parity").remedy
    assert "Entry files and their shims" in remedy
    assert "`boardkit init` scaffolds" in remedy
    for name in SHIM_TEMPLATES:
        assert f'{name} reads "{SHIM.strip()}"' in remedy


def test_parity_shimlike_opening_with_own_rules_warns(tmp_path: Path) -> None:
    """S24 Gate A: mentioning AGENTS.md once does not make a divergent
    entry file a shim."""
    (tmp_path / "AGENTS.md").write_text("# Agent instructions\n", encoding="utf-8")
    body = "Read `AGENTS.md` first.\n\nAlways use tabs and never run the linter."
    (tmp_path / "CLAUDE.md").write_text(body, encoding="utf-8")
    checks = _Checks()
    _check_entry_parity(checks, tmp_path)
    assert "follow different rules" in _findings(checks)["entry.parity"]


def test_parity_short_divergent_shim_warns(tmp_path: Path) -> None:
    """The four evasions the R-wave review cycle found, one per round. Under
    the S29 convention none of them is the canonical text, so all four flag
    without doctor having to recognize what each one is doing."""
    (tmp_path / "AGENTS.md").write_text("# Agent instructions\n", encoding="utf-8")
    (tmp_path / "GEMINI.md").write_text(SHIM, encoding="utf-8")
    for body in (
        # A directive glued to the pointer sentence.
        "Read `AGENTS.md` first. Always use tabs.\n",
        "# CLAUDE.md\nAlways use tabs.\n",
        # A directive wearing heading syntax is still a directive.
        "Read `AGENTS.md` first.\n# Always use tabs\n",
        # Text after a stamp that closes mid-line is prose, not stamp.
        "Read `AGENTS.md` first.\n<!-- stamp\nstamp --> Always use tabs.\n",
        # One sentence that names AGENTS.md while contradicting it: the
        # limit the heuristic could not reach, and the reason it was
        # replaced.
        "Read `AGENTS.md` first, except for its commit rules, which are wrong.\n",
    ):
        (tmp_path / "CLAUDE.md").write_text(body, encoding="utf-8")
        checks = _Checks()
        _check_entry_parity(checks, tmp_path)
        assert "follow different rules" in _findings(checks)["entry.parity"], body


def test_parity_drops_only_a_title_that_is_the_files_own_name(tmp_path: Path) -> None:
    """The convention says the optional title is the file's own name, so the
    check drops exactly that and nothing else. Gate A round 1 finding 2: the
    dropped form is a real heading at column 0, so an indented title, a
    missing space, and a seven-hash run are all content."""
    (tmp_path / "AGENTS.md").write_text("# Agent instructions\n", encoding="utf-8")
    (tmp_path / "GEMINI.md").write_text(SHIM, encoding="utf-8")
    (tmp_path / "CLAUDE.md").write_text(f"# CLAUDE.md\n\n{SHIM}", encoding="utf-8")
    checks = _Checks()
    _check_entry_parity(checks, tmp_path)
    assert "entry.parity" in checks.passed

    for title in (
        "# AGENTS.md",  # a title naming another file is not this file's title
        "    # CLAUDE.md",  # indented: an indented code block, not a heading
        "#CLAUDE.md",  # no space: not a heading
        "####### CLAUDE.md",  # seven hashes: past the six markdown allows
    ):
        (tmp_path / "CLAUDE.md").write_text(f"{title}\n\n{SHIM}", encoding="utf-8")
        checks = _Checks()
        _check_entry_parity(checks, tmp_path)
        assert "CLAUDE.md" in _findings(checks)["entry.parity"], title
        assert "follow different rules" in _findings(checks)["entry.parity"], title


def test_parity_drops_only_comments_standing_on_their_own_lines(tmp_path: Path) -> None:
    """Gate A round 1 finding 1: the normalizer does not parse markdown, so
    every comment tolerance is somewhere a directive could hide. Only a
    well-formed comment opening a line and closing one drops out; anything
    looser is content and warns, including an unterminated `<!--` that a
    run-to-end-of-file rule would have let erase the whole file."""
    (tmp_path / "AGENTS.md").write_text("# Agent instructions\n", encoding="utf-8")
    (tmp_path / "GEMINI.md").write_text(SHIM, encoding="utf-8")
    for body in (
        # The reviewer's evasion: an indented code block whose `<!--` opens
        # a span that a run-to-EOF rule erases, directive and all.
        f"# CLAUDE.md\n\n{SHIM}\n    <!-- fenced\n    Always use tabs.\n",
        # An unterminated comment is content, not a licence to drop the rest.
        f"# CLAUDE.md\n\n{SHIM}\n<!-- Always use tabs.\n",
        # A comment that closes mid-line leaves prose beside it.
        "# CLAUDE.md\n\n<!-- stamp --> Always use tabs.\n",
        # An indented open is not a comment block, so the directive stands.
        f"# CLAUDE.md\n\n  <!-- stamp -->\n{SHIM}Always use tabs.\n",
        # Two comments where the first closes mid-line: a lazy span would
        # jump to the second close and swallow the directive between them.
        f"# CLAUDE.md\n\n<!-- a --> Always use tabs.\n<!-- b -->\n{SHIM}",
    ):
        (tmp_path / "CLAUDE.md").write_text(body, encoding="utf-8")
        checks = _Checks()
        _check_entry_parity(checks, tmp_path)
        assert "follow different rules" in _findings(checks)["entry.parity"], body


def test_parity_warns_on_a_faithful_rewording(tmp_path: Path) -> None:
    """The limit the S29 convention accepts, pinned so it stays deliberate:
    a shim that means the right thing in its own words still warns, and the
    remedy names the convention and where its text lives."""
    (tmp_path / "AGENTS.md").write_text("# Agent instructions\n", encoding="utf-8")
    (tmp_path / "GEMINI.md").write_text(SHIM, encoding="utf-8")
    (tmp_path / "CLAUDE.md").write_text(
        "# CLAUDE.md\n\nRead `AGENTS.md` first. It is the handoff for this repo.\n",
        encoding="utf-8",
    )
    checks = _Checks()
    _check_entry_parity(checks, tmp_path)
    finding = next(f for f in checks.findings if f.check == "entry.parity")
    assert finding.severity == "warn"
    assert "CLAUDE.md" in finding.message
    assert "GEMINI.md" not in finding.message
    assert "Entry files and their shims" in finding.remedy
    assert SHIM.strip() in finding.remedy


def test_parity_accepts_a_multiline_stamp(tmp_path: Path) -> None:
    """Round 4: a stamp spanning lines is boilerplate throughout, not
    substantive prose whose punctuation reads as directives."""
    (tmp_path / "AGENTS.md").write_text("# Agent instructions\n", encoding="utf-8")
    (tmp_path / "GEMINI.md").write_text(SHIM, encoding="utf-8")
    (tmp_path / "CLAUDE.md").write_text(
        f"# CLAUDE.md\n\n<!-- boardkit-contract: v2.\nGenerated stamp. -->\n\n{SHIM}",
        encoding="utf-8",
    )
    checks = _Checks()
    _check_entry_parity(checks, tmp_path)
    assert "entry.parity" in checks.passed


def test_parity_resolves_the_host_root_above_a_docked_board(tmp_path: Path) -> None:
    """S24 Gate A: for a .boardkit/boards/<code> layout the entry files
    live at the host repo root, not the board root."""
    host = _repo(tmp_path)
    (host / "AGENTS.md").write_text("# Agent instructions\n", encoding="utf-8")
    (host / "CLAUDE.md").write_text(SHIM, encoding="utf-8")
    board_root = host / ".boardkit" / "boards" / "bk"
    board_root.mkdir(parents=True)
    checks = _Checks()
    _check_entry_parity(checks, board_root)
    assert "entry.parity" in checks.passed
