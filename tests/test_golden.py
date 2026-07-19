from pathlib import Path

from boardkit.board import build_board
from boardkit.cli import cmd_check, cmd_render
from boardkit.config import load_config

# Fixture provenance: byte-identical copy of terminalbench-aura's
# docs/redesign/cards/ except for one deviation - the generated-view banner
# lines in INDEX.md and board.md say "boardkit render" instead of the source
# repo's "scripts/cards_index.py". Every other byte is checked as-is.
GOLDEN_CARDS_DIR = Path(__file__).parent / "golden" / "aura-cards"


class _Args:
    def __init__(self, config: str) -> None:
        self.config = config


def test_render_matches_committed_golden_views(golden_board: Path) -> None:
    config = load_config(golden_board)
    result = build_board(config)

    for name in ("INDEX.md", "board.md"):
        rendered = result.views[name]
        committed = (GOLDEN_CARDS_DIR / name).read_text(encoding="utf-8")
        assert rendered == committed, f"{name} is not byte-identical to the committed golden"


def test_check_passes_clean_on_untouched_golden(golden_board: Path) -> None:
    exit_code = cmd_check(_Args(config=str(golden_board)))
    assert exit_code == 0


def test_check_detects_drift(golden_board: Path) -> None:
    config = load_config(golden_board)
    index_path = config.board.cards_dir / "INDEX.md"
    index_path.write_text(
        index_path.read_text(encoding="utf-8") + "\nperturbed\n", encoding="utf-8"
    )

    exit_code = cmd_check(_Args(config=str(golden_board)))
    assert exit_code == 1


def test_render_writes_generated_views(golden_board: Path) -> None:
    config = load_config(golden_board)
    index_path = config.board.cards_dir / "INDEX.md"
    board_path = config.board.cards_dir / "board.md"
    original_index = index_path.read_text(encoding="utf-8")
    original_board = board_path.read_text(encoding="utf-8")

    exit_code = cmd_render(_Args(config=str(golden_board)))
    assert exit_code == 0
    assert index_path.read_text(encoding="utf-8") == original_index
    assert board_path.read_text(encoding="utf-8") == original_board
