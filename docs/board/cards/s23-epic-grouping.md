---
id: S23
title: R2 epic cards and epic membership
status: ready
depends: []
serialize-with: []
lineage: primary
executor: smart
gates: "S -> A -> U(code-review)"
user-gates: [code-review]
---

# S23: R2 epic cards and epic membership

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Drain record:
[2026-08-09-feedback-drain-7.md](../../plans/2026-08-09-feedback-drain-7.md)
(same-sitting mints, interview decision 7); requirement R2 in the aura
requirements doc, evidence: the aura-agent-driver epic spans three
surfaces while existing on none, and the 2026-08-04 hitl/webhook
consolidation discovered late that two boards were one initiative.

## Scope

`src/boardkit/board.py` (the `kind:` and `epic:` keys, validation,
rollup rendering), `src/boardkit/data/templates/PROCESS.md`,
`docs/board/PROCESS.md`, `_template.md` (schema prose), tests.

## Deliverable

An epic is itself a card: optional `kind:` frontmatter, `card` when
absent, `epic` for epic cards. Member cards carry an optional
`epic: <id>` validated against an existing same-board epic card. An
epic card holds the initiative's goal prose and may carry gates like
any card; per the plan of record, the aura A5 epic card gains its
`epic:`-related keys only after this ships. Views gain a per-epic
rollup: which cards serve which initiative, answered mechanically.
Build order per the plan of record: this card lands last in the
Session B wave, and its landing unblocks the R9 epic-cluster pass on
S22.

## Acceptance

- `uv run pytest -q` green; tests cover kind validation, epic refs to
  missing or non-epic cards failing, and the rollup rendering.
- A fixture board with one epic and two member cards renders a rollup
  naming both members; a member naming a plain card as its epic fails
  `check`.
- The schema prose in the shipped template and this board's PROCESS
  copy agree.

## Gate checklist

- [ ] Gate S: load skill `gate-probes`, then `uv run pytest -q`,
  `uv run ruff check`, `vale` on touched markdown.
- [ ] Gate A: adversarial review, focus: epic cycles (an epic member of
  itself or of another epic), status semantics of an epic card with
  open members.
- [ ] Gate U (code-review): present the review packet; stop.

## Branch

direct

## Log

- 2026-08-09 Minted by the seventh feedback drain from standing
  requirement R2, epic-card shape chosen at the interview.
