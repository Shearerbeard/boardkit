---
id: S43
title: Land the phase 2 residue - canary fallback, degraded close, review notes
status: in-progress
depends: []
serialize-with: []
lineage: primary
executor: smart
gates: "S -> A -> U(code-review)"
user-gates: [code-review]
---

# S43: Land the phase 2 residue - canary fallback, degraded close, review notes

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Minting record: the wave-2
plan's Phase 2 change list
([2026-08-19-wave-2-plan.md](../../plans/2026-08-19-wave-2-plan.md)),
whose decision-5 and documentation items were phase deliverables
attached to no card; this card closes the gap so Phase 2's done-when is
met before its user gate presents.

## Scope

`boardkit.toml` (this board's live `[roles.canary]`), the init
scaffold's boardkit.toml source in `src/boardkit/`, `docs/board/PROCESS.md`
and `src/boardkit/data/templates/PROCESS.md` (the orientation-canary
section), `plugins/board/skills/board-hygiene/SKILL.md` (plus the
plugin manifest bump), `docs/board/REVIEW-TOOLING.md`, the
dispatch-brief data in `src/boardkit/`, tests where template or brief
text is pinned.

## Deliverable

The wave-2 plan's unassigned Phase 2 items, verbatim from its approved
decisions:

- Decision 5 in full: `roles.canary` gains `codex-reviewer` as its
  fallback (the board's only cross-provider escape) in this board's
  live `boardkit.toml` AND the init scaffold; the degraded-close
  definition lands in the live PROCESS orientation-canary section, the
  template copy, and the `board-hygiene` skill: canary-key generated
  and stored, deferral logged with outage evidence, canary owed at
  next session start.
- REVIEW-TOOLING documents the `--suffix` fix-packet pattern and the
  read-the-reviewer's-own-final-message rule.
- The dispatch-brief data gains the parallel-fill interference note.

## Acceptance

- `uv run pytest -q` green; `boardkit resolve-route canary` resolves a
  fallback on this board.
- Both PROCESS copies state the degraded close in the canary section
  and agree; the hygiene skill answers the outage case in writing.
- `vale` clean on every touched markdown file.

## Gate checklist

- [ ] Gate S: load skill `gate-probes`, then `uv run pytest -q`,
  `uv run ruff check`, `boardkit check`, `boardkit render --check`,
  `boardkit doctor`; `vale` on touched markdown.
- [ ] Gate A: adversarial review of the diff against the plan's
  decision-5 wording and the shipped resolver of `resolve-route`.
- [ ] Gate U (code-review): packet to Mike, batched with the Phase 2
  window; stop.

## Branch

direct

## Log

- 2026-08-22 Minted and pulled by the board owner on finding Phase 2's
  done-when unmet: the plan's decision-5 and documentation items were
  phase deliverables attached to no card, discovered while preparing
  the batched user gate. The content is pre-approved plan text; this
  card exists so it lands through the standard pipeline rather than as
  gateless board-owner edits.
