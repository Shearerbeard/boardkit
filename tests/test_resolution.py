"""Tests for the R5' board-resolution order in boardkit.config.

Each test builds the smallest filesystem that exercises one step of the
order: flag, env var, `.boardkit/` walk-up (manifest plus overlay), git
common-dir fallback, legacy walk-up. The git case uses a real linked
worktree because the fallback's whole point is zero per-worktree setup.
"""

import subprocess
from pathlib import Path

import pytest
from conftest import config_text

from boardkit.config import (
    BOARD_ENV_VAR,
    parse_store_ref,
    resolve_board,
)


def _board(root: Path) -> Path:
    """A minimal board root: boardkit.toml at `root`."""
    root.mkdir(parents=True, exist_ok=True)
    (root / "boardkit.toml").write_text(config_text(), encoding="utf-8")
    return root


def _manifest(repo: Path, body: str) -> Path:
    bk = repo / ".boardkit"
    bk.mkdir(parents=True, exist_ok=True)
    (bk / "manifest.toml").write_text(body, encoding="utf-8")
    return bk


def test_flag_path_beats_everything(tmp_path: Path) -> None:
    flag_board = _board(tmp_path / "flagged")
    repo = tmp_path / "repo"
    _board(repo)
    _manifest(repo, 'default = "other"\n[boards.other]\nlocation = "dir:."\n')
    resolution = resolve_board(
        repo, board=str(flag_board), env={BOARD_ENV_VAR: str(repo)}
    )
    assert resolution.config_path == flag_board / "boardkit.toml"
    assert resolution.source == "--board"


def test_env_beats_walk_up(tmp_path: Path) -> None:
    env_board = _board(tmp_path / "env-board")
    repo = tmp_path / "repo"
    _board(repo)
    _manifest(repo, 'default = "bk"\n[boards.bk]\nlocation = "dir:."\n')
    resolution = resolve_board(repo, env={BOARD_ENV_VAR: str(env_board)})
    assert resolution.config_path == env_board / "boardkit.toml"
    assert resolution.source == BOARD_ENV_VAR


def test_flag_short_code_resolves_via_manifest(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _board(repo / "boards" / "aux")
    _board(repo)
    _manifest(
        repo,
        'default = "main"\n'
        '[boards.main]\nlocation = "dir:."\n'
        '[boards.aux]\nlocation = "dir:boards/aux"\n',
    )
    resolution = resolve_board(repo / "src", board="aux", env={})
    assert resolution.config_path == (repo / "boards" / "aux" / "boardkit.toml").resolve()
    assert resolution.code == "aux"


def test_bare_name_is_a_code_even_when_a_directory_shares_it(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _board(repo)
    # A directory named like the code, holding its own boardkit.toml, must
    # not hijack the short-code; path form requires a separator.
    decoy = _board(repo / "aux")
    _manifest(
        repo,
        'default = "aux"\n[boards.aux]\nlocation = "dir:."\n',
    )
    resolution = resolve_board(repo, board="aux", env={})
    assert resolution.config_path == (repo / "boardkit.toml").resolve()
    assert resolution.config_path != decoy / "boardkit.toml"


def test_walk_up_uses_manifest_default(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _board(repo / ".boardkit" / "boards" / "bk")
    _manifest(repo, 'default = "bk"\n[boards.bk]\nlocation = "dir:.boardkit/boards/bk"\n')
    nested = repo / "src" / "deep"
    nested.mkdir(parents=True)
    resolution = resolve_board(nested, env={})
    assert resolution.config_path == (
        repo / ".boardkit" / "boards" / "bk" / "boardkit.toml"
    ).resolve()
    assert resolution.code == "bk"


def test_external_resolves_through_overlay(tmp_path: Path) -> None:
    wiki_board = _board(tmp_path / "wiki" / "boards" / "aura")
    repo = tmp_path / "repo"
    bk = _manifest(repo, 'default = "aura"\n[boards.aura]\nlocation = "external"\n')
    (bk / "local.toml").write_text(
        f'[boards.aura]\npath = "{wiki_board}"\n', encoding="utf-8"
    )
    resolution = resolve_board(repo, env={})
    assert resolution.config_path == wiki_board / "boardkit.toml"


def test_external_without_overlay_names_the_fix(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _manifest(repo, 'default = "aura"\n[boards.aura]\nlocation = "external"\n')
    with pytest.raises(ValueError, match="local.toml"):
        resolve_board(repo, env={})


def test_common_dir_fallback_from_linked_worktree(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _board(repo)
    _manifest(repo, 'default = "bk"\n[boards.bk]\nlocation = "dir:."\n')
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    identity = ["-c", "user.email=t@t", "-c", "user.name=t"]
    subprocess.run(
        ["git", "-C", str(repo), *identity, "commit", "-q", "--allow-empty", "-m", "seed"],
        check=True,
    )
    worktree = tmp_path / "wt"
    subprocess.run(
        ["git", "-C", str(repo), "worktree", "add", "-q", str(worktree)], check=True
    )
    # The worktree carries no .boardkit and no boardkit.toml of its own.
    nested = worktree / "sub"
    nested.mkdir()
    resolution = resolve_board(nested, env={})
    assert resolution.config_path == (repo / "boardkit.toml").resolve()
    assert "common-dir" in resolution.source


def test_legacy_walk_up_still_works(tmp_path: Path) -> None:
    repo = _board(tmp_path / "repo")
    nested = repo / "src"
    nested.mkdir()
    resolution = resolve_board(nested, env={})
    assert resolution.config_path == repo / "boardkit.toml"
    assert resolution.source == "legacy walk-up"


def test_nothing_found_names_the_whole_order(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match=r"\.boardkit/manifest\.toml"):
        resolve_board(tmp_path, env={})


def test_unknown_code_lists_known(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _board(repo)
    _manifest(repo, 'default = "bk"\n[boards.bk]\nlocation = "dir:."\n')
    with pytest.raises(ValueError, match="known: bk"):
        resolve_board(repo, board="nope", env={})


def test_malformed_manifest_is_loud_not_a_fallthrough(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _board(repo)  # legacy config exists, but the manifest error must win
    _manifest(repo, '[boards.bk]\nlocation = "dir:."\n')  # no default
    with pytest.raises(ValueError, match="'default' must name a board short-code"):
        resolve_board(repo, env={})


def test_resolved_board_without_config_names_the_gap(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "empty").mkdir(parents=True)
    _manifest(repo, 'default = "bk"\n[boards.bk]\nlocation = "dir:empty"\n')
    with pytest.raises(ValueError, match="no boardkit.toml there"):
        resolve_board(repo, env={})


def test_store_ref_schemes() -> None:
    assert parse_store_ref("dir:boards/bk", "t").value == "boards/bk"
    assert parse_store_ref("boards/bk", "t").scheme == "dir"
    assert parse_store_ref("external", "t").scheme == "external"
    assert parse_store_ref("dir:external", "t").value == "external"
    with pytest.raises(ValueError, match="reserved"):
        parse_store_ref("linear:TEAM-1", "t")
    with pytest.raises(ValueError, match="unknown store scheme"):
        parse_store_ref("ftp:nope", "t")
