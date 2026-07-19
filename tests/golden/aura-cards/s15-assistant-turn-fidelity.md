---
id: S15
title: Assistant-turn fidelity
status: backlog
depends: [S9, S10]
serialize-with: []
lineage: accepted-head
executor: smart
gates: "U(mockup) -> S -> A -> U(launch) -> M -> U(baseline)"
user-gates: [mockup, launch, baseline]
---

# S15: Assistant-turn fidelity

Plan section: Stage 7 in
[2026-07-11-orchestration-redesign.md](../plans/2026-07-11-orchestration-redesign.md).
Mechanics: [PROCESS.md](../PROCESS.md). Required reading:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md).

## Scope

One behavior variable, split from S9 so each mechanism is measured
alone: keep the coordinator's native output as the assistant turn
instead of the 136-char stub. Base: the accepted head, after the S9
and S10 baseline decisions.

## Deliverable

Continuation threads whose assistant turns carry the model's native
output, with its own N=3 comparison on the accepted head.

## Acceptance

- Rendered before/after envelopes from the S2 harness at the mockup
  gate.
- Comparison metrics and minimum effect thresholds pre-registered at
  the launch gate; no post-hoc materiality.
- A recorded baseline decision either way; the lineage rule held.

## Gate checklist

- [ ] Gate U (mockup): rendered before/after envelopes from the S2
      harness; user approves the exact surface.
- [ ] Gate S: fmt, clippy, lib tests; golden frames re-snapshotted
      and reviewed.
- [ ] Gate A: fresh strong-class agent review of the diff and the
      rendered envelopes; the golden-frame re-baseline checkpoint
      applies.
- [ ] Gate U (launch): provenance, canary, and pre-registered metrics
      and thresholds.
- [ ] Gate M: N=3 trace-complete on the Nobara lineage; S16 sre-hard
      regression run alongside.
- [ ] Gate U (baseline): accept or reject against the pre-registered
      thresholds; on rejection, commits move to `evidence/S15`.

## Branch

Local branch `card/S15` off the accepted head; no pushes before gates
pass; rebased onto the primary; commit range recorded here at Done.

## Log

- 2026-07-11 Filed by S0 from the approved plan.
