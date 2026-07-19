---
id: S6
title: Dead-code sweep
status: done
depends: [S3, S4, S5]
serialize-with: [S3, S4, S5, S17]
lineage: primary
executor: any
gates: "S -> A"
user-gates: []
commit-range: 5fdbdd3f..d2ba2b9d
---

# S6: Dead-code sweep

Plan section: Stage 3 (S6 bullet) in
[2026-07-11-orchestration-redesign.md](../plans/2026-07-11-orchestration-redesign.md).
Mechanics: [PROCESS.md](../PROCESS.md). Required reading:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md).

## Scope

Experiment worktree, deletion only. Depends on S3, S4, and S5 because
it consumes their leftovers. No prompt-surface changes; behavior on
every S2 manifest surface stays byte-identical.

## Deliverable

Removal of `chat_with_timeout` (orchestrator.rs:870), the dead
`prompt_constants`, stale `#[allow(dead_code)]` attributes, and
whatever S3-S5 left behind.

## Acceptance

- Golden-frame envelope identity over the S2 coverage manifest; a
  card that cannot keep it is misfiled and moves to Track B.
- `cargo fmt --check`, `cargo clippy -- -D warnings`, and `cargo test
  --package aura --lib` pass.
- LOC script output for the card's commit range is pasted on this
  card.
- Residual risks outside the manifest are named on this card.
- No prompt-surface changes.
- If normalization pass 2 (the worker-order sort) survived S3/S4, it
  is retired here or the reason it must stay is logged on this card.
- Test accessors in orchestrator.rs that no longer serve a golden
  snapshot or comparison gate are deleted with the other leftovers.

## Gate checklist

- [x] Gate S: fmt, clippy, full lib tests, golden-frame envelope
      identity, LOC script output pasted on the card.
- [x] Gate A: fresh-agent diff review against this card's acceptance;
      rust-review skill applied.

## Branch

Local branch `card/S6` off the base named by `lineage` (the primary
head); no pushes before gates pass; rebased onto the primary. The
board owner sets the `commit-range` frontmatter at In Review and
repeats the final range in the Done log entry.

## Log

- 2026-07-11 Filed by S0 from the approved plan.
- 2026-07-17 Promoted to Ready by the board owner (GLM 5.2 opencode).
  Dependencies S3, S4, S5 all done; no active serialize-with conflict
  (S3, S4, S5, S17 all done). S5 completion unblocked this card.
- 2026-07-17 In Progress. Board owner (Fable, Claude Code, attended)
  created branch `card/S6` off primary head `5fdbdd3f` (S5 promoted
  earlier this session). Dispatching a Claude Sonnet subagent as
  executor; Gate A reviewer will be a fresh-context Fable subagent
  with `rust-review` (models differ, invariant holds). Parallel with
  S18 (doc-only, no worktree overlap: drafts staged outside the
  repos until gate time).
- 2026-07-17 Implementation complete (Claude Sonnet executor).
  Deleted `chat_with_timeout` (no callers), the dead
  `prompt_constants` section/field header module plus its re-export
  and two unit tests, and eight fully-dead `bounding.rs` methods.
  Kept, with evidence: eight `bounding.rs` methods with live
  `cfg(test)` callers, the `ScratchpadBudget` seam (documented
  unwired in `bounding/DESIGN.md`), and the worker-order
  normalization sort (`OrchestrationConfig::workers` is a `HashMap`,
  iteration order still nondeterministic). Board owner verified
  directly on `card/S6`: `cargo fmt --check` clean, `cargo clippy
  --package aura --lib -- -D warnings` clean, `INSTA_UPDATE=no cargo
  test --package aura --lib` green, no `.snap.new` files (golden
  envelope identity holds). Committed as `a3fb98de`.
- 2026-07-17 Gate S PASSED. Deletion-only diff, LOC output below,
  net-negative. In Review; commit-range `5fdbdd3f..d2ba2b9d` set,
  review packet generated.
- 2026-07-17 Gate A PASSED. Reviewer: fresh-context Fable subagent
  (`rust-review`). Author: Claude Sonnet. Families differ. Verdict
  PASS, 1 MINOR, 0 BLOCKING: two comments in `orchestrator.rs`
  (:1069, :1223) still named the deleted `chat_with_timeout`. Fixed
  in commit `d2ba2b9d` (comment-only scrub); board owner re-verified
  clippy + lib suite green.
- 2026-07-17 Fix-commit re-review PASSED (fix-commit re-review duty,
  PROCESS.md Gate A). `commit-range` extended to
  `5fdbdd3f..d2ba2b9d`, packet regenerated over the full range, fresh
  Gate A dispatched on `d2ba2b9d`. Reviewer: fresh-context Fable
  subagent (`rust-review`), differs from the Sonnet author. Verdict
  PASS, 0 findings: the fix is comment-only, no behavior change, no
  stale `chat_with_timeout` reference remains anywhere in `crates/`.
- 2026-07-17 Done. Final commit range `5fdbdd3f..d2ba2b9d`, two
  commits (`a3fb98de` + `d2ba2b9d`), every gate passed and verified
  by the board owner directly. MILESTONE dependency S6 satisfied.

## LOC script output

```
LOC report for S6 (a3fb98de^ -> d2ba2b9d)
bucket        before     after     delta
product        12653     12526      -127
template         367       367        +0
test           12669     12649       -20
doc              932       932        +0
product+template delta (the reduction target): -127
```

## Residual risks

- `bounding.rs` still carries eight `#[allow(dead_code)]` methods
  exercised only under `#[cfg(test)]` (convenience constructors and
  branch helpers for documented business rules). Retiring them means
  rewriting those tests to build fixtures without the constructors -
  out of this card's deletion-only scope. A future card could take
  it.
- `ScratchpadBudget` (struct plus impl, dead by the compiler today)
  is kept because `bounding/DESIGN.md` documents it as an intentional
  not-yet-wired seam (`Agent::scratchpad_budget`). Deleting it would
  contradict a live design decision; wiring it is future-card work.
- `mcp_dynamic.rs:16` carries an unrelated `#[allow(dead_code)]`
  outside the orchestration/S3-S5 scope; not evaluated here.
