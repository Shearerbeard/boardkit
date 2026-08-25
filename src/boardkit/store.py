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

import hashlib
import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
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
from boardkit.config import (
    BOARDKIT_DIRNAME,
    LOCAL_FILENAME,
    Config,
    StoreRef,
    find_boardkit,
    git_common_boardkit,
    load_overlay,
    registry_rows,
)


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


# --- The ArtifactStore seam (ADR 0001) --------------------------------------
#
# A second seam beside CardStore: where review packets are published. The
# seam moves bytes and nothing else - digests, verdicts, and gate state
# are computed kit-side and handed in through the packet's own manifest
# file (driver 4). `list`, `delete`, and garbage collection stay off the
# seam on purpose (driver 6): no caller needs them, and a delete's only
# correct use is one the append-only rollback rule forbids.

# The one packet file the digest table does not attest (a table cannot
# hash its own root). The receipt writer computes it core-side; drivers
# read it for addressing and collision comparison and never hash a
# payload. Its bytes are exactly the manifest root's input, so a
# byte-for-byte comparison IS the full-root comparison ADR section 5
# states.
MANIFEST_FILENAME = "receipt-manifest.txt"

# Where the in-repo posture publishes: a tracked directory under the board.
IN_REPO_PACKETS_DIR = "docs/board/packets"


@dataclass(frozen=True)
class PacketRef:
    """A packet's logical identity (ADR 0001 section 1).

    Names no filesystem path, so the same ref resolves under every
    posture. `suffix` is the `review-packet --suffix` of a multi-repo or
    fix-round packet.
    """

    card_id: str
    gate: str
    round: int
    suffix: str | None = None

    @property
    def slug(self) -> str:
        """The receipt-filename and store-path form: `A-r1[-<suffix>]`."""
        return f"{self.gate}-r{self.round}" + (f"-{self.suffix}" if self.suffix else "")


@dataclass(frozen=True)
class Published:
    """What a receipt records about one packet (ADR 0001 section 1).

    Carries no digests - those are the receipt's own attestation,
    computed core-side. `locator` is None exactly when publication did
    not happen, so an unpublished entry can never point anywhere.
    """

    store: str
    locator: str | None
    published: bool


@dataclass(frozen=True)
class StoreInfo:
    """What `boardkit doctor` may print about a store."""

    posture: str
    location: str
    writable: bool


class ArtifactStore(Protocol):
    """What the CLI core may ask of any artifact store."""

    def describe(self) -> StoreInfo: ...

    def publish(self, ref: PacketRef, source: Path) -> Published: ...

    def fetch(self, published: Published, dest: Path) -> Path: ...


def _read_manifest(source: Path) -> bytes:
    """The core-written manifest of the packet being published.

    A packet with no manifest was never hashed by the receipt writer, so
    publishing it would attest nothing - refuse rather than ship bytes no
    receipt can name.
    """
    manifest = source / MANIFEST_FILENAME
    if not manifest.is_file():
        raise StoreError(
            [
                f"{source}: no {MANIFEST_FILENAME}; the receipt writer hashes the "
                "packet before publish, and this packet was never hashed"
            ]
        )
    return manifest.read_bytes()


def _copy_in(source: Path, target: Path) -> bool:
    """Copy the packet to `target` under the append-only rule. False if equal.

    A target that already exists compares manifests (ADR 0001 section 5):
    equal is an idempotent republish needing no write, different is a
    refusal, because overwriting would silently invalidate every receipt
    already naming that path.
    """
    manifest = _read_manifest(source)
    if target.exists():
        existing = target / MANIFEST_FILENAME
        if existing.is_file() and existing.read_bytes() == manifest:
            return False
        raise StoreError(
            [
                f"{target}: a different packet already occupies this path; the store "
                "is append-only, so overwriting it would invalidate the receipts "
                "that name it"
            ]
        )
    shutil.copytree(source, target)
    return True


class EphemeralStore:
    """The default posture: packets stay gitignored working material."""

    def __init__(self, config: Config) -> None:
        self.config = config

    def describe(self) -> StoreInfo:
        return StoreInfo("ephemeral", str(self.config.review.output_dir), True)

    def publish(self, ref: PacketRef, source: Path) -> Published:
        """A recorded no-op: the receipt says `published: false`, honestly."""
        return Published(store="ephemeral", locator=None, published=False)

    def fetch(self, published: Published, dest: Path) -> Path:
        raise StoreError(
            [
                "ephemeral packets were never published; there is nothing to fetch. "
                "Regenerate the packet with `boardkit review-packet` if the range "
                "still resolves"
            ]
        )


class InRepoStore:
    """The in-repo posture: packets are copied into a tracked directory."""

    def __init__(self, config: Config) -> None:
        self.root = config.root
        self.packets_dir = config.root / IN_REPO_PACKETS_DIR

    def describe(self) -> StoreInfo:
        return StoreInfo("in-repo", str(self.packets_dir), os.access(self.root, os.W_OK))

    def publish(self, ref: PacketRef, source: Path) -> Published:
        target = self.packets_dir / ref.card_id / ref.slug
        _copy_in(source, target)
        # The locator is the repo-relative path; the tracked repo's own
        # history is the anchor, the same one receipts rest on.
        locator = f"dir:{target.relative_to(self.root).as_posix()}"
        return Published(store="in-repo", locator=locator, published=True)

    def fetch(self, published: Published, dest: Path) -> Path:
        locator = published.locator or ""
        value = locator.removeprefix("dir:")
        if value == locator or Path(value).is_absolute() or ".." in Path(value).parts:
            raise StoreError([f"in-repo locator {locator!r} is not a repo-relative dir: path"])
        source = self.root / value
        if not source.is_dir():
            raise StoreError(
                [f"nothing at {value} in {self.root}; the packet is not in this clone"]
            )
        shutil.copytree(source, dest)
        return dest


class SidecarStore:
    """The sidecar posture: publish into a git repository or a directory.

    The path addresses, the anchor verifies (ADR 0001 section 5): under
    `git:` the anchor is the publish commit's sha, under `dir:` it is a
    prefix of the manifest root. Both share one locator grammar,
    `<scheme>:<store-name>@<anchor>#<board>/<ID>/<gate>-r<N>[-<suffix>]`.
    """

    def __init__(self, name: str, location: StoreRef, board: str) -> None:
        self.name = name
        self.location = location
        self.board = board

    def describe(self) -> StoreInfo:
        printable = f"{self.location.scheme}:{self.location.value}"
        if self.location.scheme == "dir":
            root = Path(self.location.value)
            writable = not root.exists() or (root.is_dir() and os.access(root, os.W_OK))
        else:
            # A remote URL cannot be probed without a network round trip;
            # publish fails loudly if it is unreachable.
            writable = "://" in self.location.value or Path(self.location.value).is_dir()
        return StoreInfo("sidecar", printable, writable)

    def _target_rel(self, ref: PacketRef) -> str:
        return f"{self.board}/{ref.card_id}/{ref.slug}"

    def publish(self, ref: PacketRef, source: Path) -> Published:
        if self.location.scheme == "git":
            return self._publish_git(ref, source)
        return self._publish_dir(ref, source)

    def _publish_dir(self, ref: PacketRef, source: Path) -> Published:
        root = Path(self.location.value)
        root.mkdir(parents=True, exist_ok=True)
        manifest = _read_manifest(source)
        # The dir backend's anchor is a prefix of the manifest root - an
        # identifier, never the check (the full root in the receipt is).
        anchor = hashlib.sha256(manifest).hexdigest()[:12]
        target = root / self._target_rel(ref)
        _copy_in(source, target)
        locator = f"dir:{self.name}@{anchor}#{self._target_rel(ref)}"
        return Published(store=self.name, locator=locator, published=True)

    def _publish_git(self, ref: PacketRef, source: Path) -> Published:
        manifest = _read_manifest(source)
        target_rel = self._target_rel(ref)
        with tempfile.TemporaryDirectory(prefix="boardkit-sidecar-") as tmp:
            clone = Path(tmp) / "repo"
            _git(None, "clone", "--quiet", self.location.value, str(clone))
            target = clone / target_rel
            if target.exists():
                existing = target / MANIFEST_FILENAME
                if existing.is_file() and existing.read_bytes() == manifest:
                    # Idempotent republish: the bytes already sit at this
                    # path in HEAD's tree, so HEAD is a valid anchor.
                    sha = _git(clone, "rev-parse", "HEAD").strip()
                    return Published(self.name, f"git:{self.name}@{sha}#{target_rel}", True)
                raise StoreError(
                    [
                        f"{target_rel}: a different packet already occupies this path "
                        "in the sidecar; the store is append-only, so overwriting it "
                        "would invalidate the receipts that name it"
                    ]
                )
            shutil.copytree(source, target)
            _git(clone, "add", "-A", "--", target_rel)
            _git(clone, "commit", "--quiet", "-m", f"Publish {target_rel}")
            self._push(clone)
            sha = _git(clone, "rev-parse", "HEAD").strip()
        return Published(self.name, f"git:{self.name}@{sha}#{target_rel}", True)

    def _push(self, clone: Path) -> None:
        """Push, rebasing and retrying exactly once on a non-fast-forward."""
        try:
            _git(clone, "push", "origin", "HEAD")
            return
        except StoreError:
            pass
        branch = _git(clone, "rev-parse", "--abbrev-ref", "HEAD").strip()
        try:
            _git(clone, "pull", "--rebase", "origin", branch)
            _git(clone, "push", "origin", "HEAD")
        except StoreError as exc:
            raise StoreError(
                [f"sidecar push rejected, and the rebase-and-retry also failed: {exc}"]
            ) from exc

    def fetch(self, published: Published, dest: Path) -> Path:
        store_name, anchor, path = _parse_sidecar_locator(published.locator)
        if store_name != self.name:
            raise StoreError(
                [f"locator names store '{store_name}', but this store is '{self.name}'"]
            )
        if self.location.scheme == "dir":
            source = Path(self.location.value) / path
            if not source.is_dir():
                raise StoreError(
                    [
                        f"nothing at {path} under {self.location.value}; the packet may "
                        "never have been archived (a dir: fetch that finds nothing "
                        "cannot tell, per ADR 0001 section 5)"
                    ]
                )
            shutil.copytree(source, dest)
            return dest
        with tempfile.TemporaryDirectory(prefix="boardkit-sidecar-") as tmp:
            clone = Path(tmp) / "repo"
            _git(None, "clone", "--quiet", self.location.value, str(clone))
            try:
                _git(clone, "checkout", "--quiet", anchor)
            except StoreError as exc:
                raise StoreError(
                    [
                        f"locator commit {anchor} does not resolve in the sidecar; "
                        "if its history was rewritten, the digests in the receipt "
                        "still identify the content (ADR 0001 section 6)"
                    ]
                ) from exc
            source = clone / path
            if not source.is_dir():
                raise StoreError([f"nothing at {path} in sidecar commit {anchor}"])
            shutil.copytree(source, dest)
        return dest


_LOCATOR_RE = re.compile(r"^(dir|git):([^@#]+)@([^@#]+)#(.+)$")


def _parse_sidecar_locator(locator: str | None) -> tuple[str, str, str]:
    """A sidecar locator as (store name, anchor, store-relative path)."""
    match = _LOCATOR_RE.match(locator or "")
    if match is None:
        raise StoreError(
            [
                f"{locator!r} is not a sidecar locator "
                "(`<scheme>:<store-name>@<anchor>#<board>/<ID>/<gate>-r<N>`)"
            ]
        )
    _scheme, store_name, anchor, path = match.groups()
    return store_name, anchor, path


def _git(repo: Path | None, *args: str) -> str:
    """Run git, raising StoreError with stderr on failure. None means PATH cwd."""
    cmd = ["git"] if repo is None else ["git", "-C", str(repo)]
    result = subprocess.run([*cmd, *args], capture_output=True, text=True, check=False)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"git exited {result.returncode}"
        raise StoreError([f"git {' '.join(args)} failed: {detail}"])
    return result.stdout


def open_artifact_store(config: Config, boardkit_dir: Path | None = None) -> ArtifactStore:
    """The driver behind the board's configured posture (ADR 0001).

    Mirrors `open_store`: the single place a posture picks a driver. A
    sidecar resolves its logical store name through the machine overlay;
    a name the overlay does not define fails naming the store and the
    file to add it to, and a board no registry row resolves fails too,
    because the short-code namespaces the sidecar paths.
    """
    posture = config.artifacts.posture
    if posture == "ephemeral":
        return EphemeralStore(config)
    if posture == "in-repo":
        return InRepoStore(config)

    name = config.artifacts.store
    if name is None:  # load_config refuses this; guard the type, not the case
        raise ValueError("[artifacts]: posture 'sidecar' requires a 'store'")
    boardkit_dir = boardkit_dir or find_boardkit(config.root) or git_common_boardkit(config.root)
    if boardkit_dir is None:
        raise ValueError(
            f"[artifacts] posture 'sidecar' namespaces packets by registry "
            f"short-code, but no {BOARDKIT_DIRNAME}/ registry is reachable from "
            f"{config.root}"
        )
    rows, _errors = registry_rows(boardkit_dir)
    code = next((row.code for row in rows if row.resolved_root == config.root), None)
    if code is None:
        raise ValueError(
            f"no row in {boardkit_dir / 'manifest.toml'} resolves to {config.root}; "
            "a sidecar board needs its registry short-code to namespace packets"
        )
    location = load_overlay(boardkit_dir).stores.get(name)
    if location is None:
        raise ValueError(
            f"store '{name}' is not defined on this machine; add it to "
            f"{boardkit_dir / LOCAL_FILENAME} "
            f'([stores.{name}] location = "git:/absolute/path/to/sidecar.git")'
        )
    return SidecarStore(name, location, code)
