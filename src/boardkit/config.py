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

TOP_LEVEL_SECTIONS = {"board", "review", "contract", "routes", "roles"}
BOARD_KEYS = {"cards_dir", "id_prefix", "sentinel_ids"}
REVIEW_KEYS = {"repo", "output_dir"}

# `external` boards resolve through local.toml; everything else is a
# scheme-prefixed store ref. A relative directory literally named
# "external" must be written `dir:external`.
EXTERNAL_KEYWORD = "external"
KNOWN_SCHEMES = {"dir"}
RESERVED_SCHEMES = {"linear"}


@dataclass(frozen=True)
class BoardConfig:
    cards_dir: Path
    id_prefix: str
    sentinel_ids: list[str]


@dataclass(frozen=True)
class ReviewConfig:
    repo: Path
    output_dir: Path


@dataclass(frozen=True)
class Config:
    root: Path
    board: BoardConfig
    review: ReviewConfig
    contract: ContractConfig


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


# Registry row fields beyond `location` land with the S18 registry card;
# the manifest loader is strict so a typo never silently drops a field.
MANIFEST_BOARD_KEYS = {"location"}


@dataclass(frozen=True)
class ManifestEntry:
    location: StoreRef


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
        unknown_row = row_data.keys() - MANIFEST_BOARD_KEYS
        if unknown_row:
            raise ValueError(f"{path}: [boards.{code}]: unknown key(s): {sorted(unknown_row)}")
        if "location" not in row_data:
            raise ValueError(f"{path}: [boards.{code}]: missing required key 'location'")
        boards[code] = ManifestEntry(
            location=parse_store_ref(row_data["location"], f"{path}: [boards.{code}]")
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
        overlay[code] = Path(row_data["path"]).expanduser()
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
    return BoardResolution(config_path=config_path, source=source, code=code)


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
    missing_top = TOP_LEVEL_SECTIONS - data.keys()
    if missing_top:
        raise ValueError(f"{config_path}: missing required section(s): {sorted(missing_top)}")

    board_data = require_table("board", data["board"])
    require_keys("board", board_data, BOARD_KEYS)
    if not isinstance(board_data["cards_dir"], str) or not board_data["cards_dir"]:
        raise ValueError("[board]: cards_dir must be a non-empty string path")
    if not isinstance(board_data["id_prefix"], str) or not board_data["id_prefix"]:
        raise ValueError("[board]: id_prefix must be a non-empty string")
    if not isinstance(board_data["sentinel_ids"], list) or not all(
        isinstance(s, str) for s in board_data["sentinel_ids"]
    ):
        raise ValueError("[board]: sentinel_ids must be a list of strings")

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
    )
    review = ReviewConfig(
        repo=(root / review_data["repo"]).resolve(),
        output_dir=(root / review_data["output_dir"]).resolve(),
    )
    contract = parse_contract(data["contract"], data["routes"], data["roles"])
    return Config(root=root, board=board, review=review, contract=contract)
