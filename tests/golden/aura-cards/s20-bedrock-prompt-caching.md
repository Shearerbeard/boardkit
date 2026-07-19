---
id: S20
title: Bedrock prompt caching with cache points
status: backlog
depends: [MILESTONE]
serialize-with: []
lineage: accepted-head
executor: smart
gates: "scope at promotion -> S -> A -> U(launch) -> M -> U(baseline)"
user-gates: [launch, baseline]
---

# S20: Bedrock prompt caching with cache points

Fix candidate filed from the S8 latency profile
([2026-07-12-s8-latency-profile.md](../evidence/2026-07-12-s8-latency-profile.md)).
Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md).

## Scope

Scoped at promotion. Candidate surfaces: the Aura provider layer
(rig-bedrock 0.3.10 carries `CachePointBlock` wire types, unused at
`9df96382`) plus, for the planning ceiling, an append-only coordinator
continuation (which overlaps S9's thread-shape work; the promotion
scope must reconcile with S9 rather than duplicate it).

## Deliverable

Cache points on worker and coordinator calls, with an N=3 comparison
under pre-registered token-cost and wall-clock metrics.

## Acceptance

Written at promotion. Standing evidence: the S8 idealized cache model
estimates a 3.64x worker prompt-token multiple (4,057,075 tokens over
44 workers per 3-run batch) and a 1.32x planning ceiling that the
re-rendered continuation defeats today (54 percent continuation
prefix commonality).

## Gate checklist

- [ ] Scope at promotion: provider-layer design, cache-point
      placement, and the S9 reconciliation written on this card.
- [ ] Gate S: deterministic checks named at promotion.
- [ ] Gate A: fresh-agent review.
- [ ] Gate U (launch): provenance, canary, pre-registered metrics.
- [ ] Gate M: N=3 trace-complete plus the S16 sre-hard check.
- [ ] Gate U (baseline): accept or reject; on rejection commits move
      to `evidence/S20`.

## Branch

Local branch `card/S20` off the accepted head; no pushes before gates
pass; rebased onto the primary; commit range recorded here at Done.

## Log

- 2026-07-12 Filed as backlog by the board owner from S8 fix
  candidate 2.
