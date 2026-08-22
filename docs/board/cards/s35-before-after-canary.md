---
id: S35
title: Before/after canary extension for the PROCESS templates
status: backlog
depends: [S34]
serialize-with: []
lineage: primary
executor: smart
gates: "S -> A"
user-gates: []
---

# S35: Before/after canary extension for the PROCESS templates

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Minting record:
[2026-08-19-wave-2-plan.md](../../plans/2026-08-19-wave-2-plan.md)

## Scope

`src/boardkit/data/templates/PROCESS.md` canary section; this board's
live copy.

## Deliverable

The aura board-consistency program's canary extensions as a reusable
template section: per-question grading atoms, surface manifests pinned
by commit shas, sealed-key immutability with dated pre-run amendments,
defect-probe questions, and the invented-answer-is-a-miss rule.

## Acceptance

- Template and live copies agree; `vale` clean.

## Gate checklist

- [ ] Gate S: `boardkit check`, `boardkit render --check`, `vale` on
  touched markdown.
- [ ] Gate A: adversarial prose review.

## Branch

direct

## Log

- 2026-08-22 Minted at the wave-2 Gate U (Phase 0) per the plan's
  card map; Mike approved the plan and its dispositions that day.
