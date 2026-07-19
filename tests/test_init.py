from pathlib import Path

from boardkit.board import build_board
from boardkit.cli import cmd_check, cmd_init, cmd_render
from boardkit.config import CONFIG_FILENAME, load_config


class _Args:
    def __init__(self, config: str | None = None) -> None:
        self.config = config


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


def test_init_installs_review_packet_gitignore(tmp_path: Path) -> None:
    (tmp_path / ".gitignore").write_text("node_modules/\n", encoding="utf-8")
    assert cmd_init(_Args(config=str(tmp_path / CONFIG_FILENAME))) == 0

    content = tmp_path / ".gitignore"
    lines = content.read_text(encoding="utf-8").splitlines()
    assert "node_modules/" in lines  # existing content preserved
    assert "docs/board/reviews/" in lines
