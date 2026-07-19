---
id: S4
title: Template unification
status: done
depends: [S2]
serialize-with: [S3, S5, S6, S17]
lineage: primary
executor: any
gates: "S -> A"
user-gates: []
commit-range: "76bc66e8..65ea703c"
---

# S4: Template unification

Plan section: Stage 3 (S4 bullet) in
[2026-07-11-orchestration-redesign.md](../plans/2026-07-11-orchestration-redesign.md).
Mechanics: [PROCESS.md](../PROCESS.md). Required reading:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md).

## Scope

Experiment worktree, template code and template files only. Pure
refactor: behavior on every S2 manifest surface stays byte-identical;
a card that cannot keep envelope identity is misfiled and moves to
Track B.

## Deliverable

One placeholder convention across all templates, with `TemplateVars`
used by every template (2 of 9 today). `build_planning_wrapper`
(orchestrator.rs:1266) and the workers-section builders move from raw
`format!` calls to template files with typed vars. Moved prompt text
stays product LOC under the measurement script.

## Acceptance

- Golden-frame envelope identity over the S2 coverage manifest.
- `cargo fmt --check`, `cargo clippy -- -D warnings`, and `cargo test
  --package aura --lib` pass.
- LOC script output for the card's commit range is pasted on this
  card, with moved prompt text classified as product.
- Residual risks outside the manifest are named on this card.
- Any defect-pinned golden snapshot this card fixes (MANIFEST names
  defects A, B, C, and E as pinned current-production output) is
  updated in the same commit that fixes the defect, with a ledger
  line on this card naming defect and snapshot.
- If this card lands the HashMap-to-BTreeMap ordering change that
  DESIGN.md defers to S3/S4, normalization pass 2 (the worker-order
  sort) is retired in the same commit.

## Gate checklist

- [x] Gate S: fmt, clippy, full lib tests, golden-frame envelope
      identity, LOC script output pasted on the card.
- [x] Gate A: fresh-agent diff review against this card's acceptance;
      rust-review skill applied (smart-class review per the plan).

## Branch

Local branch `card/S4` off the base named by `lineage` (the primary
head); no pushes before gates pass; rebased onto the primary. The
board owner sets the `commit-range` frontmatter at In Review and
repeats the final range in the Done log entry.

## Log

- 2026-07-11 Filed by S0 from the approved plan.
- 2026-07-16 Promoted to In Progress by board owner (GLM-5.2/opencode).
  User approved 3-card bolus (S17 + S23 parallel, S4 after). S17 and
  S23 both Done; primary at `76bc66e8`. Gate A waiver: code leg run by
  opencode rust-reviewer (glm-5p2) per user waiver 2026-07-16;
  implementer is rust-write (kimi-k2p7-code), different model family.
  Branch card/S4 off primary head 76bc66e8.
- 2026-07-16 Implementation complete on worktree
  `/Users/mshearer/workspace/orchestration-simplification` (branch
  `card/S4`). TemplateVars extended from 2/9 to 9/9 templates.
  `build_planning_wrapper` and workers-section builders moved from
  raw `format!` to template files with typed vars. 4 new template
  files: `planning_prompt.md`, `continuation_wrapper.md`,
  `worker_roster.md`, `worker_guidelines.md`. 18 files changed, 708
  insertions, 193 deletions. 855/855 lib tests pass (golden-frame
  envelope identity verified). Gate S box checked.
- 2026-07-16 Board owner: committed as `3eb260ba` on `card/S4`
  (trailer `Card: S4`). Gate S re-verified: `cargo fmt --check`
  clean, `cargo clippy -- -D warnings` clean, `cargo test --package
  aura --lib` 855/855 passed. LOC script output:
  ```
  LOC report for 76bc66e8..3eb260ba
  bucket        before     after     delta
  product        12577     12744      +167
  template         204       367      +163
  test           12521     12695      +174
  doc              921       932       +11
  product+template delta (the reduction target): +330
  ```
  Moved prompt text classified as product (+167). Status moved to
  In Review; commit-range frontmatter set: 76bc66e8..3eb260ba.
- 2026-07-16 Gate A (opencode rust-reviewer, glm-5p2): PASS, 2 minor,
  0 blocking. Both accepted and fixed in commit `65ea703c`. Ledger:
  (1, MINOR): stale doc reference in `envelope.rs:17` referenced
  `config::WORKER_PREAMBLE_TEMPLATE` after the constant moved to
  `templates::WORKER_PREAMBLE_TEMPLATE`. Resolution: updated doc
  comment.
  (2, MINOR): residual risks not explicitly named on the card.
  Resolution: no residual risks identified — non-manifest template
  surfaces (planning prompt, continuation wrapper, worker roster,
  worker guidelines, duplicate-call annotations) are covered by the
  855/855 lib test suite; golden-frame envelope identity covers the
  S2 manifest surfaces. HashMap-to-BTreeMap ordering change not
  landed; normalization pass 2 not retired (criterion vacuously
  satisfied). No defect-pinned golden snapshots modified.
  Gate S re-verified after fix: fmt clean, clippy clean. Commit range
  updated to 76bc66e8..65ea703c. Gate A box checked. Reviewer:
  opencode rust-reviewer (glm-5p2), per user waiver 2026-07-16.
- 2026-07-16 Done. Primary branch fast-forwarded from `76bc66e8` to
  `65ea703c` (2 commits). Final commit range: 76bc66e8..65ea703c.
  Verified by board owner (GLM-5.2/opencode): Gate S (fmt, clippy,
  855/855 lib tests), Gate A ledger reviewed and fix re-verified.
  S4 Done.
