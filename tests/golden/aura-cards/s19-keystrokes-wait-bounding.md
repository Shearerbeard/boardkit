---
id: S19
title: Bound and poll keystrokes waits
status: backlog
depends: [MILESTONE]
serialize-with: []
lineage: accepted-head
executor: smart
gates: "scope at promotion -> S -> A -> U(launch) -> M -> U(baseline)"
user-gates: [launch, baseline]
---

# S19: Bound and poll keystrokes waits

Fix candidate filed from the S8 latency profile
([2026-07-12-s8-latency-profile.md](../evidence/2026-07-12-s8-latency-profile.md)).
Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md).

## Scope

Scoped at promotion. Candidate surfaces: a wait cap on the keystrokes
MCP tool or an Aura-side clamp on `wait_time_sec`, replacing long
blind sleeps with capped waits plus capture-pane polling. Behavior
change on the benchmark cell, so it bases on the accepted head and
carries its own N=3.

## Deliverable

Bounded waits with polling, plus an N=3 comparison against the
baseline under pre-registered metrics (wall clock is the primary
expected mover).

## Acceptance

Written at promotion. Standing requirement: the S8 profile names blind
waits as 62.6 percent of wall clock (7,976s requested sleep over 436
calls; the 60s-plus tail alone is 38.0 percent), so the launch gate
pre-registers a wall-clock threshold alongside score neutrality.

## Gate checklist

- [ ] Scope at promotion: exact surface (tool-side cap versus Aura
      clamp), cap value, and polling design written on this card.
- [ ] Gate S: deterministic checks named at promotion.
- [ ] Gate A: fresh-agent review.
- [ ] Gate U (launch): provenance, canary, pre-registered metrics.
- [ ] Gate M: N=3 trace-complete plus the S16 sre-hard check.
- [ ] Gate U (baseline): accept or reject; on rejection commits move
      to `evidence/S19`.

## Branch

Local branch `card/S19` off the accepted head; no pushes before gates
pass; rebased onto the primary; commit range recorded here at Done.

## Log

- 2026-07-12 Filed as backlog by the board owner from S8 fix
  candidate 1 (largest lever in the latency profile; spans
  23c1ada85e2aaf91, cdec7588ef6c62f9 cited in the evidence file).
