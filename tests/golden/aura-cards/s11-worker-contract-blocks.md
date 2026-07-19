---
id: S11
title: Worker contract blocks
status: backlog
depends: [S9, S10]
serialize-with: []
lineage: accepted-head
executor: smart
gates: "scope at promotion -> U(mockup) -> S -> A -> U(launch) -> M -> U(baseline)"
user-gates: [mockup, launch, baseline]
---

# S11: Worker contract blocks

Plan section: Stage 7 in
[2026-07-11-orchestration-redesign.md](../plans/2026-07-11-orchestration-redesign.md).
Mechanics: [PROCESS.md](../PROCESS.md). Required reading:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md).

## Scope

Config-only behavior variable, filed at S0 and scoped at promotion
once the S9 and S10 baseline decisions land: the worker preambles in
`configs/sre-shell-orchestrated.toml` (with S10, one of exactly two
cards allowed to touch that config). Base: the accepted head. Per the
North star, word changes as generic, role-shaped guidance wherever
the variable discipline allows.

## Deliverable

Worker preambles restructured on the Desktop delegation principles
([2026-07-07-worker-prompt-delegation-principles.md](../evidence/2026-07-07-worker-prompt-delegation-principles.md)):
an input contract, a labelled-prose output contract, and an
escalation packet, written as labelled prose sections, not
constrained JSON.

## Acceptance

Detailed acceptance is written at promotion. Standing requirements:
one variable per run; metrics and thresholds pre-registered at the
launch gate; its own N=3 on the accepted head; the provenance config
sha proves no file outside this card's map moved.

## Gate checklist

- [ ] Scope at promotion: full scope, mockup surface, and residual
      risks written on this card once S9 and S10 decisions land.
- [ ] Gate U (mockup): rendered before/after worker preambles; user
      approves the exact surface.
- [ ] Gate S: vale on config prose; golden frames re-snapshotted for
      the worker surfaces.
- [ ] Gate A: fresh strong-class agent review; the golden-frame
      re-baseline checkpoint applies.
- [ ] Gate U (launch): provenance, canary, and pre-registered metrics
      and thresholds.
- [ ] Gate M: N=3 trace-complete on the Nobara lineage; S16 sre-hard
      regression run alongside.
- [ ] Gate U (baseline): accept or reject against the pre-registered
      thresholds; on rejection, commits move to `evidence/S11`.

## Branch

Local branch `card/S11` off the accepted head; no pushes before gates
pass; rebased onto the primary; commit range recorded here at Done.

## Log

- 2026-07-11 Filed by S0 from the approved plan.
