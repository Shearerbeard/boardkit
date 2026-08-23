"""Tests for check-level warnings added in S30.

These are warnings, not errors: `boardkit check` exits 0 but prints a WARN
line for each. Each fix from S30 gets at least one test here.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from conftest import config_text

from boardkit.cli import build_parser, cmd_check

CARD_FRONTMATTER = """---
id: {id}
title: {title}
status: {status}
depends: []
serialize-with: []
lineage: {lineage}
executor: any
gates: "{gates}"
user-gates: []
{extra}---

# {id}: {title}
"""


def _card(
    id: str,
    title: str,
    status: str = "in-review",
    lineage: str = "primary",
    gates: str = "S -> A -> U(code-review)",
    range: str = "",
) -> str:
    extra = f"commit-range: {range}\n" if range else ""
    return CARD_FRONTMATTER.format(
        id=id, title=title, status=status, lineage=lineage, gates=gates, extra=extra
    )


class _Args:
    def __init__(self, config: str) -> None:
        self.config = config


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def _init_repo(repo: Path) -> None:
    repo.mkdir(parents=True, exist_ok=True)
    _git(repo, "init", "-q", "--object-format=sha1")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")
    _git(repo, "config", "commit.gpgsign", "false")
    _git(repo, "config", "core.hooksPath", "hooks-disabled")


def _commit(repo: Path, message: str) -> str:
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", message)
    return _git(repo, "rev-parse", "HEAD").strip()


def test_trailer_commits_outside_recorded_range_warn(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = tmp_path / "repo"
    _init_repo(repo)
    (repo / "file.txt").write_text("a\n", encoding="utf-8")
    base = _commit(repo, "C0 base")
    (repo / "file.txt").write_text("b\n", encoding="utf-8")
    in_range = _commit(repo, "C1 in range\n\nCard: S1")
    (repo / "file.txt").write_text("c\n", encoding="utf-8")
    outside = _commit(repo, "C2 outside range\n\nCard: S1")

    cards_dir = tmp_path / "cards"
    cards_dir.mkdir()
    (cards_dir / "s1-a.md").write_text(
        _card(id="S1", title="A card", range=f"{base}..{in_range}"),
        encoding="utf-8",
    )
    config_path = tmp_path / "boardkit.toml"
    config_path.write_text(config_text(repo="repo"), encoding="utf-8")

    from boardkit.cli import cmd_render

    assert cmd_render(_Args(config=str(config_path))) == 0
    assert cmd_check(_Args(config=str(config_path))) == 0
    out = capsys.readouterr().out
    assert "Card: trailer commits" in out
    assert outside[:8] in out
    assert "rebase hazard or excluded-first-commit trap" in out


def test_trailer_commit_grep_escapes_regex_metacharacters(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = tmp_path / "repo"
    _init_repo(repo)
    (repo / "file.txt").write_text("a\n", encoding="utf-8")
    base = _commit(repo, "C0 base")
    (repo / "file.txt").write_text("b\n", encoding="utf-8")
    in_range = _commit(repo, "C1 in range\n\nCard: S.1")
    (repo / "file.txt").write_text("c\n", encoding="utf-8")
    _commit(repo, "C2 similar but different\n\nCard: SX1")

    cards_dir = tmp_path / "cards"
    cards_dir.mkdir()
    (cards_dir / "s.1-a.md").write_text(
        _card(id="S.1", title="A card", range=f"{base}..{in_range}"),
        encoding="utf-8",
    )
    config_path = tmp_path / "boardkit.toml"
    config_path.write_text(config_text(repo="repo", id_prefix="S."), encoding="utf-8")

    from boardkit.cli import cmd_render

    assert cmd_render(_Args(config=str(config_path))) == 0
    assert cmd_check(_Args(config=str(config_path))) == 0
    out = capsys.readouterr().out
    assert "Card: trailer commits" not in out


def test_uncheckable_commit_range_warns(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    repo = tmp_path / "repo"
    _init_repo(repo)
    (repo / "file.txt").write_text("a\n", encoding="utf-8")
    _commit(repo, "C0 base\n\nCard: S1")

    cards_dir = tmp_path / "cards"
    cards_dir.mkdir()
    (cards_dir / "s1-a.md").write_text(
        _card(id="S1", title="A card", range="missing..also-missing"),
        encoding="utf-8",
    )
    config_path = tmp_path / "boardkit.toml"
    config_path.write_text(config_text(repo="repo"), encoding="utf-8")

    from boardkit.cli import cmd_render

    assert cmd_render(_Args(config=str(config_path))) == 0
    assert cmd_check(_Args(config=str(config_path))) == 0
    out = capsys.readouterr().out
    assert "could not check commit-range 'missing..also-missing'" in out


def test_src_paths_without_code_review_gate_warn(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = tmp_path / "repo"
    _init_repo(repo)
    (repo / "src" / "mod.py").parent.mkdir(parents=True)
    (repo / "src" / "mod.py").write_text("# module\n", encoding="utf-8")
    base = _commit(repo, "C0 base")
    (repo / "src" / "mod.py").write_text("# changed\n", encoding="utf-8")
    last = _commit(repo, "C1 change src\n\nCard: S1")

    cards_dir = tmp_path / "cards"
    cards_dir.mkdir()
    (cards_dir / "s1-a.md").write_text(
        _card(id="S1", title="A card", gates="S -> A", range=f"{base}..{last}"),
        encoding="utf-8",
    )
    config_path = tmp_path / "boardkit.toml"
    config_path.write_text(config_text(repo="repo"), encoding="utf-8")

    from boardkit.cli import cmd_render

    assert cmd_render(_Args(config=str(config_path))) == 0
    assert cmd_check(_Args(config=str(config_path))) == 0
    out = capsys.readouterr().out
    assert "commit-range touches src/ paths but gates lack U(code-review)" in out


def test_src_paths_with_code_review_gate_do_not_warn(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = tmp_path / "repo"
    _init_repo(repo)
    (repo / "src" / "mod.py").parent.mkdir(parents=True)
    (repo / "src" / "mod.py").write_text("# module\n", encoding="utf-8")
    base = _commit(repo, "C0 base")
    (repo / "src" / "mod.py").write_text("# changed\n", encoding="utf-8")
    last = _commit(repo, "C1 change src\n\nCard: S1")

    cards_dir = tmp_path / "cards"
    cards_dir.mkdir()
    (cards_dir / "s1-a.md").write_text(
        _card(id="S1", title="A card", range=f"{base}..{last}"),
        encoding="utf-8",
    )
    config_path = tmp_path / "boardkit.toml"
    config_path.write_text(config_text(repo="repo"), encoding="utf-8")

    from boardkit.cli import cmd_render

    assert cmd_render(_Args(config=str(config_path))) == 0
    assert cmd_check(_Args(config=str(config_path))) == 0
    out = capsys.readouterr().out
    assert "src/ paths" not in out


def test_entity_name_collision_warns(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cards_dir = tmp_path / "cards"
    cards_dir.mkdir()
    (cards_dir / "s1-a.md").write_text(
        _card(id="S1", title="Shared title", status="ready", lineage="none", gates="S -> A"),
        encoding="utf-8",
    )
    (cards_dir / "s2-b.md").write_text(
        _card(id="S2", title="Shared title", status="ready", lineage="none", gates="S -> A"),
        encoding="utf-8",
    )
    config_path = tmp_path / "boardkit.toml"
    config_path.write_text(config_text(), encoding="utf-8")

    from boardkit.cli import cmd_render

    assert cmd_render(_Args(config=str(config_path))) == 0
    assert cmd_check(_Args(config=str(config_path))) == 0
    out = capsys.readouterr().out
    assert "entity-name collision: title 'Shared title'" in out


def test_check_with_config_uses_the_boards_registry_not_the_shell_cwd(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    board_root = tmp_path / "board-root"
    cards_dir = board_root / "cards"
    cards_dir.mkdir(parents=True)
    (cards_dir / "s1-a.md").write_text(
        _card(id="S1", title="A card", status="ready", lineage="none", gates="S -> A"),
        encoding="utf-8",
    )
    (board_root / "boardkit.toml").write_text(config_text(), encoding="utf-8")
    registry = board_root / ".boardkit"
    registry.mkdir()
    (registry / "manifest.toml").write_text(
        'default = "bk"\n\n[boards.bk]\nlocation = "dir:."\nid_prefix = "S"\n',
        encoding="utf-8",
    )

    from boardkit.cli import cmd_render

    assert cmd_render(_Args(config=str(board_root / "boardkit.toml"))) == 0
    shell_cwd = tmp_path / "shell-cwd"
    shell_cwd.mkdir()
    monkeypatch.chdir(shell_cwd)

    assert cmd_check(_Args(config=str(board_root / "boardkit.toml"))) == 0


def test_revision_expression_accepted_in_review_packet_cli(
    tmp_path: Path,
) -> None:
    """The CLI passes a revision-expression range through to review-packet."""
    from boardkit.cli import cmd_review_packet

    repo = tmp_path / "repo"
    _init_repo(repo)
    (repo / "file.txt").write_text("a\n", encoding="utf-8")
    _commit(repo, "C0 base")
    (repo / "file.txt").write_text("b\n", encoding="utf-8")
    _commit(repo, "C1 change\n\nCard: S1")

    cards_dir = tmp_path / "cards"
    cards_dir.mkdir()
    (cards_dir / "s1-a.md").write_text(
        "---\nid: S1\ntitle: A card\n---\n\n# S1\n",
        encoding="utf-8",
    )
    config_path = tmp_path / "boardkit.toml"
    config_path.write_text(config_text(repo="repo"), encoding="utf-8")

    args = build_parser().parse_args(
        [
            "--config",
            str(config_path),
            "review-packet",
            "S1",
            "--commit-range",
            "HEAD~1..HEAD",
        ]
    )

    assert cmd_review_packet(args) == 0
    review = (tmp_path / "reviews" / "S1" / "REVIEW.md").read_text(encoding="utf-8")
    assert "C1 change" in review
