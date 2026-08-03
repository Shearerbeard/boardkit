"""Tests for boardkit.config.

The valid-config cases use the shared `config_text` helper so the schema
lives in one place; the malformation cases mutate that helper's output, so
each test says exactly which one thing it broke.
"""

from pathlib import Path

import pytest
from conftest import config_text

from boardkit.config import load_config


def _write(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    return path


def test_missing_required_key_raises(tmp_path: Path) -> None:
    config_path = _write(
        tmp_path / "boardkit.toml",
        config_text().replace('sentinel_ids = ["MILESTONE"]\n', ""),
    )
    with pytest.raises(ValueError, match="missing required key"):
        load_config(config_path)


def test_unknown_key_raises(tmp_path: Path) -> None:
    config_path = _write(
        tmp_path / "boardkit.toml",
        config_text().replace('id_prefix = "S"', 'id_prefix = "S"\nunexpected = "nope"'),
    )
    with pytest.raises(ValueError, match="unknown key"):
        load_config(config_path)


def test_unknown_top_level_section_raises(tmp_path: Path) -> None:
    config_path = _write(
        tmp_path / "boardkit.toml",
        config_text() + '\n[extra]\nfoo = "bar"\n',
    )
    with pytest.raises(ValueError, match="unknown top-level key"):
        load_config(config_path)


def test_missing_config_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_config(tmp_path / "does-not-exist.toml")


def test_valid_config_resolves_paths_relative_to_config_root(tmp_path: Path) -> None:
    config_path = _write(tmp_path / "boardkit.toml", config_text())
    config = load_config(config_path)
    assert config.board.cards_dir == (tmp_path / "cards").resolve()
    assert config.review.repo == tmp_path.resolve()
    assert config.review.output_dir == (tmp_path / "reviews").resolve()


@pytest.mark.parametrize("section", ["board", "review"])
def test_a_section_written_as_a_scalar_is_a_config_error(tmp_path: Path, section: str) -> None:
    """`board = "cards"` is a plausible typo; it must read as a config error
    rather than an AttributeError from inside the key checker."""
    body = config_text().split(f"[{section}]", 1)[1].split("\n[", 1)[0]
    # the scalar goes above every table header, or TOML reads it as a key of
    # whichever table precedes it rather than as the top-level section
    without_section = config_text().replace(f"[{section}]{body}\n", "")
    config_path = _write(tmp_path / "boardkit.toml", f'{section} = "nope"\n\n{without_section}')
    with pytest.raises(ValueError, match=rf"\[{section}\]: must be a table"):
        load_config(config_path)


def test_non_string_path_values_are_config_errors(tmp_path: Path) -> None:
    bad = _write(
        tmp_path / "boardkit.toml",
        config_text().replace('cards_dir = "cards"', "cards_dir = 7"),
    )
    with pytest.raises(ValueError, match="cards_dir"):
        load_config(bad)
