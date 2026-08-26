---
id: S4
title: Declare the typed-holes skill canonical over PLAYBOOK
status: ready
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

- [ ] Gate S: `vale` on touched files; the never-publish rule intact.
- [ ] Gate A: adversarial review, focus: did thinning PLAYBOOK drop any
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
