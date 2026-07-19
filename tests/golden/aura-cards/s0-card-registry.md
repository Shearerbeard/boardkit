---
id: S0
title: Card registry and board guardrails
status: done
depends: []
serialize-with: []
lineage: none
executor: smart
gates: "S -> A -> M -> U"
user-gates: [format]
---

# S0: Card registry and board guardrails

Plan section: Stage 0 in
[2026-07-11-orchestration-redesign.md](../plans/2026-07-11-orchestration-redesign.md).
Mechanics: [PROCESS.md](../PROCESS.md). Required reading:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md).

## Scope

Adapter repo only, one atomic commit: `docs/redesign/cards/` (this
registry), `scripts/cards_index.py`, `scripts/loc_measure.py`,
`.claude/skills/board-hygiene/`, `AGENTS.md` pointer, `BOARD.md`
freeze pointer.

## Deliverable

A per-card registry fresh agents orient on cheaply: one file per card
with validated frontmatter, a generated [INDEX.md](INDEX.md) and
Obsidian-kanban [board.md](board.md), the LOC measurement script, the
board-hygiene skill, and the pointers that make it discoverable.

## Acceptance

- `uv run python scripts/cards_index.py --check` exits 0 (schema, DAG
  acyclicity, link resolution, index drift).
- `uv run python scripts/loc_measure.py --help` runs; a demo range on
  the aura worktree prints classified totals.
- `vale` clean on every new markdown file (or dispositioned).
- S1-S18 plus MILESTONE filed; `AGENTS.md` points at the registry.

## Gate checklist

- [x] Gate S: vale on new files; generator validations pass; LOC demo.
- [x] Gate A: fresh agent review. The first round found one blocking
      and seven minor issues; all were fixed and the reviewer then
      signed off on re-verification.
- [x] Gate M: Obsidian kanban renders the format (evidence: the
      identically formatted preview was live-rewritten by the user's
      plugin on 2026-07-11; user re-confirm invited at handoff).
- [x] Gate U: user approved execution 2026-07-11 ("S0 go") after
      reviewing the plan and the rendered preview.

## Branch

Adapter repo, direct (one atomic commit on
`mshearer/coordinator-context-program`).

## Log

- 2026-07-11 Filed and executed from the approved plan, same session.
- 2026-07-11 DIVERGENCE: the BOARD.md freeze pointer is deferred; a
  concurrent session holds uncommitted BOARD.md edits and this card
  must not sweep them into its commit. Apply the pointer in a
  follow-up commit once BOARD.md is clean. AGENTS.md pointer landed
  (that file was clean).
- 2026-07-11 Gate S passed: vale clean on all cards and views;
  generator schema/DAG/link/drift validations green; ruff, format,
  and pyright clean on both scripts; LOC script verified against the
  known W13 range (buckets reconcile with git diff --stat, -234).
- 2026-07-11 Gate A round 1: FAIL (1 blocking, 7 minor). Blocking:
  S14 filed on primary lineage despite being a behavior change.
  Fixed as prescribed (accepted-head, depends MILESTONE, branch text)
  plus all minors: serialize-with symmetry (S6, S17) with a new
  validator check, ready-requires-done-deps validator check,
  serialize-with/user-gates now required keys, S12/S13 evidence
  links, template contract corrected, PROCESS.md registry-era note.
  Sent back for re-verification.
- 2026-07-11 Gate A round 2: PASS. All eight fixes verified by the
  same reviewer; residuals (stale views pending the done-flip
  regeneration; PROCESS.md date bump) addressed at the flip.
- 2026-07-11 Done. Gate M evidence is the live plugin render of the
  identical format; Gate U is the user's "S0 go". Status flipped,
  views regenerated, atomic commit follows in the same turn.
