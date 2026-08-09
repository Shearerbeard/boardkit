from pathlib import Path

from boardkit.board import build_board
from boardkit.cli import cmd_check, cmd_render
from boardkit.config import load_config

# Fixture provenance: byte-identical copy of terminalbench-aura's
# docs/redesign/cards/ except for one deviation - the generated-view banner
# lines in INDEX.md and board.md say "boardkit render" instead of the source
# repo's "scripts/cards_index.py". Every other byte is checked as-is.
#
# NEVER regenerate the committed INDEX.md/board.md fixtures with boardkit
# itself: a renderer bug would then be baked into the expectation and this
# test would prove nothing. The fixtures may only be refreshed by re-copying
# from the source repo's board. test_golden_views_match_card_population below
# is the renderer-independent tripwire for that mistake.
#
# Exception: graph.md is a boardkit-native view (R9, 2026-08-09) with no
# upstream source to copy from. Its committed fixture was generated once by
# the renderer that introduced it and is frozen from then on, so it guards
# regressions rather than proving first-render correctness.
#
# Format-evolution refreshes: when the kit deliberately changes view format,
# the fixtures are regenerated and the DIFF is hand-reviewed against an
# independently derived expectation before committing, and the change is
# recorded here. 2026-08-09 (S16): the two active cards' Gates cells gained
# an `@ <position>` suffix (S9 `@ U`, S36 `@ S`, both fully unticked
# ladders) - four lines, nothing else.
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


def test_golden_views_match_card_population(golden_board: Path) -> None:
    """Renderer-independent guard: the committed views must account for every
    card file, counted straight from the filesystem, not via the renderer."""
    card_files = [
        p
        for p in GOLDEN_CARDS_DIR.glob("*.md")
        if p.name not in ("INDEX.md", "board.md", "graph.md", "deferred.md")
        and not p.name.startswith("_")
    ]
    index_rows = [
        line
        for line in (GOLDEN_CARDS_DIR / "INDEX.md").read_text(encoding="utf-8").splitlines()
        if line.startswith("| ") and not line.startswith(("| ID", "| ---"))
    ]
    assert len(index_rows) == len(card_files)


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
