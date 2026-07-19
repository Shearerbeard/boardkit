from pathlib import Path

import pytest

from boardkit.config import load_config


def _write(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    return path


def test_missing_required_key_raises(tmp_path: Path) -> None:
    config_path = _write(
        tmp_path / "boardkit.toml",
        """
        [board]
        cards_dir = "cards"
        id_prefix = "S"

        [review]
        repo = "."
        output_dir = "reviews"
        """,
    )
    with pytest.raises(ValueError, match="missing required key"):
        load_config(config_path)


def test_unknown_key_raises(tmp_path: Path) -> None:
    config_path = _write(
        tmp_path / "boardkit.toml",
        """
        [board]
        cards_dir = "cards"
        id_prefix = "S"
        sentinel_ids = ["MILESTONE"]
        unexpected = "nope"

        [review]
        repo = "."
        output_dir = "reviews"
        """,
    )
    with pytest.raises(ValueError, match="unknown key"):
        load_config(config_path)


def test_unknown_top_level_section_raises(tmp_path: Path) -> None:
    config_path = _write(
        tmp_path / "boardkit.toml",
        """
        [board]
        cards_dir = "cards"
        id_prefix = "S"
        sentinel_ids = ["MILESTONE"]

        [review]
        repo = "."
        output_dir = "reviews"

        [extra]
        foo = "bar"
        """,
    )
    with pytest.raises(ValueError, match="unknown top-level key"):
        load_config(config_path)


def test_missing_config_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_config(tmp_path / "does-not-exist.toml")


def test_valid_config_resolves_paths_relative_to_config_root(tmp_path: Path) -> None:
    config_path = _write(
        tmp_path / "boardkit.toml",
        """
        [board]
        cards_dir = "cards"
        id_prefix = "S"
        sentinel_ids = ["MILESTONE"]

        [review]
        repo = "."
        output_dir = "reviews"
        """,
    )
    config = load_config(config_path)
    assert config.board.cards_dir == (tmp_path / "cards").resolve()
    assert config.review.repo == tmp_path.resolve()
    assert config.review.output_dir == (tmp_path / "reviews").resolve()
