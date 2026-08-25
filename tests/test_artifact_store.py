"""Tests for the ArtifactStore seam: the three posture drivers and the resolver.

Real temp directories and real git repos throughout (no mocking): a
sidecar's collision and push-retry rules are git behavior, and a fake git
would prove nothing about them. The manifest file in each packet stands in
for the receipt writer's hashing step, which receipts.py's own tests cover.
"""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

import pytest
from conftest import config_text

from boardkit.config import StoreRef, load_config
from boardkit.store import (
    MANIFEST_FILENAME,
    EphemeralStore,
    InRepoStore,
    PacketRef,
    SidecarStore,
    StoreError,
    open_artifact_store,
)

REF = PacketRef(card_id="S1", gate="A", round=1)
REF_SUFFIXED = PacketRef(card_id="S1", gate="A", round=1, suffix="consumer")


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True
    )
    return result.stdout


@pytest.fixture
def git_identity(monkeypatch: pytest.MonkeyPatch) -> None:
    """Commits in a fresh clone need an identity; the env carries one without
    touching global or repo config."""
    for key in ("GIT_AUTHOR_NAME", "GIT_COMMITTER_NAME"):
        monkeypatch.setenv(key, "Test User")
    for key in ("GIT_AUTHOR_EMAIL", "GIT_COMMITTER_EMAIL"):
        monkeypatch.setenv(key, "test@example.com")


def _packet(root: Path, files: dict[str, str] | None = None) -> Path:
    """A packet directory with content and its core-written manifest."""
    packet = root / "packet"
    packet.mkdir(parents=True)
    for name, content in (files or {"full-range.diff": "diff bytes\n"}).items():
        (packet / name).write_text(content, encoding="utf-8")
    lines = []
    for path in sorted(p for p in packet.rglob("*") if p.is_file()):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {path.relative_to(packet).as_posix()}")
    (packet / MANIFEST_FILENAME).write_text(
        "boardkit-receipt:v1\n" + "\n".join(lines) + "\n", encoding="utf-8"
    )
    return packet


def _bare_sidecar(root: Path) -> Path:
    bare = root / "sidecar.git"
    bare.mkdir()
    _git(bare, "init", "-q", "--bare", "--object-format=sha1", "--initial-branch=main")
    _git(bare, "config", "core.hooksPath", "hooks-disabled")
    return bare


def _config(tmp_path: Path, artifacts: str = "") -> Path:
    text = config_text() + artifacts
    (tmp_path / "boardkit.toml").write_text(text, encoding="utf-8")
    return tmp_path / "boardkit.toml"


# --- EphemeralStore ----------------------------------------------------------


def test_ephemeral_publish_is_a_recorded_noop(tmp_path: Path) -> None:
    store = EphemeralStore(load_config(_config(tmp_path)))
    published = store.publish(REF, _packet(tmp_path))
    assert published.published is False
    assert published.locator is None
    assert store.describe().posture == "ephemeral"


def test_ephemeral_fetch_raises(tmp_path: Path) -> None:
    store = EphemeralStore(load_config(_config(tmp_path)))
    with pytest.raises(StoreError, match="never published"):
        store.fetch(store.publish(REF, _packet(tmp_path)), tmp_path / "dest")


# --- InRepoStore -------------------------------------------------------------


def test_in_repo_publish_copies_and_locates_by_repo_relative_path(tmp_path: Path) -> None:
    config = load_config(_config(tmp_path, '\n[artifacts]\nposture = "in-repo"\n'))
    store = InRepoStore(config)
    published = store.publish(REF, _packet(tmp_path))
    assert published.published
    assert published.locator == "dir:docs/board/packets/S1/A-r1"
    target = tmp_path / "docs" / "board" / "packets" / "S1" / "A-r1"
    assert (target / "full-range.diff").read_text(encoding="utf-8") == "diff bytes\n"
    assert (target / MANIFEST_FILENAME).is_file()


def test_in_repo_fetch_round_trips_the_packet(tmp_path: Path) -> None:
    config = load_config(_config(tmp_path, '\n[artifacts]\nposture = "in-repo"\n'))
    store = InRepoStore(config)
    published = store.publish(REF, _packet(tmp_path))
    dest = tmp_path / "fetched"
    store.fetch(published, dest)
    assert (dest / "full-range.diff").is_file()


def test_in_repo_fetch_of_a_missing_packet_fails_loudly(tmp_path: Path) -> None:
    config = load_config(_config(tmp_path, '\n[artifacts]\nposture = "in-repo"\n'))
    store = InRepoStore(config)
    published = store.publish(REF, _packet(tmp_path))
    moved = published.__class__(
        store=published.store, locator="dir:docs/board/packets/S1/A-r9", published=True
    )
    with pytest.raises(StoreError, match="not in this clone"):
        store.fetch(moved, tmp_path / "dest")


def test_collision_rules_hold_in_every_directory_store(tmp_path: Path) -> None:
    """Equal bytes republish idempotently; different bytes are refused (append-only)."""
    config = load_config(_config(tmp_path, '\n[artifacts]\nposture = "in-repo"\n'))
    store = InRepoStore(config)
    first = store.publish(REF, _packet(tmp_path / "a"))
    second = store.publish(REF, _packet(tmp_path / "b"))
    assert second == first  # same locator, no rewrite

    different = _packet(tmp_path / "c", {"full-range.diff": "other bytes\n"})
    with pytest.raises(StoreError, match="append-only"):
        store.publish(REF, different)


# --- SidecarStore, dir backend ------------------------------------------------


def _dir_store(tmp_path: Path) -> SidecarStore:
    return SidecarStore("bk-sidecar", StoreRef("dir", str(tmp_path / "sidecar")), "bk")


def test_dir_sidecar_locator_carries_the_manifest_root_prefix(tmp_path: Path) -> None:
    store = _dir_store(tmp_path)
    packet = _packet(tmp_path / "src")
    published = store.publish(REF_SUFFIXED, packet)
    root = hashlib.sha256((packet / MANIFEST_FILENAME).read_bytes()).hexdigest()
    assert published.locator == f"dir:bk-sidecar@{root[:12]}#bk/S1/A-r1-consumer"
    assert store.describe().posture == "sidecar"


def test_dir_sidecar_refuses_a_missing_manifest(tmp_path: Path) -> None:
    packet = tmp_path / "packet"
    packet.mkdir()
    (packet / "full-range.diff").write_text("diff bytes\n", encoding="utf-8")
    with pytest.raises(StoreError, match=MANIFEST_FILENAME):
        _dir_store(tmp_path).publish(REF, packet)


def test_dir_sidecar_collision_rules(tmp_path: Path) -> None:
    store = _dir_store(tmp_path)
    first = store.publish(REF, _packet(tmp_path / "a"))
    again = store.publish(REF, _packet(tmp_path / "b"))
    assert again == first
    with pytest.raises(StoreError, match="append-only"):
        store.publish(REF, _packet(tmp_path / "c", {"full-range.diff": "changed\n"}))


def test_dir_sidecar_fetch_copies_by_path(tmp_path: Path) -> None:
    store = _dir_store(tmp_path)
    published = store.publish(REF, _packet(tmp_path / "src"))
    dest = tmp_path / "dest"
    store.fetch(published, dest)
    assert (dest / MANIFEST_FILENAME).is_file()
    with pytest.raises(StoreError, match="never have been archived"):
        store.fetch(
            published.__class__(
                store="bk-sidecar",
                locator="dir:bk-sidecar@000000000000#bk/S9/A-r1",
                published=True,
            ),
            tmp_path / "nowhere",
        )


# --- SidecarStore, git backend ------------------------------------------------


def test_git_sidecar_publishes_pushes_and_anchors_on_the_commit(
    tmp_path: Path, git_identity: None
) -> None:
    bare = _bare_sidecar(tmp_path)
    store = SidecarStore("bk-sidecar", StoreRef("git", str(bare)), "bk")
    published = store.publish(REF, _packet(tmp_path / "src"))

    scheme, rest = published.locator.split("@", 1)
    sha, _, path = rest.partition("#")
    assert scheme == "git:bk-sidecar"
    assert path == "bk/S1/A-r1"
    # The anchor resolves in the sidecar and pins exactly the published bytes.
    assert _git(bare, "rev-parse", "--verify", f"{sha}^{{commit}}")
    assert _git(bare, "show", f"{sha}:{path}/full-range.diff") == "diff bytes\n"


def test_git_sidecar_republish_is_idempotent_and_mismatch_refused(
    tmp_path: Path, git_identity: None
) -> None:
    bare = _bare_sidecar(tmp_path)
    store = SidecarStore("bk-sidecar", StoreRef("git", str(bare)), "bk")
    first = store.publish(REF, _packet(tmp_path / "a"))
    before = _git(bare, "rev-parse", "HEAD").strip()
    again = store.publish(REF, _packet(tmp_path / "b"))
    assert again == first
    assert _git(bare, "rev-parse", "HEAD").strip() == before  # no new commit

    with pytest.raises(StoreError, match="append-only"):
        store.publish(REF, _packet(tmp_path / "c", {"full-range.diff": "changed\n"}))


def test_git_sidecar_fetch_checks_out_the_anchor(tmp_path: Path, git_identity: None) -> None:
    bare = _bare_sidecar(tmp_path)
    store = SidecarStore("bk-sidecar", StoreRef("git", str(bare)), "bk")
    published = store.publish(REF, _packet(tmp_path / "src"))
    dest = tmp_path / "dest"
    store.fetch(published, dest)
    assert (dest / "full-range.diff").read_text(encoding="utf-8") == "diff bytes\n"

    bogus = published.__class__(
        store="bk-sidecar",
        locator="git:bk-sidecar@" + "0" * 40 + "#bk/S1/A-r1",
        published=True,
    )
    with pytest.raises(StoreError, match="does not resolve"):
        store.fetch(bogus, tmp_path / "dest2")


def test_git_push_rebases_and_retries_once_on_non_fast_forward(
    tmp_path: Path, git_identity: None
) -> None:
    """A concurrent push between clone and push is the one retried failure."""
    bare = _bare_sidecar(tmp_path)
    store = SidecarStore("bk-sidecar", StoreRef("git", str(bare)), "bk")
    store.publish(REF, _packet(tmp_path / "src"))

    # A stale clone holding one unpushed publish commit...
    stale = tmp_path / "stale"
    _git(tmp_path, "clone", "-q", str(bare), str(stale))
    # ...while a fresher clone lands a different packet first.
    SidecarStore("bk-sidecar", StoreRef("git", str(bare)), "bk").publish(
        PacketRef(card_id="S2", gate="A", round=1), _packet(tmp_path / "other")
    )
    (stale / "bk" / "S9").mkdir(parents=True)
    (stale / "bk" / "S9" / "dummy.txt").write_text("late\n", encoding="utf-8")
    _git(stale, "add", "-A")
    _git(stale, "commit", "-q", "-m", "Publish bk/S9")
    store._push(stale)  # rejected, rebased, retried
    assert _git(bare, "show", "HEAD:bk/S9/dummy.txt") == "late\n"


def test_git_push_fails_loudly_when_the_retry_fails_too(tmp_path: Path, git_identity: None) -> None:
    bare = _bare_sidecar(tmp_path)
    store = SidecarStore("bk-sidecar", StoreRef("git", str(bare)), "bk")
    store.publish(REF, _packet(tmp_path / "src"))

    stale = tmp_path / "stale"
    _git(tmp_path, "clone", "-q", str(bare), str(stale))
    SidecarStore("bk-sidecar", StoreRef("git", str(bare)), "bk").publish(
        PacketRef(card_id="S2", gate="A", round=1), _packet(tmp_path / "other")
    )
    # Both sides touched the same path with different content: the rebase
    # conflicts, the retry never happens, and the failure names itself.
    (stale / "bk" / "S2" / "A-r1").mkdir(parents=True)
    (stale / "bk" / "S2" / "A-r1" / "full-range.diff").write_text("conflict\n", encoding="utf-8")
    (stale / "bk" / "S2" / "A-r1" / MANIFEST_FILENAME).write_text("x\n", encoding="utf-8")
    _git(stale, "add", "-A")
    _git(stale, "commit", "-q", "-m", "Publish bk/S2/A-r1 (conflicting)")
    with pytest.raises(StoreError, match="rebase-and-retry also failed"):
        store._push(stale)


# --- The resolver -------------------------------------------------------------


def _sidecar_board(tmp_path: Path) -> Path:
    """A board whose config names posture sidecar, inside a manifest registry."""
    _config(tmp_path, '\n[artifacts]\nposture = "sidecar"\nstore = "bk-sidecar"\n')
    boardkit_dir = tmp_path / ".boardkit"
    boardkit_dir.mkdir()
    (boardkit_dir / "manifest.toml").write_text(
        'default = "bk"\n\n[boards.bk]\nlocation = "dir:."\nid_prefix = "S"\n',
        encoding="utf-8",
    )
    return tmp_path


def test_resolver_picks_the_posture_driver(tmp_path: Path) -> None:
    config = load_config(_config(tmp_path))
    assert isinstance(open_artifact_store(config), EphemeralStore)
    config = load_config(_config(tmp_path, '\n[artifacts]\nposture = "in-repo"\n'))
    assert isinstance(open_artifact_store(config), InRepoStore)


def test_sidecar_without_an_overlay_row_fails_naming_store_and_file(tmp_path: Path) -> None:
    root = _sidecar_board(tmp_path)
    config = load_config(root / "boardkit.toml")
    with pytest.raises(ValueError, match=r"store 'bk-sidecar'.*local\.toml"):
        open_artifact_store(config, root / ".boardkit")


def test_sidecar_without_a_registry_row_fails_loudly(tmp_path: Path) -> None:
    root = _sidecar_board(tmp_path)
    # A manifest that declares some other board, not this one.
    (root / ".boardkit" / "manifest.toml").write_text(
        'default = "other"\n\n[boards.other]\nlocation = "external"\n', encoding="utf-8"
    )
    config = load_config(root / "boardkit.toml")
    with pytest.raises(ValueError, match="no row .* resolves"):
        open_artifact_store(config, root / ".boardkit")


def test_sidecar_resolves_through_the_overlay(tmp_path: Path) -> None:
    root = _sidecar_board(tmp_path)
    (root / ".boardkit" / "local.toml").write_text(
        f'[stores.bk-sidecar]\nlocation = "dir:{tmp_path}/sidecar"\n', encoding="utf-8"
    )
    config = load_config(root / "boardkit.toml")
    store = open_artifact_store(config, root / ".boardkit")
    assert isinstance(store, SidecarStore)
    assert store.describe().location == f"dir:{tmp_path}/sidecar"
