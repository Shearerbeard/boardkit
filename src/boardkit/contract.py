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

import re
from dataclasses import dataclass
from pathlib import Path

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
    unknown = roles.keys() - set(REQUIRED_ROLES)
    if unknown:
        raise ValueError(f"[roles]: unknown role(s): {sorted(unknown)}")
    missing = set(REQUIRED_ROLES) - roles.keys()
    if missing:
        raise ValueError(f"[roles]: missing required role(s): {sorted(missing)}")

    parsed: dict[str, tuple[str, ...]] = {}
    for role, data in roles.items():
        section = f"roles.{role}"
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
    parsed_routes = {name: _parse_route(name, data) for name, data in routes.items()}
    parsed_roles = _parse_roles(roles, set(parsed_routes))
    return ContractConfig(version=version, routes=parsed_routes, roles=parsed_roles)
