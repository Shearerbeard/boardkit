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
- **Code anchors verified at**: `23dea92`. Re-verify and bump this stamp on
  any revision, per the Gate D duty in `PROCESS.md`.

## Context and problem statement

Every gate decision this board has taken rests on material that exists only
on one laptop. `boardkit review-packet` writes `NN-<sha>.diff`,
`full-range.diff`, and `REVIEW.md` into `docs/board/reviews/<ID>/`
(`review_packet.py:845-851`), and that directory is gitignored
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
   be identical under all three postures; only the receipt's `packet` block
   may differ. Posture SHOULD decide only whether a reader can fetch the
   bytes the receipt names.
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
9. **The models are named.** A receipt MUST name the model that authored
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

The table above is the posture table `DOCKING.md` set the precedent for, and
it carries the same property: the CLI reads the posture, and no resolution
step or validation changes behavior because of it. Posture decides where
bytes go, not what the board means.

Where the key sits in `boardkit.toml` is open question 1 below.

### 3. The receipt format

One file per gate outcome, tracked, under a receipts directory beside the
cards directory:

```
docs/board/receipts/<ID>/<gate>-r<N>.md
```

The round number is not decoration. The fix-commit re-review duty
(`PROCESS.md:284-291`) means a single Gate A on a single card routinely
produces several reviews, and the 2026-08-16 cycle produced five. A
per-round file keeps each round's verdict, ledger, and reviewer intact
instead of overwriting the earlier ones, which is the same reason
`--suffix` exists for packets.

YAML frontmatter for the fields a checker reads, then prose for the reader:

```yaml
---
receipt: v1
card: S32
gate: A
round: 1
kind: review          # review | ruling
verdict: FAIL         # PASS | FAIL | DEFERRED | RULING
findings: 4
dated: 2026-08-23
route: opencode-reviewer
author_model: <the model string that authored the work>
reviewer_model: <the model string that returned the verdict>
commit_range: 9b1c158..decedc3
packet:
  posture: sidecar
  published: true
  locator: "git:bk-sidecar@<commit-sha>#S32/gate-a-r1"
  manifest: "sha256:<64 hex>"
---
```

Then three body sections: `## Packet digests`, a table of one row per
published file (full SHA-256, then the packet-relative POSIX path);
`## Findings`, the numbered ledger with each finding's disposition, being
the fix applied or the reason it was rejected; and `## Checks the reviewer
did not run`, holding the UNVERIFIED class `PROCESS.md:274-279` defines, so
a sandbox limitation is never silently read as a passing check.

Four properties earn their place:

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

**The manifest root is derived from the table, not from the files.** It is
`sha256("boardkit-receipt:v1\n" + the sorted digest lines)`, so a reader
with no packet access can still recompute the root from the receipt's own
table and detect a receipt that was edited after the fact. Per-file digests
hash the file bytes. The framing follows the length-prefixed, domain-
separated pattern `contract_digest` established and its stated reason
("length-prefixed so two docs cannot concatenate into a third's bytes"). A
packet-relative path containing a newline is refused rather than encoded,
which is the fail-loud choice the repo takes everywhere else.

The card's log keeps its one-line gate entry and links the receipt. The log
line stays the board's own record, per `PROCESS.md`; the receipt is the
evidence it points at. Their agreement is checkable, and open question 4
covers which gates get one at all.

### 4. Sidecar mechanics

The sidecar is a git repository or a directory (open question 3 covers
which, and both are within decision 2's wording), private, holding one
directory per published packet, namespaced by the board's registry
short-code so two boards can share one sidecar without collision.

Publication has three steps: the receipt writer hashes the packet directory;
the driver copies the files in, commits, and pushes; the resulting commit
sha becomes the receipt's locator. The commit sha is what makes the locator
stable, since a branch name or a path alone would move under the reader.

**Its location is machine-local and the tracked config never names it.**
`boardkit.toml` carries the posture and a logical store name; the absolute
path or remote URL sits in the machine overlay `.boardkit/local.toml`, which
`.gitignore:9` already excludes and `boardkit init` already writes
(`cli.py:539-548`). This is the pattern `DOCKING.md` set for `external`
boards, and its rationale carries over unchanged: "The machine overlay is
the deliberate exception. `local.toml` holds absolute paths to boards
outside the repo, which makes it a pointer file in the ordinary sense: it
goes stale when a checkout it names moves ... Staleness there is surfaced
rather than prevented." Section 8 weighs that choice against S12.

### 5. Failure modes

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
| Packet regenerated on another machine | The bytes differ, so the digests do not match. This is not a bug and not a validation path. See the premise check below: `REVIEW.md` embeds an absolute machine path by construction. |

### 6. The outside-vetter validation path

The target is S41 step 5, and what the vetter can actually check varies with
what they can reach.

**With the tracked repo only, which is the common case.** Clone, read the
card, follow its log line to the receipt, then run the verification the
receipt supports without any packet: recompute the manifest root from the
digest table, confirm the card's log line and the receipt agree on gate,
round, verdict, and date, confirm `author_model` and `reviewer_model`
differ, and confirm the receipt's `commit_range` resolves in the history
they just cloned. That establishes who reviewed which exact bytes, what they
concluded, and that the record has stood unedited since it was committed. It
leaves one thing unestablished: whether those bytes said what the receipt's
findings claim. The reader is holding an attestation bound into the repo's
own history, and this ADR calls it an attestation so nobody mistakes it for
independent verification.

**With sidecar access, which a collaborator can be granted.** Fetch the
packet by locator, recompute each file's digest, compare against the table.
This is full verification, and it is the Gate M test S33 owes: digests
validate from a clean clone, and a deliberately tampered packet fails.

**Under `in-repo` posture.** Both halves come from the clone alone, which
is why the posture exists for consumers whose material is not sensitive.

A `verify-receipt` command is the natural home for the first path, and this
ADR does not specify its flags; S33 owns that surface.

### 7. The R-wave backfill

Mike ruled this at the 2026-08-22 Gate U: start fresh, plus one receipt for
the 2026-08-16 ruling. The design follows the ruling and adds only what
makes it honest.

**No retroactive receipts for the ten cards.** S13, S16, and S18 through S25
closed on the ruling record, and each carries its own log line saying so.
Manufacturing ten receipts now would mean writing digests for packets that
were never archived, in a format whose whole purpose is to distinguish a
checkable claim from an unchecked one.

**One ruling receipt.** It records the 2026-08-16 cycle: `kind: ruling`,
`verdict: RULING`, the ten cards it covers, the five rounds with their
verdicts and finding counts, the reviewer transport and both model families,
and `packet: published: false` with no locator, because the packets and
verbatims stayed on one machine. Its digest table has one row: the tracked
evidence file the ruling lives in. That digest is redundant with git's own
object hash for a tracked file, and it is kept anyway, so that every receipt
has the same shape and can be checked by a reader with a hash tool and no
git. The receipt is a pointer plus an attestation, which is exactly what the
history supports.

This makes the backfill the format's first proof that driver 2 works: the
R-wave's real evidentiary state is legible from the tracked repo, including
the part that is missing.

### 8. The machine-local pointer pattern, weighed beside S12

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
- Nothing tracked inside boardkit names `docs/adr/` as the ADR home. The
  routing line the S32 pull ruling cites ("ADR / decision-record changes
  (`docs/adr/`, `DECISIONS.md`): run `adr-review`") lives in the
  `gate-probes` skill outside this repo. The ruling stands and this document
  is at that path; what is missing is the in-repo statement of it. Owner:
  a documentation card, or S12 as it works the outsider-facing surface.
- The aura board's cards describe a house `docs/adr/` convention with a
  date prefix, while this board's ruling numbers from 0001. Two families,
  two conventions, no forcing function to reconcile them. Recorded so the
  divergence is deliberate rather than discovered.
- Commit signing would turn several attestations in section 6 into
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

**OQ4. Which gates get a receipt: every gate, or only the ones a reviewer
returns a verdict for.** Decision 2 says "a compact review receipt per
gate", which reads either way. *Recommendation: receipts for gates that
produce a verdict from a named reviewer, being A, F, and a ruling that
closes a cycle, plus U as the decision record.* Gate S is deterministic
command output with no reviewer and no findings ledger, and a receipt whose
model fields are empty would weaken the format's meaning for the gates that
need it. Gates D and M sit closer to the line: both produce a written
judgment, and if either turns out to be what a vetter reaches for, adding it
is a value in an existing field rather than a format change.

## Premises checked against the code

Every claim this ADR makes about existing behavior, verified at `23dea92`
the way `DOCKING.md` was written against the shipped resolver. Re-verify on
revision.

| Premise | Verdict | Anchor |
| --- | --- | --- |
| Packets are gitignored working material, written to `docs/board/reviews/<ID>/` | still true | `.gitignore:6`, `boardkit.toml` `[review] output_dir`, `cli.py:539-548` |
| A packet is `NN-<sha>.diff`, `full-range.diff`, `REVIEW.md`, plus non-regenerable material a rerun does not delete | still true | `review_packet.py:845-851`, `GENERATED_NAMES` at `:85`, `clean_generated` at `:762` |
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
| Nothing tracked in boardkit names `docs/adr/` | changed from the pull ruling's premise | the routing line is in the external `gate-probes` skill; recorded as a named gap |
| The suite and lint are green before this change | still true | `uv run pytest -q` 430 passed; `uv run ruff check` clean |

## Links

- Card [S32](../board/cards/s32-artifact-store-adr.md), this ADR's own card.
- Card [S33](../board/cards/s33-receipts-and-sidecar.md), the
  implementation, which cites this document.
- Card [S34](../board/cards/s34-wave-gate-design.md), the wave-gate decision
  that depends on S32.
- Card [S12](../board/cards/s12-public-repo-seam.md), the public-repo seam
  weighed in section 8.
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
