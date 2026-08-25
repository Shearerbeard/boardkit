"""Tests for `boardkit verify-receipt` and the receipt checks in check/doctor.

The command is the tracked-repo-only validation path of ADR 0001 section 7:
transcription (manifest root from the digest table), card-log agreement,
reviewer distinctness, and range resolution. The tamper case is the Gate M
shape: digests validate against fetched bytes, and altered bytes fail.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from conftest import config_text

from boardkit.cli import cmd_check, cmd_render, cmd_verify_receipt
from boardkit.config import load_config
from boardkit.doctor import Severity, _check_receipts, _Checks
from boardkit.receipts import (
    close_review_round,
    hash_tree,
    manifest_root,
    parse_receipt,
    publish_pending,
    verify_receipt,
)
from boardkit.store import DirStore, PacketRef, SidecarStore, StoreRef, open_store

CARD = """\
---
id: S1
title: First card
status: in-review
depends: []
serialize-with: []
lineage: primary
executor: any
gates: "S -> A"
user-gates: []
commit-range: {range}
---

# S1: First card

## Log

- 2026-08-01 Minted.
"""


class _Args:
    def __init__(self, config: str, receipt: str = "") -> None:
        self.config = config
        self.board = None
        self.receipt = receipt


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True
    )
    return result.stdout


def _init_repo(repo: Path) -> None:
    repo.mkdir(parents=True, exist_ok=True)
    _git(repo, "init", "-q", "--object-format=sha1")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")
    _git(repo, "config", "commit.gpgsign", "false")
    _git(repo, "config", "core.hooksPath", "hooks-disabled")


def _commit(repo: Path, message: str) -> str:
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", message)
    return _git(repo, "rev-parse", "HEAD").strip()


@pytest.fixture
def board(tmp_path: Path) -> Path:
    """A board whose card has a real commit range in a real repo."""
    repo = tmp_path / "repo"
    _init_repo(repo)
    (repo / "file.txt").write_text("a\n", encoding="utf-8")
    base = _commit(repo, "C0 base")
    (repo / "file.txt").write_text("b\n", encoding="utf-8")
    tip = _commit(repo, "C1 the work\n\nCard: S1")
    cards = tmp_path / "cards"
    cards.mkdir()
    (cards / "s1-first-card.md").write_text(CARD.format(range=f"{base}..{tip}"), encoding="utf-8")
    (tmp_path / "boardkit.toml").write_text(config_text(repo="repo"), encoding="utf-8")
    packet = tmp_path / "reviews" / "S1"
    packet.mkdir(parents=True)
    (packet / "full-range.diff").write_text("the diff\n", encoding="utf-8")
    return tmp_path


def _close(board: Path) -> Path:
    config = load_config(board / "boardkit.toml")
    return close_review_round(
        config,
        open_store(config),
        card_id="S1",
        gate="A",
        round=1,
        verdict="PASS",
        findings=0,
        route="codex-reviewer",
        author_models=["claude-fable-5"],
        reviewer_model="gpt-5.6-sol",
        commit_range=DirStore(config).get_card("S1")["commit-range"],
        findings_text="None.",
        checks_not_run="None.",
        dated="2026-08-24",
    )


def test_a_clean_receipt_passes_every_check(board: Path) -> None:
    path = _close(board)
    config = load_config(board / "boardkit.toml")
    checks = verify_receipt(config, DirStore(config).list_cards(), path)
    assert checks and all(check.ok for check in checks)


def test_a_tampered_digest_row_fails_the_manifest_root(board: Path) -> None:
    path = _close(board)
    text = path.read_text(encoding="utf-8")
    # Alter one digest row without touching the recorded root: the table no
    # longer arrives whole, and the recomputation says so.
    digest = next(line for line in text.splitlines() if line.startswith("| ") and "diff" in line)
    tampered = digest.replace(digest.split("|")[1].strip(), "0" * 64)
    path.write_text(text.replace(digest, tampered), encoding="utf-8")
    config = load_config(board / "boardkit.toml")
    checks = verify_receipt(config, DirStore(config).list_cards(), path)
    root_check = next(c for c in checks if c.name.startswith("manifest-root"))
    assert not root_check.ok


def test_an_unresolvable_commit_range_fails(board: Path) -> None:
    path = _close(board)
    text = path.read_text(encoding="utf-8")
    old = DirStore(load_config(board / "boardkit.toml")).get_card("S1")["commit-range"]
    left = old.split("..")[0]
    path.write_text(text.replace(old, f"{left}..{'0' * 40}"), encoding="utf-8")
    config = load_config(board / "boardkit.toml")
    checks = verify_receipt(config, DirStore(config).list_cards(), path)
    range_check = next(c for c in checks if c.name == "commit-range")
    assert not range_check.ok
    assert "does not resolve" in range_check.detail


def test_verify_receipt_cli_exit_codes(board: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = _close(board)
    args = _Args(config=str(board / "boardkit.toml"), receipt=str(path))
    assert cmd_verify_receipt(args) == 0
    out = capsys.readouterr().out
    assert "manifest-root[primary]" in out
    assert "card-log-agreement" in out

    missing = _Args(config=str(board / "boardkit.toml"), receipt=str(board / "none.md"))
    assert cmd_verify_receipt(missing) == 1


def test_fetched_packet_digests_validate_and_tamper_fails(board: Path) -> None:
    """The with-sidecar-access half of section 7, on the dir backend."""
    _close(board)
    receipt_path = board / "receipts" / "S1" / "A-r1.md"
    receipt = parse_receipt(receipt_path)
    store = SidecarStore("bk-sidecar", StoreRef("dir", str(board / "sidecar")), "bk")
    published = store.publish(PacketRef("S1", "A", 1), board / "reviews" / "S1")

    fetched = board / "fetched"
    store.fetch(published, fetched)

    assert manifest_root(hash_tree(fetched)) == receipt.packets[0].manifest

    (fetched / "full-range.diff").write_text("altered\n", encoding="utf-8")
    assert manifest_root(hash_tree(fetched)) != receipt.packets[0].manifest


# --- check and doctor integration ----------------------------------------------


def test_check_fails_when_a_receipt_and_its_log_line_disagree(board: Path) -> None:
    path = _close(board)
    config_path = board / "boardkit.toml"
    assert cmd_render(_Args(config=str(config_path))) == 0
    assert cmd_check(_Args(config=str(config_path))) == 0

    # Break the agreement: rewrite the verdict in the receipt alone.
    path.write_text(
        path.read_text(encoding="utf-8").replace("verdict: PASS", "verdict: FAIL"),
        encoding="utf-8",
    )
    assert cmd_check(_Args(config=str(config_path))) == 1


def test_doctor_warns_while_a_publishable_receipt_sits_unpublished(board: Path) -> None:
    # In-repo is a publishable posture, so an unpublished receipt is a queue
    # item doctor warns about; the remedy names the drain command.
    config_path = board / "boardkit.toml"
    config_path.write_text(
        config_path.read_text(encoding="utf-8") + '\n[artifacts]\nposture = "in-repo"\n',
        encoding="utf-8",
    )
    _close(board)
    checks = _Checks()
    _check_receipts(checks, load_config(config_path))
    warnings = {f.check: f for f in checks.findings if f.severity is Severity.WARN}
    assert set(warnings) == {"receipts.unpublished"}
    assert "boardkit publish-pending" in warnings["receipts.unpublished"].remedy
    assert "receipts.valid" in checks.passed


def test_doctor_does_not_warn_on_ephemeral_receipts(board: Path) -> None:
    """Ephemeral packets never publish, so published: false is their final state."""
    _close(board)
    checks = _Checks()
    _check_receipts(checks, load_config(board / "boardkit.toml"))
    assert checks.findings == []


def test_doctor_errors_on_an_unparseable_receipt(board: Path) -> None:
    receipts = board / "receipts" / "S1"
    receipts.mkdir(parents=True)
    (receipts / "A-r1.md").write_text("not a receipt\n", encoding="utf-8")
    checks = _Checks()
    _check_receipts(checks, load_config(board / "boardkit.toml"))
    errors = {f.check for f in checks.findings if f.severity is Severity.ERROR}
    assert errors == {"receipts.valid"}


def test_doctor_quiet_on_a_board_with_no_receipts(tmp_path: Path) -> None:
    (tmp_path / "boardkit.toml").write_text(config_text(), encoding="utf-8")
    checks = _Checks()
    _check_receipts(checks, load_config(tmp_path / "boardkit.toml"))
    assert checks.findings == []
    assert {"receipts.valid", "receipts.unpublished"} <= set(checks.passed)


def test_doctor_clears_once_published(board: Path) -> None:
    _close(board)
    # Repoint the board at an in-repo posture so publish needs no overlay.
    config_path = board / "boardkit.toml"
    config_path.write_text(
        config_path.read_text(encoding="utf-8") + '\n[artifacts]\nposture = "in-repo"\n',
        encoding="utf-8",
    )
    config = load_config(config_path)
    publish_pending(config, board / "receipts" / "S1" / "A-r1.md")
    checks = _Checks()
    _check_receipts(checks, config)
    assert checks.findings == []
