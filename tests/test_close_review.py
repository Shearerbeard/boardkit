"""Tests for `boardkit close-review` and `boardkit publish-pending`.

The close command is the ADR 0001 section 4 ordering as one invocation:
hash, write (published: false), log - one local unit - then publish as a
separate step whose failure is loud and leaves the receipt standing. The
drain command is the remedy doctor's receipts.unpublished warning names.
Real git sidecars throughout, per the driver suite's rule that a fake git
proves nothing.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from conftest import config_text

from boardkit.cli import build_parser
from boardkit.config import load_config
from boardkit.doctor import _check_receipts, _Checks
from boardkit.receipts import ReviewReceipt, parse_receipt, pending_review_receipts

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


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True
    )
    return result.stdout


@pytest.fixture
def git_identity(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in ("GIT_AUTHOR_NAME", "GIT_COMMITTER_NAME"):
        monkeypatch.setenv(key, "Test User")
    for key in ("GIT_AUTHOR_EMAIL", "GIT_COMMITTER_EMAIL"):
        monkeypatch.setenv(key, "test@example.com")


@pytest.fixture
def board(tmp_path: Path) -> Path:
    """A sidecar-posture board in a manifest registry, overlay not yet written."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "--object-format=sha1")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")
    _git(repo, "config", "commit.gpgsign", "false")
    _git(repo, "config", "core.hooksPath", "hooks-disabled")
    (repo / "file.txt").write_text("a\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "C0 base")
    base = _git(repo, "rev-parse", "HEAD").strip()
    (repo / "file.txt").write_text("b\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "C1 the work\n\nCard: S1")
    tip = _git(repo, "rev-parse", "HEAD").strip()

    cards = tmp_path / "cards"
    cards.mkdir()
    (cards / "s1-first-card.md").write_text(CARD.format(range=f"{base}..{tip}"), encoding="utf-8")
    (tmp_path / "boardkit.toml").write_text(
        config_text(repo="repo") + '\n[artifacts]\nposture = "sidecar"\nstore = "bk-sidecar"\n',
        encoding="utf-8",
    )
    boardkit_dir = tmp_path / ".boardkit"
    boardkit_dir.mkdir()
    (boardkit_dir / "manifest.toml").write_text(
        'default = "bk"\n\n[boards.bk]\nlocation = "dir:."\nid_prefix = "S"\n',
        encoding="utf-8",
    )
    packet = tmp_path / "reviews" / "S1"
    packet.mkdir(parents=True)
    (packet / "full-range.diff").write_text("the diff\n", encoding="utf-8")
    (packet / "REVIEW.md").write_text("# Review\n", encoding="utf-8")
    return tmp_path


def _sidecar(board: Path) -> Path:
    bare = board / "sidecar.git"
    bare.mkdir()
    _git(bare, "init", "-q", "--bare", "--object-format=sha1", "--initial-branch=main")
    return bare


def _overlay(board: Path, location: str) -> None:
    (board / ".boardkit" / "local.toml").write_text(
        f'[stores.bk-sidecar]\nlocation = "git:{location}"\n', encoding="utf-8"
    )


def _run(board: Path, *argv: str) -> int:
    args = build_parser().parse_args(["--config", str(board / "boardkit.toml"), *argv])
    return args.handler(args)


def _close_args(*extra: str) -> list[str]:
    return [
        "close-review",
        "S1",
        "A",
        "1",
        "--verdict",
        "PASS",
        "--findings",
        "0",
        "--route",
        "codex-reviewer",
        "--author-model",
        "claude-fable-5",
        "--reviewer-model",
        "gpt-5.6-sol",
        *extra,
    ]


def _receipt(board: Path) -> ReviewReceipt:
    receipt = parse_receipt(board / "receipts" / "S1" / "A-r1.md")
    assert isinstance(receipt, ReviewReceipt)
    return receipt


def test_close_review_writes_logs_and_publishes_in_one_invocation(
    board: Path, git_identity: None
) -> None:
    bare = _sidecar(board)
    _overlay(board, str(bare))
    assert _run(board, *_close_args()) == 0

    entry = _receipt(board).packets[0]
    assert entry.published
    assert entry.locator is not None and entry.locator.startswith("git:bk-sidecar@")
    sha = entry.locator.split("@")[1].split("#")[0]
    assert _git(bare, "show", f"{sha}:bk/S1/A-r1/full-range.diff") == "the diff\n"

    card = (board / "cards" / "s1-first-card.md").read_text(encoding="utf-8")
    assert "Gate A round 1: PASS" in card
    assert "](../receipts/S1/A-r1.md)" in card

    # The drain sees nothing, and doctor has no receipts findings.
    config = load_config(board / "boardkit.toml")
    assert pending_review_receipts(config) == []
    checks = _Checks()
    _check_receipts(checks, config)
    assert checks.findings == []


def test_close_review_publish_failure_is_loud_and_the_receipt_stands(
    board: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # No overlay row: publication cannot run on this machine.
    assert _run(board, *_close_args()) == 1
    err = capsys.readouterr().err
    assert "publish failed" in err
    assert "boardkit publish-pending" in err

    entry = _receipt(board).packets[0]
    assert entry.published is False
    assert entry.locator is None
    # The log line landed with the receipt (the local unit succeeded).
    card = (board / "cards" / "s1-first-card.md").read_text(encoding="utf-8")
    assert "](../receipts/S1/A-r1.md)" in card


def test_publish_pending_drains_the_queue(board: Path, git_identity: None) -> None:
    assert _run(board, *_close_args()) == 1  # no overlay yet
    receipt_path = board / "receipts" / "S1" / "A-r1.md"
    before = receipt_path.read_text(encoding="utf-8")

    bare = _sidecar(board)
    _overlay(board, str(bare))
    assert _run(board, "publish-pending") == 0

    after = receipt_path.read_text(encoding="utf-8")
    removed = [line for line in before.splitlines() if line not in after.splitlines()]
    added = [line for line in after.splitlines() if line not in before.splitlines()]
    assert removed == ["    published: false"]
    assert len(added) == 2 and added[0] == "    published: true"
    assert added[1].startswith('    locator: "git:bk-sidecar@')

    # Drained: a second run finds nothing, and exits clean.
    assert _run(board, "publish-pending") == 0


def test_close_review_under_ephemeral_posture_is_a_recorded_noop(
    board: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    config_path = board / "boardkit.toml"
    config_path.write_text(config_text(repo="repo"), encoding="utf-8")
    assert _run(board, *_close_args()) == 0
    assert "stays working material" in capsys.readouterr().out

    entry = _receipt(board).packets[0]
    assert entry.published is False
    # Nothing is queued: an ephemeral packet never publishes.
    assert pending_review_receipts(load_config(config_path)) == []


def test_close_review_without_a_commit_range_anywhere_fails(board: Path) -> None:
    card = board / "cards" / "s1-first-card.md"
    text = card.read_text(encoding="utf-8")
    rangeless = "\n".join(
        line for line in text.splitlines() if not line.startswith("commit-range:")
    )
    card.write_text(rangeless + "\n", encoding="utf-8")
    assert _run(board, *_close_args()) == 1
    assert not (board / "receipts").exists()


def test_close_review_rejects_a_bad_verdict_without_writing(board: Path) -> None:
    # DEFERRED with no --author-model is legal (unestablished authorship
    # defers); an out-of-vocabulary verdict is argparse's refusal.
    bare = _sidecar(board)
    _overlay(board, str(bare))
    with pytest.raises(SystemExit):
        build_parser().parse_args(
            [
                "--config",
                str(board / "boardkit.toml"),
                "close-review",
                "S1",
                "A",
                "1",
                "--verdict",
                "PASSED",
                "--findings",
                "0",
                "--route",
                "r",
                "--reviewer-model",
                "m",
            ]
        )
    assert not (board / "receipts").exists()
