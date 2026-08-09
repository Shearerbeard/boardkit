---
source: chore-lottery@0b0330e87bf8aca2e059c633665d17603a6be13a:crates/domain/DESIGN.md
date: 2026-08-09
artifact: doc-draft
note: domain crate design doc, frozen as cleanup-task input
---

# domain type design record

Baseline: skeleton commit on `main` (card S4). Scope: the
whole `domain` crate - chore FSM, kid aggregate, lottery, AI audit
trail, Vikunja sync types. Coverage ledger: none yet (lands with S5's
MANIFEST.md).

## Type inventory

| Type | Business rule | Forbidden invalid state |
|---|---|---|
| `ChoreState` | A card is in exactly one FSM lane | Two lanes at once; payload from the wrong lane (augment data on a Proposed card) |
| `ChoreCore` | Every live card has a title and a Vikunja task id | A card with no upstream anchor |
| `ProposedChore.augment_rounds` | Augment loop caps at 3 before flagging a parent | Unbounded AI retry |
| `AugmentedChore.feedback` | Every rejection note is kept for the next round | Silent loss of parent feedback |
| `ReadyChore.approved_by` | Ready requires a parent action, never AI | Auto-promoted card |
| `InProgressChore.assignment` | An in-progress card knows its kid | Orphaned work |
| `InReviewChore.submission` | Review requires submitted evidence | Empty review |
| `ChoreCommand` / `ChoreEvent` | Every lane change is an explicit, actor-stamped, stream-stamped decision | Untracked mutation |
| `StateKind` / `CommandKind` | Errors name states without carrying their data | Payload leaking into error types |
| `ChoreError` | Callers can react to illegal transitions and loop exhaustion | A bare string error |
| `KidStatus` | A kid is Idle, Working, or AwaitingReview - draw legal only from Idle | Two active chores per kid |
| `KidProfile.token` | A kid's QR identity is a rotatable token | Shared/duplicated kid identity |
| `Assignment` | The kid-card link records when and due | Assignment without provenance |
| `Submission` | Work needs at least one photo | Unverifiable "done" |
| `Lottery::draw` | Pick is uniform to within the Lemire mapping's len/2^64 bias and deterministic on a seed for tests | Untestable randomness |
| `DrawPool.audit_hash` | Draw events can prove the candidate set | Unverifiable fairness |
| `AiActionRecord` | No AI output exists without model, prompt version+hash, verdicts | Unauditable AI action |
| `JudgeVerdict` / `JudgeCheck` | Validation checks are named, per-check | A single opaque pass/fail |
| `AugmentPayload` | Steps non-empty, graphic present, video optional, grade recorded | Video-mandatory blocking; advice-less card |
| `ModelId` | Only named models write events | "some model" in the audit trail |
| `ChoreTitle`/`WorkNotes`/`StepText`/etc | Text crossing the boundary is non-empty and bounded | Unbounded/blank domain text |
| `KidLabel` | Vikunja label is always `kid:<slug>` | Freeform labels parents can't read |
| `ReadingGrade` | Grade is 0..=12 | Nonsense grade values |
| `VideoUrl` | Only https URLs | javascript:/file: links reaching kids |
| `Lane` | Exactly six lanes with canonical names | Lane name drift vs Vikunja buckets |
| `BotIdentity` | Echo suppression is a comparison, not a convention | Processing our own writes as commands |
| `VikunjaEventKey` | At-least-once delivery is deduplicated | Double-applied webhook |
| `IntakeDecision` | Every gesture resolves to accept, ignore, or revert | Ambiguous gesture handling |
| `LaneMap` | Lane<->bucket mapping is per-board and total | Moves into unmapped buckets |
| `VikunjaProjectionOp` | Every outbound write is bot-attributable | Untraceable board mutation |
| `Actor` / `ParentActor` | Every event names who caused it; parent-gated transitions require a parent | Kid or system approving work |
| `AugmentHistory` | Round count and feedback survive the reject cycle | Lost retry state across Proposed<->Augmented |
| `PromptTemplateVersion` | Prompt files are versioned; events name the version | Unversioned prompt in the audit trail |
| `PromptHash` / `PoolHash` / `PayloadFingerprint` | Hashes come from hash fns as fixed-shape newtypes | Hand-typed "hash" accepted as real |
| `VideoConfidence` / `VideoCandidate` | Video picks carry a confidence the parent sees | Silent low-quality video |
| `AiActionKind` | Augment, AskAi, and JudgeRun records are distinguishable | Mislabeled audit records |
| `AugmentInput` | RecordAugment pairs only Augment-kind records with payloads | AskAi record + payload combination |
| `DueDate` / `Assignment` | Due dates sit after draw time (fallible constructor) | Contradictory assignment timeline |
| `AssetRef` | Stored-asset references are non-empty opaque paths | Blank asset links |
| `KidState` / `KidCommand` / `KidEvent` | Kid lifecycle mirrors the card FSM from the kid side | Kid state drifting from card state |
| `DiscardReason` / `PoolReturnReason` | Terminal/return causes are enumerated | Unexplained card disappearance |
| `ParentGesture` / `VikunjaEventKind` | Intake sees only attributed, typed gestures | Anonymous or shapeless intake |
| `TextError`/`ChoreError`/`KidError`/`PhotoError`/`StepsError`/`AiActionError`/`LaneMapError`/`PoolEmpty`/`UnknownLane`/`NotAJudge`/`NotAnAugmentRecord`/`AboveReadingTarget`/`BiasedPool`/`DueBeforeDraw` | Error paths carry typed causes a caller can branch on | Panic or stringly failure |

`Evolver`/`Decider`/`Event` (reused from Epoch): owned upstream.

## Visibility and seam table

| Item reached | Visibility at baseline | Decision |
|---|---|---|
| Epoch `decider::{Decider, Evolver, Event}` | `pub` | implemented directly by `ChoreDecider`, `KidDecider` |
| All state struct fields | private | read via accessors or moved as whole values by the deciders |
| `uuid`/`url`/`time` types | `pub` | wrapped in newtypes; raw forms only inside constructors |

No production visibility was widened.

## Skeleton holes

| Hole | Marker | Filled by |
|---|---|---|
| `chore::ChoreDecider::decide` / `evolve` | filled 2026-08-03 | S5 |
| `chore::ChoreEvent::get_id` | filled 2026-08-03 | S5 |
| `kid::KidDecider::decide` / `evolve` | filled 2026-08-03 | S5 |
| `kid::KidEvent::get_id` | filled 2026-08-03 | S5 |
| `text::KidLabel::from_display_name` | filled 2026-08-03 | S5 |
| `text::VideoUrl::parse` | filled 2026-08-03 | S5 |
| `ai::PromptHash::of_rendered` | filled 2026-08-03 | S5 |
| `ai::AiActionRecord::new` | filled 2026-08-03 | S5 |
| `lottery::DrawPool::audit_hash` | filled 2026-08-03 | S5 |
| `lottery::Lottery::draw` | filled 2026-08-03 | S5 |
| `vikunja::LaneMap::new` | marker `filled by S6` | S6 |
| `vikunja::LaneMap::bucket_for` / `lane_for` | implemented at skeleton (real bodies, no behavior hole) | - |
| `vikunja::PayloadFingerprint::of_body` | filled 2026-08-03; an orphan hole the ledger missed, caught by Gate A | S5 |

Module-level `#![allow(dead_code)]`: removed 2026-08-03 with the S5
fills. `clippy::todo` stays at workspace warn while the S6 lane-map
holes stand; S6 flips the crate to deny as its own close.

## Fill-phase repairs (S5)

- 2026-08-03 Event stream ids. Epoch's `Event::get_id` is how the
  repository derives an event's stream (`StreamIdFromEvent`,
  `strategies/mod.rs`), so every event must carry its entity id. The
  S4 skeleton's events mostly did not: only `Proposed` named its card
  and only `Registered` / `ChoreDrawn` named their kid. `get_id` was
  unfillable as skeleton'd - a skeleton defect the panel missed,
  caught at the first fill. Repair: every `ChoreEvent` variant now
  carries `card: ChoreCardId` (`AugmentRecorded` becomes a struct
  variant with `input: Box<AugmentInput>`); every `KidEvent` variant
  carries `kid: KidId` (`Registered` and `ChoreDrawn` read it from
  `profile` / `assignment` and stay unchanged). Additive payload
  fields on pre-persistence events; no type removed or narrowed.
  Approved by the board owner under the card's fills-only scope rule
  as a skeleton repair, logged on S5, and surfaced at the card's
  U(code-review) gate.
- 2026-08-03 Two additive `KidError` variants. The skeleton's error
  enum had no honest rejection for a second `Register`
  (`AlreadyRegistered`) or for a draw whose due date fails the
  `Assignment` constructor (`InvalidAssignment`). Both are additive
  variants; no existing variant's meaning changed. Same approval and
  surfacing as the event-id repair above.
- 2026-08-03 `KidStatus::AwaitingReview` retains the draw time
  (`since`), so `ChoreRejectedBackToWork` restores the work period
  exactly as the chore stream still sees it. An earlier version set
  `since` to the submission's timestamp; Gate A showed that diverges
  the mirror after a rejection (the kid stream refused resubmissions
  the chore stream would accept). Additive state field; events are
  unchanged.
- 2026-08-03 Gate A remediation round (codex review FAIL, ledger on
  the S5 card). Changes beyond straight fills:
  - Parent-driven kid commands (`Register`, `RotateToken`,
    `MarkApproved`, `MarkRejected`, `MarkReturned`) and their events
    now carry `by: ParentActor`; the type inventory's actor row
    already demanded it and the skeleton's kid aggregate did not.
  - `StepsRequired` / `PhotoRequired` became the `StepsError` /
    `PhotoError` enums, gaining caps (steps at most 8, photos at most
    10) per panel finding 14's recorded fill-time rule.
  - `RecordAugment` binds the record's claimed iteration to the
    card's next round, rejected with the additive
    `AugmentIterationMismatch` error.
  - `SubmitWork` rejects a kid other than the assigned one with
    `IllegalTransition`.
  - `PromptHash` and `DrawPool::audit_hash` pin FNV-1a (new internal
    `digest` module): `DefaultHasher` documents no stability contract
    and these hashes persist in the audit trail.
  - The constrained-deserialization convention now covers every
    bounded text type, `KidDisplayName`, `KidLabel`, and `AssetRef`;
    `KidLabel` gained a `parse` constructor for it.
  - `Lottery::draw` lost its speculative index fallback.
  - Second remediation round, after the re-review returned FAIL:
    the exhaustion check now runs before the iteration binding (a
    record cannot claim iteration 4, so the old order made exhaustion
    unreachable); the deserialize-through-constructor sweep now
    covers the composite types (`ChoreSteps`, `Submission`,
    `Assignment`, `AugmentPayload`, `AugmentInput`, `JudgeVerdict`,
    `AugmentHistory`, `DrawPool`, `AiActionRecord`, and the three
    digest newtypes in their fixed shape); `KidLabel::parse` enforces
    the canonical lowercase slug and bound; `Lottery::draw` uses
    Lemire's multiply-shift mapping with the residual bias accepted
    here in writing; chore evolve arms guard on the event's card (and
    the submitter's kid); the illegal-transition coverage is the full
    7-by-11 chore matrix plus the kid command matrix, both with the
    uninitialized rows.
  - Third remediation round: the kid decider mirrors the chore
    stream's submission guard (`StaleSubmission`, additive); the
    discard-from-every-state fixture verifies event fields and the
    fold, not just the event type; serde probes pair every refusal
    with a valid round-trip; the kid decider's status matches spell
    every variant so a future status fails exhaustiveness rather than
    inheriting an error.

## S7 skeleton additions (2026-08-04)

Additive payload fields on pre-persistence events, same class as the
2026-08-03 event-id repair. Ruled on by the S7 design panel (ledger
in `crates/lottery/DESIGN.md`); surfaced at the card's
U(code-review) gate:

- New type `DrawSelection` (lottery.rs): a draw's pick bound to its
  pool's digest, constructed only by `DrawPool::select`, so a draw
  cannot record a pool it did not pick from.
- `KidCommand::DrawChore` takes the `DrawSelection`;
  `KidEvent::ChoreDrawn` carries `pool: PoolHash` alongside the
  assignment.
- `ChoreCommand::Assign` carries `pool: PoolHash`; the card is the
  stream's own, so the command does not repeat it.
- `ChoreEvent::Assigned` carries `pool: PoolHash` and LOSES its
  `by: Actor` field (panel finding 11): the draw service is the only
  author, so a non-system assignment is unrepresentable in the event.
- `KidCommand` loses its serde derives (repair finding 15): kid
  commands are constructed in-process and never rehydrated, so a
  `DrawSelection` inside one has no forge path. `ChoreCommand`
  keeps its derives: the Vikunja intake decision embeds it (S6's
  seam), and nothing round-trips a command through serde before
  executing it.
- `ChoreState::assignment` accessor added: the lottery services read
  the holding kid and draw provenance without widening field
  visibility.

Golden snapshots covering the draw and assign frames are red on
arrival by design (Layer 2); the S7 fill units re-accept them under
review.

## Design panel findings

Panel run 2026-08-02 on skeleton commit 35c3493. Seats: adversarial =
codex CLI (GPT-5 class), logic = rust-reviewer (Kimi-K2.7-Code).
Author: K3. Both seats differ from the author and each other. Both
seats returned FAIL with blocking findings; repairs landed in the
skeleton-repair commit on `card/s4`. Findings from the two seats are
merged and deduplicated; the seat column names every seat that raised
the finding.

| # | Reviewer | Finding | Disposition |
|---|---|---|---|
| 1 | logic | No InProgress -> Proposed edit path; FSM cannot express re-propose | ACCEPTED: added `Repropose` command + `Reproposed` event; assignment ends on repropose |
| 2 | logic | ReadingGrade permitted grades above the kid target | ACCEPTED differently: ReadingGrade stays a 0..=12 measurement scale; the target moved to `AugmentPayload::new`, which rejects grade > 3 with `AboveReadingTarget`. A measurement type should not encode one consumer's policy |
| 3 | both | Parent-only transitions accept `Actor::Kid`/`System` | ACCEPTED: `ParentActor` newtype; approve/reject/repropose/return/discard all require it |
| 4 | both | Propose/RecordAugment/Assign/SubmitWork lack actor stamps | ACCEPTED: `by` fields added (ParentActor on Propose, KidId on SubmitWork, Actor on Assigned; RecordAugment is System by construction and its AiActionRecord carries the model) |
| 5 | adversarial | Retry state (rounds, feedback) cannot survive Augmented -> Proposed | ACCEPTED: `AugmentHistory` shared by ProposedChore and AugmentedChore; `record_round` enforces the 3-round cap |
| 6 | adversarial | Derived Deserialize bypasses validated constructors | ACCEPTED as convention: constrained scalar types deserialize through their parsing constructors (done for ReadingGrade, VideoUrl; convention recorded in skeleton-conventions for S5 to apply crate-wide) |
| 7 | adversarial | ID types admit production-impossible values (negative Vikunja ids, nil UUIDs) | REJECTED: Vikunja ids are opaque upstream values; validation would break sync on data we do not own. UUID newtypes rehydrate from our own store; a nil there is corruption, not a domain value. Recorded as residual risk |
| 8 | adversarial | QrToken cannot forbid two kids sharing a token | ACCEPTED as documentation: uniqueness is a store concern (unique index in the kid registry, S7/S9); type inventory row updated to name the enforcement boundary |
| 9 | adversarial | Assignment admits due-before-draw | ACCEPTED: `Assignment::new` is fallible with `DueBeforeDraw`; submission-after-draw is a decider rule noted for S5 goldens |
| 10 | adversarial | Non-judge models can issue verdicts; Augment records may lack verdicts | ACCEPTED: `JudgeVerdict::new` rejects non-judge models (`NotAJudge`); `AiActionError::VerdictsRequired` added for Augment-kind records |
| 11 | both | AugmentInput pairs any record kind with a payload; fields public | ACCEPTED: fields private; `AugmentInput::new` is fallible with `NotAnAugmentRecord` |
| 12 | both | LaneMap neither total nor bijective | ACCEPTED: six named fields make totality structural; `LaneMap::new` rejects duplicate buckets; `bucket_for` total, `lane_for` returns Option for foreign buckets |
| 13 | adversarial | DrawPool permits duplicate cards (biased draw); audit hash is a raw String | ACCEPTED: `DrawPool::new` rejects duplicates (`BiasedPool`); `PoolHash` newtype |
| 14 | adversarial | Bare primitives and unbounded Vecs cross the boundary | PARTIALLY ACCEPTED: Epoch's trait shapes (`Vec<Evt>` returns, `event_type() -> String`) cannot change without an Epoch upgrade - recorded as an Epoch candidate for the retro scratchpad. `TextError::TooLong.max` is diagnostic of the bound. Collection caps (photos, steps) are fill-time rules recorded for S5 |
| 15 | adversarial | VikunjaEventKey fingerprint is an unconstrained String | ACCEPTED: `PayloadFingerprint` newtype from `of_body` only |
| 16 | adversarial | Serde variant names differ from canonical display names | REJECTED: the wire format's requirement is stability, not display parity; variant-name serialization IS the stable format. Display names are for humans only (Lane::as_str pins the Vikunja bucket names) |
| 17 | adversarial | DESIGN.md did not map every public type | ACCEPTED: inventory expanded with the missing rows |
| 18 | logic | ChoreState has 7 variants but Lane claims six lanes | ACCEPTED as documentation: DESIGN wording fixed to "exactly one FSM state"; Discarded is terminal, not a lane |
| 19 | logic | PoolReturnReason::KidUnavailable is not in the spec | REJECTED: it encodes grill answer B9 (2026-08-02): parent throws a card back when the kid cannot do it now |
| 20 | logic | DiscardReason::Duplicate/Stale are synthetic | REJECTED: parents deleting duplicate or stale cards are the two real discard paths beyond plain choice; documented on the variants |
| 21 | logic | ChoreCore lacked title/notes accessors | ACCEPTED: added |

Gate U outcome: the user reviewed and approved these dispositions on
2026-08-02, closing S4 (domain skeleton). The repairs above are final;
the residual risks below are the accepted remainder.

## Residual risks

- Vikunja/UUID identifier values are opaque (panel finding 7): a
  negative upstream id or nil UUID is storable. Accepted: invariants
  we do not own cannot be enforced at our boundary; corruption would
  surface as sync mismatches in S6's integration tests.
- QrToken uniqueness lives in the kid registry store (unique index),
  not the type (panel finding 8). Accepted: S9's registry owns it;
  the test plan there must cover rotation and collision.
- Constrained scalar deserialization through parsing constructors is
  applied to ReadingGrade and VideoUrl; the crate-wide sweep for the
  bounded text types lands with S5's fills (convention recorded).
  Accepted: skeleton scope is type surface; the sweep has a gate.
- One-active-per-kid is enforced per kid stream, but the draw spans
  two aggregates (kid accepts, then card assigns). A crash between
  the two writes leaves kid Working with the card still Ready; the
  DrawCoordinator (S7) must reconcile. Accepted: process-manager
  pattern is the designed answer; S7's adversarial test covers it.
- `Submission` mandates photos. If a chore legitimately has no
  photographable result, parents cannot waive it in v1. Accepted:
  B6 decision said photos; panel did not overturn.
- `VikunjaEventKey` dedupes by body fingerprint; a poll-backstop read
  of the same state produces a different key shape than the webhook.
  Accepted: S6 owns reconciling the two intake paths' keys.
