"""The CardStore seam (RULE-3): the CLI core's view of a board's cards.

The markdown-dir layout is driver #1, not the data model. Card identity is
the `id` frontmatter, never the filename: every method takes card ids, and
a renamed file that still declares the same id is the same card. One
source of truth per board, no bidirectional sync; generated views are
non-authoritative renders; gates, WIP, routing, and process semantics
stay kit-side permanently. A remote driver (`linear:` is reserved) would
map card CRUD, status, comments, and read-only gate visibility only.

Seam surface shipped here: board metadata, list/load/get, link checking,
`transition`, and `append_log`. `put` (whole-card replace) is deferred:
it has no caller yet and no format-preserving serialization, and a
speculative writer that reflows frontmatter would churn every card it
touched. The mutating methods are targeted text edits for the same
reason: they change the one line they mean and leave the author's
formatting alone. No CLI command calls them yet; they exist so a future
status-change command and a remote driver land against a seam that
already has driver-level tests.

`build_board` reads the board through this seam (S28), so the read half
is production code: the traversal, the id scheme and the link resolution
all arrive through a store the CLI constructs at board-resolution time.
Nothing in `board.py` names a driver.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Protocol

from boardkit.board import (
    GENERATED,
    HEADING_RE,
    LINK_RE,
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


@dataclass(frozen=True)
class BoardMeta:
    """The board-level surface a driver serves to the CLI core.

    The card identity scheme, and nothing else. Gates, WIP, lanes and
    routing are process semantics and stay kit-side permanently (module
    docstring), read from the board's own config, so no driver gets a say
    in them. What a driver does own is what counts as a card id on its
    board - `S12` under a markdown-dir prefix, an issue key on a remote
    tracker - which is what the core needs to validate an id and to order
    the generated views.
    """

    id_prefix: str
    sentinel_ids: tuple[str, ...]

    @classmethod
    def from_config(cls, config: Config) -> BoardMeta:
        return cls(
            id_prefix=config.board.id_prefix,
            sentinel_ids=tuple(config.board.sentinel_ids),
        )


class CardStore(Protocol):
    """What the CLI core may ask of any board store."""

    def board_meta(self) -> BoardMeta: ...

    def load_cards(self, errors: list[str]) -> list[dict]: ...

    def list_cards(self) -> list[dict]: ...

    def get_card(self, card_id: str) -> dict: ...

    def check_links(self, card: dict, generated: set[str], errors: list[str]) -> None: ...

    def transition(self, card_id: str, status: str) -> None: ...

    def append_log(self, card_id: str, line: str) -> None: ...


STATUS_LINE_RE = re.compile(r"^status:[^\n]*$", re.MULTILINE)


class DirStore:
    """Driver #1: one markdown file per card in the config's cards_dir."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self._meta = BoardMeta.from_config(config)
        self._file_re = card_file_pattern(self._meta)
        self._id_re = card_id_pattern(self._meta)

    def board_meta(self) -> BoardMeta:
        return self._meta

    def load_cards(self, errors: list[str]) -> list[dict]:
        """Every card on the board, appending to `errors` what it could not load.

        Card-shaped problems accumulate instead of raising so that one
        pass can report all of them; `list_cards` is the raising wrapper
        for callers that want the first failure to stop them.

        A duplicate id is a driver invariant, not a validation rule the
        core layers on top: two records claiming one id are two cards the
        seam cannot tell apart, and the driver is the only layer that can
        still name the file they came from. Both records are returned
        rather than one silently winning, and the caller raises on the
        error before anything downstream has to choose between them.
        """
        cards: list[dict] = []
        seen: set[str] = set()
        for path in sorted(self.config.board.cards_dir.glob("*.md")):
            if path.name in GENERATED or path.name.startswith("_"):
                continue
            if not self._file_re.match(path.name):
                errors.append(f"{path.name}: filename violates <id>-<slug>.md naming rule")
                continue
            card = parse_card(path, self._id_re, errors)
            if card is None:
                continue
            if card["id"] in seen:
                errors.append(f"{path.name}: duplicate id {card['id']}")
            seen.add(card["id"])
            cards.append(card)
        return cards

    def list_cards(self) -> list[dict]:
        errors: list[str] = []
        cards = self.load_cards(errors)
        if errors:
            raise StoreError(errors)
        return cards

    def check_links(self, card: dict, generated: set[str], errors: list[str]) -> None:
        """Every relative link in the card body must resolve.

        Layout-specific by nature, which is why it sits on the driver: a
        link in a markdown card resolves against the directory the cards
        sit in, and a driver with no directory answers this its own way.

        `generated` is the set of this run's own outputs, which always
        exist after it. It is not the whole GENERATED set: `deferred.md`
        is written only while some gate is open-deferred, so on a board
        with none, a link to it is as broken as a link to a deleted card.
        """
        cards_dir = self.config.board.cards_dir
        for match in LINK_RE.finditer(card["_body"]):
            target = match.group(1)
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            if target in generated:
                continue
            if target in GENERATED:
                # A generated name outside this run's outputs is stale: a copy
                # left on disk does not legitimize the link, because render
                # deletes it on the next pass.
                errors.append(f"{card['_file']}: broken link '{target}' (stale generated view)")
                continue
            if not (cards_dir / target).resolve().exists():
                errors.append(f"{card['_file']}: broken link '{target}'")

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


def open_store(config: Config) -> CardStore:
    """The driver serving a resolved board config.

    One scheme ships today, so this returns driver #1 unconditionally.
    It exists as a function anyway because it is the single place a
    second scheme is chosen: when `linear:` lands, the store ref picks
    the driver here and nowhere else.
    """
    return DirStore(config)
