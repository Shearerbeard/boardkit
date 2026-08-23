"""Tests for the CardStore seam: its markdown-dir driver, and the seam itself.

The mutating methods have no CLI caller yet (RULE-3 seam prep, accepted at
the 2026-08-09 interview), so the driver-level tests are their whole
contract: id-not-filename identity, targeted edits that leave the author's
formatting alone, loud errors for shapes the driver cannot edit safely.

The read half is wired (S28), so the seam-level tests at the bottom check
what wiring is worth: that `build_board` gets its cards, its id scheme and
its link verdicts from whatever store it is handed, and reaches past none
of them to the markdown-dir layout.
"""

from pathlib import Path

import pytest
from conftest import config_text

from boardkit.board import BoardError, build_board
from boardkit.config import Config, load_config
from boardkit.store import BoardMeta, DirStore, StoreError, open_store

CARD = """\
---
id: S1
title: First card
status: ready
depends: []
serialize-with: []
lineage: primary
executor: any
gates: "S -> A"
user-gates: []
---

# S1: First card

## Scope

One file.

## Log

- 2026-08-01 Minted.
"""


def _store(tmp_path: Path, filename: str = "s1-first-card.md", text: str = CARD) -> DirStore:
    (tmp_path / "boardkit.toml").write_text(config_text(), encoding="utf-8")
    cards = tmp_path / "cards"
    cards.mkdir()
    (cards / filename).write_text(text, encoding="utf-8")
    return DirStore(load_config(tmp_path / "boardkit.toml"))


def test_get_card_finds_by_id_not_filename(tmp_path: Path) -> None:
    store = _store(tmp_path, filename="s1-renamed-slug.md")
    card = store.get_card("S1")
    assert card["title"] == "First card"
    assert card["_file"] == "s1-renamed-slug.md"


def test_get_card_unknown_id_raises(tmp_path: Path) -> None:
    store = _store(tmp_path)
    with pytest.raises(StoreError, match="no card with id 'S9'"):
        store.get_card("S9")


def test_transition_rewrites_only_the_status_line(tmp_path: Path) -> None:
    store = _store(tmp_path)
    store.transition("S1", "in-progress")
    text = (tmp_path / "cards" / "s1-first-card.md").read_text(encoding="utf-8")
    assert "status: in-progress" in text
    # Everything else is byte-identical.
    assert text == CARD.replace("status: ready", "status: in-progress")


def test_transition_rejects_unknown_status(tmp_path: Path) -> None:
    store = _store(tmp_path)
    with pytest.raises(StoreError, match="not in"):
        store.transition("S1", "parked")


def test_transition_never_touches_a_status_word_in_the_body(tmp_path: Path) -> None:
    text = CARD.replace("One file.", "One file.\nstatus: decoy prose line.")
    store = _store(tmp_path, text=text)
    store.transition("S1", "done")
    on_disk = (tmp_path / "cards" / "s1-first-card.md").read_text(encoding="utf-8")
    assert "status: decoy prose line." in on_disk
    assert "status: done" in on_disk


def test_append_log_appends_at_end_of_trailing_log(tmp_path: Path) -> None:
    store = _store(tmp_path)
    store.append_log("S1", "2026-08-09 Worked.")
    text = (tmp_path / "cards" / "s1-first-card.md").read_text(encoding="utf-8")
    assert text.endswith("- 2026-08-01 Minted.\n- 2026-08-09 Worked.\n")


def test_append_log_inserts_before_a_following_section(tmp_path: Path) -> None:
    text = CARD + "\n## Notes\n\nAfter the log.\n"
    store = _store(tmp_path, text=text)
    store.append_log("S1", "2026-08-09 Worked.")
    on_disk = (tmp_path / "cards" / "s1-first-card.md").read_text(encoding="utf-8")
    log_index = on_disk.index("- 2026-08-09 Worked.")
    notes_index = on_disk.index("## Notes")
    assert log_index < notes_index
    assert "After the log.\n" in on_disk


def test_append_log_without_log_section_raises(tmp_path: Path) -> None:
    text = CARD.replace("## Log\n\n- 2026-08-01 Minted.\n", "")
    store = _store(tmp_path, text=text)
    with pytest.raises(StoreError, match="no Log section"):
        store.append_log("S1", "2026-08-09 Worked.")


def test_load_cards_reports_a_duplicate_id_without_raising(tmp_path: Path) -> None:
    store = _store(tmp_path)
    (tmp_path / "cards" / "s1-same-id-again.md").write_text(CARD, encoding="utf-8")
    errors: list[str] = []
    cards = store.load_cards(errors)
    # Both records come back; the collision is named, not silently collapsed.
    assert [c["_file"] for c in cards] == ["s1-first-card.md", "s1-same-id-again.md"]
    assert errors == ["s1-same-id-again.md: duplicate id S1"]
    with pytest.raises(StoreError, match="duplicate id S1"):
        store.list_cards()


# --- The seam ---------------------------------------------------------------


def _config(tmp_path: Path) -> Config:
    """A resolved config whose cards directory is never created."""
    (tmp_path / "boardkit.toml").write_text(config_text(), encoding="utf-8")
    return load_config(tmp_path / "boardkit.toml")


def test_build_board_consumes_a_store_built_from_the_resolved_config(tmp_path: Path) -> None:
    """The wiring the card names: resolve a config, open its store, build from it."""
    store = _store(tmp_path)
    config = store.config
    assert isinstance(open_store(config), DirStore)

    result = build_board(config, open_store(config))
    assert [card["id"] for card in result.cards] == ["S1"]
    assert "S1" in result.views["INDEX.md"]
    # Same board whether the caller passes the store or lets the default build it.
    assert build_board(config).views == result.views


class _MemoryStore:
    """A driver holding cards that were never written to a file.

    The seam's real test. Nothing here has a cards directory, a filename
    or a link to resolve, so if `build_board` renders this board, no part
    of the core reached past the store into the markdown-dir layout.
    """

    def __init__(self, cards: list[dict], meta: BoardMeta) -> None:
        self._cards = cards
        self._meta = meta
        self.link_checks: list[str] = []

    def board_meta(self) -> BoardMeta:
        return self._meta

    def load_cards(self, errors: list[str]) -> list[dict]:
        return [dict(card) for card in self._cards]

    def list_cards(self) -> list[dict]:
        return self.load_cards([])

    def get_card(self, card_id: str) -> dict:
        for card in self.list_cards():
            if card["id"] == card_id:
                return card
        raise StoreError([f"no card with id '{card_id}'"])

    def check_links(self, card: dict, generated: set[str], errors: list[str]) -> None:
        self.link_checks.append(card["id"])

    def transition(self, card_id: str, status: str) -> None:
        raise NotImplementedError

    def append_log(self, card_id: str, line: str) -> None:
        raise NotImplementedError


def _record(card_id: str, title: str, **extra: object) -> dict:
    card = {
        "id": card_id,
        "title": title,
        "status": "ready",
        "depends": [],
        "serialize-with": [],
        "lineage": "primary",
        "executor": "any",
        "gates": "S -> A",
        "user-gates": [],
        "_file": f"{card_id.lower()}-not-a-real-file.md",
        "_body": "",
    }
    card.update(extra)
    return card


def test_a_second_driver_drives_build_board_with_no_files_on_disk(tmp_path: Path) -> None:
    config = _config(tmp_path)
    assert not config.board.cards_dir.exists()

    store = _MemoryStore(
        [_record("S2", "Second"), _record("S1", "First")],
        BoardMeta.from_config(config),
    )
    result = build_board(config, store)

    # Ordering comes from the store's BoardMeta, not from a filename sort.
    assert [card["id"] for card in result.cards] == ["S1", "S2"]
    assert sorted(result.views) == ["INDEX.md", "board.md", "graph.md"]
    assert "Second" in result.views["INDEX.md"]
    # Link checking went to the driver for every card, and to nothing else.
    assert sorted(store.link_checks) == ["S1", "S2"]


def test_build_board_takes_its_id_scheme_from_the_store(tmp_path: Path) -> None:
    """A driver whose ids are not the config's prefix still sorts and renders."""
    config = _config(tmp_path)
    store = _MemoryStore(
        [_record("ENG-9", "Ninth"), _record("ENG-2", "Second")],
        BoardMeta(id_prefix="ENG-", sentinel_ids=()),
    )
    result = build_board(config, store)
    assert [card["id"] for card in result.cards] == ["ENG-2", "ENG-9"]


def test_store_load_errors_reach_the_caller_as_board_errors(tmp_path: Path) -> None:
    config = _config(tmp_path)

    class _BrokenStore(_MemoryStore):
        def load_cards(self, errors: list[str]) -> list[dict]:
            errors.append("s3-broken.md: missing required key 'title'")
            return []

    with pytest.raises(BoardError, match="missing required key 'title'"):
        build_board(config, _BrokenStore([], BoardMeta.from_config(config)))
