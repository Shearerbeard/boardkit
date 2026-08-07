---
id: S16
title: Render each card's current gate position in the generated views
status: ready
depends: []
serialize-with: []
lineage: primary
executor: smart
gates: "S -> A"
user-gates: []
---

# S16: Render each card's current gate position in the generated views

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Drain record:
[2026-08-07-feedback-drain-6.md](../../plans/2026-08-07-feedback-drain-6.md),
second entry.

## Scope

`src/boardkit/board.py` (view rendering), `src/boardkit/cli.py` if the
canary key needs the same field, tests. No card-schema changes: the
position derives from the gate-checklist tick state the cards already
carry.

## Deliverable

For any card that is not backlog or done, the generated views render
the card's current gate position beside its ladder: the next unticked
gate in the checklist (`S -> A -> U @ U` when S and A are ticked). A cold reader of `INDEX.md` and `board.md` alone can answer
"which gate is this in-review card parked at" without opening the
card. `boardkit canary-key` derives its gate answers from the same
computation, so the key and the views cannot disagree.

## Acceptance

- `uv run pytest -q` green; tests cover position rendering for
  in-progress and in-review cards, a fully unticked ladder, and the
  backlog/done suppression.
- On the golden fixture board, an in-review card with Gate A ticked
  renders a position of Gate U, matching the miss the epoch-board
  tracking canary hit.

## Gate checklist

- [ ] Gate S: load skill `gate-probes`, then `uv run pytest -q`,
  `uv run ruff check`, `vale` on touched markdown.
- [ ] Gate A: adversarial review, focus: can the rendered position lie
  (phase-scoped log passes with the box left unticked, sentinel cards,
  gates absent from the checklist)?

## Branch

direct

## Log

- 2026-08-07 Minted by the sixth feedback drain from the epoch-board
  E9 tracking-canary miss.
