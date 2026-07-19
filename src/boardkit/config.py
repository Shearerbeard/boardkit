"""Load and validate boardkit.toml.

The config file anchors two things: where the card registry lives (and
its id scheme) and where review packets read/write. All keys are
required; unknown keys are a hard error rather than silently ignored,
so a typo in the config never falls back to a stale default.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

CONFIG_FILENAME = "boardkit.toml"

TOP_LEVEL_SECTIONS = {"board", "review"}
BOARD_KEYS = {"cards_dir", "id_prefix", "sentinel_ids"}
REVIEW_KEYS = {"repo", "output_dir"}


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


def find_config(start: Path) -> Path:
    """Walk up from `start` looking for boardkit.toml."""
    for directory in (start, *start.resolve().parents):
        candidate = directory / CONFIG_FILENAME
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(
        f"no {CONFIG_FILENAME} found in {start.resolve()} or any parent directory"
    )


def _require_keys(section_name: str, data: dict, allowed: set[str]) -> None:
    missing = allowed - data.keys()
    if missing:
        raise ValueError(f"[{section_name}]: missing required key(s): {sorted(missing)}")
    unknown = data.keys() - allowed
    if unknown:
        raise ValueError(f"[{section_name}]: unknown key(s): {sorted(unknown)}")


def load_config(path: Path | None) -> Config:
    config_path = path if path is not None else find_config(Path.cwd())
    if not config_path.is_file():
        raise FileNotFoundError(f"config file not found: {config_path}")

    with config_path.open("rb") as f:
        data = tomllib.load(f)

    unknown_top = data.keys() - TOP_LEVEL_SECTIONS
    if unknown_top:
        raise ValueError(f"{config_path}: unknown top-level key(s): {sorted(unknown_top)}")
    missing_top = TOP_LEVEL_SECTIONS - data.keys()
    if missing_top:
        raise ValueError(f"{config_path}: missing required section(s): {sorted(missing_top)}")

    board_data = data["board"]
    _require_keys("board", board_data, BOARD_KEYS)
    if not isinstance(board_data["id_prefix"], str) or not board_data["id_prefix"]:
        raise ValueError("[board]: id_prefix must be a non-empty string")
    if not isinstance(board_data["sentinel_ids"], list) or not all(
        isinstance(s, str) for s in board_data["sentinel_ids"]
    ):
        raise ValueError("[board]: sentinel_ids must be a list of strings")

    review_data = data["review"]
    _require_keys("review", review_data, REVIEW_KEYS)

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
    return Config(root=root, board=board, review=review)
