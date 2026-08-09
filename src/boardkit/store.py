"""The CardStore seam (RULE-3): the CLI core's view of a board's cards.

The markdown-dir layout is driver #1, not the data model. Card identity is
the `id` frontmatter, never the filename: every method takes card ids, and
a renamed file that still declares the same id is the same card. One
source of truth per board, no bidirectional sync; generated views are
non-authoritative renders; gates, WIP, routing, and process semantics
stay kit-side permanently. A remote driver (`linear:` is reserved) would
map card CRUD, status, comments, and read-only gate visibility only.

Seam surface shipped here: list/get, `transition`, and `append_log`.
`put` (whole-card replace) is deferred: it has no caller yet and no
format-preserving serialization, and a speculative writer that reflows
frontmatter would churn every card it touched. The mutating methods are
targeted text edits for the same reason: they change the one line they
mean and leave the author's formatting alone. No CLI command calls them
yet; they exist so a future status-change command and a remote driver
land against a seam that already has driver-level tests.
"""

from __future__ import annotations

import re
from typing import Protocol

from boardkit.board import (
    GENERATED,
    HEADING_RE,
    LOG_HEADING,
    STATUSES,
    card_file_pattern,
    card_id_pattern,
    parse_card,
)
from boardkit.config import Config


class StoreError(Exception):
    """Raised with the full list of store errors found."""

    def __init__(self, errors: list[str]) -> None:
        super().__init__("\n".join(errors))
        self.errors = errors


class CardStore(Protocol):
    """What the CLI core may ask of any board store."""

    def list_cards(self) -> list[dict]: ...

    def get_card(self, card_id: str) -> dict: ...

    def transition(self, card_id: str, status: str) -> None: ...

    def append_log(self, card_id: str, line: str) -> None: ...


STATUS_LINE_RE = re.compile(r"^status:[^\n]*$", re.MULTILINE)


class DirStore:
    """Driver #1: one markdown file per card in the config's cards_dir."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self._file_re = card_file_pattern(config)
        self._id_re = card_id_pattern(config)

    def list_cards(self) -> list[dict]:
        errors: list[str] = []
        cards: list[dict] = []
        for path in sorted(self.config.board.cards_dir.glob("*.md")):
            if path.name in GENERATED or path.name.startswith("_"):
                continue
            if not self._file_re.match(path.name):
                errors.append(f"{path.name}: filename violates <id>-<slug>.md naming rule")
                continue
            card = parse_card(path, self._id_re, errors)
            if card is not None:
                cards.append(card)
        if errors:
            raise StoreError(errors)
        return cards

    def get_card(self, card_id: str) -> dict:
        for card in self.list_cards():
            if card["id"] == card_id:
                return card
        raise StoreError([f"no card with id '{card_id}' in {self.config.board.cards_dir}"])

    def _card_path(self, card_id: str):
        return self.config.board.cards_dir / self.get_card(card_id)["_file"]

    def transition(self, card_id: str, status: str) -> None:
        if status not in STATUSES:
            raise StoreError([f"status '{status}' not in {STATUSES}"])
        path = self._card_path(card_id)
        text = path.read_text(encoding="utf-8")
        end = text.find("\n---\n", 4)
        frontmatter = text[:end]
        replaced, count = STATUS_LINE_RE.subn(f"status: {status}", frontmatter)
        if count != 1:
            raise StoreError(
                [f"{path.name}: expected exactly one status line in frontmatter, found {count}"]
            )
        path.write_text(replaced + text[end:], encoding="utf-8")

    def append_log(self, card_id: str, line: str) -> None:
        """Append one bullet at the end of the card's Log section."""
        path = self._card_path(card_id)
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines(keepends=True)
        log_level: int | None = None
        insert_at: int | None = None
        for index, raw in enumerate(lines):
            heading = HEADING_RE.match(raw.rstrip("\n"))
            if heading is None:
                continue
            depth = len(heading.group(1))
            if log_level is not None and depth <= log_level:
                insert_at = index
                break
            if log_level is None and heading.group(2).strip().lower() == LOG_HEADING:
                log_level = depth
        if log_level is None:
            raise StoreError([f"{path.name}: no Log section to append to"])
        if insert_at is None:
            # Log runs to end of file; append after trimming trailing blank lines.
            body = "".join(lines).rstrip("\n")
            path.write_text(f"{body}\n- {line}\n", encoding="utf-8")
            return
        head = "".join(lines[:insert_at]).rstrip("\n")
        tail = "".join(lines[insert_at:])
        path.write_text(f"{head}\n- {line}\n\n{tail}", encoding="utf-8")
