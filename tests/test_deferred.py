"""Tests for the generated deferred-gates view.

A gate the board owner had to defer is recorded as a
`Gate <X> open: deferred (<reason>)` log line with its checklist box left
unticked. Finding those was a hand grep; `deferred.md` makes it a view.

The view is emitted only when at least one such gate is open, so a board
with none (the common case, and every golden fixture) renders exactly the
two views it always did.
"""

from pathlib import Path

import pytest
from conftest import config_text

from boardkit.board import DEFERRED_VIEW, BoardError, build_board, deferred_gates
from boardkit.cli import cmd_check, cmd_render
from boardkit.config import load_config

CARD = """---
id: {id}
title: {title}
status: {status}
depends: []
serialize-with: []
lineage: none
executor: any
gates: "S -> A -> U"
user-gates: []
---

# {id}: {title}

## Gate checklist

{checklist}

## Log

{log}
{extra}"""


class _Args:
    def __init__(self, config: str) -> None:
        self.config = config


def _write_card(
    cards_dir: Path,
    filename: str,
    *,
    id: str,
    title: str = "A card",
    status: str = "in-review",
    checklist: str = "",
    log: str = "",
    extra: str = "",
) -> None:
    (cards_dir / filename).write_text(
        CARD.format(
            id=id,
            title=title,
            status=status,
            checklist=checklist,
            log=log,
            extra=extra,
        ),
        encoding="utf-8",
    )


@pytest.fixture
def board(tmp_path: Path) -> Path:
    (tmp_path / "cards").mkdir()
    config_path = tmp_path / "boardkit.toml"
    config_path.write_text(config_text(), encoding="utf-8")
    return config_path


def test_no_deferred_gates_means_no_view(board: Path) -> None:
    cards_dir = board.parent / "cards"
    _write_card(cards_dir, "s1-a.md", id="S1", checklist="- [x] Gate S: checks.")

    result = build_board(load_config(board))

    assert DEFERRED_VIEW not in result.views
    assert set(result.views) == {"INDEX.md", "board.md"}


def test_open_deferred_gate_appears_with_reason_and_link(board: Path) -> None:
    cards_dir = board.parent / "cards"
    _write_card(
        cards_dir,
        "s1-a.md",
        id="S1",
        title="Adapter shim",
        checklist="- [x] Gate S: checks.\n- [ ] Gate A: fresh-agent review.",
        log="- 2026-07-27 Gate A open: deferred (no second family reachable).",
    )

    result = build_board(load_config(board))
    view = result.views[DEFERRED_VIEW]

    assert "S1" in view
    assert "(s1-a.md)" in view
    assert "no second family reachable" in view
    assert "Gate A" in view


def test_ticked_box_means_the_deferral_was_resolved(board: Path) -> None:
    cards_dir = board.parent / "cards"
    _write_card(
        cards_dir,
        "s1-a.md",
        id="S1",
        checklist="- [x] Gate A: fresh-agent review.",
        log=(
            "- 2026-07-26 Gate A open: deferred (reviewer unreachable).\n"
            "- 2026-07-27 Gate A PASS, zero findings; box ticked."
        ),
    )

    result = build_board(load_config(board))

    assert DEFERRED_VIEW not in result.views


def test_qualified_user_gate_matches_its_own_box(board: Path) -> None:
    """`Gate U (baseline)` is a different gate from `Gate U (launch)`: a tick
    on one must not clear a deferral recorded against the other."""
    cards_dir = board.parent / "cards"
    _write_card(
        cards_dir,
        "s1-a.md",
        id="S1",
        checklist="- [x] Gate U (launch): go.\n- [ ] Gate U (baseline): accept or reject.",
        log=(
            "- 2026-07-27 Gate U (baseline) open: deferred (held for re-test).\n"
            "- 2026-07-27 Gate U (launch) approved."
        ),
    )

    result = build_board(load_config(board))
    view = result.views[DEFERRED_VIEW]

    assert "U (baseline)" in view
    assert "held for re-test" in view
    assert "launch" not in view


def test_wrapped_log_line_is_still_found(board: Path) -> None:
    """Deferral lines wrap across source lines; the sweep reads the flattened
    body so a line break inside the phrase cannot hide a gate."""
    cards_dir = board.parent / "cards"
    _write_card(
        cards_dir,
        "s1-a.md",
        id="S1",
        checklist="- [ ] Gate A: fresh-agent review.",
        log=(
            "- 2026-07-27 The review stands as Gate A\n"
            "  open: deferred (every reachable reviewer authored a\n"
            "  commit in the range)."
        ),
    )

    entries = deferred_gates(build_board(load_config(board)).cards)

    assert len(entries) == 1
    assert entries[0].reason == "every reachable reviewer authored a commit in the range"


def test_prose_about_the_sweep_is_not_a_deferral(board: Path) -> None:
    """Cards discuss the `open: deferred` convention itself; only a line that
    names a gate ahead of it is an actual deferral record."""
    cards_dir = board.parent / "cards"
    _write_card(
        cards_dir,
        "s1-a.md",
        id="S1",
        checklist="- [ ] Gate A: fresh-agent review.",
        log="- 2026-07-27 Normalized the log to the canonical `open: deferred` wording.",
    )

    assert DEFERRED_VIEW not in build_board(load_config(board)).views


def test_deferral_syntax_outside_the_log_section_is_not_a_deferral(board: Path) -> None:
    """A card that documents the convention in its own Scope or Notes prose
    is describing the syntax, not recording a deferral against itself."""
    cards_dir = board.parent / "cards"
    _write_card(
        cards_dir,
        "s1-a.md",
        id="S1",
        checklist="- [ ] Gate A: fresh-agent review.",
        log="- 2026-07-27 Card opened.",
        extra=(
            "\n## Notes\n\n"
            "- The board owner writes Gate A open: deferred (reason) and leaves\n"
            "  the checklist box unticked.\n"
        ),
    )

    assert deferred_gates(build_board(load_config(board)).cards) == []
    assert DEFERRED_VIEW not in build_board(load_config(board)).views


def test_deferral_syntax_inside_backticks_in_a_log_bullet_is_not_a_deferral(
    board: Path,
) -> None:
    """A log bullet quoting the wording in inline code is a note about the
    convention; only an unquoted record defers a gate."""
    cards_dir = board.parent / "cards"
    _write_card(
        cards_dir,
        "s1-a.md",
        id="S1",
        checklist="- [ ] Gate A: fresh-agent review.",
        log=(
            "- 2026-07-27 Documented the deferral wording as\n"
            "  `Gate A open: deferred (reason)` in the process doc."
        ),
    )

    assert deferred_gates(build_board(load_config(board)).cards) == []
    assert DEFERRED_VIEW not in build_board(load_config(board)).views


def test_deferred_view_link_resolves_only_while_the_view_exists(board: Path) -> None:
    """`deferred.md` is generated only while a gate is open-deferred, so a
    link to it from a board with no deferral points at nothing."""
    cards_dir = board.parent / "cards"
    _write_card(
        cards_dir,
        "s1-a.md",
        id="S1",
        checklist="- [ ] Gate A: fresh-agent review.",
        log="- 2026-07-27 Gate A open: deferred (reviewer unvetted).",
        extra="\n## Notes\n\nOpen gates: [deferred.md](deferred.md).\n",
    )

    assert DEFERRED_VIEW in build_board(load_config(board)).views

    _write_card(
        cards_dir,
        "s1-a.md",
        id="S1",
        checklist="- [x] Gate A: fresh-agent review.",
        log="- 2026-07-28 Gate A PASS.",
        extra="\n## Notes\n\nOpen gates: [deferred.md](deferred.md).\n",
    )

    with pytest.raises(BoardError) as excinfo:
        build_board(load_config(board))

    assert any("broken link 'deferred.md'" in e for e in excinfo.value.errors)


def test_render_writes_the_view_and_check_accepts_it(board: Path) -> None:
    cards_dir = board.parent / "cards"
    _write_card(
        cards_dir,
        "s1-a.md",
        id="S1",
        checklist="- [ ] Gate A: fresh-agent review.",
        log="- 2026-07-27 Gate A open: deferred (reviewer unvetted).",
    )

    assert cmd_render(_Args(config=str(board))) == 0
    assert (cards_dir / DEFERRED_VIEW).is_file()
    assert cmd_check(_Args(config=str(board))) == 0


def test_check_reports_drift_in_the_deferred_view(board: Path) -> None:
    cards_dir = board.parent / "cards"
    _write_card(
        cards_dir,
        "s1-a.md",
        id="S1",
        checklist="- [ ] Gate A: fresh-agent review.",
        log="- 2026-07-27 Gate A open: deferred (reviewer unvetted).",
    )
    assert cmd_render(_Args(config=str(board))) == 0

    path = cards_dir / DEFERRED_VIEW
    path.write_text(path.read_text(encoding="utf-8") + "\nhand-edited\n", encoding="utf-8")

    assert cmd_check(_Args(config=str(board))) == 1


def test_missing_deferred_view_is_reported_when_a_gate_is_open(board: Path) -> None:
    cards_dir = board.parent / "cards"
    _write_card(
        cards_dir,
        "s1-a.md",
        id="S1",
        checklist="- [ ] Gate A: fresh-agent review.",
        log="- 2026-07-27 Gate A open: deferred (reviewer unvetted).",
    )
    assert cmd_render(_Args(config=str(board))) == 0
    (cards_dir / DEFERRED_VIEW).unlink()

    assert cmd_check(_Args(config=str(board))) == 1


def test_resolving_the_last_deferral_retires_the_view(board: Path) -> None:
    cards_dir = board.parent / "cards"
    _write_card(
        cards_dir,
        "s1-a.md",
        id="S1",
        checklist="- [ ] Gate A: fresh-agent review.",
        log="- 2026-07-27 Gate A open: deferred (reviewer unvetted).",
    )
    assert cmd_render(_Args(config=str(board))) == 0

    _write_card(
        cards_dir,
        "s1-a.md",
        id="S1",
        checklist="- [x] Gate A: fresh-agent review.",
        log=(
            "- 2026-07-27 Gate A open: deferred (reviewer unvetted).\n"
            "- 2026-07-28 Gate A PASS; deferral resolved."
        ),
    )

    # a leftover view is drift, not a harmless file
    assert cmd_check(_Args(config=str(board))) == 1
    assert cmd_render(_Args(config=str(board))) == 0
    assert not (cards_dir / DEFERRED_VIEW).exists()
    assert cmd_check(_Args(config=str(board))) == 0


def test_deferred_view_is_not_parsed_as_a_card(board: Path) -> None:
    cards_dir = board.parent / "cards"
    _write_card(
        cards_dir,
        "s1-a.md",
        id="S1",
        checklist="- [ ] Gate A: fresh-agent review.",
        log="- 2026-07-27 Gate A open: deferred (reviewer unvetted).",
    )
    assert cmd_render(_Args(config=str(board))) == 0

    result = build_board(load_config(board))

    assert [c["id"] for c in result.cards] == ["S1"]


def test_stale_deferred_view_on_disk_does_not_legitimize_the_link(board: Path) -> None:
    """A stale deferred.md left on disk is still a broken link once no
    deferral is open: render deletes the file on its next pass, so check
    must reject the link up front rather than trust the stale copy."""
    cards_dir = board.parent / "cards"
    _write_card(
        cards_dir,
        "s1-a.md",
        id="S1",
        checklist="- [x] Gate S: checks.",
        extra="\nSee [the deferred queue](deferred.md) for open gates.\n",
    )
    (cards_dir / "deferred.md").write_text("# stale\n", encoding="utf-8")

    with pytest.raises(BoardError) as exc:
        build_board(load_config(board))

    assert any("stale generated view" in e for e in exc.value.errors)
