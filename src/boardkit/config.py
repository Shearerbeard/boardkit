"""Load and validate boardkit.toml, and resolve which board to load.

The config file anchors three things: where the card registry lives (and
its id scheme), where review packets read/write, and which transport
serves each delegation role. All keys are required; unknown keys are a
hard error rather than silently ignored, so a typo in the config never
falls back to a stale default. The same strictness is the version skew
guard: an old kit reading a new config fails loudly on the sections it
does not know.

Board resolution (R5', ruled 2026-08-09) finds the board root before any
config loads. The order, first hit wins: an explicit `--board` value, the
`BOARDKIT_BOARD` environment variable, a walk-up `.boardkit/` directory
(committed `manifest.toml` plus a gitignored `local.toml` machine
overlay), a git common-dir fallback so linked worktrees resolve their
main checkout's `.boardkit/` with zero per-worktree setup, then the
legacy `boardkit.toml` walk-up so unported consumers keep working.
Manifest locations are scheme-prefixed store refs: `dir:` is the only
driver today, a bare string means `dir:`, the exact keyword `external`
defers to the overlay, and `linear:` is reserved. A malformed manifest
is a loud error, never a silent fall-through to the legacy walk-up.
"""

from __future__ import annotations

import os
import re
import subprocess
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple

from boardkit.contract import (
    CONTRACT_VERSION,
    ContractConfig,
    parse_contract,
    require_keys,
    require_table,
)

CONFIG_FILENAME = "boardkit.toml"
BOARDKIT_DIRNAME = ".boardkit"
MANIFEST_FILENAME = "manifest.toml"
LOCAL_FILENAME = "local.toml"
BOARD_ENV_VAR = "BOARDKIT_BOARD"

TOP_LEVEL_SECTIONS = {"board", "review", "contract", "routes", "roles", "charter"}
BOARD_KEYS = {"cards_dir", "id_prefix", "sentinel_ids"}
# The board-wide in-progress cap default. PROCESS.md board mechanics sets
# it at two; making it a config key retires the board.py hard-coded constant.
DEFAULT_WIP = 2
REVIEW_KEYS = {"repo", "output_dir"}
CHARTER_KEYS = {"owns", "not", "route"}
LANE_KEYS = {"name", "wip", "exempt"}

# `external` boards resolve through local.toml; everything else is a
# scheme-prefixed store ref. A relative directory literally named
# "external" must be written `dir:external`.
EXTERNAL_KEYWORD = "external"
KNOWN_SCHEMES = {"dir"}
RESERVED_SCHEMES = {"linear"}


@dataclass(frozen=True)
class LaneConfig:
    """One lane of the board-declared vocabulary (R1).

    `wip` is the lane's own in-progress cap, None for uncapped. `exempt`
    excludes the lane's cards from the board-wide WIP count - the config
    home for what used to be a stale PROCESS.md paragraph about a spike
    lane. Exemption is from the global count only; the lane's own `wip`
    and `serialize-with` still apply.
    """

    name: str
    wip: int | None = None
    exempt: bool = False


@dataclass(frozen=True)
class BoardConfig:
    cards_dir: Path
    id_prefix: str
    sentinel_ids: list[str]
    lanes: dict[str, LaneConfig]
    base_branch: str | None
    wip: int = DEFAULT_WIP


@dataclass(frozen=True)
class ReviewConfig:
    repo: Path
    output_dir: Path


@dataclass(frozen=True)
class CharterConfig:
    """The R10 board charter: what this board owns, refuses, and routes.

    `route` maps registry short-codes to a description of the work that
    belongs there. The admission test is one question: where does the
    diff land. Enforcement is prose-level in v1.
    """

    owns: str
    not_: str
    route: dict[str, str]


@dataclass(frozen=True)
class Config:
    root: Path
    board: BoardConfig
    review: ReviewConfig
    contract: ContractConfig
    charter: CharterConfig | None


def find_config(start: Path) -> Path:
    """Walk up from `start` looking for boardkit.toml."""
    for directory in (start, *start.resolve().parents):
        candidate = directory / CONFIG_FILENAME
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(
        f"no {CONFIG_FILENAME} found in {start.resolve()} or any parent directory"
    )


@dataclass(frozen=True)
class StoreRef:
    """A scheme-prefixed board location from the manifest (RULE-3)."""

    scheme: str
    value: str


def parse_store_ref(raw: str, context: str) -> StoreRef:
    if not isinstance(raw, str) or not raw:
        raise ValueError(f"{context}: location must be a non-empty string")
    if raw == EXTERNAL_KEYWORD:
        return StoreRef(scheme=EXTERNAL_KEYWORD, value="")
    scheme, sep, value = raw.partition(":")
    if not sep:
        return StoreRef(scheme="dir", value=raw)
    if scheme in RESERVED_SCHEMES:
        raise ValueError(f"{context}: store scheme '{scheme}:' is reserved, not implemented")
    if scheme not in KNOWN_SCHEMES:
        raise ValueError(
            f"{context}: unknown store scheme '{scheme}:'; known: "
            f"{', '.join(sorted(KNOWN_SCHEMES))}, or the keyword '{EXTERNAL_KEYWORD}'"
        )
    if not value:
        raise ValueError(f"{context}: '{scheme}:' needs a path after the scheme")
    return StoreRef(scheme=scheme, value=value)


# The manifest IS the family registry (R4, ruled 2026-08-09): rows may
# carry registry fields beyond `location`. They are optional because the
# ruled RULE-2 minimal shape is location + default; `dir:` boards
# self-describe, so `boardkit boards` fills their prefix from the board's
# own config, and a cached value is verified against it. Rows that cannot
# self-describe (external, hand-maintained, TODO-file surfaces) carry the
# fields in the family-home repo's manifest.
MANIFEST_BOARD_KEYS = {
    "location",
    "engine",
    "id_prefix",
    "scope",
    "status",
    "prefix_collision_ok",
}
ROW_STATUSES = {"active", "transitioning", "archived"}


@dataclass(frozen=True)
class ManifestEntry:
    location: StoreRef
    engine: str | None = None
    id_prefix: str | None = None
    scope: str | None = None
    status: str = "active"
    prefix_collision_ok: bool = False


@dataclass(frozen=True)
class Manifest:
    """A parsed `.boardkit/manifest.toml`, anchored at its repo root."""

    root: Path  # the directory that contains .boardkit/
    path: Path
    default: str
    boards: dict[str, ManifestEntry]


def load_manifest(boardkit_dir: Path) -> Manifest:
    path = boardkit_dir / MANIFEST_FILENAME
    with path.open("rb") as f:
        data = tomllib.load(f)
    unknown = data.keys() - {"default", "boards"}
    if unknown:
        raise ValueError(f"{path}: unknown top-level key(s): {sorted(unknown)}")
    boards_data = require_table("boards", data.get("boards", {}))
    if not boards_data:
        raise ValueError(f"{path}: no [boards.<code>] tables")
    boards: dict[str, ManifestEntry] = {}
    for code, row in boards_data.items():
        row_data = require_table(f"boards.{code}", row)
        context = f"{path}: [boards.{code}]"
        unknown_row = row_data.keys() - MANIFEST_BOARD_KEYS
        if unknown_row:
            raise ValueError(f"{context}: unknown key(s): {sorted(unknown_row)}")
        if "location" not in row_data:
            raise ValueError(f"{context}: missing required key 'location'")
        for key in ("engine", "id_prefix", "scope"):
            if key in row_data and (not isinstance(row_data[key], str) or not row_data[key]):
                raise ValueError(f"{context}: '{key}' must be a non-empty string")
        status = row_data.get("status", "active")
        if status not in ROW_STATUSES:
            raise ValueError(f"{context}: status '{status}' not in {sorted(ROW_STATUSES)}")
        collision_ok = row_data.get("prefix_collision_ok", False)
        if not isinstance(collision_ok, bool):
            raise ValueError(f"{context}: 'prefix_collision_ok' must be true or false")
        boards[code] = ManifestEntry(
            location=parse_store_ref(row_data["location"], context),
            engine=row_data.get("engine"),
            id_prefix=row_data.get("id_prefix"),
            scope=row_data.get("scope"),
            status=status,
            prefix_collision_ok=collision_ok,
        )
    default = data.get("default")
    if not isinstance(default, str) or not default:
        raise ValueError(f"{path}: 'default' must name a board short-code")
    if default not in boards:
        raise ValueError(
            f"{path}: default '{default}' is not a [boards.<code>] table "
            f"(known: {', '.join(sorted(boards))})"
        )
    return Manifest(root=boardkit_dir.parent.resolve(), path=path, default=default, boards=boards)


def load_overlay(boardkit_dir: Path) -> dict[str, Path]:
    """The machine-local `local.toml` overlay: short-code -> board root path."""
    path = boardkit_dir / LOCAL_FILENAME
    if not path.is_file():
        return {}
    with path.open("rb") as f:
        data = tomllib.load(f)
    unknown = data.keys() - {"boards"}
    if unknown:
        raise ValueError(f"{path}: unknown top-level key(s): {sorted(unknown)}")
    overlay: dict[str, Path] = {}
    for code, row in require_table("boards", data.get("boards", {})).items():
        row_data = require_table(f"boards.{code}", row)
        unknown_row = row_data.keys() - {"path"}
        if unknown_row:
            raise ValueError(f"{path}: [boards.{code}]: unknown key(s): {sorted(unknown_row)}")
        if not isinstance(row_data.get("path"), str) or not row_data["path"]:
            raise ValueError(f"{path}: [boards.{code}]: 'path' must be a non-empty string")
        overlay_path = Path(row_data["path"]).expanduser()
        if not overlay_path.is_absolute():
            # A relative overlay path would resolve against whatever cwd the
            # process happens to run from, silently landing on any directory
            # that holds a boardkit.toml. The overlay's contract is absolute
            # machine-local paths; refuse the relative form loudly.
            raise ValueError(
                f"{path}: [boards.{code}]: 'path' must be absolute "
                f"(got {row_data['path']!r}); a relative path resolves "
                "against the process working directory, not this file"
            )
        # Canonicalize: board roots are compared against `config.root`,
        # which is resolved, so an unresolved overlay path (a symlink, or
        # /tmp against /private/tmp) would silently match nothing and drop
        # this board's registry findings on the floor.
        overlay[code] = overlay_path.resolve()
    return overlay


def find_boardkit(start: Path) -> Path | None:
    """Walk up from `start` for a `.boardkit/` holding a manifest."""
    for directory in (start, *start.resolve().parents):
        candidate = directory / BOARDKIT_DIRNAME
        if (candidate / MANIFEST_FILENAME).is_file():
            return candidate
    return None


def git_common_boardkit(start: Path) -> Path | None:
    """The main checkout's `.boardkit/`, when `start` is in a linked worktree.

    `git rev-parse --git-common-dir` answers with an absolute path only from
    a linked worktree; from the main checkout it answers a relative `.git`,
    and the walk-up has already covered that case. This is what retires
    per-worktree symlinks: a worktree resolves its family board with zero
    setup.
    """
    try:
        result = subprocess.run(
            ["git", "-C", str(start), "rev-parse", "--git-common-dir"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    common = Path(result.stdout.strip())
    if not common.is_absolute():
        return None
    candidate = common.parent / BOARDKIT_DIRNAME
    return candidate if (candidate / MANIFEST_FILENAME).is_file() else None


class BoardResolution(NamedTuple):
    config_path: Path
    source: str  # which resolution step answered, for reporting
    code: str | None  # the board short-code, when one was involved
    # The `.boardkit/` whose manifest chose this board, when one did. The
    # registry that validates a board is the one that resolved it: for an
    # `external` board the manifest lives in the consuming repo, so neither
    # the board root nor the process cwd finds it reliably.
    boardkit_dir: Path | None = None


def _resolve_code(boardkit_dir: Path, code: str, source: str) -> BoardResolution:
    manifest = load_manifest(boardkit_dir)
    entry = manifest.boards.get(code)
    if entry is None:
        raise ValueError(
            f"{manifest.path}: no board '{code}' (known: {', '.join(sorted(manifest.boards))})"
        )
    ref = entry.location
    if ref.scheme == EXTERNAL_KEYWORD:
        overlay = load_overlay(boardkit_dir)
        root = overlay.get(code)
        if root is None:
            raise ValueError(
                f"board '{code}' is external; add its path to "
                f"{boardkit_dir / LOCAL_FILENAME} on this machine "
                f'([boards.{code}] path = "/absolute/path/to/board")'
            )
    else:
        root = (manifest.root / ref.value).resolve()
    config_path = root / CONFIG_FILENAME
    if not config_path.is_file():
        raise ValueError(
            f"board '{code}' resolved to {root}, but there is no {CONFIG_FILENAME} there"
        )
    return BoardResolution(
        config_path=config_path, source=source, code=code, boardkit_dir=boardkit_dir
    )


def _looks_like_path(selector: str) -> bool:
    """Path form requires a separator (`./board`, `/abs`); a bare name is a code.

    Deliberately not an existence check: a directory in cwd that happens to
    share a short-code's name must not hijack the code.
    """
    return os.sep in selector or selector in {".", "..", "~"} or selector.startswith("~/")


def _resolve_selector(selector: str, source: str, cwd: Path) -> BoardResolution:
    """A `--board` or `BOARDKIT_BOARD` value: a board path, or a short-code."""
    candidate = Path(selector).expanduser()
    if _looks_like_path(selector):
        if candidate.is_file() and candidate.name == CONFIG_FILENAME:
            return BoardResolution(config_path=candidate.resolve(), source=source, code=None)
        if candidate.is_dir() and (candidate / CONFIG_FILENAME).is_file():
            return BoardResolution(
                config_path=(candidate / CONFIG_FILENAME).resolve(), source=source, code=None
            )
        raise ValueError(f"{source}={selector!r} is a path with no {CONFIG_FILENAME}")
    boardkit_dir = find_boardkit(cwd) or git_common_boardkit(cwd)
    if boardkit_dir is None:
        raise ValueError(
            f"{source}={selector!r} reads as a board short-code, but no "
            f"{BOARDKIT_DIRNAME}/{MANIFEST_FILENAME} was found from {cwd.resolve()}"
        )
    return _resolve_code(boardkit_dir, selector, source)


def resolve_board(
    cwd: Path, board: str | None = None, env: Mapping[str, str] | None = None
) -> BoardResolution:
    """Resolve which board this invocation targets (the R5' order)."""
    env = os.environ if env is None else env
    if board is not None:
        return _resolve_selector(board, "--board", cwd)
    env_value = env.get(BOARD_ENV_VAR)
    if env_value:
        return _resolve_selector(env_value, BOARD_ENV_VAR, cwd)
    boardkit_dir = find_boardkit(cwd)
    if boardkit_dir is not None:
        manifest = load_manifest(boardkit_dir)
        return _resolve_code(boardkit_dir, manifest.default, str(boardkit_dir))
    boardkit_dir = git_common_boardkit(cwd)
    if boardkit_dir is not None:
        manifest = load_manifest(boardkit_dir)
        return _resolve_code(boardkit_dir, manifest.default, f"git common-dir {boardkit_dir}")
    try:
        return BoardResolution(config_path=find_config(cwd), source="legacy walk-up", code=None)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"no board found from {cwd.resolve()}: no --board, no {BOARD_ENV_VAR}, no "
            f"{BOARDKIT_DIRNAME}/{MANIFEST_FILENAME} in any parent or via the git "
            f"common-dir, and no legacy {CONFIG_FILENAME} in any parent"
        ) from None


@dataclass(frozen=True)
class RegistryRow:
    """One board of the family, as `boardkit boards` reports it."""

    code: str
    entry: ManifestEntry
    default: bool
    resolved_root: Path | None  # None when this machine cannot reach the board
    effective_prefix: str | None


def _board_declared_prefix(root: Path) -> tuple[str | None, bool]:
    """(declared id_prefix, readable) for a `dir:` board's own config.

    Light on purpose: enumeration must not fail because one board's
    delegation contract is mid-migration; the full strict load happens
    when that board is actually used. `readable` distinguishes a config
    that simply omits the key (fine, the row's cache stands in) from one
    where verification cannot run or would run against garbage: a
    missing or unparseable file, a `board` key that is not a table, or
    an `id_prefix` present with an invalid value. In each of those the
    caller reports rather than silently trusting the cache.
    """
    config_path = root / CONFIG_FILENAME
    if not config_path.is_file():
        return None, False
    try:
        with config_path.open("rb") as f:
            data = tomllib.load(f)
    except (OSError, tomllib.TOMLDecodeError, UnicodeDecodeError):
        return None, False
    board = data.get("board")
    if board is not None and not isinstance(board, dict):
        return None, False
    prefix = board.get("id_prefix") if isinstance(board, dict) else None
    if prefix is None:
        return None, True
    if not isinstance(prefix, str) or not prefix:
        return None, False
    return prefix, True


def _board_declared_sentinels(root: Path) -> list[str] | None:
    """The sentinel_ids a resolvable board's own config declares, read
    lightly. None when the config is missing or unparseable - sentinel
    membership cannot be established and the caller falls back to a
    warning rather than judging blind."""
    config_path = root / CONFIG_FILENAME
    if not config_path.is_file():
        return None
    try:
        with config_path.open("rb") as f:
            data = tomllib.load(f)
    except (OSError, tomllib.TOMLDecodeError, UnicodeDecodeError):
        return None
    board = data.get("board")
    sentinels = board.get("sentinel_ids") if isinstance(board, dict) else None
    if isinstance(sentinels, list) and all(isinstance(s, str) for s in sentinels):
        return sentinels
    return None


def registry_rows(boardkit_dir: Path) -> tuple[list[RegistryRow], list[str]]:
    """Every registry row plus the validation errors over the family.

    Errors cover cached-field drift (a `dir:` row whose id_prefix does not
    match the board's own config) and unmarked prefix collisions: a prefix
    shared by two or more rows is refused unless every row in the collision
    carries `prefix_collision_ok = true`. That is the R4 mint-time rule -
    the aura family's existing S-collisions stay describable as marked
    rows, while a new board silently claiming a taken prefix fails.
    """
    manifest = load_manifest(boardkit_dir)
    overlay = load_overlay(boardkit_dir)
    rows: list[RegistryRow] = []
    errors: list[str] = []
    for code, entry in sorted(manifest.boards.items()):
        if entry.location.scheme == EXTERNAL_KEYWORD:
            resolved_root = overlay.get(code)
        else:
            resolved_root = (manifest.root / entry.location.value).resolve()
        effective_prefix = entry.id_prefix
        if entry.location.scheme == "dir" and resolved_root is not None:
            declared, readable = _board_declared_prefix(resolved_root)
            if declared is None and entry.id_prefix is None:
                errors.append(
                    f"[boards.{code}]: no id_prefix on the row and none readable from "
                    f"{resolved_root / CONFIG_FILENAME}"
                )
            elif not readable:
                # The cache would win exactly when it cannot be checked;
                # report the unverifiable state instead of trusting it.
                errors.append(
                    f"[boards.{code}]: cached id_prefix '{entry.id_prefix}' cannot be "
                    f"verified - {resolved_root / CONFIG_FILENAME} is missing or "
                    "unparseable"
                )
            elif entry.id_prefix is not None and declared not in (None, entry.id_prefix):
                errors.append(
                    f"[boards.{code}]: cached id_prefix '{entry.id_prefix}' but the board "
                    f"declares '{declared}' ({resolved_root / CONFIG_FILENAME})"
                )
            effective_prefix = entry.id_prefix or declared
        rows.append(
            RegistryRow(
                code=code,
                entry=entry,
                default=code == manifest.default,
                resolved_root=resolved_root,
                effective_prefix=effective_prefix,
            )
        )
    by_prefix: dict[str, list[RegistryRow]] = {}
    for row in rows:
        if row.effective_prefix is not None:
            by_prefix.setdefault(row.effective_prefix, []).append(row)
    for prefix, group in sorted(by_prefix.items()):
        if len(group) > 1 and not all(r.entry.prefix_collision_ok for r in group):
            unmarked = ", ".join(r.code for r in group if not r.entry.prefix_collision_ok)
            claimants = ", ".join(r.code for r in group)
            # One error per row, each carrying its [boards.<code>] marker, so
            # board_row_errors' per-board filter keeps the collision visible
            # to `boardkit check` on every board it involves.
            for row in group:
                errors.append(
                    f"[boards.{row.code}]: id prefix '{prefix}' is claimed by "
                    f"{claimants}; collisions must be marked "
                    f"`prefix_collision_ok = true` on every row (unmarked: {unmarked})"
                )
    return rows, errors


def board_row_errors(config: Config, cwd: Path, boardkit_dir: Path | None = None) -> list[str]:
    """Registry errors that concern the board `config` describes, for `check`.

    Covers cached-field drift on this board's row and the R10 mirror rule:
    a chartered board's registry `scope` is the charter's `owns` one-liner,
    so the two must match byte for byte. Empty when no manifest is
    reachable from `cwd`: an unported repo has no registry to drift from.
    `boardkit_dir` names the registry that resolved this board; without one
    the search falls back to `cwd`.
    """
    boardkit_dir = boardkit_dir or find_boardkit(cwd) or git_common_boardkit(cwd)
    if boardkit_dir is None:
        return []
    rows, errors = registry_rows(boardkit_dir)
    mine = [row for row in rows if row.resolved_root == config.root]
    found = [e for e in errors if any(f"[boards.{row.code}]" in e for row in mine)]
    if config.charter is not None:
        for row in mine:
            if row.entry.scope is None:
                # Absence is drift too: deleting the mirror must not read
                # as a pass on a chartered board.
                found.append(
                    f"[boards.{row.code}]: no scope on the row; a chartered board "
                    f"mirrors its charter `owns` line here ('{config.charter.owns}')"
                )
            elif row.entry.scope != config.charter.owns:
                found.append(
                    f"[boards.{row.code}]: scope is the charter `owns` mirror and they "
                    f"differ (row: '{row.entry.scope}'; charter: '{config.charter.owns}')"
                )
    return found


def card_ref_findings(
    cards: list[dict], cwd: Path, boardkit_dir: Path | None = None
) -> tuple[list[str], list[str]]:
    """(errors, warnings) for the cards' qualified cross-board refs (R3).

    The short-code must be a registry row and the id must fit that row's
    prefix scheme when one is known. A non-prefix id against a board whose
    own config this machine can read is judged against that board's
    declared sentinel ids - a sentinel passes, anything else is an error.
    Where the board is unreachable or its config unreadable, sentinel
    membership cannot be established and the mismatch stays a warning.
    Cards that carry refs with no registry reachable at all are an error:
    resolution goes through the registry, so its absence must not read as
    a pass.
    """
    with_refs = [(card, card.get("refs")) for card in cards if card.get("refs")]
    if not with_refs:
        return [], []
    boardkit_dir = boardkit_dir or find_boardkit(cwd) or git_common_boardkit(cwd)
    if boardkit_dir is None:
        carded = ", ".join(sorted({card["_file"] for card, _ in with_refs}))
        return [
            f"cards carry refs but no {BOARDKIT_DIRNAME}/{MANIFEST_FILENAME} is "
            f"reachable from {cwd.resolve()} to validate them against ({carded})"
        ], []
    rows, _errors = registry_rows(boardkit_dir)
    by_code = {row.code: row for row in rows}
    errors: list[str] = []
    warnings: list[str] = []
    for card, refs in with_refs:
        for ref in refs:
            code, _sep, ref_id = ref.partition("/")
            row = by_code.get(code)
            if row is None:
                errors.append(
                    f"{card['_file']}: ref '{ref}' names unknown board '{code}' "
                    f"(known: {', '.join(sorted(by_code))})"
                )
                continue
            prefix = row.effective_prefix
            if prefix is not None and not re.fullmatch(re.escape(prefix) + r"\d+", ref_id):
                sentinels = (
                    _board_declared_sentinels(row.resolved_root)
                    if row.resolved_root is not None
                    else None
                )
                if sentinels is None:
                    # The board is unreachable or its config unreadable, so
                    # sentinel membership is not knowable here; warn.
                    warnings.append(
                        f"{card['_file']}: ref '{ref}' does not match board '{code}' "
                        f"prefix scheme '{prefix}<n>' (a sentinel id is fine; check the spelling)"
                    )
                elif ref_id not in sentinels:
                    errors.append(
                        f"{card['_file']}: ref '{ref}' matches neither board '{code}' "
                        f"prefix scheme '{prefix}<n>' nor its declared sentinel ids"
                    )
            if row.resolved_root is None:
                warnings.append(
                    f"{card['_file']}: ref '{ref}' points at a board this machine "
                    f"does not resolve (informational ref; add local.toml to inspect it)"
                )
    return errors, warnings


def charter_route_errors(config: Config, cwd: Path, boardkit_dir: Path | None = None) -> list[str]:
    """Charter route targets that do not resolve to a registry short-code.

    Validation needs a registry; with no manifest reachable there is
    nothing to resolve against, and the charter stays prose. That is the
    v1 enforcement level the 2026-08-09 interview accepted.
    """
    if config.charter is None or not config.charter.route:
        return []
    boardkit_dir = boardkit_dir or find_boardkit(cwd) or git_common_boardkit(cwd)
    if boardkit_dir is None:
        return []
    manifest = load_manifest(boardkit_dir)
    return [
        f"[charter.route]: '{code}' is not a registry short-code "
        f"(known: {', '.join(sorted(manifest.boards))})"
        for code in sorted(config.charter.route)
        if code not in manifest.boards
    ]


def load_config(path: Path | None) -> Config:
    config_path = path if path is not None else find_config(Path.cwd())
    if not config_path.is_file():
        raise FileNotFoundError(f"config file not found: {config_path}")

    with config_path.open("rb") as f:
        data = tomllib.load(f)

    unknown_top = data.keys() - TOP_LEVEL_SECTIONS
    if unknown_top:
        raise ValueError(f"{config_path}: unknown top-level key(s): {sorted(unknown_top)}")
    # A board written before the contract landed is a migration, not a typo,
    # so it gets named as one ahead of the generic missing-section error.
    if "contract" not in data:
        raise ValueError(
            f"{config_path}: no [contract] section; this config predates delegation "
            f"contract v{CONTRACT_VERSION}. Add [contract], [routes.<name>], and a "
            "[roles.<name>] table per required role, then run `boardkit doctor` to "
            "check the result."
        )
    missing_top = TOP_LEVEL_SECTIONS - {"charter"} - data.keys()
    if missing_top:
        raise ValueError(f"{config_path}: missing required section(s): {sorted(missing_top)}")

    board_data = require_table("board", data["board"])
    lanes_data = board_data.pop("lanes", [])
    base_branch = board_data.pop("base_branch", None)
    if base_branch is not None and (not isinstance(base_branch, str) or not base_branch):
        raise ValueError("[board]: base_branch must be a non-empty string")
    wip = board_data.pop("wip", DEFAULT_WIP)
    if not isinstance(wip, int) or isinstance(wip, bool) or wip < 0:
        raise ValueError("[board]: wip must be a non-negative integer")
    require_keys("board", board_data, BOARD_KEYS)
    if not isinstance(board_data["cards_dir"], str) or not board_data["cards_dir"]:
        raise ValueError("[board]: cards_dir must be a non-empty string path")
    if not isinstance(board_data["id_prefix"], str) or not board_data["id_prefix"]:
        raise ValueError("[board]: id_prefix must be a non-empty string")
    if not isinstance(board_data["sentinel_ids"], list) or not all(
        isinstance(s, str) for s in board_data["sentinel_ids"]
    ):
        raise ValueError("[board]: sentinel_ids must be a list of strings")
    lanes = _parse_lanes(lanes_data)

    review_data = require_table("review", data["review"])
    require_keys("review", review_data, REVIEW_KEYS)
    for key in ("repo", "output_dir"):
        if not isinstance(review_data[key], str) or not review_data[key]:
            raise ValueError(f"[review]: {key} must be a non-empty string path")

    root = config_path.parent.resolve()
    board = BoardConfig(
        cards_dir=(root / board_data["cards_dir"]).resolve(),
        id_prefix=board_data["id_prefix"],
        sentinel_ids=list(board_data["sentinel_ids"]),
        lanes=lanes,
        base_branch=base_branch,
        wip=wip,
    )
    review = ReviewConfig(
        repo=(root / review_data["repo"]).resolve(),
        output_dir=(root / review_data["output_dir"]).resolve(),
    )
    contract = parse_contract(data["contract"], data["routes"], data["roles"])
    charter = _parse_charter(data["charter"]) if "charter" in data else None
    return Config(root=root, board=board, review=review, contract=contract, charter=charter)


def _parse_lanes(lanes_data: object) -> dict[str, LaneConfig]:
    if not isinstance(lanes_data, list):
        raise ValueError("[board]: lanes must be an array of tables ([[board.lanes]])")
    lanes: dict[str, LaneConfig] = {}
    for index, row in enumerate(lanes_data):
        context = f"[[board.lanes]] entry {index + 1}"
        row_data = require_table(context, row)
        unknown = row_data.keys() - LANE_KEYS
        if unknown:
            raise ValueError(f"{context}: unknown key(s): {sorted(unknown)}")
        name = row_data.get("name")
        if not isinstance(name, str) or not name:
            raise ValueError(f"{context}: 'name' must be a non-empty string")
        if name in lanes:
            raise ValueError(f"{context}: duplicate lane '{name}'")
        wip = row_data.get("wip")
        if wip is not None and (not isinstance(wip, int) or isinstance(wip, bool) or wip < 0):
            raise ValueError(f"{context}: 'wip' must be a non-negative integer")
        exempt = row_data.get("exempt", False)
        if not isinstance(exempt, bool):
            raise ValueError(f"{context}: 'exempt' must be true or false")
        lanes[name] = LaneConfig(name=name, wip=wip, exempt=exempt)
    return lanes


def _parse_charter(charter_data: object) -> CharterConfig:
    data = require_table("charter", charter_data)
    unknown = data.keys() - CHARTER_KEYS
    if unknown:
        raise ValueError(f"[charter]: unknown key(s): {sorted(unknown)}")
    for key in ("owns", "not"):
        if not isinstance(data.get(key), str) or not data[key]:
            raise ValueError(f"[charter]: '{key}' must be a non-empty string")
    if "route" not in data:
        # The charter schema is three keys; a charter that refuses work
        # with no routing table sends a dispatch a refusal and no
        # destination. An empty [charter.route] is an explicit statement;
        # a missing one is a hole.
        raise ValueError(
            "[charter]: missing 'route' table; map refused work to registry "
            "short-codes ([charter.route])"
        )
    route_data = require_table("charter.route", data.get("route", {}))
    for code, description in route_data.items():
        if not isinstance(description, str) or not description:
            raise ValueError(f"[charter.route]: '{code}' must map to a non-empty string")
    return CharterConfig(owns=data["owns"], not_=data["not"], route=dict(route_data))
