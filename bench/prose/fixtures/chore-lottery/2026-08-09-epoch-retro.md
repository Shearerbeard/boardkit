---
source: chore-lottery@0b0330e87bf8aca2e059c633665d17603a6be13a:docs/board/retro/2026-08-04-epoch-friction-retro.md
date: 2026-08-09
artifact: doc-draft
note: epoch friction retro, frozen as fresh-write source
---

# Epoch friction retro: S7 wave (chore-lottery)

Date: 2026-08-04
Consumer: chore-lottery, card S7 (lottery service), coordinator built
directly on epoch branch `s3/postgres-repository` (feature
`in_memory`). Author: board owner kimi-for-coding/k3. Maintainer
audience: this retro is written for the Epoch maintainer; proposals
are marked R1..R5 and referenced from the S19 card.

## What Epoch gave us, and what we kept

The S7 coordinator binds Epoch's patterns directly and the design
rests on three of them:

1. `Decider`/`Evolver`/`Event` with `event_type()` and `get_id()`:
   stream-per-aggregate fell out of `get_id`, and the decider/
   evolver split kept the FSM pure. This surface needed no
   workaround.
2. `VersionedEventRepositoryWithStreams` plus `RepositoryVersion`:
   the version-checked `append` is the primitive draw atomicity
   rests on. `VersionedRepositoryError::VersionConflict` vs
   `RepoErr` is a typed, branchable race signal - a design-panel
   finding that claimed races were undecidable was REJECTED by
   citing exactly this wrapper. This is the strongest part of the
   API.
3. The in-memory repository's Clone-with-shared-stream-state: it made
   honest multi-instance race tests possible (two service namespaces
   over cloned repos racing one kid stream). Keep this capability;
   the semantics need to be *documented* (R4), not changed.

## Friction, with evidence and cost

### E2: stream identifiers pinned to `String` (your fix: generics)

Every repository impl fixes `type StreamId = String`. The consumer
wants typed ids (`KidStreamId`, `ChoreStreamId`) so a kid id can
never name a chore stream. The workaround in S7: newtypes in a
private module, `into_string()` conversion at every load/append call,
and the trait bound itself carrying `StreamId = String`. The
coordinator's generic bounds became the single ugliest surface in
the crate, and the conversions are pure boilerplate.

Proposal R2: make the impls generic over the stream id, e.g.
`impl<E, S> VersionedEventRepositoryWithStreams<...> for
InMemoryEventRepository<E, S>` with `type StreamId = S` (defaulting
to `String` via a `S = String` default so existing users do not
churn). The postgres impl would bind its natural id type the same
way. Consumers then write `StreamId = KidStreamId` in bounds and the
conversion layer disappears.

### E1: sharing a store requires Clone with subtle semantics (your fix: clone bounds)

`append` takes `&mut self`, so two service instances over one store
need clones. `InMemoryEventRepository` derives `Clone`, but the
semantics are subtle: the per-stream-entry `HashMap<String,
Arc<Mutex<State>>>` is cloned by VALUE, while each stream state is
shared. A caller can clone the map while sharing streams and never
notice from the type. S7's facade constructor had to carry `Kids:
Clone, Chores: Clone` bounds, and the review chain spent one round
on whether sharing semantics held. The S7 wave eventually made the
services stateless namespaces with `&mut` repo parameters - which
works, but only because of the audience's discipline.

Proposal R1: give the in-memory store ONE `Arc<Mutex<...>>` covering
the whole map (a `shared()` constructor or a
`Clone`-is-`same-store` contract), and document that contract on the
type. Alternative worth weighing: interior mutability on `append`
(`&self`) so sharing needs no `Clone` at all; that changes the
trait's mutability story, so the doc-first route is the cheaper fix.

### E3: the trait carries a lifetime parameter

`VersionedEventRepositoryWithStreams<'a, E, Err>` forces
`for<'a> ...` HRTB at every consumer bound, plus the
`'a: 'async_trait` clauses in the method where-bounds. This is
legacy of the async_trait-on-trait recipe. Cost: every coordinator
method signature carries the HRTB noise; fill executors tripped over
it repeatedly.

Proposal R3: make the trait lifetime-free. If the async-trait-macro
generation requires the parameter today, a GAT-based or
erased-lifetime design would remove `for<'a>` from every consumer
bound. Lower-priority than R1/R2, but the highest UI cost per line
of consumer code.

### E4: version semantics are undocumented

`load` on a missing stream returns `Exact(0)`; `load_from_version`
with `Any` reads from index 0; `NoStream`/`StreamExists` exist but no
consumer uses them, and precedence with `Exact` is undocumented.
None of it bit us, but two reviewers independently asked what the
semantics were. One doctest per variant would have closed both.

Proposal R4: document version semantics with a doctest proving
that two clones over one stream still honor the version check on
append. One doctest would have prevented a full review round in the
S7 wave.

### E5: postgres backend untested by consumers

The S7 wave ran against `in_memory` only; the adversarial review
filed "production Postgres repository behavior and integration" as
UNVERIFIED, and the coordinators' bounds assume the postgres impl
keeps `Version = usize`-compatible semantics. The postgres repo will
not be exercised until the S6 sync card wires it to the seeded
stack. That is early for a repository backend shipping in branch
form.

Proposal R5: S3's postgres branch should carry a consumer-shaped
smoke test (append/load/version-conflict round-trip against a real
database, runnable via docker compose) so the branch's claims can be
verified without a consumer project. Chore-lottery's S6 integration
tests will exercise it end to end regardless.

## Cost to the wave

Roughly a tenth of the coordinator's bulk is Epoch-boundary
machinery (HRTB bounds, stream-id conversions, error-wrapper
mapping) rather than domain logic. Two review rounds in the S7 chain
carried Epoch-shape workarounds in their bills (the facade Clone
bounds; the HRTB where-clause corrections). None of the friction
blocked the card; all of it was absorbed.

## What to fix first (maintainer's list, in order)

1. R1 clone semantics (document, then optionally restructure).
2. R2 generic stream ids (the user's ask; highest consumer payoff).
3. R4 version-semantics doctests (cheapest, closes a reviewer loop).
4. R3 lifetime-free trait (highest per-line cost).
5. R5 postgres smoke test (branch credibility).

## Human notes

Left for the user.
