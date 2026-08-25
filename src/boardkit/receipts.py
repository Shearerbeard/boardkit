"""Tracked receipts: one compact, tracked record per gate outcome (ADR 0001).

A receipt is YAML frontmatter a checker reads, then prose a person reads:
`## Digests` (one row per attested file, full 64-char SHA-256), `## Findings`
(the numbered ledger with dispositions), and `## Checks the reviewer did not
run` (the UNVERIFIED class, so a sandbox limitation never reads as a pass).
Three kinds close a gate: `review` (one reviewer's verdict on one round),
`ruling` (a board owner ending a cycle across cards and rounds), and
`decision` (a user gate, a decider, no reviewer). The fourth kind the ADR
defines, `check`, is settled-OQ4 unadopted and is not implemented here.

Digests are computed here, core-side, never by a driver (driver 4): the
writer hashes the packet directory and drops `receipt-manifest.txt` into
it before `publish` runs, so every posture yields a byte-identical
receipt for the same review and a buggy driver cannot forge an
attestation. The manifest file's bytes are exactly the manifest root's
input, and it is the one packet file the digest table does not attest -
a table cannot hash its own root.

The lifecycle (ADR section 4) is hash, write (`published: false`), log -
one local unit, `close_review_round` - then publish as a separate step,
`publish_pending`, whose flip of `published` + `locator` is the one
permitted mutation of a committed receipt. A publish failure leaves the
unpublished receipt standing and fails loudly (driver 8, settled OQ2).
"""

from __future__ import annotations

import hashlib
import os
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import ClassVar

import yaml

from boardkit.board import log_entries
from boardkit.config import POSTURES, Config
from boardkit.contract import sections
from boardkit.review_packet import RANGE_RE, ReviewPacketError
from boardkit.review_packet import git as packet_git
from boardkit.store import (
    MANIFEST_FILENAME,
    CardStore,
    PacketRef,
    Published,
    open_artifact_store,
)

RECEIPT_VERSION = "v1"
MANIFEST_DOMAIN = "boardkit-receipt:v1"
KINDS = ("review", "ruling", "decision")
VERDICTS = {
    "review": {"PASS", "FAIL", "DEFERRED"},
    "ruling": {"RULING"},
    "decision": {"ACCEPTED", "REJECTED"},
}
# MIXED exists only inside a ruling's rounds list, never as a receipt's own
# verdict: round 2 of the R-wave was one PASS and five FAILs, and flattening
# that to either value would misreport it.
ROUND_VERDICTS = {"PASS", "FAIL", "DEFERRED", "MIXED"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
DATED_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

RULINGS_DIRNAME = "_rulings"
DIGESTS_HEADING = "Digests"
FINDINGS_HEADING = "Findings"
CHECKS_HEADING = "Checks the reviewer did not run"
# A multi-packet table groups rows under a `Packet: <name>` line; a
# single-packet receipt renders one flat table.
GROUP_PREFIX = "Packet: "

REVIEW_KEYS = {
    "receipt",
    "kind",
    "card",
    "gate",
    "round",
    "suffix",
    "verdict",
    "findings",
    "dated",
    "route",
    "author_models",
    "reviewer_model",
    "commit_range",
    "packets",
}
RULING_KEYS = {
    "receipt",
    "kind",
    "cards",
    "gate",
    "verdict",
    "dated",
    "route",
    "author_models",
    "reviewer_models",
    "rounds",
    "ruling",
    "gate_ticked",
    "packets",
}
DECISION_KEYS = {
    "receipt",
    "kind",
    "card",
    "gate",
    "round",
    "verdict",
    "dated",
    "decider",
    "author_models",
    "packets",
}

# The verdict word as a log line legibly carries it (board.py's PASSED_RE is
# the precedent: `Gate A passed`, `Gate A: PASS`).
VERDICT_WORD = {
    "PASS": r"pass(?:ed)?",
    "FAIL": r"fail(?:ed)?",
    "DEFERRED": r"defer(?:red)?",
    "ACCEPTED": r"accept(?:ed)?",
    "REJECTED": r"reject(?:ed)?",
}


class ReceiptError(Exception):
    """Raised with the full list of receipt parse/validation errors found."""

    def __init__(self, errors: list[str]) -> None:
        super().__init__("\n".join(errors))
        self.errors = errors


@dataclass(frozen=True)
class DigestRow:
    """One attested file: full SHA-256, then the path.

    `packet` is the group a multi-packet receipt's table row belongs to;
    None in a single-packet receipt's flat table. Paths are packet-relative
    for a review, repo-relative for a ruling or decision.
    """

    sha256: str
    path: str
    packet: str | None = None


@dataclass(frozen=True)
class PacketEntry:
    """One packets entry: the three published states stay distinct.

    A packet fetchable (`published`, with locator and manifest), a packet
    archived but not pushed (`published` False, no locator), and no packet
    at all (no entry) are three different states a reader must tell apart
    without reasoning about posture (driver 2).
    """

    name: str
    posture: str
    published: bool
    locator: str | None
    manifest: str | None


@dataclass(frozen=True)
class RoundSummary:
    """One round of a cycle a ruling terminates."""

    round: int
    object: str
    verdict: str
    findings: int


@dataclass(frozen=True)
class ReceiptBody:
    """The three prose sections every kind carries."""

    digests: tuple[DigestRow, ...]
    findings: str
    checks_not_run: str


@dataclass(frozen=True)
class ReviewReceipt:
    kind: ClassVar[str] = "review"

    card: str
    gate: str
    round: int
    suffix: str | None
    verdict: str
    findings: int
    dated: str
    route: str
    author_models: tuple[str, ...]
    reviewer_model: str
    commit_range: str
    packets: tuple[PacketEntry, ...]
    body: ReceiptBody


@dataclass(frozen=True)
class RulingReceipt:
    kind: ClassVar[str] = "ruling"

    cards: tuple[str, ...]
    gate: str
    verdict: str
    dated: str
    route: str
    author_models: tuple[str, ...]
    reviewer_models: tuple[str, ...]
    rounds: tuple[RoundSummary, ...]
    ruling: str
    gate_ticked: bool
    packets: tuple[PacketEntry, ...]
    body: ReceiptBody


@dataclass(frozen=True)
class DecisionReceipt:
    kind: ClassVar[str] = "decision"

    card: str
    gate: str
    round: int
    verdict: str
    dated: str
    decider: str
    author_models: tuple[str, ...]
    packets: tuple[PacketEntry, ...]
    body: ReceiptBody


Receipt = ReviewReceipt | RulingReceipt | DecisionReceipt


# --- Digests and the manifest root ------------------------------------------


def hash_tree(root: Path) -> tuple[DigestRow, ...]:
    """Every file in the packet directory as a DigestRow, manifest excluded.

    Packet-relative paths containing a newline are refused rather than
    encoded (ADR section 3): the fail-loud choice, taken everywhere else
    in this repo too.
    """
    if not root.is_dir():
        raise ReceiptError([f"{root}: no packet directory to hash"])
    rows = []
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = path.relative_to(root).as_posix()
        if rel == MANIFEST_FILENAME:
            continue
        if "\n" in rel:
            raise ReceiptError(
                [
                    f"{root}: packet-relative path {rel!r} contains a newline, which "
                    "the digest-line format cannot represent"
                ]
            )
        rows.append(DigestRow(sha256=hashlib.sha256(path.read_bytes()).hexdigest(), path=rel))
    if not rows:
        raise ReceiptError([f"{root}: no files to attest"])
    return tuple(rows)


def manifest_bytes(rows: tuple[DigestRow, ...]) -> bytes:
    """The bytes the manifest root hashes, and the manifest file's content.

    `<64 hex>  <path>` lines, sorted, newline-terminated, under the
    versioned domain separator. Fixed-width digests plus refused newlines
    make the concatenation unambiguous, which is the property
    `contract_digest`'s length-prefixing buys (contract.py), here by
    construction rather than by prefix.
    """
    lines = sorted(f"{row.sha256}  {row.path}" for row in rows)
    return (MANIFEST_DOMAIN + "\n" + "\n".join(lines) + "\n").encode()


def manifest_root(rows: tuple[DigestRow, ...]) -> str:
    """sha256 over the digest table alone: a transcription check, nothing stronger."""
    return hashlib.sha256(manifest_bytes(rows)).hexdigest()


def write_manifest(packet_dir: Path) -> tuple[tuple[DigestRow, ...], str]:
    """Hash the packet and drop its manifest file in. The receipt writer's step 1."""
    rows = hash_tree(packet_dir)
    (packet_dir / MANIFEST_FILENAME).write_bytes(manifest_bytes(rows))
    return rows, manifest_root(rows)


# --- Rendering ---------------------------------------------------------------


def _yaml_quoted(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _packet_lines(entry: PacketEntry) -> list[str]:
    lines = [
        f"  - name: {entry.name}",
        f"    posture: {entry.posture}",
        f"    published: {'true' if entry.published else 'false'}",
    ]
    if entry.published:
        lines.append(f"    locator: {_yaml_quoted(entry.locator or '')}")
    lines.append(f'    manifest: "sha256:{entry.manifest}"')
    return lines


def receipt_filename(gate: str, round: int, suffix: str | None) -> str:
    ref = PacketRef(card_id="", gate=gate, round=round, suffix=suffix)
    return f"{ref.slug}.md"


def receipt_path(
    receipts_dir: Path, card_id: str, gate: str, round: int, suffix: str | None
) -> Path:
    return receipts_dir / card_id / receipt_filename(gate, round, suffix)


def render_review(receipt: ReviewReceipt) -> str:
    """A `review` receipt as tracked markdown. The only kind with a writer:
    rulings and decisions are written at the event they record (driver 6)."""
    frontmatter = [
        "---",
        f"receipt: {RECEIPT_VERSION}",
        "kind: review",
        f"card: {receipt.card}",
        f"gate: {receipt.gate}",
        f"round: {receipt.round}",
        f"suffix: {receipt.suffix if receipt.suffix else 'null'}",
        f"verdict: {receipt.verdict}",
        f"findings: {receipt.findings}",
        f"dated: {receipt.dated}",
        f"route: {receipt.route}",
        "author_models:",
        *(f"  - {model}" for model in receipt.author_models),
        f"reviewer_model: {receipt.reviewer_model}",
        f"commit_range: {receipt.commit_range}",
    ]
    if receipt.packets:
        frontmatter.append("packets:")
        for entry in receipt.packets:
            frontmatter.extend(_packet_lines(entry))
    else:
        frontmatter.append("packets: []")
    frontmatter.append("---")

    digest_lines = ["## Digests", ""]
    if len(receipt.packets) > 1:
        for entry in receipt.packets:
            rows = [row for row in receipt.body.digests if row.packet == entry.name]
            digest_lines += [f"{GROUP_PREFIX}{entry.name}", "", *_table_lines(rows), ""]
    else:
        digest_lines += _table_lines(list(receipt.body.digests))
        digest_lines.append("")

    return "\n".join(
        [
            *frontmatter,
            "",
            f"# Review receipt: {receipt.card} Gate {receipt.gate} round {receipt.round}",
            "",
            *digest_lines,
            f"## {FINDINGS_HEADING}",
            "",
            receipt.body.findings,
            "",
            f"## {CHECKS_HEADING}",
            "",
            receipt.body.checks_not_run,
            "",
        ]
    )


def _table_lines(rows: list[DigestRow]) -> list[str]:
    return [
        "| SHA-256 | Path |",
        "| --- | --- |",
        *(f"| {row.sha256} | `{row.path}` |" for row in rows),
    ]


# --- Parsing and validation --------------------------------------------------


def _string_list(meta: dict, key: str, errors: list[str]) -> tuple[str, ...]:
    value = meta.get(key)
    if not isinstance(value, list) or not all(isinstance(m, str) and m for m in value):
        errors.append(f"'{key}' must be a list of non-empty strings")
        return ()
    return tuple(value)


def _dated(meta: dict, errors: list[str]) -> str:
    value = meta.get("dated")
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, str) and DATED_RE.match(value):
        return value
    errors.append(f"'dated' must be an ISO date, got {value!r}")
    return ""


def _packets(meta: dict, errors: list[str], *, require_manifest: bool) -> tuple[PacketEntry, ...]:
    raw = meta.get("packets")
    if not isinstance(raw, list):
        errors.append("'packets' must be a list (possibly empty)")
        return ()
    entries = []
    for index, item in enumerate(raw):
        context = f"packets entry {index + 1}"
        if not isinstance(item, dict):
            errors.append(f"{context}: must be a table")
            continue
        unknown = item.keys() - {"name", "posture", "published", "locator", "manifest"}
        if unknown:
            errors.append(f"{context}: unknown key(s): {sorted(unknown)}")
        name = item.get("name")
        if not isinstance(name, str) or not name:
            errors.append(f"{context}: 'name' must be a non-empty string")
            name = ""
        posture = item.get("posture")
        if posture not in POSTURES:
            errors.append(f"{context}: posture '{posture}' not in {sorted(POSTURES)}")
            posture = ""
        published = item.get("published")
        if not isinstance(published, bool):
            errors.append(f"{context}: 'published' must be true or false")
            published = False
        locator = item.get("locator")
        if locator is not None and not isinstance(locator, str):
            errors.append(f"{context}: 'locator' must be a string")
            locator = None
        manifest = item.get("manifest")
        if manifest is not None:
            if isinstance(manifest, str) and manifest.startswith("sha256:"):
                manifest = manifest.removeprefix("sha256:")
            if not isinstance(manifest, str) or not SHA256_RE.match(manifest):
                errors.append(f"{context}: 'manifest' must be \"sha256:<64 hex>\"")
                manifest = None
        if published and not locator:
            errors.append(f"{context}: published: true requires a locator")
        if not published and locator:
            errors.append(f"{context}: an unpublished entry carries no locator")
        if require_manifest and manifest is None:
            errors.append(f"{context}: a review packet entry requires a manifest root")
        entries.append(
            PacketEntry(
                name=name,
                posture=str(posture),
                published=published,
                locator=locator,
                manifest=manifest,
            )
        )
    return tuple(entries)


def _parse_digest_table(body: str, errors: list[str]) -> tuple[DigestRow, ...]:
    rows: list[DigestRow] = []
    group: str | None = None
    saw_group = False
    for line in body.splitlines():
        if line.startswith(GROUP_PREFIX):
            group = line[len(GROUP_PREFIX) :].strip()
            saw_group = True
            continue
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 2:
            continue
        digest, path = cells
        if not SHA256_RE.match(digest):
            # The header and separator rows are expected; anything else that
            # is not a digest row is a malformed table.
            if digest not in ("SHA-256", "---"):
                errors.append(f"malformed digest table row: {line.strip()}")
            continue
        rows.append(DigestRow(sha256=digest, path=path.strip("`"), packet=group))
    if not rows:
        errors.append(f"## {DIGESTS_HEADING}: no digest rows; no adopted kind attests nothing")
    if saw_group and any(row.packet is None for row in rows):
        errors.append(f"## {DIGESTS_HEADING}: a grouped table groups every row")
    return tuple(rows)


def _parse_body(text: str, errors: list[str]) -> ReceiptBody:
    found = sections(text)
    for heading in (DIGESTS_HEADING, FINDINGS_HEADING, CHECKS_HEADING):
        if heading not in found:
            errors.append(f"missing body section '## {heading}'")
    digests = _parse_digest_table(found.get(DIGESTS_HEADING, ""), errors)
    return ReceiptBody(
        digests=digests,
        findings=found.get(FINDINGS_HEADING, "").strip("\n"),
        checks_not_run=found.get(CHECKS_HEADING, "").strip("\n"),
    )


def _frontmatter(path: Path, text: str, errors: list[str]) -> dict:
    if not text.startswith("---\n"):
        errors.append("missing frontmatter")
        return {}
    end = text.find("\n---\n", 4)
    if end < 0:
        errors.append("unterminated frontmatter")
        return {}
    try:
        meta = yaml.safe_load(text[4:end])
    except yaml.YAMLError as exc:
        errors.append(f"bad YAML ({exc})")
        return {}
    if not isinstance(meta, dict):
        errors.append("frontmatter is not a mapping")
        return {}
    return meta


def parse_receipt(path: Path) -> Receipt:
    """Parse and validate a receipt file; raises ReceiptError listing every problem.

    Parse-don't-validate: a returned Receipt has already passed its kind's
    key set, verdict vocabulary, reviewer-distinctness, and digest-table
    checks, so consumers (doctor, check, verify-receipt) hold only valid
    receipts.
    """
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    meta = _frontmatter(path, text, errors)
    if errors:
        raise ReceiptError([f"{path.name}: {e}" for e in errors])
    if meta.get("receipt") != RECEIPT_VERSION:
        errors.append(f"'receipt' must be '{RECEIPT_VERSION}', got {meta.get('receipt')!r}")
    kind = meta.get("kind")
    if kind not in KINDS:
        errors.append(f"'kind' must be one of {list(KINDS)}, got {kind!r}")
        raise ReceiptError([f"{path.name}: {e}" for e in errors])
    allowed = {"review": REVIEW_KEYS, "ruling": RULING_KEYS, "decision": DECISION_KEYS}[kind]
    unknown = meta.keys() - allowed
    missing = allowed - meta.keys()
    if unknown:
        errors.append(f"unknown key(s): {sorted(unknown)}")
    if missing:
        errors.append(f"missing required key(s): {sorted(missing)}")
    verdict = meta.get("verdict")
    if verdict not in VERDICTS[kind]:
        errors.append(
            f"verdict '{verdict}' not in {sorted(VERDICTS[kind])} for kind '{kind}'; "
            "an absent or out-of-kind verdict is an error, not a reading"
        )
    body = _parse_body(text, errors)
    if errors:
        raise ReceiptError([f"{path.name}: {e}" for e in errors])

    if kind == "review":
        receipt = _build_review(meta, body, errors)
    elif kind == "ruling":
        receipt = _build_ruling(meta, body, errors)
    else:
        receipt = _build_decision(meta, body, errors)
    if errors:
        raise ReceiptError([f"{path.name}: {e}" for e in errors])
    return receipt


def _common_str(meta: dict, key: str, errors: list[str]) -> str:
    value = meta.get(key)
    if not isinstance(value, str) or not value:
        errors.append(f"'{key}' must be a non-empty string")
        return ""
    return value


def _build_review(meta: dict, body: ReceiptBody, errors: list[str]) -> ReviewReceipt:
    round_no = meta.get("round")
    if not isinstance(round_no, int) or isinstance(round_no, bool) or round_no < 1:
        errors.append(f"'round' must be a positive integer, got {round_no!r}")
        round_no = 0
    suffix = meta.get("suffix")
    if suffix is not None and (not isinstance(suffix, str) or not suffix):
        errors.append("'suffix' must be null or a non-empty string")
        suffix = None
    findings = meta.get("findings")
    if not isinstance(findings, int) or isinstance(findings, bool) or findings < 0:
        errors.append(f"'findings' must be a non-negative integer, got {findings!r}")
        findings = 0
    commit_range = _common_str(meta, "commit_range", errors)
    if commit_range and not RANGE_RE.match(commit_range):
        errors.append(f"commit_range '{commit_range}' is not a range (expected A..B)")
    author_models = _string_list(meta, "author_models", errors)
    reviewer_model = _common_str(meta, "reviewer_model", errors)
    # The reviewer-must-differ invariant is set membership (PROCESS.md's
    # multi-commit rule); an empty author_models is the
    # unestablished-authorship case that defers, never a vacuous pass.
    if reviewer_model and reviewer_model in author_models:
        errors.append(f"reviewer_model '{reviewer_model}' appears in author_models")
    if not author_models and meta.get("verdict") != "DEFERRED":
        errors.append("empty author_models is the defer case; the verdict must be DEFERRED")
    packets = _packets(meta, errors, require_manifest=True)
    _check_digest_groups(body, packets, errors)
    return ReviewReceipt(
        card=_common_str(meta, "card", errors),
        gate=_common_str(meta, "gate", errors),
        round=round_no,
        suffix=suffix,
        verdict=str(meta.get("verdict")),
        findings=findings,
        dated=_dated(meta, errors),
        route=_common_str(meta, "route", errors),
        author_models=author_models,
        reviewer_model=reviewer_model,
        commit_range=commit_range,
        packets=packets,
        body=body,
    )


def _build_ruling(meta: dict, body: ReceiptBody, errors: list[str]) -> RulingReceipt:
    cards = _string_list(meta, "cards", errors)
    if not cards:
        errors.append("'cards' must name at least one card")
    rounds_raw = meta.get("rounds")
    rounds: list[RoundSummary] = []
    if not isinstance(rounds_raw, list) or not rounds_raw:
        errors.append("'rounds' must be a non-empty list of round summaries")
    else:
        for index, item in enumerate(rounds_raw):
            context = f"rounds entry {index + 1}"
            if not isinstance(item, dict):
                errors.append(f"{context}: must be a table")
                continue
            unknown = item.keys() - {"round", "object", "verdict", "findings"}
            if unknown:
                errors.append(f"{context}: unknown key(s): {sorted(unknown)}")
            round_no = item.get("round")
            if not isinstance(round_no, int) or isinstance(round_no, bool) or round_no < 1:
                errors.append(f"{context}: 'round' must be a positive integer")
                round_no = 0
            verdict = item.get("verdict")
            if verdict not in ROUND_VERDICTS:
                errors.append(f"{context}: verdict '{verdict}' not in {sorted(ROUND_VERDICTS)}")
            findings = item.get("findings")
            if not isinstance(findings, int) or isinstance(findings, bool) or findings < 0:
                errors.append(f"{context}: 'findings' must be a non-negative integer")
                findings = 0
            obj = item.get("object")
            if not isinstance(obj, str) or not obj:
                errors.append(f"{context}: 'object' must be a non-empty string")
                obj = ""
            rounds.append(
                RoundSummary(round=round_no, object=obj, verdict=str(verdict), findings=findings)
            )
    gate_ticked = meta.get("gate_ticked")
    if not isinstance(gate_ticked, bool):
        errors.append("'gate_ticked' must be true or false")
        gate_ticked = False
    author_models = _string_list(meta, "author_models", errors)
    reviewer_models = _string_list(meta, "reviewer_models", errors)
    overlap = set(reviewer_models) & set(author_models)
    if overlap:
        errors.append(f"reviewer_models appear in author_models: {sorted(overlap)}")
    packets = _packets(meta, errors, require_manifest=False)
    if packets:
        errors.append("a ruling names no packet to publish; its packets list is empty")
    return RulingReceipt(
        cards=cards,
        gate=_common_str(meta, "gate", errors),
        verdict=str(meta.get("verdict")),
        dated=_dated(meta, errors),
        route=_common_str(meta, "route", errors),
        author_models=author_models,
        reviewer_models=reviewer_models,
        rounds=tuple(rounds),
        ruling=_common_str(meta, "ruling", errors),
        gate_ticked=gate_ticked,
        packets=packets,
        body=body,
    )


def _build_decision(meta: dict, body: ReceiptBody, errors: list[str]) -> DecisionReceipt:
    round_no = meta.get("round")
    if not isinstance(round_no, int) or isinstance(round_no, bool) or round_no < 1:
        errors.append(f"'round' must be a positive integer, got {round_no!r}")
        round_no = 0
    packets = _packets(meta, errors, require_manifest=False)
    if packets:
        errors.append("a decision names no packet to publish; its packets list is empty")
    return DecisionReceipt(
        card=_common_str(meta, "card", errors),
        gate=_common_str(meta, "gate", errors),
        round=round_no,
        verdict=str(meta.get("verdict")),
        dated=_dated(meta, errors),
        decider=_common_str(meta, "decider", errors),
        author_models=_string_list(meta, "author_models", errors),
        packets=packets,
        body=body,
    )


def _check_digest_groups(
    body: ReceiptBody, packets: tuple[PacketEntry, ...], errors: list[str]
) -> None:
    """Group lines must exist exactly when more than one packet stands behind the verdict."""
    grouped = {row.packet for row in body.digests if row.packet is not None}
    if len(packets) > 1:
        names = {entry.name for entry in packets}
        if grouped != names:
            errors.append(
                f"## {DIGESTS_HEADING}: groups {sorted(grouped)} do not match the "
                f"packets {sorted(names)}"
            )
    elif grouped:
        errors.append(f"## {DIGESTS_HEADING}: a single-packet receipt renders a flat table")


# --- The lifecycle (ADR section 4) -------------------------------------------


def packet_dir(config: Config, card_id: str, name: str) -> Path:
    """The local packet directory behind one packets entry."""
    dirname = card_id if name == "primary" else f"{card_id}-{name}"
    return config.review.output_dir / dirname


def _log_line(receipt: ReviewReceipt, receipt_file: Path, cards_dir: Path) -> str:
    """The card-log entry for the close. Links the receipt, so a card's log
    line and its receipt are checkably in agreement (the check below)."""
    rel = Path(os.path.relpath(receipt_file, cards_dir)).as_posix()
    ref = PacketRef(receipt.card, receipt.gate, receipt.round, receipt.suffix)
    return (
        f"{receipt.dated} Gate {receipt.gate} round {receipt.round}: {receipt.verdict}, "
        f"{receipt.findings} finding(s). Reviewer {receipt.reviewer_model} via "
        f"{receipt.route}; authors {', '.join(receipt.author_models) or 'unestablished'}. "
        f"Receipt: [{ref.slug}]({rel})."
    )


def close_review_round(
    config: Config,
    card_store: CardStore,
    *,
    card_id: str,
    gate: str,
    round: int,
    suffix: str | None = None,
    verdict: str,
    findings: int,
    route: str,
    author_models: list[str],
    reviewer_model: str,
    commit_range: str,
    findings_text: str,
    checks_not_run: str,
    packet_names: list[str] | None = None,
    dated: str | None = None,
) -> Path:
    """Hash, write (`published: false`), log: one local unit, no network.

    Steps 1-3 of ADR section 4's ordering. Publication is deliberately not
    here: it is the one step that can fail for reasons nothing local
    controls, so it runs separately (`publish_pending`) and its failure
    leaves the valid unpublished receipt standing. If the log append fails
    after the receipt is written, the receipt comes back off disk - a
    partial close has no excuse when every step is local.
    """
    names = packet_names or [suffix or "primary"]
    entries = []
    rows: list[DigestRow] = []
    for name in names:
        packet_rows, root = write_manifest(packet_dir(config, card_id, name))
        entries.append(
            PacketEntry(
                name=name,
                posture=config.artifacts.posture,
                published=False,
                locator=None,
                manifest=root,
            )
        )
        rows.extend(
            DigestRow(row.sha256, row.path, packet=name if len(names) > 1 else None)
            for row in packet_rows
        )
    receipt = ReviewReceipt(
        card=card_id,
        gate=gate,
        round=round,
        suffix=suffix,
        verdict=verdict,
        findings=findings,
        dated=dated or date.today().isoformat(),
        route=route,
        author_models=tuple(author_models),
        reviewer_model=reviewer_model,
        commit_range=commit_range,
        packets=tuple(entries),
        body=ReceiptBody(
            digests=tuple(rows), findings=findings_text, checks_not_run=checks_not_run
        ),
    )
    path = receipt_path(config.artifacts.receipts_dir, card_id, gate, round, suffix)
    if path.exists():
        raise ReceiptError(
            [
                f"{path}: a receipt already sits there; receipts are append-only, and "
                "a correction is a new receipt for a new round"
            ]
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_review(receipt), encoding="utf-8")
    try:
        # The writer's output must be a valid receipt; parse it back before
        # the log links it, so a bad argument never lands on the board.
        parse_receipt(path)
        card_store.append_log(card_id, _log_line(receipt, path, config.board.cards_dir))
    except Exception:
        path.unlink()
        # Prune the directories the write created; nothing-written means
        # nothing written, empty scaffolding included.
        parent = path.parent
        while parent != config.artifacts.receipts_dir.parent and not any(parent.iterdir()):
            parent.rmdir()
            if parent == config.artifacts.receipts_dir:
                break
            parent = parent.parent
        raise
    return path


def pending_review_receipts(config: Config) -> list[Path]:
    """Every review receipt with an unpublished packet entry, for the drain.

    Ephemeral entries are their own final state, not a queue: an ephemeral
    packet is never published, so only in-repo and sidecar entries count as
    pending. A receipt that does not parse raises rather than being skipped
    - a drain that walked past a corrupt receipt would hide it.
    """
    receipts_dir = config.artifacts.receipts_dir
    if not receipts_dir.is_dir():
        return []
    pending = []
    for path in sorted(receipts_dir.rglob("*.md")):
        if RULINGS_DIRNAME in path.relative_to(receipts_dir).parts:
            continue
        receipt = parse_receipt(path)
        if isinstance(receipt, ReviewReceipt) and any(
            not entry.published and entry.posture != "ephemeral"
            for entry in receipt.packets
        ):
            pending.append(path)
    return pending


def publish_pending(
    config: Config, path: Path, boardkit_dir: Path | None = None
) -> list[Published]:
    """Step 4: publish every unpublished packet entry and flip its two fields.

    The flip is the one permitted mutation of a written receipt (ADR
    section 4): `published` and `locator` change, nothing else, and the
    digest table stays byte-identical across it. A publish failure raises
    and leaves the receipt unpublished (driver 8) - never a silent
    downgrade, never a recorded publication that did not happen.
    """
    receipt = parse_receipt(path)
    if not isinstance(receipt, ReviewReceipt):
        raise ReceiptError([f"{path.name}: only a review receipt has packets to publish"])
    pending = [entry for entry in receipt.packets if not entry.published]
    if not pending:
        return []
    store = open_artifact_store(config, boardkit_dir)
    text = path.read_text(encoding="utf-8")
    results = []
    for entry in pending:
        suffix = None if entry.name == "primary" else entry.name
        ref = PacketRef(receipt.card, receipt.gate, receipt.round, suffix)
        published = store.publish(ref, packet_dir(config, receipt.card, entry.name))
        if published.published:
            text = _flip_entry(text, entry, published)
        results.append(published)
    path.write_text(text, encoding="utf-8")
    return results


def _flip_entry(text: str, entry: PacketEntry, published: Published) -> str:
    """Rewrite exactly the `published` line of one entry, adding its locator."""
    anchor = f'    manifest: "sha256:{entry.manifest}"'
    block = text.rfind("  - name:", 0, text.index(anchor))
    line = "    published: false"
    at = text.index(line, block)
    replacement = f"    published: true\n    locator: {_yaml_quoted(published.locator or '')}"
    return text[:at] + replacement + text[at + len(line) :]


# --- Card-log agreement (boardkit check) -------------------------------------


def _agreement_errors(
    config: Config, cards: dict[str, dict], receipt: Receipt, path: Path
) -> list[str]:
    """One receipt against its card's log: link, gate, verdict, and date."""
    if not isinstance(receipt, ReviewReceipt | DecisionReceipt):
        return []  # a ruling spans cards; no single log owns it
    errors = []
    name = path.name
    # The filename encodes card, gate, round, and suffix; it must agree
    # with the frontmatter it wraps.
    expected = receipt_filename(receipt.gate, receipt.round, getattr(receipt, "suffix", None))
    if path.parent.name != receipt.card or name != expected:
        errors.append(
            f"{path.relative_to(config.artifacts.receipts_dir)}: filename does not "
            f"match its frontmatter (want {receipt.card}/{expected})"
        )
    card = cards.get(receipt.card)
    if card is None:
        errors.append(f"{name}: card '{receipt.card}' is not on this board")
        return errors
    rel = Path(os.path.relpath(path, config.board.cards_dir)).as_posix()
    link_entry = next((e for e in log_entries(card["_body"]) if rel in e), None)
    if link_entry is None:
        errors.append(
            f"{name}: no entry in {card['_file']}'s log links {rel}; the log line "
            "and its receipt must agree"
        )
        return errors
    gate_re = rf"Gate\s+{re.escape(receipt.gate)}(?![A-Za-z])"
    if not re.search(gate_re, link_entry):
        errors.append(f"{name}: the log entry naming it does not mention Gate {receipt.gate}")
    word = VERDICT_WORD.get(receipt.verdict, re.escape(receipt.verdict.lower()))
    if not re.search(rf"\b{word}\b", link_entry, re.IGNORECASE):
        errors.append(f"{name}: the log entry naming it does not carry verdict {receipt.verdict}")
    if receipt.dated not in link_entry:
        errors.append(f"{name}: the log entry naming it does not carry date {receipt.dated}")
    return errors


def receipt_log_errors(config: Config, cards: list[dict]) -> list[str]:
    """Every per-card receipt checked against its card's gate log lines.

    `boardkit check` folds these into its errors: the verdict living in two
    tracked places is a drift surface (ADR, Consequences), and this is the
    validator that closes it. Rulings under `_rulings/` span cards and are
    not checked against any one log.
    """
    receipts_dir = config.artifacts.receipts_dir
    if not receipts_dir.is_dir():
        return []
    by_id = {card["id"]: card for card in cards}
    errors: list[str] = []
    for path in sorted(receipts_dir.rglob("*.md")):
        if RULINGS_DIRNAME in path.relative_to(receipts_dir).parts:
            continue
        try:
            receipt = parse_receipt(path)
        except ReceiptError as exc:
            errors.extend(exc.errors)
            continue
        errors.extend(_agreement_errors(config, by_id, receipt, path))
    return errors


# --- The outside-vetter path (ADR section 7) ---------------------------------


@dataclass(frozen=True)
class Verification:
    """One named check's outcome, for `boardkit verify-receipt` to print."""

    name: str
    ok: bool
    detail: str


def verify_receipt(config: Config, cards: list[dict], path: Path) -> list[Verification]:
    """The tracked-repo-only validation path of ADR section 7.

    Consistency checks on what the board asserts: the digest table arrived
    whole, the log and the receipt agree, a named reviewer distinct from
    every author reached this verdict over these commits. They do not
    establish that the reviewer existed or saw the bytes; nothing here is
    signed, and the command says so rather than letting "digest" imply it.
    """
    try:
        receipt = parse_receipt(path)
    except ReceiptError as exc:
        return [Verification("schema", False, "; ".join(exc.errors))]
    checks = [Verification("schema", True, f"kind: {receipt.kind}, verdict: {receipt.verdict}")]

    if isinstance(receipt, ReviewReceipt):
        for entry in receipt.packets:
            rows = tuple(row for row in receipt.body.digests if row.packet in (None, entry.name))
            root = manifest_root(rows)
            checks.append(
                Verification(
                    f"manifest-root[{entry.name}]",
                    root == entry.manifest,
                    "recomputed root matches the receipt"
                    if root == entry.manifest
                    else f"recomputed {root}, receipt records {entry.manifest}",
                )
            )
        checks.append(_reviewer_distinct_check(receipt.reviewer_model, receipt.author_models))
        checks.append(_commit_range_check(config, receipt.commit_range))
    else:
        # A ruling or decision attests tracked documents: recompute each
        # row's digest against the file in this clone.
        for row in receipt.body.digests:
            target = config.root / row.path
            if not target.is_file():
                checks.append(Verification(f"digest[{row.path}]", False, "file not in this clone"))
                continue
            actual = hashlib.sha256(target.read_bytes()).hexdigest()
            checks.append(
                Verification(
                    f"digest[{row.path}]",
                    actual == row.sha256,
                    "matches the tracked file"
                    if actual == row.sha256
                    else f"file digests to {actual}",
                )
            )
        models = receipt.reviewer_models if isinstance(receipt, RulingReceipt) else ()
        overlap = set(models) & set(receipt.author_models)
        checks.append(
            Verification(
                "reviewer-distinct",
                not overlap,
                "reviewer appears in no author set"
                if not overlap
                else f"overlap: {sorted(overlap)}",
            )
        )

    by_id = {card["id"]: card for card in cards}
    agreement = _agreement_errors(config, by_id, receipt, path)
    checks.append(
        Verification(
            "card-log-agreement",
            not agreement,
            "card log and receipt agree on gate, round, verdict, and date"
            if not agreement
            else "; ".join(agreement),
        )
    )
    return checks


def _reviewer_distinct_check(reviewer: str, authors: tuple[str, ...]) -> Verification:
    ok = bool(authors) and reviewer not in authors
    if not authors:
        return Verification(
            "reviewer-distinct",
            False,
            "author_models is empty: unestablished authorship defers, it never passes",
        )
    return Verification(
        "reviewer-distinct",
        ok,
        f"{reviewer} is none of {', '.join(authors)}"
        if ok
        else f"{reviewer} appears in author_models",
    )


def _commit_range_check(config: Config, commit_range: str) -> Verification:
    left, _, right = commit_range.partition("..")
    for side in (left, right):
        try:
            packet_git(config.review.repo, "rev-parse", "--verify", f"{side}^{{commit}}")
        except ReviewPacketError as exc:
            return Verification(
                "commit-range", False, f"'{side}' does not resolve in this clone: {exc}"
            )
    return Verification("commit-range", True, f"{commit_range} resolves in this clone")
