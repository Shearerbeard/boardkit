---
id: S40
title: README developer path, canary brief template, plan navigation
status: ready
depends: []
serialize-with: []
lineage: primary
executor: any
gates: "S -> A"
user-gates: []
epic: S41
---

# S40: README developer path, canary brief template, plan navigation

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Minting record:
[2026-08-22-spread-readiness-hypothesis.md](../../plans/2026-08-22-spread-readiness-hypothesis.md)

## Scope

README.md, `src/boardkit/data/templates/` (AGENTS template, a canary
brief template), `docs/plans/` navigation pointer.

## Deliverable

The kit-developer quick start beside the consumer quick start
(including the self-hosted `BOARDKIT_HOME` note the flash canary
flagged); a shipped orientation-canary brief template with a worked
example; the kit's clone URL stated in README and the AGENTS
template; a navigation pointer so wave plans in `docs/plans/` stop
hanging off card logs alone. Deliberately pulls part of PLAN.md's
Phase 6 publish-gate README work forward.

## Acceptance

- The two quick starts are distinct and both run cold; `vale` clean;
  the canary template matches what `board-hygiene` prescribes.

## Gate checklist

- [ ] Gate S: `boardkit check`, `boardkit render --check`, `vale` on
  touched markdown.
- [ ] Gate A: adversarial prose review.

## Branch

direct

## Log

- 2026-08-22 Minted at the wave-2 Gate U (Phase 0) from the approved
  spread-readiness action list.
