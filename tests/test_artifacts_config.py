"""Tests for the [artifacts] table, the overlay stores schema, and the grammar.

ADR 0001, settled OQ1 and section 5: the posture key lives in an optional
[artifacts] table, strict in both directions; the machine overlay gains a
[stores.<name>] table whose only key is `location`, a scheme-prefixed store
ref under the same grammar board locations already use (DOCKING.md
requirement 8), now with `git:` alongside `dir:`.
"""

from pathlib import Path

import pytest
from conftest import config_text

from boardkit.config import load_config, load_overlay, parse_store_ref


def _write(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    return path


# --- [artifacts] in boardkit.toml --------------------------------------------


def test_no_artifacts_table_means_ephemeral_defaults(tmp_path: Path) -> None:
    """Driver 7: a board whose config names no posture behaves exactly as today."""
    config = load_config(_write(tmp_path / "boardkit.toml", config_text()))
    assert config.artifacts.posture == "ephemeral"
    assert config.artifacts.store is None
    # The receipts directory defaults to a `receipts` sibling of cards_dir.
    assert config.artifacts.receipts_dir == config.board.cards_dir.parent / "receipts"


def test_artifacts_table_parses(tmp_path: Path) -> None:
    text = config_text() + (
        '\n[artifacts]\nposture = "sidecar"\nstore = "bk-sidecar"\n'
        'receipts_dir = "docs/board/receipts"\n'
    )
    config = load_config(_write(tmp_path / "boardkit.toml", text))
    assert config.artifacts.posture == "sidecar"
    assert config.artifacts.store == "bk-sidecar"
    assert config.artifacts.receipts_dir == (tmp_path / "docs" / "board" / "receipts").resolve()


def test_unknown_artifacts_key_is_an_error(tmp_path: Path) -> None:
    text = config_text() + '\n[artifacts]\nposture = "ephemeral"\nbucket = "s3"\n'
    with pytest.raises(ValueError, match=r"\[artifacts\]: unknown key"):
        load_config(_write(tmp_path / "boardkit.toml", text))


def test_an_unknown_posture_is_an_error_naming_the_three(tmp_path: Path) -> None:
    text = config_text() + '\n[artifacts]\nposture = "cloud"\n'
    with pytest.raises(ValueError, match="posture 'cloud' not in"):
        load_config(_write(tmp_path / "boardkit.toml", text))


def test_sidecar_without_a_store_name_is_an_error(tmp_path: Path) -> None:
    text = config_text() + '\n[artifacts]\nposture = "sidecar"\n'
    with pytest.raises(ValueError, match="requires a 'store'"):
        load_config(_write(tmp_path / "boardkit.toml", text))


def test_artifacts_written_as_a_scalar_is_a_config_error(tmp_path: Path) -> None:
    text = 'artifacts = "sidecar"\n' + config_text()
    with pytest.raises(ValueError, match=r"\[artifacts\]: must be a table"):
        load_config(_write(tmp_path / "boardkit.toml", text))


# --- The store-ref grammar -----------------------------------------------------


def test_git_is_now_a_known_scheme() -> None:
    ref = parse_store_ref("git:/abs/sidecar.git", "test")
    assert ref.scheme == "git" and ref.value == "/abs/sidecar.git"


def test_an_unknown_scheme_errors_naming_the_schemes_that_exist() -> None:
    with pytest.raises(ValueError, match=r"unknown store scheme 's3:'.*dir.*git"):
        parse_store_ref("s3:bucket", "test")


def test_a_reserved_scheme_is_refused_as_reserved() -> None:
    with pytest.raises(ValueError, match="reserved"):
        parse_store_ref("linear:bk", "test")


def test_bare_string_means_dir_and_external_defers() -> None:
    assert parse_store_ref("relative/board", "test").scheme == "dir"
    assert parse_store_ref("external", "test").scheme == "external"


# --- The overlay's [stores.<name>] schema --------------------------------------


def _overlay(tmp_path: Path, local_toml: str) -> Path:
    boardkit_dir = tmp_path / ".boardkit"
    boardkit_dir.mkdir(exist_ok=True)
    (boardkit_dir / "local.toml").write_text(local_toml, encoding="utf-8")
    return boardkit_dir


def test_stores_rows_parse(tmp_path: Path) -> None:
    boardkit_dir = _overlay(
        tmp_path,
        f'[stores.bk-sidecar]\nlocation = "dir:{tmp_path}/sidecar"\n\n'
        '[stores.remote]\nlocation = "git:https://example.com/sidecar.git"\n',
    )
    overlay = load_overlay(boardkit_dir)
    assert overlay.stores["bk-sidecar"].scheme == "dir"
    assert overlay.stores["remote"].value == "https://example.com/sidecar.git"


def test_boards_rows_are_untouched(tmp_path: Path) -> None:
    boardkit_dir = _overlay(tmp_path, f'[boards.aura]\npath = "{tmp_path}/aura"\n')
    overlay = load_overlay(boardkit_dir)
    assert overlay.boards["aura"] == (tmp_path / "aura").resolve()
    assert overlay.stores == {}


def test_an_unknown_stores_row_key_is_an_error(tmp_path: Path) -> None:
    boardkit_dir = _overlay(
        tmp_path, f'[stores.bk-sidecar]\nlocation = "dir:{tmp_path}/s"\nbranch = "main"\n'
    )
    with pytest.raises(ValueError, match=r"\[stores\.bk-sidecar\]: unknown key"):
        load_overlay(boardkit_dir)


def test_a_relative_dir_store_location_is_refused(tmp_path: Path) -> None:
    boardkit_dir = _overlay(tmp_path, '[stores.bk-sidecar]\nlocation = "dir:relative/s"\n')
    with pytest.raises(ValueError, match="must be absolute"):
        load_overlay(boardkit_dir)


def test_a_relative_git_path_is_refused_but_a_url_is_not(tmp_path: Path) -> None:
    boardkit_dir = _overlay(tmp_path, '[stores.bk-sidecar]\nlocation = "git:relative/s.git"\n')
    with pytest.raises(ValueError, match="must be absolute"):
        load_overlay(boardkit_dir)


def test_external_is_not_a_store_location(tmp_path: Path) -> None:
    boardkit_dir = _overlay(tmp_path, '[stores.bk-sidecar]\nlocation = "external"\n')
    with pytest.raises(ValueError, match="cannot be 'external'"):
        load_overlay(boardkit_dir)


def test_an_absent_overlay_is_empty(tmp_path: Path) -> None:
    boardkit_dir = tmp_path / ".boardkit"
    boardkit_dir.mkdir()
    overlay = load_overlay(boardkit_dir)
    assert overlay.boards == {} and overlay.stores == {}
