# ADR 0001: An artifact store, tracked receipts, and per-board evidence posture

<!-- boardkit-contract: v2 -->

- **Status**: proposed. Accepted at S32's Gate U, or amended there.
- **Date**: 2026-08-23
- **Deciders**: Mike at Gate U; the board owner session that pulled S32.
- **Card**: [S32](../board/cards/s32-artifact-store-adr.md). Implemented by
  [S33](../board/cards/s33-receipts-and-sidecar.md); cited by
  [S34](../board/cards/s34-wave-gate-design.md).
- **Ruled inputs**: wave-2 decision 2 and Phase 4
  ([plan](../plans/2026-08-19-wave-2-plan.md)), plus the R-wave backfill
  ruling Mike made at the 2026-08-22 Gate U.
- **Supersedes**: nothing. **Superseded by**: nothing.
- **Author model**: `claude-opus-5[1m]`, board-owner harness Claude Code.
  Named because a receipt names its author, and this document is the first
  artifact the rule applies to.
- **Code anchors verified at**: `57b6390`. Every anchor in the premise table
  was re-verified against this commit at the Gate A round-1 fix. Re-verify
  and bump this stamp on any revision, per the Gate D duty in `PROCESS.md`.

## Context and problem statement

Every gate decision this board has taken rests on material that exists only
on one laptop. `boardkit review-packet` writes `NN-<sha>.diff`,
`full-range.diff`, and `REVIEW.md` into `docs/board/reviews/<ID>/`
(`review_packet.py:846-851`), and that directory is gitignored
(`.gitignore:6`, written by `boardkit init` at `cli.py:539-548`). The
reviewer's own transcript lands beside them by hand. `PROCESS.md:387-393`
states the retention contract plainly: "A packet is regenerable working
material, never the record", and the cards and their logs are what endures.

That contract held while the only reader was the person who ran the review.
It stops holding now that outside vetters read the tracked repo, and epic
S41 says so in its acceptance scenario, step 5: a second developer on a
machine that has never seen this repo "audit[s] one past gate decision from
receipts tracked in the repo, with no access to this machine's transcripts".
Nothing tracked today can carry that step.

Two records show the gap already cost something.

The first is Gate F finding F2 from 2026-07-18, in
[`reviews/2026-07-18-codex-gate-f.md`](../../reviews/2026-07-18-codex-gate-f.md).
Half of it was accepted and fixed; the other half was rejected with this
reason: "packets are gitignored per-machine working material, so their
existence is not a property of the board and cannot be validated across
sessions". That is the problem stated by a reviewer three months before this
ADR, and the rejection was correct given the design at the time.

The second is the R-wave close. Ten cards (S13, S16, S18 through S25) held
Gate A open across five review rounds, and the cycle ended in a written
ruling rather than a pass:
[`docs/board/evidence/2026-08-16-gate-a-review-cycle.md`](../board/evidence/2026-08-16-gate-a-review-cycle.md).
That file names the reviewer transport, both model families, the per-round
verdicts and finding counts, and where the material sits. It is a receipt
written by hand, for ten cards at once, and it says of its own evidence:
"Per-card packets and reviewer verbatims sit under the board's gitignored
`docs/board/reviews/` ... Regenerate them at will; the durable record is the
card logs and this file." The reviewer verbatims are the part regeneration
cannot rebuild. They are the part an outside vetter most wants to read, and
they exist on exactly one machine.

Wave-2 decision 2 ruled the shape of the answer: an ArtifactStore seam
beside CardStore, a per-board posture key in `boardkit.toml`
(`ephemeral`, `in-repo`, `sidecar`), and a compact tracked receipt per gate
carrying the verdict, a numbered findings ledger, the author and reviewer
models, and content digests of the packet files. This ADR turns that ruling
into a design that S33 can implement, and settles the parts the ruling left
open. It writes no storage code and changes nothing under `src/`.

## Decision drivers

Hard constraints first. Each one is testable against a candidate design.

1. **Tracked-only audit.** A receipt MUST be readable and internally
   checkable from a clean clone of the tracked repo, with no access to the
   authoring machine and no network. This is S41 step 5 restated as a
   requirement.
2. **A receipt claims only what it supports.** It MUST NOT assert more.
   A packet that was never published, or that has since been lost, MUST be
   representable, and MUST be distinguishable at a glance from one a reader
   can fetch and check.
3. **A small public surface.** The tracked surface MUST NOT carry diffs,
   reviewer transcripts, or machine-local absolute paths. Decision 2 puts it
   as "without a single diff or transcript shipping in the public repo", and
   S12 is working to shrink that surface, not grow it.
4. **Process semantics stay kit-side.** The store moves bytes. It MUST NOT
   compute digests, verify them, decide a verdict, or read gate state. This
   is the rule `store.py:5-9` already states for CardStore: "gates, WIP,
   routing, and process semantics stay kit-side permanently."
5. **Posture changes retrievability, not the record.** For one review, the
   verdict, the findings ledger, the model fields, and the digest table MUST
   be identical under all three postures; only the receipt's `packets`
   entries may differ. Posture SHOULD decide only whether a reader can fetch
   the bytes the receipt names.
6. **No method without a caller.** The seam MUST ship only what S33's
   callers use, per the deferral `store.py:12-19` records for CardStore's
   `put`: "it has no caller yet and no format-preserving serialization, and
   a speculative writer that reflows frontmatter would churn every card it
   touched."
7. **Silence about posture means today's behavior.** A board whose config
   names no posture MUST behave exactly as it does now.
8. **Loud failure.** A store that cannot publish MUST fail saying so. It
   MUST NOT quietly downgrade to a weaker posture, and the receipt MUST NOT
   record a publication that did not happen.
9. **The models are named.** A receipt MUST name every model that authored
   the work and the model that reviewed it. `MODEL-CLASSES.md:155-160` warns
   against model ids downstream, and that warning governs prescriptive text:
   "a recipe, card, brief, or doc that names a specific model id is a drift
   hazard", because a followed-literally recipe can invert the
   reviewer-differs-from-author invariant. A receipt is not prescriptive. It
   is a past-tense record, in the same class as the cost ledger that rule
   exempts, and `PROCESS.md:271-274` requires it: the ledger "names the model
   that authored the diff and the model that reviewed it, so the
   reviewer-differs-from-author invariant is checkable from the record
   itself". The existing hand-written Gate F record does exactly this.
10. **Human-readable first.** A receipt SHOULD read as prose to a person
    with no tooling, and parse as data second. Revisit if a second consumer
    ever needs to read receipts in bulk, where the cost of a markdown parser
    would outweigh the cost of a reader learning JSON.

## Considered options

**A. Keep the status quo: ephemeral packets plus hand-written evidence
files.** Rejected. It is the design that produced both records in the
Context above. Its failure is not that evidence goes unwritten, since the
2026-08-16 file is thorough; it is that the evidence is unverifiable by
anyone who was not there, and that writing it is a manual act nobody owes.

**B. Track everything in the repo.** Rejected as the default. It satisfies
driver 1 completely and driver 3 not at all: every diff, every reviewer
transcript, and (per the premise check below) this machine's absolute
checkout path would enter the repo's permanent history.
`PROCESS.md:391-393` already names this as a deliberate, owned choice for a
repo that wants it, and boardkit is not that repo. Kept as the `in-repo`
posture, for a consumer whose material is not sensitive and whose vetters
want a single artifact. Rejected as the whole story.

**C. A sidecar store plus tracked receipts.** Chosen. Ruled by decision 2.
The tracked repo carries a compact receipt per gate; the bulk material goes
to a private store the CLI publishes to; digests bind one to the other.

**D. An external artifact service (object storage, a CI artifact store, a
release asset).** Rejected as the first implementation, kept as a future
driver. It would give the strongest retention story, and it adds a
credentialed dependency and a second authentication path to a CLI that
today needs only git and a filesystem. The seam this ADR defines is what
makes it cheap to add later, which is the argument for defining the seam
now rather than hard-coding a git sidecar.

Mentioned and not pursued: `git notes` or `git lfs` in the same repository,
which keep the bulk material in the public repo's object store and so fail
driver 3 the way option B does; and commit signing as the attestation
mechanism, which is orthogonal to this decision and would strengthen any of
the options above rather than replace one.

## Decision outcome

Option C. The parts below are the design S33 implements.

### 1. The ArtifactStore seam

A second Protocol in `src/boardkit/store.py`, beside `CardStore`, with one
driver per posture and a single resolver, mirroring `open_store`
(`store.py:229-237`).

```python
class ArtifactStore(Protocol):
    """What the CLI core may ask of any artifact store."""

    def describe(self) -> StoreInfo: ...

    def publish(self, ref: PacketRef, source: Path) -> Published: ...

    def fetch(self, published: Published, dest: Path) -> Path: ...
```

- `PacketRef` is the packet's logical identity: card id, gate, round, and
  the optional `suffix` that `review-packet` already uses for a multi-repo
  or fix-round packet (`REVIEW-TOOLING.md`, "Fix-round packets"). It names
  no filesystem path, so the same ref resolves under every posture.
- `Published` is what the receipt records: the store's name, a
  scheme-prefixed locator, and whether publication actually happened. It
  carries no digests, per driver 4.
- `StoreInfo` reports the posture, a printable location safe to show in
  `boardkit doctor`, and whether the store can be written to from here.

Three drivers: `EphemeralStore` (publish is a recorded no-op, `fetch`
raises), `InRepoStore` (copies into a tracked directory under the board),
and `SidecarStore` (commits and pushes into a git repository or directory
the machine overlay names).

Three things stay off the seam on purpose, per driver 6: `list`, `delete`,
and any garbage collection. No caller in S33 needs them, and a `delete` in
particular would be a method whose only correct use is one the rollback rule
already forbids: "The sidecar is append-only external state ... no sidecar
deletion is part of any rollback" (plan, Rollback).

**Digests are computed core-side, never by a driver.** The receipt writer
hashes the packet directory before handing it to `publish`, so a buggy or
hostile driver cannot forge an attestation, and every posture yields a
byte-identical receipt for the same review. This is driver 5 made
structural rather than conventional.

**The store ref grammar is the one the repo already has.** A sidecar
location parses like a manifest board location does today, through the
scheme-prefixed grammar `DOCKING.md` specifies as adopter requirement 8 and
`config.py:132-176` implements: `dir:<path>` for a plain directory,
`git:<url-or-path>` added for a sidecar repository, the bare keyword
`external` deferring to the machine overlay, and any other scheme an error
naming the schemes that exist. Reusing the grammar means a reader who has
learned one store ref has learned both.

### 2. The posture key

Three values, `ephemeral | in-repo | sidecar`, per decision 2. Default
`ephemeral`, which satisfies driver 7: a consumer board that never edits its
config behaves exactly as it does today, and the key is what a board opts
into.

| Posture | Packet lives | Receipt | Outsider can verify bytes |
| --- | --- | --- | --- |
| `ephemeral` | gitignored working dir, regenerated on demand | tracked, `published: false` | no |
| `in-repo` | tracked, under the board | tracked, `published: true` | yes, from the clone alone |
| `sidecar` | private repo or directory the CLI pushes to | tracked, `published: true` | yes, with sidecar access |

This board sets `sidecar`, per decision 2.

`sidecar` splits by backend, and the split matters to a reader choosing one.
A `git:` sidecar pins the published bytes with a commit sha the receipt
names, so the locator resolves to one immutable snapshot. A `dir:` sidecar
has no such anchor: the locator names a path, and whether that path still
holds the reviewed bytes is answered only by recomputing the digests.
Section 5 gives both backends their semantics.

The table above is the posture table `DOCKING.md` set the precedent for, and
it carries the same property: the CLI reads the posture, and no resolution
step or validation changes behavior because of it. Posture decides where
bytes go, not what the board means.

Where the key sits in `boardkit.toml` is open question 1 below.

### 3. The receipt format

One file per gate outcome, tracked, under a receipts directory beside the
cards directory:

```
docs/board/receipts/<ID>/<gate>-r<N>[-<suffix>].md
docs/board/receipts/_rulings/<date>-<slug>.md
```

The round number is not decoration. The fix-commit re-review duty
(`PROCESS.md:284-291`) means a single Gate A on a single card routinely
produces several reviews, and the 2026-08-16 cycle produced five. A
per-round file keeps each round's verdict, ledger, and reviewer intact
instead of overwriting the earlier ones, which is the same reason
`--suffix` exists for packets.

The optional filename suffix is that same `--suffix`, and it separates
verdicts. `PROCESS.md:379-382` has a card spanning two repos present one
packet per repo, and each is reviewed and concluded on its own, so each
earns a receipt: `A-r1.md` and `A-r1-consumer.md`. The other use of
`--suffix`, the fix-round packet that sits beside a regenerated full-range
packet, is one verdict over two packets and stays one receipt, with both
packets in the `packets` list below. `REVIEW-TOOLING.md` fixes which is
which: "A packet built on the fix diff alone is never the packet a gate is
graded on." A receipt concludes one verdict and may name several packets.

**Three kinds, because three things close a gate.** `review` carries a
reviewer's verdict and requires `reviewer_model`. `ruling` carries a board
owner's written termination of a cycle, covers a list of cards, and has no
single reviewer. `decision` carries a user gate, names the decider, and has
no `reviewer_model` at all. Splitting them means no kind has a required
field it cannot fill, which is what a single shape forced.

YAML frontmatter for the fields a checker reads, then prose for the reader.
A `review` receipt:

```yaml
---
receipt: v1
kind: review                 # review | ruling | decision
card: S32
gate: A
round: 1
suffix: null                 # the --suffix this receipt concludes on, or null
verdict: FAIL                # PASS | FAIL | DEFERRED
findings: 10
dated: 2026-08-23
route: codex-reviewer
author_models:               # every model that authored a commit in the range
  - <model string>
reviewer_model: <the model string that returned the verdict>
commit_range: 9b1c158..decedc3
packets:                     # one entry per packet behind this one verdict
  - name: primary            # `primary`, or the --suffix that names it
    posture: sidecar
    published: true
    locator: "git:bk-sidecar@<commit-sha>#S32/A-r1"
    manifest: "sha256:<64 hex>"
---
```

`ruling` replaces `card` with `cards` and `round` with a rounds summary,
because a ruling is exactly the artifact that spans both, and its verdict is
`RULING`. `decision` replaces `reviewer_model` with `decider`, names the
gate it closes, and takes verdict `ACCEPTED` or `REJECTED`. The full verdict
vocabulary across the three kinds is `PASS`, `FAIL`, `DEFERRED`, `RULING`,
`ACCEPTED`, `REJECTED`, and each kind admits only its own subset, so an
absent or out-of-kind verdict is a validation error rather than a reading
the reader has to interpret. Section 8 shows the R-wave ruling written out
in full against this schema.

Then three body sections: `## Packet digests`, a table of one row per
published file (full SHA-256, then the packet-relative POSIX path, grouped
by packet name when there is more than one); `## Findings`, the numbered
ledger with each finding's disposition, being the fix applied or the reason
it was rejected; and `## Checks the reviewer did not run`, holding the
UNVERIFIED class `PROCESS.md:274-279` defines, so a sandbox limitation is
never silently read as a passing check. This review is the worked example:
its round-1 reviewer could not run the `uv`-backed checks at all.

**`author_models` is a list, and the invariant reads it as one.** A
`commit_range` can span commits several models wrote, and `PROCESS.md:266-268`
requires the reviewer to differ from every one of them: "for a multi-commit
range, the reviewer must differ from every model that wrote any commit in
it, and a range whose authorship cannot be established defers rather than
being reviewed blind." The check is set membership rather than string
inequality: `reviewer_model` MUST NOT appear in `author_models`, and an
empty `author_models` is the unestablished-authorship case that defers,
never a vacuous pass.

Five further properties earn their place:

**The verdict field is required and has no empty value.** An absent or
verdict-less review is a failed review, per `REVIEW-TOOLING.md:33-36`, and a
format that can represent silence invites a reader to interpret it. Zero
findings is written `verdict: PASS` with `findings: 0`, which is the same
rule's "Zero findings is recorded as an explicit PASS, distinguishable from
a tool that silently returned nothing."

**`published` is a first-class field, not an inference.** Driver 2 needs a
reader to tell an attested packet from a fetchable one without reasoning
about posture, and the R-wave backfill below is the first record whose
accuracy depends on `published: false` existing.

**Digests are full 64-character SHA-256.** `contract_digest`
(`contract.py:372-389`) truncates to 12 hex characters, which suits its job:
it fingerprints staleness, and a reader compares it against a value they
computed a minute ago. A receipt digest answers a different question, asked
by a reader who wants to know whether a file was altered by someone hoping
they would not notice, and 48 bits is thin for that. The departure from the
house scheme is deliberate, and recorded here so a later reader does not
take it for an oversight.

**The manifest root checks transcription, and nothing stronger.** It is
`sha256("boardkit-receipt:v1\n" + the sorted digest lines)`, computed over
the digest table alone, so a reader with no packet access can confirm the
table arrived whole: a truncated copy-paste, a mangled fetch, a row lost to
a bad merge. It does not detect tampering, and an earlier draft of this ADR
claimed it did. Anyone who edits the table can recompute the root, and the
root covers none of the verdict, models, findings, or dispositions in the
first place. Per-file digests hash the file bytes. The framing follows the
length-prefixed, domain-separated pattern `contract_digest` established and
its stated reason ("length-prefixed so two docs cannot concatenate into a
third's bytes"). A packet-relative path containing a newline is refused
rather than encoded, which is the fail-loud choice the repo takes
everywhere else.

**Tamper-evidence for a receipt comes from git, not from the receipt.** The
receipt is committed to the tracked repo in the same commit as the card's
log line, so what makes a later edit visible is the history everyone else
has already fetched, not a hash the editor also controls. That is a real
property and a modest one: it detects a quiet edit, and it does not stop a
board owner from committing a false receipt in the first place. Commit
signing is the upgrade path, named in the gaps below, and it is the only
thing here that would raise the floor.

The card's log keeps its one-line gate entry and links the receipt. The log
line stays the board's own record, per `PROCESS.md`; the receipt is the
evidence it points at. Their agreement is checkable, and open question 4
covers which gates get one at all.

### 4. The receipt lifecycle

No CLI command closes a gate today, so the ordering below is a contract S33
implements rather than a description of something running. It exists because
the alternative is S33 inventing transactional behavior under deadline.

**When a receipt is written.** One per round, at the moment the round
concludes, which is when the reviewer's final message yields a verdict.
A FAIL receipt is written the same as a PASS: the fix-round duty makes
failed rounds part of the record, and the 2026-08-16 cycle is five rounds
of evidence that the failures are the interesting part. A round that never
returns a verdict is a failed delegation per `REVIEW-TOOLING.md`, and it
produces a `verdict: DEFERRED` receipt naming what happened, never silence.

**The order is hash, write, log, publish.**

1. Hash the packet directory. Local, no network.
2. Write the receipt with `published: false`. Local.
3. Append the card's log line, which links the receipt. Local.
4. Publish the packet, then flip `published` to `true` and record the
   locator.

Steps 1 through 3 land in one commit, so a card's log line and its receipt
are never separately revertible. Step 4 is deliberately outside that commit,
which is open question 2's recommendation made concrete: publication is the
only step that can fail for reasons nothing local controls, and the design
refuses to let a network failure block a gate close or, worse, push the
board owner back to closing gates by hand.

**Failure at each step.** A failure in 1 through 3 aborts the close with
nothing written, since all three are local and a partial write has no
excuse. A failure in step 4 leaves a valid receipt marked `published:
false`, which is the honest state and not an error: the review happened,
the digests are recorded, the bytes are not yet reachable. `boardkit doctor`
warns for as long as any receipt sits unpublished, which is the pressure
that keeps the queue from becoming permanent.

**The flip is the one permitted mutation.** A committed receipt is otherwise
append-only. Publishing may change exactly two fields, `published` and
`locator`, in one commit that changes nothing else, and whose message says
so. Every other field is frozen at write time, and a correction to one of
them is a new receipt for a new round, never an edit.

That narrowness is what makes the flip auditable. A reader who wants to
check it reads the receipt's history: the commit that flips `published` must
touch those two fields and no others, and the digest table must be
byte-identical across the flip. A flip commit that also moved a verdict or a
digest is the anomaly, and it is visible with one `git log -p` on the file.
This is the same modest guarantee as above, resting on git history rather
than on anything the receipt asserts about itself.

### 5. Sidecar mechanics

The sidecar is a git repository or a directory (open question 3 covers
which, and both are within decision 2's wording), private, holding one
directory per published packet, namespaced by the board's registry
short-code so two boards can share one sidecar without collision.

**The git backend.** Publication has three steps: the receipt writer hashes
the packet directory; the driver copies the files in, commits, and pushes;
the resulting commit sha becomes the receipt's locator, in the shape
`git:<store-name>@<commit-sha>#<board>/<ID>/<gate>-r<N>[-<suffix>]`. The
commit sha is what makes the locator stable, since a branch name or a path
alone would move under the reader.

**The directory backend.** Open question 3 keeps `dir:` reachable, so it
needs semantics rather than an implied port of the git ones, and its
guarantee is weaker in a way worth stating plainly.

- **Locator.** `dir:<store-name>#<board>/<ID>/<gate>-r<N>[-<suffix>]`, with
  no `@` component, because a directory has no commit to name.
- **What replaces the commit sha.** The manifest root already in the
  receipt. A directory publication is content-addressed by that value and
  by nothing else, so a `dir:` locator resolves to a path and the reader's
  only assurance that the path still holds the reviewed bytes is
  recomputing the per-file digests. Under git the sha pins the bytes before
  a digest is computed; under `dir:` nothing does.
- **Collision.** A publish whose target directory exists refuses and says
  so. The store is append-only (plan, Rollback), so an existing directory
  means either a republish of the same round, which needs no write, or a
  ref collision, which is a defect. Overwriting would silently invalidate
  every receipt already naming that path.
- **Fetch.** Copy the directory back out to a caller-named destination.
  There is no revision to check out and no history to consult, so a fetch
  that returns nothing is indistinguishable from a packet that was never
  published; the receipt's `published` field is what tells them apart.

That asymmetry is stated in the posture and failure tables too, so a reader
choosing a backend sees it without reading this section.

**The location is machine-local and the tracked config never names it.**
`boardkit.toml` carries the posture and a logical store name; the absolute
path or remote URL sits in the machine overlay `.boardkit/local.toml`, which
`.gitignore:9` already excludes and `boardkit init` already writes
(`cli.py:539-548`). This is the pattern `DOCKING.md` set for `external`
boards, and its rationale carries over unchanged: "The machine overlay is
the deliberate exception. `local.toml` holds absolute paths to boards
outside the repo, which makes it a pointer file in the ordinary sense: it
goes stale when a checkout it names moves ... Staleness there is surfaced
rather than prevented." Section 9 weighs that choice against S12.

**The overlay needs a schema it does not have yet.** Today `local.toml`
accepts one top-level table and one row key: the parser raises on any
top-level key but `boards` (`config.py:252-254`) and on any row key but
`path` (`config.py:258-260`), and a row's `path` must be absolute. A store
name, a remote URL, and a backend scheme all fail that parser today. The
extension is stated here so S33 implements a schema rather than inventing
one:

```toml
# .boardkit/local.toml, machine-local, never committed
[boards.aura]
path = "/absolute/path/to/board"        # unchanged

[stores.bk-sidecar]
location = "git:/absolute/path/to/sidecar.git"
```

- A new top-level `stores` table, keyed by the logical store name the
  tracked `boardkit.toml` refers to. `boards` keeps its meaning untouched.
- `location` is the only key a row may carry, and it is a scheme-prefixed
  store ref under the grammar of `DOCKING.md` requirement 8: `git:` or
  `dir:`, with a bare string meaning `dir:`. A `git:` value may be a remote
  URL or an absolute local path; a `dir:` value must be an absolute path,
  refused when relative for the same reason `boards` refuses one.
- The same strictness applies in both directions, per `contract.py:143-151`:
  an unknown key in a `stores` row is an error, and a tracked config naming
  a store the overlay does not define fails saying which name is missing and
  which file to add it to. That is the error `DOCKING.md` already specifies
  for an unresolved `external` board, reused rather than reinvented.
- A board whose posture is `sidecar` with no matching overlay row cannot
  publish. It still writes receipts, marked `published: false`, which is
  the second machine's correct behavior rather than a failure.

### 6. Failure modes

Each row is a failure the design expects, with what the reader sees.

| Failure | Behavior |
| --- | --- |
| Sidecar unreachable at gate close (network, auth) | Publication fails loudly, per driver 8. Whether the gate close blocks or the receipt is written unpublished is open question 2. |
| Push rejected, non-fast-forward | The driver rebases and retries once, then fails. The locator is a commit sha, so a concurrent publisher's push does not invalidate an earlier receipt. |
| Sidecar history rewritten | The locator's sha stops resolving. The digests still identify the content, so the packet re-attests from any surviving copy, and the mismatch is visible rather than silent. |
| Sidecar lost or deleted | Every receipt that named it degrades to an attestation. This is stated, not prevented: no design that keeps bulk material out of the public repo can also guarantee its survival. |
| Receipt committed, publish never ran | The reconciliation check below finds a receipt whose `published: true` names a locator nothing can fetch, or a `published: false` that has sat unpublished across sessions. `boardkit doctor` warns. |
| A packet carries a secret | The sidecar is private, and the receipt exposes file names and digests only. A digest still confirms a guess about a small file's exact content. Named as a residual, not mitigated. |
| Two boards share one sidecar | Short-code namespacing prevents collision. A board whose short-code changes orphans its earlier packets, which the locator makes visible. |
| A `dir:` sidecar's published bytes change underneath a receipt | Nothing detects it at fetch time, because the locator names a path rather than a snapshot. Recomputing the digests is the only check, and it reports a mismatch without saying which side moved. This is the weaker guarantee open question 3 trades away. |
| A publish targets a `dir:` path that already exists | Refused, since the store is append-only. Overwriting would invalidate every receipt already naming that path. |
| Packet regenerated on another machine | The bytes differ, so the digests do not match. This is not a bug and not a validation path. See the premise check below: `REVIEW.md` embeds an absolute machine path by construction. |

### 7. The outside-vetter validation path

The target is S41 step 5, and what the vetter can actually check varies with
what they can reach.

**With the tracked repo only, which is the common case.** Clone, read the
card, follow its log line to the receipt, then run the verification the
receipt supports without any packet: recompute the manifest root from the
digest table, confirm the card's log line and the receipt agree on gate,
round, verdict, and date, confirm `reviewer_model` does not appear in
`author_models`, and confirm the receipt's `commit_range` resolves in the
history they just cloned.

Every one of those checks is a consistency check on what the board asserts.
Together they establish that the board claims a named reviewer, distinct
from every author, reached this verdict over these commits and these
digests, that the claim was committed at a particular point in the repo's
history, and that nothing has quietly contradicted it since. They do not
establish that the reviewer existed, ran, or ever saw the bytes the digest
table names. Nothing in the receipt is signed, and the same board owner
writes the log line, the receipt, and the digests. An outsider is reading an
attestation and checking it for self-consistency, which is worth doing and
is not verification. The design says so here rather than
letting the word "digest" imply otherwise.

**With sidecar access, which a collaborator can be granted.** Fetch the
packet by locator, recompute each file's digest, compare against the table.
That closes the gap between the receipt and the bytes: the reader now knows
the digests describe the packet they are holding. It is the Gate M test S33
owes, where digests validate from a clean clone and a deliberately tampered
packet fails. What stays open even here is provenance, since the packet is
still material the board owner produced; reading the reviewer's transcript
inside it is judgment, not proof.

**Under `in-repo` posture.** Both halves come from the clone alone, which
is why the posture exists for consumers whose material is not sensitive.

A `verify-receipt` command is the natural home for the first path, and this
ADR does not specify its flags; S33 owns that surface.

### 8. The R-wave backfill

Mike ruled this at the 2026-08-22 Gate U: start fresh, plus one receipt for
the 2026-08-16 ruling. The design follows the ruling and adds only what
makes it honest.

**No retroactive receipts for the ten cards.** S13, S16, and S18 through S25
closed on the ruling record, and each carries its own log line saying so.
Manufacturing ten receipts now would mean writing digests for packets that
were never archived, in a format whose whole purpose is to distinguish a
checkable claim from an unchecked one.

**One ruling receipt**, at
`docs/board/receipts/_rulings/2026-08-16-r-wave.md`. Written out against the
`ruling` schema, so the shape is settled here rather than at implementation
time:

```yaml
---
receipt: v1
kind: ruling
cards: [S13, S16, S18, S19, S20, S21, S22, S23, S24, S25]
gate: A
verdict: RULING
dated: 2026-08-16
route: codex-reviewer
author_models: [<the model that authored the wave>]
reviewer_model: <the model that ran every round>
rounds:                      # one entry per round the cycle ran
  - round: 1
    object: "the ten card diffs, one packet each"
    verdict: FAIL
    findings: 24
  - round: 2
    object: "six fix commits"
    verdict: MIXED           # 1 PASS, 5 FAIL
    findings: 5
  - round: 3
    object: "2121d41"
    verdict: FAIL
    findings: 3
  - round: 4
    object: "8487140"
    verdict: FAIL
    findings: 3
  - round: 5
    object: "3a4b001"
    verdict: FAIL
    findings: 1
ruling: docs/board/evidence/2026-08-16-gate-a-review-cycle.md
gate_ticked: false           # the ruling explicitly did not tick Gate A
packets: []                  # never archived; nothing to point at
---
```

Three things the shape has to carry, and does. `cards` is a list because the
cycle was batched across ten. `rounds` is a list of summaries rather than a
single count, because the interesting fact about this cycle is its shape:
each round narrower than the last. And `packets: []` with an empty digest
table is the honest encoding of material that stayed on one machine, which
is why `published` had to be a real field rather than an inference.

`MIXED` appears only inside a ruling's `rounds` list, never as a receipt's
own verdict. Round 2 above returned one PASS and five FAILs across six
cards, and flattening that to either value would misreport it. A
receipt-level verdict stays one of the four in the vocabulary, because a
receipt concludes one thing.

`gate_ticked: false` is specific to a ruling, and it comes straight from
point 4 of the 2026-08-16 ruling: "**Gate A does not tick on any of the ten
cards.**" A ruling that ends a cycle without a pass is exactly the case a
reader would otherwise misread, since every other receipt in the directory
records a gate that closed.

Its digest table has one row, the tracked evidence file the ruling lives in.
That digest is redundant with git's own object hash for a tracked file, and
it is kept anyway, so that every receipt has the same shape and can be
checked by a reader with a hash tool and no git.

This makes the backfill the format's first proof that driver 2 works: the
R-wave's real evidentiary state is legible from the tracked repo, including
the part that is missing.

### 9. The machine-local pointer pattern, weighed beside S12

The pattern comes from the 2026-08-12 consumer-seam entry, drained in
Phase 0. Its proposal, verbatim: "the kit's entry-file templates could ship
a per-harness machine-local pointer pattern (a permanent index line to a
curated consumer file) rather than expecting tracked-file edits." The worked
case was a permanent index line pointing at a file that did not exist;
creating the file "activated a persistent above-the-fold seam with zero
renderer changes", while a machine without the file saw a line that pointed
at nothing and lost nothing by it.

Weighed against this design, the pattern splits cleanly in two.

**Adopted for the sidecar location.** A tracked config naming a logical
store, resolved through a machine-local overlay, is this pattern exactly,
and it is already the shape `DOCKING.md` ships for `external` boards. A
machine with the overlay row publishes; a machine without it reads the
receipts and cannot publish, which is a correct outcome rather than a
broken one.

**Rejected for receipts themselves.** A receipt whose content depends on
machine-local state fails driver 1 outright: the outsider is precisely the
reader who has none. Receipts are tracked, resolvable, and complete on their
own.

The repo enforces this split in code, which is worth knowing before someone
tries the other arrangement. `DirStore.check_links` (`store.py:149-175`)
errors on any relative link in a card body that does not resolve, so a card
may not carry a pointer to machine-local material at all: `boardkit check`
fails the board. Receipts live outside `cards_dir`, so the rule does not
reach them, and a card's link to its receipt resolves because receipts are
tracked. The design is compatible with the check as it stands.

**For S12.** The relevant finding here is not the pattern but a leak the
pattern would not fix. `REVIEW.md` embeds the board's absolute repo path by
construction (see the premise check), so publishing packets unmodified under
`in-repo` posture would write one contributor's home directory layout into
the repo's permanent history. That is the surface S12 exists to shrink.
Recommendation, recorded here for S12 to take or leave: keep S12's
`--public` gitignore route for the contract docs, and treat the absolute
path in the packet header as this ADR's named gap rather than S12's, since
it is a packet-generation defect that predates both cards.

## Consequences

**Positive.**

- An outside vetter can audit a gate decision from the tracked repo, which
  is S41 step 5 and the thing nothing today supports.
- The reviewer verbatim, the one artifact regeneration cannot rebuild,
  stops being machine-local for boards that opt in.
- The receipt writes itself at gate close, so the evidence no longer depends
  on someone choosing to write an evidence file by hand.
- The seam makes a fourth backend an afternoon rather than a redesign, which
  is what keeps option D available without paying for it now.
- `ephemeral` as default means no consumer board changes behavior until it
  edits its config.

**Negative.**

- The tracked repo gains a directory that grows with every gate. A wave the
  size of wave 2 adds tens of small files, and they are permanent.
- The verdict now lives in two tracked places, the card log and the receipt.
  That is a new drift surface, and Gate D inherits it. `boardkit check`
  should validate that a card's gate log lines and its receipts agree; that
  validation is S33's to write, and until it exists the drift is real.
- Without sidecar access the vetter gets an attestation, not a proof. The
  trust rests on the board owner's honesty plus tamper-evidence, and the
  design should not be described as more than that.
- Digest validation requires the archived bytes. Regeneration is not a
  substitute, and a reader who assumes it is will conclude a healthy packet
  was tampered with.
- Publishing depends on machine-local state, so a second machine cannot
  publish for the same board until its overlay is set up. The staleness is
  surfaced, not prevented, exactly as `DOCKING.md` says of overlays.
- A board that adopts the posture key pins itself to a boardkit new enough
  to parse it. Config parsing is strict in both directions
  (`contract.py:143-151`), so an older CLI reading a newer config raises
  rather than ignoring the key.

**Named gaps, each with an owner.**

- The absolute repo path in `REVIEW.md` (`review_packet.py:748`,
  `config.py:726`) blocks a safe `in-repo` posture. Owner: S33, which cannot
  ship `in-repo` without fixing it or excluding that file from
  publication. Flagged to S12 as adjacent public-surface work.
- Receipt-versus-log agreement has no validator. Owner: S33.
- No living contract document names `docs/adr/` as the ADR home. S32's card
  log records the ruling, and the routing line it cites ("ADR /
  decision-record changes (`docs/adr/`, `DECISIONS.md`): run `adr-review`")
  lives in the `gate-probes` skill outside this repo. Neither is where a
  fresh agent looks: `AGENTS.md`'s read order and `PROCESS.md` say nothing
  about ADRs, so the convention survives in a card log that scrolls and a
  skill this repo does not ship. Owner: a documentation card, or S12 as it
  works the outsider-facing surface.
- The aura board's cards describe a house `docs/adr/` convention with a
  date prefix, while this board's ruling numbers from 0001. Two families,
  two conventions, no forcing function to reconcile them. Recorded so the
  divergence is deliberate rather than discovered.
- Commit signing would turn several attestations in section 7 into
  verifications. Out of scope here, and a candidate for its own ADR.

## Open questions

Each is an either-or the ruled inputs leave open, with a recommendation. All
four are Mike's to settle at Gate U, or S33's to settle with evidence.

**OQ1. Where the posture key lives: `[board] posture` or a new `[artifacts]`
table.** Decision 2 says "a per-board posture key in `boardkit.toml`" and
does not say which table. The compatibility argument is a wash: `[board]`
rejects unknown keys and the top-level rejects unknown sections
(`config.py:675-677`), so either is a breaking read for an older CLI. What
differs is cohesion and headroom. *Recommendation: a new optional
`[artifacts]` table holding `posture`, the logical store name, and a
`receipts_dir`.* Posture needs more than one key, and `[board]` is the
card-identity surface `BoardMeta` mirrors to a driver (`store.py:54-75`). An
optional section has a precedent to copy exactly: `charter` is excluded from
the required set at `config.py:687`, and an optional key with a default has
one too, `wip` at `config.py:696`.

**OQ2. What a failed publish does to the gate close: fail closed, or write
the receipt unpublished and queue.** Driver 8 forbids a silent downgrade and
does not choose between these. *Recommendation: two-phase.* Write the
receipt with its digests, which needs no network and always succeeds, mark
it `published: false`, publish as a separate step, and have `boardkit
doctor` warn while any receipt sits unpublished. Fail-closed couples a board
write to a network round trip and, on a flaky link, pushes the board owner
toward doing the close by hand, which is the outcome the whole design exists
to end. One counter-argument holds: a queue nobody drains is a slower
version of the same failure, which is what the doctor warning exists to
catch.

**OQ3. Sidecar transport: a git repository, or a plain directory.** Decision
2 names both ("a private git repo or directory the CLI pushes packets to")
and picks neither. *Recommendation: git, with `dir:` accepted for the same
grammar reason `DOCKING.md` gives.* Only git gives the locator a commit sha,
which is what makes a receipt point at an immutable snapshot rather than at
a path whose content can change underneath it. A plain directory is the
right answer for a synced-folder setup and should stay reachable, with its
weaker guarantee stated where a reader will see it.

**OQ4. Which gates get a receipt: every gate, as decision 2 literally says,
or the narrowed set below.** This one is a departure from the ruled input
rather than a gap in it, and it is flagged for Gate U approval on that
basis. Decision 2 reads "The tracked repo carries only a compact review
receipt per gate", and the honest reading of "per gate" is every gate.

*Recommendation: narrow it to the gates that conclude something a reader
would audit, being A and F as `review`, a cycle-ending ruling as `ruling`,
and U as `decision`.* Two reasons, and the second is the one that changed
the design.

Gate S is deterministic command output. It has no reviewer, no verdict a
model returned, and no findings ledger, so a `review` receipt for it would
have empty model fields, and an empty model field is exactly what driver 2
says the format must not contain. Gate S evidence is the pasted command
output the card's checklist already requires.

The other reason is that "every gate" and "named-reviewer verdicts only"
are not the only two options, and an earlier draft of this ADR tried to have
both by listing Gate U under a rule that required a `reviewer_model` Gate U
does not have. That contradiction is what produced the three kinds in
section 3: `review` for a reviewer's verdict, `ruling` for a board owner
ending a cycle, `decision` for a user gate with a decider and no reviewer.
With the kinds split, "which gates" stops being a question about the schema
and becomes a question about scope alone.

Gates D and M sit closest to the line. Both produce a written judgment a
vetter might reach for, and both fit `decision` without a format change, so
including them later costs a value in an existing field. If Mike prefers
decision 2's literal reading, the cost is bounded in the same way: every
gate gets a `decision` receipt, Gate S receipts carry command output instead
of a findings ledger, and nothing in sections 1 through 5 changes.

## Premises checked against the code

Every claim this ADR makes about existing behavior, verified at `57b6390`
the way `DOCKING.md` was written against the shipped resolver. Re-verify on
revision.

| Premise | Verdict | Anchor |
| --- | --- | --- |
| Packets are gitignored working material, written to `docs/board/reviews/<ID>/` | still true | `.gitignore:6`, `boardkit.toml` `[review] output_dir`, `cli.py:539-548` |
| A packet is `NN-<sha>.diff`, `full-range.diff`, `REVIEW.md`, plus non-regenerable material a rerun does not delete | still true | `review_packet.py:846-851`, `GENERATED_NAMES` at `:85`, `clean_generated` at `:762` |
| `REVIEW.md` embeds an absolute machine path | still true; two sections above depend on it | `config.py:726` resolves `review.repo` absolute; `review_packet.py:748` renders ``Repo: `{repo}` `` |
| No `ArtifactStore` and no posture key exist today | still true | `store.py` defines `CardStore` only; no `posture` anywhere in `src/` |
| Config parsing is strict in both directions | still true | `contract.py:143-151`, `config.py:675-677`, `config.py:687-689` |
| An optional section and an optional defaulted key both have a precedent | still true | `charter` excluded at `config.py:687`; `wip` popped with a default at `config.py:696` |
| A scheme-prefixed store-ref grammar already ships | still true | `config.py:132-176`, `KNOWN_SCHEMES`/`RESERVED_SCHEMES` at `:60-63`; `DOCKING.md` requirement 8 |
| The house digest is SHA-256 truncated to 12 hex, length-prefixed, machine-independent | still true | `contract.py:372-389` |
| `CardStore` exposes `transition` and `append_log` with no CLI caller yet | still true | `store.py:19-20`, `:186-226` |
| No receipt-shaped writer exists in the CLI | still true | ten subcommands at `cli.py:596-674`; only `render`, `init`, `review-packet` write |
| `check_links` errors on an unresolvable relative link in a card body | still true | `store.py:149-175` |
| The R-wave ruling covers ten cards and did not tick Gate A | still true | `docs/board/evidence/2026-08-16-gate-a-review-cycle.md:6`, `:72-89` |
| The ten cards closed on that record at the wave-2 Gate U | still true | plan decision 1; identical log lines on all ten cards |
| Gate F finding F2 rejected packet-existence validation for this reason | still true | `reviews/2026-07-18-codex-gate-f.md`, F2 |
| `PROCESS.md` requires the ledger to name author and reviewer models | still true | `PROCESS.md:271-274` |
| The no-model-ids rule targets prescriptive text and exempts the cost ledger | still true | `MODEL-CLASSES.md:155-160` |
| No living contract doc names `docs/adr/` as the ADR home | still true, with a correction | S32's card log names it (`s32-artifact-store-adr.md`, Log, 2026-08-23), and the routing line is in the external `gate-probes` skill; no entry-file or process doc carries it. An earlier draft of this ADR said nothing tracked named the path at all, which was wrong |
| The suite and lint are green before this change | still true | `uv run pytest -q` 430 passed; `uv run ruff check` clean |

## Links

- Card [S32](../board/cards/s32-artifact-store-adr.md), this ADR's own card.
- Card [S33](../board/cards/s33-receipts-and-sidecar.md), the
  implementation, which cites this document.
- Card [S34](../board/cards/s34-wave-gate-design.md), the wave-gate decision
  that depends on S32.
- Card [S12](../board/cards/s12-public-repo-seam.md), the public-repo seam
  weighed in section 9.
- Card [S28](../board/cards/s28-store-seam-wiring.md), the CardStore wiring
  this seam sits beside.
- [Wave-2 plan](../plans/2026-08-19-wave-2-plan.md), decision 2 and Phase 4.
- [PROCESS.md](../board/PROCESS.md), the gate ladder and the packet
  retention contract.
- [MODEL-CLASSES.md](../board/MODEL-CLASSES.md), the no-model-ids rule and
  the reviewer pre-vet.
- [REVIEW-TOOLING.md](../board/REVIEW-TOOLING.md), the ledger rule and the
  fix-round packet shape.
- [DOCKING.md](../DOCKING.md), the versioned-doc precedent, the posture
  table, the machine overlay, and the store-ref grammar.
- [2026-08-16 Gate A review cycle](../board/evidence/2026-08-16-gate-a-review-cycle.md),
  the ruling the backfill receipt records.
- [2026-07-18 Gate F review](../../reviews/2026-07-18-codex-gate-f.md), the
  hand-written record this format generalizes, and finding F2.

## Review ledger

Gate A has not run. The adversarial prose review appends its numbered
findings ledger here, with an explicit verdict and both model names, per
`REVIEW-TOOLING.md`. An empty ledger is not a pass.
