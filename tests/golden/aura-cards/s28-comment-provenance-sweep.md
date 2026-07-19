---
id: S28
title: Comment provenance sweep before PR re-cut
status: backlog
depends: [MILESTONE]
serialize-with: []
lineage: primary
executor: any
gates: "S -> A"
user-gates: []
---

# S28: Comment provenance sweep before PR re-cut

Mechanics: [PROCESS.md](../PROCESS.md). Required reading:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Filed from the user's S2
review. Card and gate references in code comments steer card
executors well during the epic, yet a mainline PR reviewer has no
tracker context, so the re-cut branches must not carry any of them.

## Scope

Experiment worktree, comments and test-only identifier names in
`crates/aura/src/` plus `slot_coverage.sh`. No behavior changes; all
golden snapshots stay byte-identical. `DESIGN.md` and `MANIFEST.md`
are records, not shipped comments; their disposition belongs to the
PR-decomposition map, not this card.

This card runs immediately before the PR-decomposition map is cut.
If any code card lands after this card completes, the grep acceptance
below is re-run before the map is cut.

## Deliverable

Code comments that stand alone for a cold mainline reviewer:

- Card and process references (`S2`, `skeleton`, gate names) removed
  or replaced with self-contained wording.
- Residual-risk codes (`R3`, `R5`, `R8`) replaced with a short
  description or a `MANIFEST.md` section cite.
- The `_for_golden` test accessor names and their "golden-frame seam"
  doc comments renamed and reworded to describe what they expose, not
  which card added them.
- Constraint comments (the "deliberately partial/absent" family) are
  kept, reworded to cite the manifest section that owns the
  exclusion.

## Acceptance

- `grep -rnE '//.*\b(S[0-9]{1,2}|R[0-9])\b' crates/aura/src/orchestration --include='*.rs'`
  returns nothing: no line or doc comment in the orchestration tree
  carries a card or residual-risk code. Any such token that must stay
  outside a comment (a string literal naming production behavior) is
  listed on this card with its reason.
- `grep -nE '#.*\b(S[0-9]{1,2}|R[0-9])\b' crates/aura/src/orchestration/context_fixture/slot_coverage.sh`
  returns nothing (comment lines only; the script's checks themselves
  carry no card codes).
- `grep -rn '_for_golden' crates/aura/src --include='*.rs'` returns
  nothing (the DESIGN.md and MANIFEST.md records keep their historical
  references; their disposition belongs to the PR-decomposition map).
- `cargo test --package aura --lib` green under `INSTA_UPDATE=no`
  with zero pending snapshots.

## Gate checklist

- [ ] Gate S: the acceptance greps plus fmt, clippy, full lib tests
      with zero pending snapshots.
- [ ] Gate A: fresh-agent read of the touched comments as a cold PR
      reviewer; every kept comment must make sense without tracker
      context.

## Branch

Local branch `card/S28` off the base named by `lineage` (the primary
head); no pushes before gates pass; rebased onto the primary. The
board owner sets the `commit-range` frontmatter at In Review and
repeats the final range in the Done log entry.

## Log

- 2026-07-12 Filed as backlog by the board owner from the user's S2
  review round.
- 2026-07-12 codex adversarial review (standing rule): acceptance
  greps made comment-aware, scoped to the orchestration tree, and
  extended to slot_coverage.sh; finding dispositioned accepted.
- 2026-07-12 Gate A review of the filing: `_for_golden` grep
  restricted to `.rs` (the unscoped form matched the DESIGN.md record
  this card refuses to touch) and the slot_coverage.sh grep made
  comment-aware. Both accepted.
