---
id: S13
title: Board discovery beyond cwd - sibling boards and pointers
status: ready
depends: []
serialize-with: []
lineage: primary
executor: smart
gates: "S -> A"
user-gates: []
---

# S13: Board discovery beyond cwd - sibling boards and pointers

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Drain record:
[2026-08-05-feedback-drain-4.md](../../plans/2026-08-05-feedback-drain-4.md),
final entry.

## Scope

`src/boardkit/config.py` (config discovery), `src/boardkit/cli.py`,
`src/boardkit/doctor.py`, `plugins/board/skills/board-hygiene/SKILL.md`
and `plugins/board/skills/delegating-work/SKILL.md` (the precondition
prose), tests.

## Deliverable

A missing root `boardkit.toml` stops meaning "no board exists". The
CLI resolves a board from, in order: an explicit user-supplied path, a
`BOARDKIT_BOARD` env var, a local untracked pointer file, then cwd. In
a split layout the tooling reminds that the code repo needs an
untracked pointer back to the board. Both board skills replace the
"hard stop, offer `boardkit init`" precondition with "honor a
user-named board and check for a sibling board before offering init".
Init in a hand-made board repo is also covered: a repo with cards but
no entry files gets a repair path rather than silence.

## Acceptance

- `uv run pytest -q` green; tests cover the resolution order and the
  pointer-file path.
- With `BOARDKIT_BOARD` set to a sibling board, `boardkit check` runs
  from the code repo without a root `boardkit.toml`.
- Both skill texts drop the init-first precondition in favor of the
  discovery order, and their contract stamps stay consistent.

## Gate checklist

- [ ] Gate S: load skill `gate-probes`, then `uv run pytest -q`,
  `uv run ruff check`, `vale` on touched markdown.
- [ ] Gate A: adversarial review, focus: can the new resolution order
  silently target the wrong board (env var pointing at a stale
  checkout, pointer file drifting after a board move)?

## Branch

direct

## Log

- 2026-08-05 Minted by the fourth feedback drain from the Epoch
  split-layout discovery findings.
