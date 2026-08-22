---
id: S41
title: Co-worker consumption readiness
status: backlog
depends: []
serialize-with: []
lineage: primary
executor: smart
gates: "S -> U"
user-gates: [acceptance]
kind: epic
---

# S41: Co-worker consumption readiness

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Minting record:
[2026-08-22-spread-readiness-hypothesis.md](../../plans/2026-08-22-spread-readiness-hypothesis.md)

## Goal

A co-worker can clone boardkit, orient from the repo alone, reach a
dispatch-ready machine from the written recipe, read the board
visually, and trust its gate decisions without access to this
machine. The 2026-08-22 spread-readiness assessment is the baseline
evidence; the agent-driver conversion run is the acceptance test the
user offers when this epic's members land.

## Members

S8, S12, S15, S30, S31, S32, S33, S36, S37, S38, S39, S40 carry
`epic: S41`. Membership is grouping, not dependency; `boardkit dag
--to S41` computes the schedulable plan.

## Gate checklist

- [ ] Gate S: `boardkit dag --to S41` shows an empty remaining set;
  members all done.
- [ ] Gate U: Mike accepts consumption readiness, and decides the
  conversion-run offer; stop.

## Branch

direct

## Log

- 2026-08-22 Minted at the wave-2 Gate U (Phase 0) from the approved
  spread-readiness action list.
