---
id: S21
title: R3 qualified cross-board references
status: in-progress
depends: [S18]
serialize-with: []
lineage: primary
executor: smart
gates: "S -> A -> U(code-review)"
user-gates: [code-review]
---

# S21: R3 qualified cross-board references

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Drain record:
[2026-08-09-feedback-drain-7.md](../../plans/2026-08-09-feedback-drain-7.md)
(same-sitting mints); requirement R3 in the aura requirements doc,
evidence: coordination prose already names three boards in one clause
with no qualifiers, and `depends` resolves same-board only.

## Scope

`src/boardkit/board.py` (the `refs:` field and its validation),
`src/boardkit/data/templates/PROCESS.md`, `docs/board/PROCESS.md`, and
`_template.md` (schema prose), tests.

## Deliverable

A qualified reference syntax `<code>/<id>` (as in `tb/S91`), valid in
card prose and in a new optional `refs:` frontmatter list. Resolution
goes through the S18 registry: the short-code must be a registry row,
and the id must match that row's declared prefix scheme. Refs are
informational for DAG purposes - the local scheduler never blocks on
another board's state - so `check` validates form and short-code
existence, warns when the target board is unreachable on this machine,
and never reads the other board's card status. Bare ids stay valid
inside a single board.

## Acceptance

- `uv run pytest -q` green; tests cover ref parsing, unknown
  short-code errors, prefix-mismatch errors, the unreachable-board
  warning, and that a ref never affects ready/blocked computation.
- A fixture card with `refs: [tb/S91]` passes `check` against a
  manifest that rows `tb`, and fails against one that does not.
- The schema prose in the shipped template and this board's PROCESS
  copy agree.

## Gate checklist

- [x] Gate S: load skill `gate-probes`, then `uv run pytest -q`,
  `uv run ruff check`, `vale` on touched markdown.
- [ ] Gate A: adversarial review, focus: can an informational ref leak
  into scheduling, and does the prefix check hold for sentinel ids?
- [ ] Gate U (code-review): present the review packet; stop.

## Branch

direct

## Log

- 2026-08-09 Minted by the seventh feedback drain from standing
  requirement R3, per the Session B build order.
- 2026-08-09 Pulled in-progress straight from backlog (S18 in-review,
  same-hand build order per drain 7); executor is the maintainer
  session.
- 2026-08-09 Built: `refs:` optional frontmatter list with `<code>/<id>`
  shape validated at parse; registry resolution in `check` via
  `card_ref_findings` - unknown short-code is an error, a
  prefix-scheme mismatch or an unreachable board is a warning (sentinel
  ids of another board are not knowable from its row); refs never feed
  readiness; schema prose in both PROCESS and both _template copies.
  Gate S PASS: 316 pytest green (5 ref tests), ruff clean, vale clean.
