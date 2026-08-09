---
source: chore-lottery@0b0330e87bf8aca2e059c633665d17603a6be13a:crates/lottery/DESIGN.md
date: 2026-08-09
artifact: doc-draft
note: lottery crate design doc, frozen as cleanup-task input
---

# lottery type design record

Baseline: skeleton commit 9dea1e0 on `card/s7` (card S7), repaired by
the skeleton-repair commit after the design panel failed both seats.
Scope: the draw and return services (process managers spanning the
kid and chore streams) and the ready-pool read model the draw picks
from. The FSM types themselves live in `crates/domain`; the S7
additions to them (draw selections, pool digests on draw commands and
events) are recorded in `crates/domain/DESIGN.md`.

## Placement decision

The card allows a new crate or a merge into `domain`. Both panel seats
ruled AGREE on a new crate: the services own store, read-model, and
entropy seams, and merging would hand `domain` those dependencies.
Confirmed.

## Type inventory

| Type | Business rule | Forbidden invalid state |
|---|---|---|
| `LotteryService` | The only stateful service object; every lottery operation goes through its `&mut self` | A draw and a return interleaving mid-flight (F1) |
| `DrawService` | Stateless namespace: a draw reserves on the chore stream, then the kid stream accepts | A draw reaching the kid stream without a reservation; a second service object to race with |
| `ReturnService` | Stateless namespace: a return frees the holder and restores the card to Ready; only an InProgress card is returnable (F2) | A half-applied return with no recovery path; freeing a kid whose card is in review |
| `DrawSelection` (domain) | A pick is bound to its pool's digest at construction | A draw recording a pool it did not pick from |
| `EntropySource` / `OsEntropy` | Randomness enters through one named seam, scripted in tests | Hidden entropy a test cannot control |
| `ReadyPool` / `SqliteReadyPool` | The draw reads candidates as a validated `DrawPool` from a projection | Duplicates biasing the draw; fold-at-read cost |
| `PoolDelta` / `pool_delta` | Ready membership is a pure, total function of chore events | Incremental and rebuild paths that can disagree |
| `DrawOutcome` | A draw ends in a fresh assignment or the one already held | A retry that draws a second card |
| `DrawError::NoChoresAvailable` | An empty pool is typed, so the kid view can say "all caught up" | A stringly or panicking empty state |
| `DrawError` / `ReturnError` mapped rejections | Callers see only the rejection cases the operation can reach | Tests covering production-unreachable errors |
| `LostRace` (both errors) | A lost optimistic-concurrency race is retryable, never a double assignment | Two cards held by one kid after concurrent draws |
| `Store` / `Inconsistent` variants | Out-of-envelope failures are named; `detail` is diagnostic-only | Callers parsing error strings |
| `ReturnOutcome.freed_kid` | A return frees the holder, or records that nobody held it | Freeing a kid from a card they do not hold |
| `ReturnError::NotInProgress` | Only a held card can be returned | Returning a Ready or Discarded card |
| `KidStreamId` / `ChoreStreamId` | Stream names come only from aggregate ids, one constructor per kind | A kid id naming a chore stream |
| `StreamKind` | Errors name which stream failed | Ambiguous store errors |

## Draw ordering and recovery (panel ruling, repaired)

Chore-first: the chore stream reserves with a version-checked append,
then the kid stream accepts with its own version-checked append.

- A lost race on the reservation applies nothing anywhere: concurrent
  draws never double-assign, however many service instances run.
  Correctness does not depend on instance count (the skeleton's
  single-writer envelope claim was overturned).
- A crash or lost kid-side race leaves an orphan: the card is
  Assigned, the kid stream untouched. Orphans are visible in the
  parent UI's held-time view (S9) and a parent return releases them;
  `return_to_pool` skips the kid side when the kid does not hold the
  card, and `ReturnOutcome.freed_kid` is `None`. The kid stream is
  the authority on what the kid holds, so the skip also covers a kid
  who has since drawn a DIFFERENT card (Gate A finding 1: a same-kid,
  different-card race produces exactly this shape).
- The kid stream is never ahead of the chore stream, so a Working kid
  with a Ready card is unreachable. The idempotent-retry path
  (`reconcile`) only re-reads the held card and reports
  `AlreadyHolds` with the original pool digest from the card's
  `Assigned` event. Anything else is `Inconsistent`, not a panic.

Returns run kid-first (repair-review finding 17). The holder is freed
with a version-checked append; the card then returns to Ready. A crash
between the two leaves the card InProgress with the kid already Idle,
and a repeated parent return completes it while skipping the kid side.
So both half-applied shapes - the orphaned reservation from a draw and
the stranded hold from a return - recover through the same parent
return.

Draws and returns never interleave within a process: every operation
goes through the `LotteryService` facade's `&mut self`, and the
operation namespaces are stateless functions, so no second service
object can exist to race with. A parent return cannot slip between a
draw's reservation and its acceptance.

## Visibility and seam table

| Item reached | Visibility | Decision |
|---|---|---|
| `domain` FSM types and deciders | `pub` | commands and events as defined upstream; no widening |
| Epoch `VersionedEventRepositoryWithStreams` | `pub` trait bound | services are generic over it; in-memory impl in tests, postgres when a later card wires the service |
| `KidStreamId` / `ChoreStreamId` | private module `streams` | the only aggregate-id-to-stream-name path |
| `SqliteReadyPool.conn` | private | all access through `ReadyPool` |
| `ReturnOutcome` fields | private | constructor is crate-internal; accessors public |
| `ReadyPoolError` details | diagnostic-only `String` per operation variant | rusqlite's error type never crosses the seam |

## Decisions

1. Chore-first draw ordering with typed LostRace on both appends
   (panel ruling; see the ordering section). The skeleton's kid-first
   ordering and its parent-re-deriving reconcile were overturned; the
   repair also retired seat 2's finding 4, since no freeing path
   remains that would need a re-derived actor.
2. `DrawService` and `ReturnService` are separate types over the same
   repository seams (panel finding 7): draw and return have different
   ordering, errors, and recovery rules.
3. rusqlite with the bundled feature for the read model: small,
   sync, single-writer; the trait borrows `&mut self` rather than
   wrapping the connection in a lock. Panel seat 1 AGREE.
4. `rand` for `OsEntropy`; tests script `EntropySource` directly.
   Panel seat 1 AGREE.
5. Stream-id newtypes in a private module (panel finding 8, repairing
   the skeleton's raw-`String` helpers). Epoch's impls pin
   `StreamId = String`, so the bound names `String`; every
   construction goes through the newtypes.

## Design panel findings

Panel run 2026-08-04 on skeleton commit 9dea1e0. Seats: adversarial =
codex CLI (gpt-5.6-sol per the run header), logic = rust-reviewer
(gpt-5.5). Author: K3. Both seats differ from the author and each
other. Both seats returned FAIL with blocking findings; repairs landed
in the skeleton-repair commit on `card/s7`. The ledger below merges
and deduplicates; the seat column names every seat that raised the
finding.

| # | Seat | Finding | Disposition |
|---|---|---|---|
| 1 | both | `ready_cards` returned an unbounded `Vec<ChoreCardId>`; duplicates bias the draw | ACCEPTED: the seam returns a validated `DrawPool`; `rebuild` takes one too |
| 2 | adversarial | `ReadyPool` mixed read, apply, and rebuild with equivalence unenforced | PARTIALLY ACCEPTED: the trait stays whole; `ready_cards` and `rebuild` now speak in validated `DrawPool`. Equivalence rests on the pure, total `pool_delta`. The pool is passed `&mut` per call, so no service owns it |
| 3 | adversarial | `DrawError::Kid/Chore` and `ReturnError` admitted production-unreachable aggregate errors | ACCEPTED: mapped to operation-specific variants (`KidNotRegistered`, `InvalidAssignment`, `CardNotReady`, `NotInProgress`) |
| 4 | adversarial | LostRace vs Store undecidable from a `Debug`-only repository error | REJECTED: Epoch's `VersionedRepositoryError` wrapper types the conflict (`VersionConflict`) apart from store failure (`RepoErr`); the fills match on it |
| 5 | adversarial | Kid-first ordering is not atomic; reconcile cases incomplete (competing assignment, repropose, discard) | ACCEPTED: chore-first ordering; the stuck-kid class becomes unreachable and the orphan class is parent-releasable |
| 6 | adversarial | `&mut self` does not hold a single-writer invariant across instances | ACCEPTED: the claim removed; correctness now rests on the version-checked reservation, independent of instance count |
| 7 | adversarial | One coordinator owned two business rules (draw and return) | ACCEPTED: split into `DrawService` and `ReturnService` |
| 8 | adversarial | Raw `String` stream ids in public bounds | ACCEPTED: `KidStreamId`/`ChoreStreamId` newtypes in a private module are the only construction path |
| 9 | adversarial | `ReadyPoolError` exposed branchable `rusqlite::Error` | ACCEPTED: per-operation variants with diagnostic-only `detail` |
| 10 | adversarial | `PoolHash` fields independently constructible across commands and streams | ACCEPTED: `DrawSelection`, constructed only by `DrawPool::select`, feeds both streams; the chore command takes only the digest because the stream address already carries the card |
| 11 | adversarial | `ChoreEvent::Assigned` carried `by: Actor` while production always writes System | ACCEPTED: the field is removed; a non-system assignment is unrepresentable in the event |
| 12 | logic | The card's adversarial concurrent-draw acceptance had no design support | ACCEPTED: fill briefs include two-instance races over shared repositories (same kid; two kids one card), both resolving as typed outcomes |
| 13 | logic | `ReturnError` had no read-model failure mode | ACCEPTED: `ReturnError::Pool` added, documented as land-then-project with rebuild as the recovery |
| 14 | logic | Parent-actor re-derivation was convention, not type | SUPERSEDED: chore-first ordering removed every freeing path that needed a re-derived actor (finding 5's repair) |

Repair re-review 2026-08-04 (seat 2, rust-reviewer/gpt-5.5, over the
skeleton-repair diff): rows 1-9, 11, 13, 14 verified IMPLEMENTED; rows
10 and 12 NOT IMPLEMENTED; one new blocking finding. Verdict FAIL;
the second repair commit closes all three:

| # | Seat | Finding | Disposition |
|---|---|---|---|
| 15 | logic | `DrawSelection` derived `Deserialize`, so serde rehydration forged selections around the constructor | PARTIALLY ACCEPTED: `KidCommand` and `DrawSelection` drop serde entirely, closing the forge path on the selection. `ChoreCommand` keeps its derives because the Vikunja intake decision embeds it (S6's seam); its `Assign` carries only the fixed-shape-validated digest, no production path round-trips a command through serde before executing it, and `Assign` never arrives via intake |
| 16 | logic | Row 12's race coverage existed as a ledger sentence, not a test contract | ACCEPTED: the test contract below enumerates the required tests; fill briefs must name the rows they close |
| 17 | logic | Chore-first return could strand a Working kid with a Ready card after a crash | ACCEPTED: returns run kid-first; the stranded shape becomes a card held by a freed kid, which a repeated parent return completes |

## Adversarial review findings (2026-08-04, codex route, gpt-5.6-sol)

A fresh adversarial pass over the full post-Gate-A range returned FAIL
with five blocking findings. Dispositions:

| # | Finding | Disposition |
|---|---|---|
| F1 | A draw mid-flight can race an orphan return into a Working-kid/Ready-card split | ACCEPTED: `LotteryService` is the only stateful object and every operation goes through its `&mut self`; `DrawService`/`ReturnService` are stateless namespaces, so no second service object exists to race with (re-review round: public constructors would have left the interleave representable, so the restructure removes instances entirely). Cross-process fencing is deferred to the card that introduces multi-instance serving; recorded as a residual risk |
| F2 | `return_to_pool` accepted InReview/Done cards (the `ChoreState::assignment` accessor covers them), freeing the kid before the chore side rejected | ACCEPTED: only `ChoreState::InProgress` is returnable; every other state is `NotInProgress` before the kid stream is touched. Regression test T13 |
| F3 | The projection is idempotent only for in-order redelivery; no stream versions are stored | PARTIALLY ACCEPTED: the delivery contract (in-order per stream, at-least-once, single-process application, rebuild on start) is now stated on the `ReadyPool` trait; duplicate-delivery test T14 added. Versioned, checkpointed projections are S16's scope, noted on that card |
| F4 | T1 scripted both racers to the same card, so only the chore-stream CAS was exercised | ACCEPTED: T1 now scripts distinct cards so the kid-stream guard is the thing under test; full card-stream accounting and orphan release included |
| F5 | T3 rolled 0 over a shrinking pool, proving nothing about distribution | ACCEPTED: T3 now drives stratified rolls over a fixed pool through `DrawPool::select` and asserts every candidate is selectable |

## Test contract

The fills owe these tests; each fill brief names the rows it closes.
All run against cloned, shared in-memory Epoch repositories (clones
share stream state, so separate service instances race for real).

| # | Test | Closes |
|---|---|---|
| T1 | Same-kid concurrent draws from two `DrawService` instances: exactly one `Drawn`; the loser sees `LostRace` or `AlreadyHolds`; the kid holds exactly one card | Card acceptance: adversarial one-active invariant |
| T2 | Two kids, one-card pool, concurrent draws: one `Drawn`, one `LostRace` on the chore stream; the loser's kid stream is untouched and can redraw | Card deliverable 1 atomicity |
| T3 | Distribution sanity over seeded fixtures: every pool card is drawable across enough scripted rolls (smoke, not statistical proof) | Card deliverable 5 |
| T4 | Empty pool: `NoChoresAvailable` | Card deliverable 2 |
| T5 | Pool exhaustion across multiple kids: every card held by exactly one kid; the next draw reports `NoChoresAvailable` | Card deliverable 5 |
| T6 | Orphaned reservation (simulated crash between the appends): `return_to_pool` returns `freed_kid: None` and the card re-enters the pool | Finding 5 repair |
| T7 | Return happy path: the holder is freed and the card re-enters the pool, with events naming the parent and reason | Card deliverable 3 |
| T8 | Idempotent redraw: a second draw returns `AlreadyHolds` with the original pool digest | `DrawOutcome` row |
| T9 | `rebuild` after replaying the full event history equals incremental `apply` of the same history | `pool_delta` row |
| T10 | Every draw event records the pool digest it picked from, on both streams, and the digests agree | Card deliverable 4 |
| T11 | Orphan release while the kid holds a different card: `freed_kid: None`, the orphan re-enters the pool, the kid's real assignment is untouched | Gate A finding 1 |
| T12 | `ready_cards` returns canonical order regardless of insertion order, so the audit digest is canonical for a candidate set | Gate A finding 2 |
| T13 | Returning an InReview card is `NotInProgress` and neither stream moves | F2 |
| T14 | Duplicate `apply` of the same event changes nothing | F3 |

## Gate A findings

Gate A round 1 (rust-reviewer/gpt-5.5, 2026-08-04, over packet range
9bb9968..3c6f9a9): FAIL, two findings. Resolutions landed in the
Gate A fix commit; a fresh review of that commit closes the round.

| # | Finding | Resolution |
|---|---|---|
| A1 | A same-kid, different-card race strands the second card: `return_to_pool` reported `Inconsistent` when the kid held another card, so the orphan was unreleasable | The orphan skip now covers a kid holding a different card (the kid stream is the authority on what the kid holds); T11 tests the release |
| A2 | `ready_cards` read rows without `ORDER BY`, so the pool digest was not canonical for a candidate set | `ORDER BY card` at the seam; T12 pins canonical order and digest |

## Skeleton holes

| Hole | Marker | Filled by |
|---|---|---|
| `pool::pool_delta` | `filled by S7` | S7 fill: read model |
| `pool::SqliteReadyPool::open` | `filled by S7` | S7 fill: read model |
| `pool::SqliteReadyPool::in_memory` | zero-parameter hole, unmarked | S7 fill: read model |
| `SqliteReadyPool` `ReadyPool` impl (3 methods) | `filled by S7` | S7 fill: read model |
| `coordinator::DrawService::draw` | `filled by S7` | S7 fill: draw path |
| `coordinator::DrawService::reconcile` | `filled by S7` | S7 fill: draw path |
| `coordinator::ReturnService::return_to_pool` | `filled by S7` | S7 fill: return path |

`DrawPool::select` is implemented, not a hole: it is the binding
guarantee behind `DrawSelection`, two lines over already-filled
domain functions. Module-level `#![allow(dead_code)]` at crate root:
removed slice by slice as fills land; the last fill unit flips
`clippy::todo` to deny in this crate's lint config.

## Residual risks

- Cross-process draw-vs-return interleaving is out of envelope: the
  `LotteryService` facade serializes per process and v1 deploys one
  process. Multi-instance serving needs store-level fencing first
  (F1); the deferral is recorded here and on the S8 card's radar via
  the board.
- Orphaned reservations (card Assigned, kid stream untouched) wait
  for a parent return; the parent UI's held-time view (S9) is what
  makes them visible. Accepted for v1 family scale.
- The ready pool is eventually consistent with the chore streams by
  one process boundary: services append events, then apply them to
  the pool. A crash between leaves the pool stale until the next
  `rebuild`; v1 rebuilds on service start. A `Pool` error after a
  landed command is documented on the error variants (rebuild, do
  not retry).
- `DrawSelection` has no serde surface at all (repair finding 15):
  commands are constructed in-process and never rehydrated, so the
  card-pool binding has no forge path. Event payloads rehydrate from
  the store under the accepted store-trust class.
- A stranded hold (card InProgress, kid already Idle from a crashed
  return) waits for a repeated parent return, exactly like an
  orphaned reservation. Accepted for v1 family scale.
