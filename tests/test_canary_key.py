"""Tests for `boardkit canary-key`.

The orientation canary is graded against a key the board owner computes
before dispatch. These tests pin the whole key output for a synthetic
board, so a wording or ordering change is visible in the diff rather than
silently changing what a canary is graded against.

The board here is synthetic on purpose: the golden aura fixture is a
byte-identity tripwire for the renderer and may never be regenerated.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from conftest import config_text

from boardkit.cli import cmd_canary_key, cmd_render

CARD = """---
id: {id}
title: {title}
status: {status}
depends: {depends}
serialize-with: []
lineage: none
executor: any
gates: "S -> A"
user-gates: []
---

# {id}: {title}

## Gate checklist

{checklist}

## Log

{log}
"""


class _Args:
    def __init__(self, config: str) -> None:
        self.config = config


def _write(
    cards_dir: Path,
    filename: str,
    *,
    id: str,
    title: str,
    status: str,
    depends: str = "[]",
    checklist: str = "",
    log: str = "",
) -> None:
    (cards_dir / filename).write_text(
        CARD.format(
            id=id,
            title=title,
            status=status,
            depends=depends,
            checklist=checklist,
            log=log,
        ),
        encoding="utf-8",
    )


@pytest.fixture
def board(tmp_path: Path) -> Path:
    (tmp_path / "cards").mkdir()
    config_path = tmp_path / "boardkit.toml"
    config_path.write_text(config_text(), encoding="utf-8")
    return config_path


def _key(board: Path, capsys: pytest.CaptureFixture[str]) -> str:
    capsys.readouterr()  # drop whatever the fixture's render printed
    assert cmd_canary_key(_Args(config=str(board))) == 0
    return capsys.readouterr().out


def test_key_over_a_working_board(board: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cards = board.parent / "cards"
    _write(cards, "s1-foundation.md", id="S1", title="Foundation", status="done")
    _write(
        cards,
        "s2-adapter.md",
        id="S2",
        title="Adapter shim",
        status="in-review",
        depends="[S1]",
        checklist="- [ ] Gate A: fresh-agent review.",
        log="- 2026-07-27 Gate A open: deferred (every reviewer authored a commit).",
    )
    _write(cards, "s3-runner.md", id="S3", title="Runner", status="in-progress", depends="[S1]")
    _write(cards, "s4-report.md", id="S4", title="Report", status="ready", depends="[S1]")
    _write(cards, "s5-publish.md", id="S5", title="Publish", status="ready", depends="[S1]")
    assert cmd_render(_Args(config=str(board))) == 0

    assert _key(board, capsys) == """\
# Canary key

Computed by `boardkit canary-key` from card frontmatter. Grade the
orientation canary's answers against this key, never against the
canary's own confidence. The fourth question (who owns the board,
and where must it stop) has a static key: the Roles and Gates
sections of `PROCESS.md`.

## In Review

- [S2](s2-adapter.md) Adapter shim

## In Progress

- [S3](s3-runner.md) Runner

## Next pull

- [S4](s4-report.md) Report (top of the ready queue)

Ready queue: S4, S5.

## Open deferred gates

- [S2](s2-adapter.md) Gate A: every reviewer authored a commit

## Views

Current: INDEX.md, board.md, deferred.md, graph.md.
"""


def test_key_flags_a_promotion_gap(board: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Empty Ready with a dependency-satisfied Backlog card is a board defect,
    and the key has to say so or the canary cannot be graded on it."""
    cards = board.parent / "cards"
    _write(cards, "s1-foundation.md", id="S1", title="Foundation", status="done")
    _write(cards, "s2-next.md", id="S2", title="Next up", status="backlog", depends="[S1]")
    _write(cards, "s3-blocked.md", id="S3", title="Blocked", status="backlog", depends="[S2]")
    assert cmd_render(_Args(config=str(board))) == 0

    out = _key(board, capsys)

    assert "PROMOTION GAP" in out
    assert "- [S2](s2-next.md) Next up" in out
    assert "S3" not in out.split("## Next pull", 1)[1].split("## Open", 1)[0]


def test_key_says_none_when_nothing_is_pullable(
    board: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    cards = board.parent / "cards"
    _write(cards, "s1-foundation.md", id="S1", title="Foundation", status="in-progress")
    _write(cards, "s2-blocked.md", id="S2", title="Blocked", status="backlog", depends="[S1]")
    assert cmd_render(_Args(config=str(board))) == 0

    out = _key(board, capsys)

    assert "- none: no ready card, and no backlog card has all dependencies done." in out
    assert "## In Review\n\n- none" in out
    assert "## Open deferred gates\n\n- none" in out


def test_key_reports_view_drift_rather_than_grading_over_it(
    board: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    cards = board.parent / "cards"
    _write(cards, "s1-foundation.md", id="S1", title="Foundation", status="ready")
    assert cmd_render(_Args(config=str(board))) == 0
    index = cards / "INDEX.md"
    index.write_text(index.read_text(encoding="utf-8") + "dragged\n", encoding="utf-8")

    out = _key(board, capsys)

    assert "DRIFTED: INDEX.md." in out


def test_key_fails_loudly_on_an_invalid_board(board: Path) -> None:
    cards = board.parent / "cards"
    _write(cards, "s1-foundation.md", id="S1", title="Foundation", status="backlog")
    _write(cards, "s2-early.md", id="S2", title="Early", status="ready", depends="[S1]")

    assert cmd_canary_key(_Args(config=str(board))) == 1
