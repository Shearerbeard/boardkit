"""Tests for the R4 registry: manifest rows, enumeration, validation.

The manifest IS the registry (interview decision 5, drain 7): rows carry
engine/id_prefix/scope, `dir:` boards self-describe and cached fields are
verified against them, and an unmarked prefix collision is refused while a
fully marked one stays describable (the aura family's real shape).
"""

from pathlib import Path

import pytest
from conftest import config_text

from boardkit.config import (
    board_row_errors,
    load_config,
    load_manifest,
    registry_rows,
)


def _board(root: Path, id_prefix: str = "S") -> Path:
    root.mkdir(parents=True, exist_ok=True)
    (root / "boardkit.toml").write_text(config_text(id_prefix=id_prefix), encoding="utf-8")
    return root


def _manifest(repo: Path, body: str) -> Path:
    bk = repo / ".boardkit"
    bk.mkdir(parents=True, exist_ok=True)
    (bk / "manifest.toml").write_text(body, encoding="utf-8")
    return bk


FULL_ROW = """\
default = "bk"

[boards.bk]
location = "dir:."
engine = "boardkit-v2"
id_prefix = "S"
scope = "the kit family"
"""


def test_registry_fields_parse(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _board(repo)
    bk = _manifest(repo, FULL_ROW)
    manifest = load_manifest(bk)
    entry = manifest.boards["bk"]
    assert entry.engine == "boardkit-v2"
    assert entry.id_prefix == "S"
    assert entry.scope == "the kit family"
    assert entry.status == "active"


def test_unknown_row_status_raises(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    bk = _manifest(
        repo,
        'default = "bk"\n[boards.bk]\nlocation = "dir:."\nstatus = "sleeping"\n',
    )
    with pytest.raises(ValueError, match="status 'sleeping'"):
        load_manifest(bk)


def test_dir_row_fills_prefix_from_the_board_config(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _board(repo, id_prefix="E")
    bk = _manifest(repo, 'default = "bk"\n[boards.bk]\nlocation = "dir:."\n')
    rows, errors = registry_rows(bk)
    assert errors == []
    assert rows[0].effective_prefix == "E"


def test_cached_prefix_drift_is_an_error(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _board(repo, id_prefix="E")
    bk = _manifest(
        repo,
        'default = "bk"\n[boards.bk]\nlocation = "dir:."\nid_prefix = "S"\n',
    )
    _rows, errors = registry_rows(bk)
    assert len(errors) == 1
    assert "cached id_prefix 'S'" in errors[0]
    assert "declares 'E'" in errors[0]


def test_unverifiable_cached_prefix_is_an_error(tmp_path: Path) -> None:
    """S18 Gate A: the cache must not win exactly when it cannot be checked.
    A missing or unparseable board config with a cached prefix reports."""
    repo = tmp_path / "repo"
    board = repo / "gone"
    board.mkdir(parents=True)
    (board / "boardkit.toml").write_text("[board\nbroken", encoding="utf-8")
    bk = _manifest(
        repo,
        'default = "bk"\n[boards.bk]\nlocation = "dir:gone"\nid_prefix = "S"\n',
    )
    _rows, errors = registry_rows(bk)
    assert len(errors) == 1
    assert "cannot be verified" in errors[0]

    # A readable config that simply omits id_prefix stays clean: the
    # row's cache legitimately stands in.
    (board / "boardkit.toml").write_text(
        '[board]\ncards_dir = "cards"\n', encoding="utf-8"
    )
    _rows, errors = registry_rows(bk)
    assert errors == []

    # A present-but-invalid id_prefix is not an absent key: the cache
    # must not win against garbage (S18 fix re-review).
    (board / "boardkit.toml").write_text(
        '[board]\ncards_dir = "cards"\nid_prefix = 5\n', encoding="utf-8"
    )
    _rows, errors = registry_rows(bk)
    assert len(errors) == 1
    assert "cannot be verified" in errors[0]


def test_collision_reaches_the_involved_boards_check(tmp_path: Path) -> None:
    """S18 Gate A: board_row_errors keeps a collision visible to the very
    board being checked instead of dropping it at the marker filter."""
    repo = tmp_path / "repo"
    _board(repo / "one")
    _board(repo / "two")
    _manifest(
        repo,
        'default = "one"\n'
        '[boards.one]\nlocation = "dir:one"\n'
        '[boards.two]\nlocation = "dir:two"\n',
    )
    config = load_config(repo / "one" / "boardkit.toml")
    errors = board_row_errors(config, repo)
    assert any("id prefix 'S' is claimed by one, two" in e for e in errors)


def test_unmarked_prefix_collision_is_refused(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _board(repo / "one")
    _board(repo / "two")
    bk = _manifest(
        repo,
        'default = "one"\n'
        '[boards.one]\nlocation = "dir:one"\n'
        '[boards.two]\nlocation = "dir:two"\n',
    )
    _rows, errors = registry_rows(bk)
    # One error per involved row, each carrying its own [boards.<code>]
    # marker so the per-board check filter keeps collisions visible.
    assert len(errors) == 2
    assert all("id prefix 'S' is claimed by one, two" in e for e in errors)
    assert any(e.startswith("[boards.one]") for e in errors)
    assert any(e.startswith("[boards.two]") for e in errors)


def test_fully_marked_collision_is_describable(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _board(repo / "one")
    _board(repo / "two")
    bk = _manifest(
        repo,
        'default = "one"\n'
        '[boards.one]\nlocation = "dir:one"\nprefix_collision_ok = true\n'
        '[boards.two]\nlocation = "dir:two"\nprefix_collision_ok = true\n',
    )
    _rows, errors = registry_rows(bk)
    assert errors == []


def test_external_row_without_overlay_is_listed_unresolved(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _board(repo)
    bk = _manifest(
        repo,
        'default = "bk"\n'
        '[boards.bk]\nlocation = "dir:."\n'
        '[boards.aura]\nlocation = "external"\nengine = "boardkit-v2"\n'
        'id_prefix = "P"\nscope = "the aura family"\n',
    )
    rows, errors = registry_rows(bk)
    assert errors == []
    aura = next(r for r in rows if r.code == "aura")
    assert aura.resolved_root is None
    assert aura.effective_prefix == "P"


def test_external_row_with_overlay_resolves(tmp_path: Path) -> None:
    wiki = _board(tmp_path / "wiki", id_prefix="P")
    repo = tmp_path / "repo"
    _board(repo)
    bk = _manifest(
        repo,
        'default = "bk"\n'
        '[boards.bk]\nlocation = "dir:."\n'
        '[boards.aura]\nlocation = "external"\nid_prefix = "P"\n',
    )
    (bk / "local.toml").write_text(f'[boards.aura]\npath = "{wiki}"\n', encoding="utf-8")
    rows, _errors = registry_rows(bk)
    aura = next(r for r in rows if r.code == "aura")
    assert aura.resolved_root == wiki


def test_board_row_errors_scopes_to_this_board(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _board(repo, id_prefix="E")
    _board(repo / "other")
    _manifest(
        repo,
        'default = "bk"\n'
        '[boards.bk]\nlocation = "dir:."\nid_prefix = "S"\n'
        '[boards.other]\nlocation = "dir:other"\nid_prefix = "X"\n',
    )
    config = load_config(repo / "boardkit.toml")
    errors = board_row_errors(config, repo)
    assert len(errors) == 1  # my drift, not other's (other has its own drift)
    assert "[boards.bk]" in errors[0]


def test_board_row_errors_empty_without_manifest(tmp_path: Path) -> None:
    repo = _board(tmp_path / "repo")
    config = load_config(repo / "boardkit.toml")
    assert board_row_errors(config, repo) == []
