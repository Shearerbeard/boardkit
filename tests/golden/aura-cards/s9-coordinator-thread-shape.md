---
id: S9
title: Coordinator thread shape (W17)
status: in-progress
depends: [S2, MILESTONE]
serialize-with: []
lineage: accepted-head
executor: smart
gates: "U(mockup) -> S -> A -> U(launch) -> M -> U(baseline)"
user-gates: [mockup, launch, baseline]
---

# S9: Coordinator thread shape (W17)

Plan section: Stage 5 in
[2026-07-11-orchestration-redesign.md](../plans/2026-07-11-orchestration-redesign.md).
Mechanics: [PROCESS.md](../PROCESS.md). Required reading:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md).

## Scope

One behavior variable, frozen to one mechanism: instruction
placement. Files: the continuation template, the preamble template,
and the wrapper code that fills them. Base: the accepted head.
Assistant-turn fidelity (native output instead of the 136-char stub)
is out; that is S15, its own variable.

## Deliverable

Durable instructions (routing menu, synthesis rules, goal-handling
guidance) live once in the preamble. Each continuation turn becomes
observation-shaped, carrying the iteration outcome, evidence delta,
budget status, and pinned verbatim goal, with FINAL_ATTEMPT urgency
preserved. Tony's synthesis-inlining rules move to the preamble
rather than being deleted (R5 lesson: purges regress).

## Acceptance

- Mockup envelopes and a duplication-ledger delta versus
  [2026-07-10-coordinator-thread-anatomy.md](../evidence/2026-07-10-coordinator-thread-anatomy.md).
- Comparison metrics and minimum effect thresholds pre-registered at
  the launch gate; no post-hoc materiality.
- A recorded baseline decision either way, with the lineage rule
  held: S10 bases only on the accepted head.

## Gate checklist

- [ ] Gate U (mockup): rendered before/after envelopes from the S2
      harness at three planning depths, plus the duplication-ledger
      delta versus the anatomy doc; user approves the exact surface.
- [ ] Gate S: fmt, clippy, lib tests; golden frames re-snapshotted
      and reviewed (the surface change is intentional here).
- [ ] Gate A: fresh strong-class agent review of the diff and the
      rendered envelopes; the re-baseline checkpoint applies (frames
      reviewed plus registry state review before dependents proceed).
- [ ] Gate U (launch): provenance plus canary per standing rules, and
      pre-registration of metrics and thresholds (score, per-task
      flips under the variance reading rule, wall-clock, tokens,
      failed-run treatment).
- [ ] Gate M: N=3 trace-complete on the Nobara lineage; comparison
      report with the provenance-delta table and the pre-registered
      metric columns; S16 sre-hard regression run alongside.
- [ ] Gate U (baseline): accept or reject against the pre-registered
      thresholds; outcome logged on this card. On rejection, commits
      move to `evidence/S9` and the accepted head is unchanged.

## Branch

Local branch `card/S9` off the accepted head; no pushes before gates
pass; rebased onto the primary; commit range recorded here at Done.

## Log

- 2026-07-11 Filed by S0 from the approved plan.
- 2026-07-18 Promoted to Ready by the board owner (Opus 4.8, Claude
  Code) on MILESTONE acceptance. Both dependencies (S2, MILESTONE) are
  Done, and the accepted Track A head is 7a0f0651 (the N=3 replication
  cleared it: distribution {2,3,4}, mean 3.0, matched baseline; the two
  stable-task flips diagnosed as variance). S9's base is that accepted
  head. First gate is U(mockup): the rendered before/after envelopes
  from the S2 harness at three planning depths, plus the
  duplication-ledger delta, await the user before any code. This is the
  head of the coordinator-simplification / frame wave the user
  prioritized (S9 -> S10 -> S11/S12/S13/S15).
- 2026-07-18 Pulled to In Progress by the board owner (Fable, Claude
  Code) at the user's direction. Branch `card/S9` created off the
  accepted head 7a0f0651 in the epic primary worktree. First work
  unit: prototype the instruction-placement change and render the
  U(mockup) packet (before/after envelopes from the S2 harness at
  three planning depths, duplication-ledger delta vs the anatomy doc).
- 2026-07-18 Prototype implemented by a Fable executor subagent
  (templates + 2 test relocations only; zero wrapper-code changes; 13
  coordinator snapshots re-rendered, no worker snapshot changed; full
  lib suite, fmt, clippy green). Two deixis-only wording deviations,
  enumerated in the packet. Mockup packet at
  `docs/redesign/reviews/S9/mockup-packet.md` (gitignored working
  material). Gate D drift audit ran clean (Haiku, 6 checks: worktree
  scope, packet quote, arithmetic, board views, test claim, logged
  divergences). U(mockup) presented to the user; awaiting surface
  approval and the msg1-routing-menu in/out decision.
