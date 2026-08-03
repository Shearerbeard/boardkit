"""Load and validate boardkit.toml.

The config file anchors three things: where the card registry lives (and
its id scheme), where review packets read/write, and which transport
serves each delegation role. All keys are required; unknown keys are a
hard error rather than silently ignored, so a typo in the config never
falls back to a stale default. The same strictness is the version skew
guard: an old kit reading a new config fails loudly on the sections it
does not know.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

from boardkit.contract import CONTRACT_VERSION, ContractConfig, parse_contract, require_keys

CONFIG_FILENAME = "boardkit.toml"

TOP_LEVEL_SECTIONS = {"board", "review", "contract", "routes", "roles"}
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

    board_data = data["board"]
    require_keys("board", board_data, BOARD_KEYS)
    if not isinstance(board_data["cards_dir"], str) or not board_data["cards_dir"]:
        raise ValueError("[board]: cards_dir must be a non-empty string path")
    if not isinstance(board_data["id_prefix"], str) or not board_data["id_prefix"]:
        raise ValueError("[board]: id_prefix must be a non-empty string")
    if not isinstance(board_data["sentinel_ids"], list) or not all(
        isinstance(s, str) for s in board_data["sentinel_ids"]
    ):
        raise ValueError("[board]: sentinel_ids must be a list of strings")

    review_data = data["review"]
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
