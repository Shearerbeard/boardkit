# Feedback drain: seven inbox entries vetted and prioritized (2026-08-03)

Status: triaged 2026-08-03 by a maintainer session. This file is the
durable record for the seven `FEEDBACK.md` entries drained on this date;
the queue entries themselves are deleted per the inbox contract. Each
disposition below was verified against the tree at `2d16da4`, not taken
from the entry's own claims. Implementation of the accepted items runs
under plan-discipline as its own wave; this document is the triage
record and the backlog, not the implementation design.

## Verification notes

- The wave-close documentation bus test the first entry asked for exists
  in the shipped template (`src/boardkit/data/templates/PROCESS.md`,
  "Wave close: documentation bus test").
- Deferral clearing keys on the checkbox tick, exactly as the fifth
  entry claims: `board.py` `deferred_gates()` clears a deferral only
  when a matching checklist box is ticked, while the PROCESS Deferrals
  section calls the log line "the only shape boardkit reads as a
  deferral". Both statements are true (one records, one clears), but the
  prose does not say so, and a session satisfied the written rule while
  leaving a phantom deferral open.
- The generated dispatch brief (`brief.py`) quotes the card, the routes,
  and the contract clauses; nothing in it tells a reviewer how to treat
  a check its sandbox cannot run. The sixth entry's gap is real.
- `vale` over the shipped templates today: two `ai-tells.VerbTricolon`
  hits, both in `PROCESS.md` (lines 165 and 328);
  `REVIEW-TOOLING.md.template` is clean in the current tree. The seventh
  entry claimed three spans across the two files; the count has moved
  but the finding stands, and nothing gates the kit's own templates on
  the prose standard the templates impose on consumers.
  [Correction, recorded during the implementation wave's stage 1
  review: the "clean" reading of `REVIEW-TOOLING.md.template` was
  vacuous - vale skips `.template` files without a format mapping, so
  this drain never linted it. With the mapping in place the file shows
  two more spans, four total across the two files, so the entry's
  count was closer to right than this note claimed.]
- The REVIEW-TOOLING template already carries a stall protocol
  (caller-owned `timeout`, switch-tools-on-stall, empty-return-is-fail)
  and the opencode staging rule (`.review/` inside the working
  directory). The fourth entry's remaining gap is that the codex
  contract is the *opposite* (repo-trust, so staged packets outside a
  git repo hang), that no route carries its staging contract, and that
  the mandated pre-vet is an echo test that proves nothing about read
  access.

## Priority 1 - silent-failure class

### D1. Transport staging contracts and a contract-shaped pre-vet

From `2026-08-03 adversarial-review-transport-contracts`
(terminalbench-aura, two codex stalls of 17 and 10 minutes with empty
output around a passing echo pre-vet). Accepted in three parts, sized as
one wave:

1. The `[routes.<slug>]` schema in `boardkit.toml` gains a
   `staging` field stating the transport's read contract -
   `working-dir` for opencode's stage-into-`.review/` shape,
   `repo-native` for codex's cwd-at-the-repo shape - and
   `resolve-route` and `dispatch-brief` print it with the route. The
   contract stays strict both ways, and the contract version bumps per
   the topology-hardening skew rule.
2. The pre-vet recommendation in the MODEL-CLASSES and REVIEW-TOOLING
   templates changes dimension: a read probe shaped like the dispatch
   (the reviewer reads one staged or repo-native file and echoes a
   nonce from its content) replaces the bare echo, which proved
   liveness of the wrong layer.
3. The stall protocol gains a liveness convention for dispatched
   reviews: an output heartbeat or CPU check under the caller-owned
   deadline, bounded retry-then-switch, so a stall is detected by the
   harness rather than by the user asking.

### D2. Deferral clearing: say what clears, warn on the phantom

From `2026-08-03 deferral-clearing-exact-match` (chore-lottery, a
passing Gate A log line left `deferred.md` non-empty until a second
edit added the bare tick). Accepted in two parts:

1. Doc fix: the PROCESS Deferrals section states the full cycle - the
   log line records a deferral, the checklist tick clears it - so the
   written rule matches what `deferred_gates()` reads.
2. `boardkit check` warns when a card has a deferral log line for a
   gate, a later log line recording that gate as passed, and an
   unticked box for it. Scoping caveat the implementer must honor: the
   board mechanics allow phase-scoped interim passes as log lines with
   the box deliberately unticked, so the warning must key on the
   deferral-then-pass sequence, not on any pass line over an unticked
   box. Rejected alternative: clearing on the log line alone was
   declined because the tick is the deliberate, greppable close and the
   interim-pass convention depends on log lines that do not clear.

## Priority 2 - contract gaps with recorded workarounds

### D3. Reviewer briefs state the unrunnable-check rule

From `2026-08-03 reviewer-briefs-unrunnable-checks` (chore-lottery, a
sandboxed reviewer graded its own denied `cargo test` as a BLOCKER).
Accepted. Per `brief.py`'s no-restated-policy design, the sentence
lands in the PROCESS template's Gate A bullet - a check the reviewer
cannot execute is reported as unverified, never as a finding against
the diff - so the generated brief quotes it from the consumer's own
contract. Consumers re-sync PROCESS.md to pick it up; chore-lottery's
local REVIEW-TOOLING copy already carries the interim wording.

### D4. Lint suppressions carry a recorded reason

From `2026-08-02 lint-suppression-disposition` (terminalbench-aura, an
archive-directory exemption with no recorded justification). Accepted
as scoped: one sentence on the prose-lint bullet in the PROCESS
template's Commit standards - a lint suppression or exemption carries
its reason where it lands, in the config comment or the commit body.

### D5. Gate checklists restate their deterministic steps

From `2026-08-02 per-gate-skill-loads` (aura-orchestration-mode, a
stated-once "load gate-probes first" imperative that decayed by the
commit boundary). Accepted as scoped: the PROCESS template's Gates
section notes that per-gate checklists restate their deterministic
steps rather than pointing at an earlier statement, since restated
checklists fired reliably and one-time prose did not.

### D6. The kit's templates pass the kit's own prose standard

From `2026-08-03 shipped-templates-trip-tricolon` (chore-lottery, local
prose diffs against templates it was told to re-sync from). Accepted in
two parts: rephrase the two `VerbTricolon` spans in the shipped
`PROCESS.md` (lines 165 and 328 today), and add a kit-side gate so
`vale` runs over `src/boardkit/data/templates/` before templates ship -
either in the kit's own pre-commit or as a doctor-adjacent check. D3,
D4, and D5 edit the same template, so the wave that lands them runs
this gate over the result.

## Closed without new work

### C1. Wave-close docs bus test

From `2026-08-02 docs-bustest-wave-close`. The fix the entry predicted
landed: the shipped PROCESS template defines the documentation bus test
as a wave-close step, carrying the six-area rubric, the
one-fact-one-place rule, and P1-blocks-the-gate semantics. Verified in
the current tree; closed as already-fixed, per the entry's own
instruction to verify rather than re-plan.

## Sequencing

D3, D4, D5, and D6 are one small template wave (they touch the same
file and D6 gates the result). D2 is one small code-plus-doc wave. D1
is the largest and rides the topology-hardening contract machinery
(schema bump, resolver, brief); run it as its own wave after the
template wave so the brief it regenerates quotes the corrected
contract text.
