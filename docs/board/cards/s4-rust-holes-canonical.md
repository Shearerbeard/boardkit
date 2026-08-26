---
id: S4
title: Declare the typed-holes skill canonical over PLAYBOOK
status: done
commit-range: 0f0311c..fac496c
depends: []
serialize-with: [S47]
lineage: none
executor: any
gates: "S -> A"
user-gates: []
---

# S4: Declare the typed-holes skill canonical over PLAYBOOK

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Plan:
[2026-08-04-productionize-verification.md](../../plans/2026-08-04-productionize-verification.md),
stage 3. External repo: `~/dev/rust-holes` (private; never publish).

## Scope

In `~/dev/rust-holes` only: `PLAYBOOK.md`, `README.md`,
`templates/dispatch-brief.md`, `templates/design-panel-prompts.md`,
`EXTRACTION.md`.

## Deliverable

The typed-holes skill becomes the canonical statement of the doctrine;
PLAYBOOK.md thins to what only this repo can hold - the fill-in
templates and worked examples plus the never-public provenance ledger -
and a pointer to the skill for the practice itself. The four recorded divergences
(fmt gate, fill-order check step, two dropped evidence claims) are
reconciled in the skill's favor or explicitly kept with a reason.
EXTRACTION.md gains a ledger note that doctrine drift is now checked
against the skill, not against PLAYBOOK prose.

## Acceptance

- No doctrine paragraph exists in both files; `grep` for the four
  divergence sites shows one owner each.
- README's self-sufficiency claim is updated to match (templates stand
  alone; doctrine lives in the skill).

## Gate checklist

- [x] Gate S: `vale` on touched files; the never-publish rule intact.
- [x] Gate A: adversarial review, focus: did thinning PLAYBOOK drop any
  rule that has no home in the skill?

## Branch

direct; external commits recorded in the Log as they land.

## Log

- 2026-08-04 Authored from the rust-holes audit (playbook/skill twin,
  four divergences in nine days).
- 2026-08-23 Serialized with S47 (drain 8): both cards touch
  rust-holes `templates/dispatch-brief.md`. Drain 8 also vetted the
  claude-skills retro §6a sentence for use when this card runs; the
  public SKILL.md diff stays user-gated and outside this card's
  scope.
- 2026-08-26 Pulled to in-progress under the cleanup execution plan
  (rust-holes `docs/plans/2026-08-25-cleanup-execution.md`); S47's
  edits are committed, so the serialize-with is satisfied. Executor
  lane: opencode on bedrock, write-only dispatch from the rust-holes
  worktree with the canonical skill staged beside the brief;
  reviewer lane: codex. Scope stays the card's five files; the public
  skill sentence is a separate, user-gated step outside this card.
- 2026-08-26 Executor (bedrock lane, write-only) thinned PLAYBOOK,
  updated README and EXTRACTION, and adopted the skill's fmt wording
  in the dispatch brief. Board-owner repairs before Gate S, recorded
  as deviations: reverted edits to `templates/skeleton-conventions.md`
  and `templates/golden-frame-harness.md` (outside this card's five
  files; the fmt residual there is noted on EXTRACTION's fmt-gate
  row); removed the verbatim "Known limits" copy the executor kept
  despite reporting it identical to the skill's; dropped two
  "repo-specific" notes that restated the skill and README (fmt
  fallback, never-publish); kept the provenance note and the clippy
  flag-sequence note, the latter because the staged skill text does
  not carry the `-A clippy::todo` sequence; rewrote PLAYBOOK as an
  18-line map; wrapped prose to 72 columns; reworded the README row
  so PLAYBOOK is described as the map, not as the templates.
- 2026-08-26 Gate S passed: `bin/check` exits 0 on the rebased tree;
  grep of the four divergence sites shows one owner each; Private
  notice intact; vale clean. Commit `fac496c` on rust-holes master;
  commit-range set; packet generated; Gate A dispatched to the codex
  lane.
- 2026-08-26 Gate A (codex lane): PASS, zero findings, on `fac496c`.
  Acceptance re-run by the board owner: no skill doctrine sentence
  appears in PLAYBOOK (five spot-checked); fmt wording only in the
  dispatch brief; both evidence counts only in EXTRACTION; README's
  row and composition paragraph name the skill as the practice's
  home; Private notice intact; `bin/check` green. Done. Residual
  recorded on EXTRACTION's fmt-gate row: two per-module templates
  still carry the nightly-first fmt form, outside this card's scope.
  The public skill-canonical sentence is staged uncommitted in
  claude-skills for Mike's gate, as the drain record specified.
