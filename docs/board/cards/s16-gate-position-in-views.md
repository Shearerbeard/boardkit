---
id: S16
title: Render each card's current gate position in the generated views
status: in-review
depends: []
serialize-with: []
lineage: primary
commit-range: a95fcab..5211b1b
executor: smart
gates: "S -> A -> U(code-review)"
user-gates: [code-review]
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

- [x] Gate S: load skill `gate-probes`, then `uv run pytest -q`,
  `uv run ruff check`, `vale` on touched markdown.
- [ ] Gate A: adversarial review, focus: can the rendered position lie
  (phase-scoped log passes with the box left unticked, sentinel cards,
  gates absent from the checklist)?
- [ ] Gate U (code-review): present the review packet; stop.

## Branch

direct

## Log

- 2026-08-07 Minted by the sixth feedback drain from the epoch-board
  E9 tracking-canary miss.
- 2026-08-09 Pulled in-progress as a Session B ride-along (interview
  decision 8, drain 7); U(code-review) gate inserted per PROCESS (card
  predates the standing gate). Executor is the maintainer session.
- 2026-08-09 Built: `gate_cell` renders `<ladder> @ <position>` for
  ready/in-progress/in-review cards in INDEX and board.md, position =
  first letter `remaining_gates` reports (a letter with no checklist
  box counts open; matching by letter holds a multi-U card at U until
  every U box ticks); backlog/done render the bare ladder; the canary
  key's In Review / In Progress sections use the same computation, so
  key and views cannot disagree. Golden fixtures refreshed by the
  recorded diff-review procedure (S9 `@ U`, S36 `@ S`, four lines).
  Gate S PASS: 338 pytest green, ruff clean. Acceptance note: the
  in-review-with-A-ticked shape is covered by the constructed fixture
  in test_board.py (renders `@ U`), not the golden board, which has no
  such card - the epoch E9 miss shape is the test's exact scenario.
- 2026-08-09 In-review; commit-range a95fcab..5211b1b.
- 2026-08-09 Gate A open: deferred (adversarial reviews batch at the
  Session B boundary; packets present at the Gate B user gate).
