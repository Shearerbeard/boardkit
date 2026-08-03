"""The delegation contract: which roles exist and what transports serve them.

Lowest layer of the package — it imports nothing from boardkit, so config,
board, and the diagnostic commands can all depend on it. It owns the
contract version, the kit's shipped data paths, the strict-key helper the
config loader shares, and the placeholder vocabulary that tells a filled-in
board apart from a freshly scaffolded one.

A route names a transport (`adapter`) and where its live model pins are read
at dispatch time (`pin_source`). `pin_source` is a pointer, never a pin: model
ids go stale, so the contract records where to look them up instead of
copying them. `preflight` strings are printed by boardkit and run by the
caller — a diagnostic that shells out to repo config is a code-execution
surface, so this kit never executes them.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # a type-only import: config imports this module, never the reverse
    from boardkit.config import Config

CONTRACT_VERSION = 1
SUPPORTED_CONTRACT_VERSIONS = frozenset({1})

# Every board declares a transport for each of these; there is no default
# route, because a silently defaulted reviewer is an ungraded reviewer.
REQUIRED_ROLES = (
    "executor",
    "code-review",
    "prose-review",
    "frontier-review",
    "drift-audit",
    "canary",
)

CONTRACT_KEYS = {"version"}
ROUTE_KEYS = {"adapter", "skill", "pin_source", "preflight"}
ROLE_KEYS = {"routes"}

ROUTE_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PLACEHOLDER_RE = re.compile(r"<[^<>\n]+>")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$", re.MULTILINE)
# Shipped docs carry the stamp in whatever comment syntax their format has:
# an HTML comment in markdown, a `#` line in the hook sample.
STAMP_RE = re.compile(r"boardkit-contract: v(\d+)")

# The env var the entry shims tell a fresh agent to export, and the worktree
# path a delegation harness leaves behind. Both are named in shipped prose
# and read back by the diagnostics, so they live here rather than in either.
BOARDKIT_HOME_VAR = "BOARDKIT_HOME"
JOB_WORKTREE_GLOB = ".agy-mcp/worktrees/job-*"

DATA_DIR = Path(__file__).resolve().parent / "data"
TEMPLATES_DIR = DATA_DIR / "templates"

# (template filename, destination relative to the repo root). The contract
# docs are the subset a consumer repo is compared against doc by doc; the
# pre-commit sample carries a stamp too, but it is a hook, not policy.
CONTRACT_DOCS = (
    ("PROCESS.md", Path("docs/board/PROCESS.md")),
    ("MODEL-CLASSES.md", Path("docs/board/MODEL-CLASSES.md")),
    ("REVIEW-TOOLING.md.template", Path("docs/board/REVIEW-TOOLING.md")),
)
BOARD_DOCS = (
    *CONTRACT_DOCS,
    # Opt-in only: init writes the sample, never .git/hooks.
    ("pre-commit.sample", Path("docs/board/pre-commit.sample")),
)
# Init writes these only when absent, so a consumer's own entry file survives
# scaffolding — which is also why their stamp is a warning, not an error.
ENTRY_SHIMS = (
    ("AGENTS.md.template", Path("AGENTS.md")),
    ("CLAUDE.md.template", Path("CLAUDE.md")),
    ("GEMINI.md.template", Path("GEMINI.md")),
)


@dataclass(frozen=True)
class Route:
    name: str
    adapter: str
    skill: str
    pin_source: str
    preflight: tuple[str, ...]


@dataclass(frozen=True)
class ContractConfig:
    version: int
    routes: dict[str, Route]
    roles: dict[str, tuple[str, ...]]


@dataclass(frozen=True)
class Resolution:
    """One role resolved to the transport that serves it.

    `position` is (index, of) for the route chosen — always the first, because
    boardkit fails closed rather than silently walking past a broken route.
    `fallbacks` are printed so the caller can walk them deliberately.
    """

    role: str
    route: Route
    fallbacks: tuple[Route, ...]
    position: tuple[int, int]


class ContractError(Exception):
    """A role could not be resolved to a usable transport."""


def require_table(section_name: str, value: object) -> dict:
    """A section written as a scalar is a config error, not a crash."""
    if not isinstance(value, dict):
        raise ValueError(f"[{section_name}]: must be a table, not {type(value).__name__}")
    return value


def require_keys(section_name: str, data: dict, allowed: set[str]) -> None:
    """Strict in both directions: a missing key and a typo both raise."""
    missing = allowed - data.keys()
    if missing:
        raise ValueError(f"[{section_name}]: missing required key(s): {sorted(missing)}")
    unknown = data.keys() - allowed
    if unknown:
        raise ValueError(f"[{section_name}]: unknown key(s): {sorted(unknown)}")


def placeholders(text: str) -> list[str]:
    """Angle-bracket tokens a scaffolded template ships and a filled one does not."""
    return PLACEHOLDER_RE.findall(text)


def read_stamp(text: str) -> int | None:
    """The contract version a shipped doc declares, or None if it declares none.

    An unstamped doc is not a v0 doc — it is a doc from before stamping, or
    one a consumer wrote themselves, and the caller decides which.
    """
    match = STAMP_RE.search(text)
    return int(match.group(1)) if match else None


def _parse_version(contract: dict) -> int:
    require_table("contract", contract)
    require_keys("contract", contract, CONTRACT_KEYS)
    version = contract["version"]
    if not isinstance(version, int) or isinstance(version, bool):
        raise ValueError("[contract]: version must be an integer")
    if version not in SUPPORTED_CONTRACT_VERSIONS:
        supported = sorted(SUPPORTED_CONTRACT_VERSIONS)
        raise ValueError(
            f"[contract]: unsupported contract version {version}; "
            f"this boardkit supports {supported}"
        )
    return version


def _parse_route(name: str, data: dict) -> Route:
    if not ROUTE_NAME_RE.match(name):
        raise ValueError(
            f"[routes.{name}]: route name must be a lowercase slug "
            "(letters, digits, and single hyphens)"
        )
    section = f"routes.{name}"
    require_table(section, data)
    require_keys(section, data, ROUTE_KEYS)
    for key in ("adapter", "pin_source"):
        if not isinstance(data[key], str) or not data[key]:
            raise ValueError(f"[{section}]: {key} must be a non-empty string")
    # "" is the honest value for a transport that loads no child skill.
    if not isinstance(data["skill"], str):
        raise ValueError(f"[{section}]: skill must be a string")
    preflight = data["preflight"]
    if not isinstance(preflight, list) or not all(isinstance(s, str) for s in preflight):
        raise ValueError(f"[{section}]: preflight must be a list of strings")
    return Route(
        name=name,
        adapter=data["adapter"],
        skill=data["skill"],
        pin_source=data["pin_source"],
        preflight=tuple(preflight),
    )


def _parse_roles(roles: dict, declared: set[str]) -> dict[str, tuple[str, ...]]:
    require_table("roles", roles)
    unknown = roles.keys() - set(REQUIRED_ROLES)
    if unknown:
        raise ValueError(f"[roles]: unknown role(s): {sorted(unknown)}")
    missing = set(REQUIRED_ROLES) - roles.keys()
    if missing:
        raise ValueError(f"[roles]: missing required role(s): {sorted(missing)}")

    parsed: dict[str, tuple[str, ...]] = {}
    for role, data in roles.items():
        section = f"roles.{role}"
        require_table(section, data)
        require_keys(section, data, ROLE_KEYS)
        names = data["routes"]
        if not isinstance(names, list) or not all(isinstance(n, str) for n in names):
            raise ValueError(f"[{section}]: routes must be a list of route names")
        if not names:
            raise ValueError(f"[{section}]: routes must name at least one route")
        for route_name in names:
            if route_name not in declared:
                raise ValueError(f"[{section}]: route '{route_name}' is not declared in [routes]")
        parsed[role] = tuple(names)
    return parsed


def parse_contract(contract: dict, routes: dict, roles: dict) -> ContractConfig:
    """Validate the three contract tables together and freeze them.

    Route order inside a role is the fallback order the dispatcher walks, so
    the declared sequence is preserved rather than sorted.
    """
    version = _parse_version(contract)
    require_table("routes", routes)
    parsed_routes = {name: _parse_route(name, data) for name, data in routes.items()}
    parsed_roles = _parse_roles(roles, set(parsed_routes))
    return ContractConfig(version=version, routes=parsed_routes, roles=parsed_roles)


def read_text_or_none(path: Path) -> str | None:
    """File contents, or None when it cannot be read. For diagnostics only."""
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


def slugify(heading: str) -> str:
    """A markdown heading as its anchor, the way GitHub and Obsidian form it."""
    kept = re.sub(r"[^\w\s-]", "", heading.strip().lower())
    return re.sub(r"[\s_]+", "-", kept).strip("-")


def sections(text: str) -> dict[str, str]:
    """Every markdown heading mapped to its body.

    A section runs to the next heading of the same or higher level, so a
    consumer who fills a section in by adding subsections still compares as
    filled. The single walk here is what every section helper projects from.
    """
    matches = list(HEADING_RE.finditer(text))
    found: dict[str, str] = {}
    for index, match in enumerate(matches):
        level = len(match.group(1))
        end = len(text)
        for later in matches[index + 1 :]:
            if len(later.group(1)) <= level:
                end = later.start()
                break
        found.setdefault(match.group(2), text[match.end() : end])
    return found


def route_placeholders(route: Route) -> list[str]:
    """Placeholder tokens still sitting in a route's values."""
    return [
        token
        for value in (route.adapter, route.skill, route.pin_source, *route.preflight)
        for token in placeholders(value)
    ]


def pin_source_problem(route: Route, root: Path) -> str | None:
    """Why a route's `pin_source` does not resolve in this repo, or None.

    A pin source that points nowhere is worse than none at all: dispatch
    follows it expecting live model pins and finds a 404.
    """
    path_part, _, anchor = route.pin_source.partition("#")
    target = root / path_part
    if not target.is_file():
        return f"pin_source path `{path_part}` does not exist"
    if not anchor:
        return None
    text = read_text_or_none(target)
    if text is None:
        return f"pin_source file `{path_part}` could not be read"
    if anchor.lower() not in {slugify(heading) for heading in sections(text)}:
        return f"pin_source anchor `#{anchor}` matches no heading in `{path_part}`"
    return None


def missing_pin_sources(contract: ContractConfig, root: Path) -> list[tuple[str, str]]:
    """(route, reason) for every `pin_source` that does not resolve in the repo."""
    return [
        (name, problem)
        for name, route in contract.routes.items()
        if (problem := pin_source_problem(route, root)) is not None
    ]


def canonical_contract(contract: ContractConfig) -> str:
    """The contract tables as stable text, independent of how the TOML was laid out.

    Serialized as JSON rather than joined by delimiters: route values are free
    strings, so any separator can appear inside one. A `|`-joined preflight
    cannot tell `["a|b"]` from `["a", "b"]`, which is a digest collision
    between two genuinely different contracts. JSON escapes its own delimiters.

    `sort_keys` makes table order irrelevant, so reordering `[routes.*]` in the
    file does not read as a change. Arrays keep their order, which is what
    makes a role's fallback sequence significant.
    """
    payload = {
        "version": contract.version,
        "routes": {
            name: {
                "adapter": route.adapter,
                "skill": route.skill,
                "pin_source": route.pin_source,
                "preflight": list(route.preflight),
            }
            for name, route in contract.routes.items()
        },
        "roles": {role: list(names) for role, names in contract.roles.items()},
    }
    return json.dumps(payload, sort_keys=True, ensure_ascii=True, separators=(",", ":")) + "\n"


def contract_digest(config: Config) -> str:
    """A short fingerprint of everything a dispatch depends on.

    Covers the contract version, the consumer's three contract docs, and the
    contract tables. Only repo-relative paths are hashed, so a clone in another
    directory digests identically — the digest identifies the contract, not
    the machine. A brief whose digest differs from doctor's is stale.
    """
    digest = hashlib.sha256()
    digest.update(f"boardkit-contract:v{CONTRACT_VERSION}\n".encode())
    for _template, dest in CONTRACT_DOCS:
        path = config.root / dest
        data = path.read_bytes() if path.is_file() else b""
        # length-prefixed so two docs cannot concatenate into a third's bytes
        digest.update(f"{dest.as_posix()}:{len(data)}\n".encode())
        digest.update(data)
    digest.update(canonical_contract(config.contract).encode())
    return digest.hexdigest()[:12]


def resolve_role(config: Config, role: str) -> Resolution:
    """Resolve one role to the transport that serves it, or fail closed.

    Deliberately lazy: only the named role and its first route are validated.
    A board whose `canary` route is half-written must still dispatch its
    executor, or one unfinished binding blocks every gate on the board.
    """
    contract = config.contract
    if role not in contract.roles:
        raise ContractError(f"unknown role '{role}'; this board declares {sorted(contract.roles)}")

    names = contract.roles[role]
    route = contract.routes[names[0]]

    unfilled = route_placeholders(route)
    if unfilled:
        raise ContractError(
            f"role '{role}' resolves to route '{route.name}', which is still a template: "
            f"{', '.join(unfilled)}. Fill it in before dispatching."
        )

    problem = pin_source_problem(route, config.root)
    if problem is not None:
        raise ContractError(
            f"role '{role}' resolves to route '{route.name}', whose {problem}. "
            "A pin source that points nowhere cannot be read at dispatch time."
        )

    return Resolution(
        role=role,
        route=route,
        fallbacks=tuple(contract.routes[name] for name in names[1:]),
        position=(1, len(names)),
    )


def render_resolution_text(resolution: Resolution) -> str:
    """The resolution as flat `key: value` lines, one line per value."""
    route = resolution.route
    index, total = resolution.position
    lines = [
        f"role: {resolution.role}",
        f"route: {route.name} ({index} of {total})",
        f"adapter: {route.adapter}",
        f"skill: {route.skill}"
        if route.skill
        else "skill: none (this transport loads no child skill)",
        f"pin source: {route.pin_source}",
    ]
    lines.extend(f"preflight: {command}" for command in route.preflight)
    if not route.preflight:
        lines.append("preflight: none")
    lines.extend(f"fallback: {fallback.name}" for fallback in resolution.fallbacks)
    if not resolution.fallbacks:
        lines.append("fallback: none")
    return "\n".join(lines) + "\n"


def render_resolution_json(resolution: Resolution) -> str:
    index, total = resolution.position
    payload = {
        "role": resolution.role,
        "route": _route_payload(resolution.route),
        "position": {"index": index, "of": total},
        "fallbacks": [_route_payload(route) for route in resolution.fallbacks],
    }
    return json.dumps(payload, indent=2) + "\n"


def _route_payload(route: Route) -> dict:
    return {
        "name": route.name,
        "adapter": route.adapter,
        "skill": route.skill,
        "pin_source": route.pin_source,
        "preflight": list(route.preflight),
    }
