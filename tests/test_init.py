from pathlib import Path

import pytest

from boardkit.board import build_board
from boardkit.cli import cmd_check, cmd_doctor, cmd_init, cmd_render
from boardkit.config import CONFIG_FILENAME, load_config
from boardkit.contract import CONTRACT_VERSION


class _Args:
    def __init__(self, config: str | None = None, json: bool = False) -> None:
        self.config = config
        self.json = json


def test_init_scaffolds_config_and_template(tmp_path: Path) -> None:
    config_path = tmp_path / CONFIG_FILENAME
    exit_code = cmd_init(_Args(config=str(config_path)))
    assert exit_code == 0

    assert config_path.is_file()
    template = tmp_path / "docs" / "board" / "cards" / "_template.md"
    assert template.is_file()

    for rel in (
        "docs/board/PROCESS.md",
        "docs/board/MODEL-CLASSES.md",
        "docs/board/REVIEW-TOOLING.md",
        "AGENTS.md",
        "CLAUDE.md",
        "GEMINI.md",
    ):
        assert (tmp_path / rel).is_file(), f"init did not place {rel}"


def test_init_leaves_existing_entry_shims_untouched(tmp_path: Path) -> None:
    existing = tmp_path / "AGENTS.md"
    existing.write_text("mine\n", encoding="utf-8")

    assert cmd_init(_Args(config=str(tmp_path / CONFIG_FILENAME))) == 0
    assert existing.read_text(encoding="utf-8") == "mine\n"
    assert (tmp_path / "CLAUDE.md").is_file()


def test_init_refuses_to_overwrite_existing_config(tmp_path: Path) -> None:
    config_path = tmp_path / CONFIG_FILENAME
    assert cmd_init(_Args(config=str(config_path))) == 0
    assert cmd_init(_Args(config=str(config_path))) == 1


def test_fresh_board_with_zero_cards_is_valid(tmp_path: Path) -> None:
    config_path = tmp_path / CONFIG_FILENAME
    assert cmd_init(_Args(config=str(config_path))) == 0

    config = load_config(config_path)
    result = build_board(config)
    assert result.cards == []

    # init must leave a board that checks clean with no intervening render
    assert cmd_check(_Args(config=str(config_path))) == 0
    assert cmd_render(_Args(config=str(config_path))) == 0


def test_init_prints_the_stamp_and_points_at_doctor(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The operator has to know which contract their board speaks, and what is
    left before it can dispatch; neither is discoverable from a clean exit."""
    assert cmd_init(_Args(config=str(tmp_path / CONFIG_FILENAME))) == 0

    out = capsys.readouterr().out
    assert f"Stamped at delegation contract v{CONTRACT_VERSION}." in out
    assert "NEXT:" in out
    assert "boardkit.toml" in out
    assert "docs/board/REVIEW-TOOLING.md" in out
    assert "`boardkit doctor`" in out


def test_a_fresh_board_passes_check_and_fails_doctor(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The split, by design: `check` is board validity, doctor is installation
    readiness. init scaffolds placeholders rather than lying about them, so a
    fresh board is valid and not yet dispatchable."""
    config_path = tmp_path / CONFIG_FILENAME
    assert cmd_init(_Args(config=str(config_path))) == 0
    capsys.readouterr()

    assert cmd_check(_Args(config=str(config_path))) == 0
    assert cmd_doctor(_Args(config=str(config_path))) == 1

    assert "roles.filled" in capsys.readouterr().out


def test_init_installs_all_four_boardkit_ignore_lines(tmp_path: Path) -> None:
    (tmp_path / ".gitignore").write_text("node_modules/\n", encoding="utf-8")
    assert cmd_init(_Args(config=str(tmp_path / CONFIG_FILENAME))) == 0

    content = tmp_path / ".gitignore"
    lines = content.read_text(encoding="utf-8").splitlines()
    assert "node_modules/" in lines  # existing content preserved
    assert "docs/board/reviews/" in lines
    assert ".review/" in lines
    assert ".boardkit/local.toml" in lines
    assert ".claude/settings.local.json" in lines


def test_init_writes_an_opt_in_pre_commit_sample(tmp_path: Path) -> None:
    assert cmd_init(_Args(config=str(tmp_path / CONFIG_FILENAME))) == 0

    sample = tmp_path / "docs" / "board" / "pre-commit.sample"
    assert sample.is_file()
    body = sample.read_text(encoding="utf-8")
    assert body.startswith("#!/bin/sh\n")
    assert "boardkit check" in body
    # the header has to say how to turn it on; a sample nobody can install
    # is just a file
    assert ".git/hooks/pre-commit" in body


def test_init_never_installs_a_git_hook(tmp_path: Path) -> None:
    hooks = tmp_path / ".git" / "hooks"
    hooks.mkdir(parents=True)

    assert cmd_init(_Args(config=str(tmp_path / CONFIG_FILENAME))) == 0

    assert list(hooks.iterdir()) == []


def test_init_refuses_to_overwrite_an_existing_pre_commit_sample(tmp_path: Path) -> None:
    sample = tmp_path / "docs" / "board" / "pre-commit.sample"
    sample.parent.mkdir(parents=True)
    sample.write_text("mine\n", encoding="utf-8")

    assert cmd_init(_Args(config=str(tmp_path / CONFIG_FILENAME))) == 1
    assert sample.read_text(encoding="utf-8") == "mine\n"
