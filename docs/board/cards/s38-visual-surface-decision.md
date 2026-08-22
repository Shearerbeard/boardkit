---
id: S38
title: Pick the board's visual home
status: ready
depends: [S16]
serialize-with: []
lineage: primary
executor: smart
gates: "S -> A -> D -> U"
user-gates: [decision]
epic: S41
---

# S38: Pick the board's visual home

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Minting record:
[2026-08-22-spread-readiness-hypothesis.md](../../plans/2026-08-22-spread-readiness-hypothesis.md)

## Scope

A design card; deliverable is a decision plus, if accepted, an
implementation card.

## Deliverable

Decide where a human looks at the board: GitHub's native rendering of
the committed views, Obsidian's kanban plugin, or a generated
static-HTML board. Build-nothing is an acceptable outcome. S27
(architecture flowchart) folds in or stays separate per the decision.
The hand-built Gate U runbook and packet-companion artifacts from
2026-08-22 are worked examples of the consumption shape.

## Acceptance

- Decision logged with its reason; S27's disposition recorded.

## Gate checklist

- [ ] Gate S: decision doc drafted, then `boardkit check`,
  `boardkit render --check`, `vale` on the prose.
- [ ] Gate A: adversarial review of the decision doc.
- [ ] Gate D: drift audit before the user gate.
- [ ] Gate U: Mike decides; stop.

## Branch

direct

## Log

- 2026-08-22 Minted at the wave-2 Gate U (Phase 0) from the approved
  spread-readiness action list.
