"""Tests for boardkit.receipts: schema, digests, lifecycle, and agreement.

The known-answer manifest-root test recomputes the root from the ADR's
formula independently of the module under test; everything else asserts
behavior (what parses, what refuses, what the flip touches) rather than
snapshots.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
from conftest import config_text

from boardkit.config import load_config
from boardkit.receipts import (
    MANIFEST_DOMAIN,
    DecisionReceipt,
    DigestRow,
    ReceiptError,
    ReviewReceipt,
    RulingReceipt,
    close_review_round,
    hash_tree,
    manifest_bytes,
    manifest_root,
    parse_receipt,
    publish_pending,
    receipt_log_errors,
    write_manifest,
)
from boardkit.store import MANIFEST_FILENAME, DirStore, open_store

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
commit-range: deadbeef..cafef00d
---

# S1: First card

## Log

- 2026-08-01 Minted.
"""


def _board(tmp_path: Path, artifacts: str = "") -> Path:
    (tmp_path / "boardkit.toml").write_text(config_text() + artifacts, encoding="utf-8")
    cards = tmp_path / "cards"
    cards.mkdir(exist_ok=True)
    (cards / "s1-first-card.md").write_text(CARD, encoding="utf-8")
    return tmp_path


def _packet(tmp_path: Path, dirname: str = "S1") -> Path:
    packet = tmp_path / "reviews" / dirname
    packet.mkdir(parents=True, exist_ok=True)
    (packet / "full-range.diff").write_text("diff bytes\n", encoding="utf-8")
    (packet / "REVIEW.md").write_text("# Review\n", encoding="utf-8")
    return packet


def _write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "receipt.md"
    path.write_text(text, encoding="utf-8")
    return path


def _review_text(**overrides: object) -> str:
    """A minimal valid review receipt; each malformed case breaks one thing."""
    fields: dict[str, object] = {
        "card": "S1",
        "gate": "A",
        "round": "1",
        "suffix": "null",
        "verdict": "PASS",
        "findings": "0",
        "dated": "2026-08-24",
        "route": "codex-reviewer",
        "author_models": "claude-fable-5",
        "reviewer_model": "gpt-5.6-sol",
        "commit_range": "9b1c158..decedc3",
    }
    fields.update(overrides)
    return f"""\
---
receipt: v1
kind: review
card: {fields["card"]}
gate: {fields["gate"]}
round: {fields["round"]}
suffix: {fields["suffix"]}
verdict: {fields["verdict"]}
findings: {fields["findings"]}
dated: {fields["dated"]}
route: {fields["route"]}
author_models: [{fields["author_models"]}]
reviewer_model: {fields["reviewer_model"]}
commit_range: {fields["commit_range"]}
packets:
  - name: primary
    posture: ephemeral
    published: false
    manifest: "sha256:{"ab" * 32}"
---

# Review receipt: S1 Gate A round 1

## Digests

| SHA-256 | Path |
| --- | --- |
| {"cd" * 32} | `REVIEW.md` |

## Findings

None.

## Checks the reviewer did not run

None.
"""


# --- Digests and the manifest root -------------------------------------------


def test_manifest_root_matches_the_adr_formula(tmp_path: Path) -> None:
    rows = (
        DigestRow(sha256="cd" * 32, path="REVIEW.md"),
        DigestRow(sha256="ab" * 32, path="01-deadbeef.diff"),
    )
    # The ADR: sha256("boardkit-receipt:v1\n" + the sorted digest lines),
    # computed here from first principles, not through the module.
    lines = sorted(f"{row.sha256}  {row.path}" for row in rows)
    expected = hashlib.sha256(
        (MANIFEST_DOMAIN + "\n" + "\n".join(lines) + "\n").encode()
    ).hexdigest()
    assert manifest_root(rows) == expected
    assert len(expected) == 64


def test_write_manifest_drops_the_manifests_own_input_bytes(tmp_path: Path) -> None:
    packet = _packet(tmp_path)
    rows, root = write_manifest(packet)
    on_disk = (packet / MANIFEST_FILENAME).read_bytes()
    assert on_disk == manifest_bytes(rows)
    assert hashlib.sha256(on_disk).hexdigest() == root
    # The manifest never attests itself.
    assert {row.path for row in rows} == {"REVIEW.md", "full-range.diff"}


def test_hash_tree_refuses_a_newline_in_a_path(tmp_path: Path) -> None:
    packet = _packet(tmp_path)
    (packet / "two\nlines.diff").write_text("x\n", encoding="utf-8")
    with pytest.raises(ReceiptError, match="newline"):
        hash_tree(packet)


def test_hash_tree_refuses_an_empty_directory(tmp_path: Path) -> None:
    empty = tmp_path / "empty"
    empty.mkdir()
    with pytest.raises(ReceiptError, match="no files to attest"):
        hash_tree(empty)


# --- Schema validation ---------------------------------------------------------


def test_a_valid_review_receipt_round_trips(tmp_path: Path) -> None:
    receipt = parse_receipt(_write(tmp_path, _review_text()))
    assert isinstance(receipt, ReviewReceipt)
    assert receipt.card == "S1"
    assert receipt.packets[0].manifest == "ab" * 32
    assert receipt.packets[0].published is False
    assert receipt.body.digests[0].path == "REVIEW.md"


def test_reviewer_in_author_models_is_an_error(tmp_path: Path) -> None:
    text = _review_text(reviewer_model="claude-fable-5")
    with pytest.raises(ReceiptError, match="appears in author_models"):
        parse_receipt(_write(tmp_path, text))


def test_empty_author_models_is_the_defer_case_never_a_pass(tmp_path: Path) -> None:
    with pytest.raises(ReceiptError, match="defer"):
        parse_receipt(_write(tmp_path, _review_text(author_models="")))

    receipt = parse_receipt(_write(tmp_path, _review_text(author_models="", verdict="DEFERRED")))
    assert receipt.verdict == "DEFERRED"
    assert receipt.author_models == ()


def test_out_of_kind_verdict_is_an_error(tmp_path: Path) -> None:
    with pytest.raises(ReceiptError, match="not in"):
        parse_receipt(_write(tmp_path, _review_text(verdict="RULING")))


def test_unknown_and_missing_keys_are_errors(tmp_path: Path) -> None:
    text = _review_text().replace("route: codex-reviewer\n", "")
    with pytest.raises(ReceiptError, match="missing required key"):
        parse_receipt(_write(tmp_path, text))
    text = _review_text().replace("route: codex-reviewer\n", "route: codex-reviewer\nextra: 1\n")
    with pytest.raises(ReceiptError, match="unknown key"):
        parse_receipt(_write(tmp_path, text))


def test_published_entry_requires_a_locator(tmp_path: Path) -> None:
    text = _review_text().replace("published: false", "published: true")
    with pytest.raises(ReceiptError, match="requires a locator"):
        parse_receipt(_write(tmp_path, text))


def test_empty_digest_table_is_an_error(tmp_path: Path) -> None:
    text = _review_text().replace(f"| {'cd' * 32} | `REVIEW.md` |\n", "")
    with pytest.raises(ReceiptError, match="no digest rows"):
        parse_receipt(_write(tmp_path, text))


def test_a_bad_commit_range_is_an_error(tmp_path: Path) -> None:
    with pytest.raises(ReceiptError, match="not a range"):
        parse_receipt(_write(tmp_path, _review_text(commit_range="deadbeef")))


RULING_TEXT = """\
---
receipt: v1
kind: ruling
cards: [S13, S16]
gate: A
verdict: RULING
dated: 2026-08-16
route: codex-reviewer
author_models: [claude-fable-5]
reviewer_models: [gpt-5.6-sol]
rounds:
  - round: 1
    object: "the card diffs"
    verdict: FAIL
    findings: 24
ruling: docs/board/evidence/cycle.md
gate_ticked: false
packets: []
---

# Ruling receipt

## Digests

| SHA-256 | Path |
| --- | --- |
| {digest} | `docs/board/evidence/cycle.md` |

## Findings

In the ruling document.

## Checks the reviewer did not run

The uv-backed checks.
"""


def test_a_valid_ruling_parses(tmp_path: Path) -> None:
    receipt = parse_receipt(_write(tmp_path, RULING_TEXT.format(digest="ef" * 32)))
    assert isinstance(receipt, RulingReceipt)
    assert receipt.cards == ("S13", "S16")
    assert receipt.rounds[0].verdict == "FAIL"
    assert receipt.gate_ticked is False
    assert receipt.packets == ()


def test_mixed_is_a_round_verdict_never_a_receipt_verdict(tmp_path: Path) -> None:
    text = RULING_TEXT.format(digest="ef" * 32).replace("verdict: RULING", "verdict: MIXED")
    with pytest.raises(ReceiptError, match="not in"):
        parse_receipt(_write(tmp_path, text))


def test_a_ruling_with_packets_is_an_error(tmp_path: Path) -> None:
    text = RULING_TEXT.format(digest="ef" * 32).replace(
        "packets: []",
        "packets:\n  - name: primary\n    posture: sidecar\n    published: false",
    )
    with pytest.raises(ReceiptError, match="names no packet"):
        parse_receipt(_write(tmp_path, text))


DECISION_TEXT = """\
---
receipt: v1
kind: decision
card: S1
gate: U
round: 1
verdict: ACCEPTED
dated: 2026-08-24
decider: Mike
author_models: [claude-fable-5]
packets: []
---

# Decision receipt: S1 Gate U

## Digests

| SHA-256 | Path |
| --- | --- |
| {digest} | `docs/board/receipts/S1/A-r1.md` |

## Findings

Approved on the ledger.

## Checks the reviewer did not run

None - a user gate has no reviewer.
"""


def test_a_valid_decision_parses(tmp_path: Path) -> None:
    receipt = parse_receipt(_write(tmp_path, DECISION_TEXT.format(digest="01" * 32)))
    assert isinstance(receipt, DecisionReceipt)
    assert receipt.decider == "Mike"
    assert receipt.verdict == "ACCEPTED"


def test_a_decision_admits_only_its_own_verdicts(tmp_path: Path) -> None:
    text = DECISION_TEXT.format(digest="01" * 32).replace("ACCEPTED", "PASS")
    with pytest.raises(ReceiptError, match="not in"):
        parse_receipt(_write(tmp_path, text))


def test_missing_body_sections_are_named(tmp_path: Path) -> None:
    text = _review_text().replace("## Checks the reviewer did not run\n\nNone.\n", "")
    with pytest.raises(ReceiptError, match="missing body section"):
        parse_receipt(_write(tmp_path, text))


# --- The lifecycle -------------------------------------------------------------


def _close(tmp_path: Path, **overrides: object) -> Path:
    config = load_config(tmp_path / "boardkit.toml")
    _packet(tmp_path)
    args: dict[str, object] = {
        "card_id": "S1",
        "gate": "A",
        "round": 1,
        "verdict": "FAIL",
        "findings": 2,
        "route": "codex-reviewer",
        "author_models": ["claude-fable-5"],
        "reviewer_model": "gpt-5.6-sol",
        "commit_range": "deadbeef..cafef00d",
        "findings_text": "1. One. 2. Two.",
        "checks_not_run": "The uv-backed checks.",
        "dated": "2026-08-24",
    }
    args.update(overrides)
    return close_review_round(config, open_store(config), **args)  # type: ignore[arg-type]


def test_close_writes_hash_receipt_and_log_as_one_unit(tmp_path: Path) -> None:
    _board(tmp_path)
    path = _close(tmp_path)
    # docs/board layout here is flat (cards/, receipts/ side by side).
    assert path.name == "A-r1.md"
    assert path.parent.name == "S1"
    assert path.parent.parent.name == "receipts"
    assert path.is_file()

    receipt = parse_receipt(path)
    assert isinstance(receipt, ReviewReceipt)
    entry = receipt.packets[0]
    assert entry.published is False and entry.locator is None
    assert entry.posture == "ephemeral"
    assert entry.manifest == manifest_root(receipt.body.digests)
    assert {row.path for row in receipt.body.digests} == {"REVIEW.md", "full-range.diff"}
    # The packet gained its manifest file during hashing.
    assert (tmp_path / "reviews" / "S1" / MANIFEST_FILENAME).is_file()

    card = (tmp_path / "cards" / "s1-first-card.md").read_text(encoding="utf-8")
    assert "Gate A round 1: FAIL" in card
    assert "](../receipts/S1/A-r1.md)" in card
    # The log line the writer produces passes the agreement check.
    config = load_config(tmp_path / "boardkit.toml")
    card_dict = DirStore(config).get_card("S1")
    assert receipt_log_errors(config, [card_dict]) == []


def test_close_refuses_to_overwrite_an_existing_receipt(tmp_path: Path) -> None:
    _board(tmp_path)
    _close(tmp_path)
    with pytest.raises(ReceiptError, match="append-only"):
        _close(tmp_path)


def test_deferred_round_with_unestablished_authorship_round_trips(tmp_path: Path) -> None:
    """The ADR's defer case through the writer, not parse_receipt alone:
    empty author_models must render as `[]` (a bare key parses back as None),
    land on disk, parse, and pass the agreement check."""
    _board(tmp_path)
    path = _close(
        tmp_path,
        verdict="DEFERRED",
        author_models=[],
        findings_text="The delegation returned no verdict; the round is deferred.",
    )
    receipt = parse_receipt(path)
    assert isinstance(receipt, ReviewReceipt)
    assert receipt.verdict == "DEFERRED"
    assert receipt.author_models == ()
    config = load_config(tmp_path / "boardkit.toml")
    assert receipt_log_errors(config, DirStore(config).list_cards()) == []


def test_a_failed_log_append_leaves_nothing_written(tmp_path: Path) -> None:
    _board(tmp_path)
    # No Log section: append_log raises, and the receipt comes back off disk.
    card = tmp_path / "cards" / "s1-first-card.md"
    card.write_text(CARD.replace("## Log\n\n- 2026-08-01 Minted.\n", ""), encoding="utf-8")
    with pytest.raises(Exception, match="no Log section"):
        _close(tmp_path)
    assert not (tmp_path / "receipts").exists()


def test_publish_flips_exactly_published_and_locator(tmp_path: Path) -> None:
    _board(tmp_path, '\n[artifacts]\nposture = "in-repo"\n')
    path = _close(tmp_path)
    before = path.read_text(encoding="utf-8")

    config = load_config(tmp_path / "boardkit.toml")
    results = publish_pending(config, path)
    assert len(results) == 1 and results[0].published

    after = path.read_text(encoding="utf-8")
    # The flip is the one permitted mutation: published plus locator, and
    # the digest table byte-identical across it (ADR section 4).
    removed = [line for line in before.splitlines() if line not in after.splitlines()]
    added = [line for line in after.splitlines() if line not in before.splitlines()]
    assert removed == ["    published: false"]
    assert len(added) == 2
    assert added[0] == "    published: true"
    assert added[1].startswith('    locator: "dir:docs/board/packets/S1/A-r1"')

    receipt = parse_receipt(path)
    assert isinstance(receipt, ReviewReceipt)
    assert receipt.packets[0].published
    # A second publish run has nothing to do.
    assert publish_pending(config, path) == []


def test_a_failed_publish_leaves_the_receipt_unpublished(tmp_path: Path) -> None:
    # posture sidecar with no overlay row: publish cannot run, the receipt
    # stands with published: false, and the failure says why (driver 8).
    _board(tmp_path, '\n[artifacts]\nposture = "sidecar"\nstore = "bk-sidecar"\n')
    boardkit_dir = tmp_path / ".boardkit"
    boardkit_dir.mkdir()
    (boardkit_dir / "manifest.toml").write_text(
        'default = "bk"\n\n[boards.bk]\nlocation = "dir:."\nid_prefix = "S"\n',
        encoding="utf-8",
    )
    path = _close(tmp_path)
    config = load_config(tmp_path / "boardkit.toml")
    with pytest.raises(ValueError, match="bk-sidecar"):
        publish_pending(config, path, boardkit_dir=boardkit_dir)
    receipt = parse_receipt(path)
    assert isinstance(receipt, ReviewReceipt)
    assert receipt.packets[0].published is False


# --- Card-log agreement --------------------------------------------------------


def _receipt_with_log(tmp_path: Path) -> tuple[Path, list[dict]]:
    _board(tmp_path)
    path = _close(tmp_path)
    config = load_config(tmp_path / "boardkit.toml")
    cards = DirStore(config).list_cards()
    return path, cards


def test_agreement_holds_for_a_writer_produced_pair(tmp_path: Path) -> None:
    _receipt_with_log(tmp_path)
    config = load_config(tmp_path / "boardkit.toml")
    assert receipt_log_errors(config, DirStore(config).list_cards()) == []


def test_a_receipt_no_log_line_links_is_an_error(tmp_path: Path) -> None:
    path, _cards = _receipt_with_log(tmp_path)
    card = tmp_path / "cards" / "s1-first-card.md"
    card.write_text(CARD, encoding="utf-8")  # the card without the log line
    config = load_config(tmp_path / "boardkit.toml")
    errors = receipt_log_errors(config, DirStore(config).list_cards())
    assert any("no entry" in e and path.name in e for e in errors)


def test_a_verdict_mismatch_between_log_and_receipt_is_an_error(tmp_path: Path) -> None:
    _receipt_with_log(tmp_path)
    card = tmp_path / "cards" / "s1-first-card.md"
    text = card.read_text(encoding="utf-8").replace("FAIL, 2 finding(s)", "PASS, 0 findings")
    card.write_text(text, encoding="utf-8")
    config = load_config(tmp_path / "boardkit.toml")
    errors = receipt_log_errors(config, DirStore(config).list_cards())
    assert any("verdict FAIL" in e for e in errors)


def test_a_renamed_receipt_file_disagrees_with_its_frontmatter(tmp_path: Path) -> None:
    path, _cards = _receipt_with_log(tmp_path)
    renamed = path.rename(path.parent / "A-r9.md")
    card = tmp_path / "cards" / "s1-first-card.md"
    card.write_text(
        card.read_text(encoding="utf-8").replace("A-r1.md", "A-r9.md"), encoding="utf-8"
    )
    config = load_config(tmp_path / "boardkit.toml")
    errors = receipt_log_errors(config, DirStore(config).list_cards())
    assert any("filename" in e for e in errors)
    renamed.unlink()


def test_a_multi_packet_receipt_groups_its_digest_table(tmp_path: Path) -> None:
    """The fix-round shape: one verdict over two packets, one receipt."""
    _board(tmp_path)
    _packet(tmp_path)
    _packet(tmp_path, "S1-fix")
    config = load_config(tmp_path / "boardkit.toml")
    path = close_review_round(
        config,
        open_store(config),
        card_id="S1",
        gate="A",
        round=2,
        verdict="PASS",
        findings=0,
        route="codex-reviewer",
        author_models=["claude-fable-5"],
        reviewer_model="gpt-5.6-sol",
        commit_range="deadbeef..cafef00d",
        findings_text="None.",
        checks_not_run="None.",
        packet_names=["primary", "fix"],
        dated="2026-08-24",
    )
    receipt = parse_receipt(path)
    assert isinstance(receipt, ReviewReceipt)
    assert [entry.name for entry in receipt.packets] == ["primary", "fix"]
    # Each entry's root recomputes from its own group of table rows.
    for entry in receipt.packets:
        rows = tuple(row for row in receipt.body.digests if row.packet == entry.name)
        assert manifest_root(rows) == entry.manifest


def test_a_suffixed_receipt_names_its_file_and_packet(tmp_path: Path) -> None:
    """The multi-repo shape: one packet per repo, each concluded on its own."""
    _board(tmp_path)
    packet = _packet(tmp_path)
    packet.rename(packet.parent / "S1-consumer")
    config = load_config(tmp_path / "boardkit.toml")
    path = close_review_round(
        config,
        open_store(config),
        card_id="S1",
        gate="A",
        round=1,
        suffix="consumer",
        verdict="FAIL",
        findings=1,
        route="codex-reviewer",
        author_models=["claude-fable-5"],
        reviewer_model="gpt-5.6-sol",
        commit_range="deadbeef..cafef00d",
        findings_text="1. One.",
        checks_not_run="None.",
        dated="2026-08-24",
    )
    assert path.name == "A-r1-consumer.md"
    receipt = parse_receipt(path)
    assert isinstance(receipt, ReviewReceipt)
    assert receipt.suffix == "consumer"
    assert receipt.packets[0].name == "consumer"
