"""Driver-level tests for the CardStore seam's markdown-dir driver.

The mutating methods have no CLI caller yet (RULE-3 seam prep, accepted at
the 2026-08-09 interview), so these tests are the seam's whole contract:
id-not-filename identity, targeted edits that leave the author's
formatting alone, loud errors for shapes the driver cannot edit safely.
"""

from pathlib import Path

import pytest
from conftest import config_text

from boardkit.config import load_config
from boardkit.store import DirStore, StoreError

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
