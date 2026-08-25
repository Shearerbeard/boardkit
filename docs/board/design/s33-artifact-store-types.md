# S33 design record: artifact-store and receipt types

The typed-holes design record for S33. The spec is
[ADR 0001](../../adr/0001-artifact-store.md), accepted 2026-08-24 with
OQ1-OQ4 settled and both Gate U amendments applied; this record maps the
types the ADR names to the rules they enforce and names the seams the
implementation reaches through. Where the ADR fixes a shape (receipt
frontmatter, locator grammar, lifecycle order) the type below cites the
section; nothing here reopens a settled question.

Executor note on process: the typed-holes skeleton commit is a commit,
and the S33 executor role forbids git mutations, so the skeleton and its
fills land together in the executor's working tree; this record is the
design panel's input in place of a retrievable skeleton commit.

## Type relationships

```text
Config.artifacts (ArtifactsConfig)
    posture, store name, receipts_dir          <- boardkit.toml [artifacts]
         |
         v
open_artifact_store(config, boardkit_dir)      mirrors open_store
         |
         v
ArtifactStore (Protocol)                       store.py, beside CardStore
    describe() -> StoreInfo
    publish(PacketRef, source) -> Published
    fetch(Published, dest) -> Path
    ^ implemented by EphemeralStore, InRepoStore, SidecarStore
         |
         |  drivers move bytes only; they never hash packet payloads
         v
receipts.py (the core side, kit-side semantics)
    hash_tree / write_manifest / manifest_root digest the packet
    ReviewReceipt / RulingReceipt / DecisionReceipt
        parse and validate the receipt file, per-kind key sets
    ReceiptBody: digests table + findings + checks-not-run sections
    close_review_round: hash -> write receipt (published: false)
        -> CardStore.append_log, one local unit
    publish_pending: ArtifactStore.publish -> flip published + locator
        (the one permitted mutation, ADR section 4)
    receipt_log_errors: card log lines <-> receipts agreement (check)
    verify_receipt: the ADR section 7 tracked-repo-only path (CLI)

Overlay (config.py): boards + stores tables of .boardkit/local.toml
    stores: logical name -> StoreRef (scheme-prefixed, DOCKING.md req. 8)
```

`PacketRef` names a packet (card id, gate, round, optional suffix) and
never a path, so the same ref resolves under every posture. `Published`
is what a receipt records: store name, locator, and whether publication
happened; it carries no digests (driver 4). `StoreInfo` is what
`boardkit doctor` may print. Digests flow one way only: `receipts.py`
computes them, the receipt and the packet's own manifest file carry
them, and drivers read the manifest file for addressing and collision
comparison without ever hashing a payload.

## Type-to-business-rule map

| Type | Business rule | Invalid state it forbids |
| --- | --- | --- |
| `PacketRef` | A packet is a logical identity, not a path (ADR section 1) | a ref that only resolves on one posture |
| `Published` | A receipt records whether publication happened (driver 2) | a locator on a packet that was never published (`locator` is None unless `published`) |
| `StoreInfo` | Doctor output never leaks more than a printable location (driver 3) | n/a - reporting type |
| `ArtifactsConfig` | Posture is opt-in; silence means today's behavior (driver 7) | a posture outside `ephemeral/in-repo/sidecar`; a sidecar with no store name |
| `Overlay.stores` | Machine-local locations never enter the tracked config (ADR section 5) | a `dir:` row that is not absolute; a row key that is not `location` |
| `ReviewReceipt` | A review receipt concludes one reviewer's verdict on one round (ADR section 3) | a verdict outside PASS/FAIL/DEFERRED; a reviewer who is also an author; a PASS/FAIL with unestablished authorship (empty `author_models` defers) |
| `RulingReceipt` | A ruling spans cards and rounds and publishes nothing (ADR section 8) | a ruling with packet entries; `MIXED` as the receipt's own verdict |
| `DecisionReceipt` | A user-gate decision has a decider and no reviewer (ADR OQ4) | a reviewer field on a user gate |
| `PacketEntry` | The three published states stay distinct (ADR section 3) | `published: true` without a locator and manifest |
| `DigestRow` | Attestation is full 64-char SHA-256 (ADR section 3) | a truncated digest in a receipt |
| `ReceiptError` | Parse/validation failures name every problem found | n/a - error carrier |

Enforcement is parse-don't-validate: the three receipt dataclasses are
constructed only by `parse_receipt`, whose per-kind key sets and field
checks raise `ReceiptError` on the first pass, so every downstream
consumer (doctor, check, verify-receipt) holds an already-valid receipt.

## Visibility and seam table

- `store.py` gains the seam and the drivers; it imports nothing new
  beyond `hashlib`/`shutil`/`subprocess`/`tempfile` and `config` types it
  already imports. Process semantics stay kit-side (module docstring).
- `receipts.py` (new) reaches into `board.py` for `log_entries` (the
  agreement check reads logs the same way the deferred sweep does), into
  `contract.sections` for body-section parsing, and into `store.py` for
  the seam and `CardStore.append_log`. Nothing in `store.py` imports
  `receipts.py`.
- `config.py` owns the `[artifacts]` table and the overlay `stores`
  schema extension, reusing `parse_store_ref`; `KNOWN_SCHEMES` gains
  `git` so board manifests and store refs share one grammar (ADR section
  1). A `git:` manifest board location parses but has no board driver;
  resolution then fails loudly at the missing `boardkit.toml`, the same
  refusal an unresolvable `dir:` row gets today.
- `doctor.py` gains two checks; `cli.py` gains one command and one
  `check` error source. `review_packet.py` changes REVIEW.md rendering
  only (the named gap). `contract.py` and `board.py` are unchanged.
- Test-only surface: none. Every function here has a production caller.

## Decisions the ADR leaves to S33

- **Manifest file in the packet.** Section 5's collision rule reads a
  root "from the existing target's own manifest file", so publication
  carries one: `receipt-manifest.txt`, written by `hash_tree`'s caller
  core-side, whose bytes are exactly the manifest root's input
  (`"boardkit-receipt:v1\n"` + sorted digest lines). The manifest file is
  the one packet file the digest table does not attest (a table cannot
  hash its own root). Drivers compare manifests byte-for-byte, which is
  the full-root comparison with no hashing on the driver side.
- **`publish(ref, source)` keeps the ADR's signature.** The `dir:`
  locator's `@<root-prefix>` anchor comes from hashing the manifest file
  - the driver's own addressing metadata, never a packet payload, so
  driver 4's "never computes digests" holds over attestation.
- **In-repo locator.** ADR section 5 fixes locator shapes for the two
  sidecar backends only. In-repo publishes to `docs/board/packets/`
  under the board root and records `dir:<repo-relative path>`; the
  tracked repo's own history is the anchor, the same one receipts
  themselves rest on (ADR section 3, tamper-evidence paragraph).
- **REVIEW.md gap: omit the path.** Chosen over relativizing; see the
  executor report. `Repo:` becomes a sentence, and the `git -C <abs>`
  commands become `git` commands run from the repo root.
- **Receipt writers exist for `review` only** (driver 6): the lifecycle
  of section 4 governs `review`; `ruling` and `decision` are written at
  the event by hand, as the R-wave backfill is. All three kinds parse
  and validate, because doctor, check, and verify-receipt read them.
- **The `check` kind is not implemented** (settled OQ4).

## Residual risks

- **No CLI command closes a gate.** `close_review_round` and
  `publish_pending` are library functions; ADR section 4 states the
  ordering as a contract, and no command exists to drive it. Wiring a
  gate-close command is follow-up work, flagged in the report.
- **A second machine cannot publish until its overlay row exists** -
  surfaced at publish time with the file to edit, and unpublished
  receipts carry the doctor warning. Stated in ADR section 5, not
  mitigated.
- **Receipt-versus-log agreement checks the link, gate letter, verdict
  word, and date** - the fields a log line legibly carries. A log line
  that links the receipt but misstates a field it does not carry (the
  round, say) is caught only through the filename. Named, accepted.
