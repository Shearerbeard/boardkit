---
id: S1
title: Wave-close retro with snapshots and driver input
status: ready
depends: []
serialize-with: [S6]
lineage: primary
executor: any
gates: "S -> A -> U"
user-gates: [contract-docs]
---

# S1: Wave-close retro with snapshots and driver input

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Plan:
[2026-08-04-productionize-verification.md](../../plans/2026-08-04-productionize-verification.md),
stage 1.

## Scope

`src/boardkit/data/templates/PROCESS.md`,
`plugins/board/skills/board-hygiene/SKILL.md`, `FEEDBACK.md` (entry
format block only), `tests/test_process_template.py`, and the consumer
copies under `docs/board/` re-synced from the templates.

## Deliverable

A required wave-close retro step in the PROCESS template, extracted from
the s29 orchestrator-retro fixture pattern: the closing agent grades the
wave against the card's own acceptance record, names the tough areas,
and emits one snapshot artifact per tough area, linked from the card
that produced it. The step ends by asking the session driver for
observations; the driver may skip with an explicit "nothing to add",
which is recorded, never assumed. The FEEDBACK entry format gains a
`reporter` field distinguishing human-sourced entries from
agent-sourced ones. board-hygiene's checklist carries the step between
the docs bus test and the orientation canary.

## Acceptance

- `uv run pytest -q` green; `vale` clean over the touched markdown.
- The retro step appears in the shipped PROCESS template with an inline
  degrade path for sessions without the board-hygiene skill.
- The FEEDBACK format block documents `reporter` and the skip rule.

## Gate checklist

- [ ] Gate S: `uv run pytest -q`, `uv run ruff check`, `vale` on touched
  files.
- [ ] Gate A: adversarial review of the template diff, focus: can a
  closing session satisfy the step without actually asking the driver?
- [ ] Gate U: contract-doc wording and the reporter field shape are the
  user's call.

## Branch

direct

## Log

- 2026-08-04 Authored from the four-agent audit; retro pattern traced to
  the s29 fixture card.
