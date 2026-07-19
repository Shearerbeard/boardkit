---
id: S5
title: Artifact module consolidation
status: done
depends: [S2]
serialize-with: [S3, S4, S6, S17]
lineage: primary
executor: smart
gates: "S -> A"
user-gates: []
commit-range: 65ea703c..5fdbdd3f
---

# S5: Artifact module consolidation

Plan section: Stage 3 (S5 bullet) in
[2026-07-11-orchestration-redesign.md](../plans/2026-07-11-orchestration-redesign.md).
Mechanics: [PROCESS.md](../PROCESS.md). Required reading:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md).

## Scope

Experiment worktree, artifact-handling code only: persistence.rs,
orchestrator.rs, context/evidence.rs, and tools/read_artifact.rs.
Pure consolidation: behavior on every S2 manifest surface stays
byte-identical; a card that cannot keep envelope identity is misfiled
and moves to Track B.

## Deliverable

One owner module for artifact storage, spill trigger, pointer render,
and the read tool, today split across the four files above. Facade
per the rust-modules discipline; net-negative LOC.

## Acceptance

- Golden-frame envelope identity over the S2 coverage manifest.
- `cargo fmt --check`, `cargo clippy -- -D warnings`, and `cargo test
  --package aura --lib` pass.
- LOC script output for the card's commit range is pasted on this
  card and shows a net-negative delta.
- Residual risks outside the manifest (artifact I/O ordering among
  them) are named on this card.
- Any defect-pinned golden snapshot this card fixes (MANIFEST names
  defects A, B, C, and E as pinned current-production output) is
  updated in the same commit that fixes the defect, with a ledger
  line on this card naming defect and snapshot.

## Gate checklist

- [x] Gate S: fmt, clippy, full lib tests, golden-frame envelope
      identity, LOC script output pasted on the card.
- [x] Gate A: fresh-agent diff review against this card's acceptance;
      rust-review skill applied.

## Branch

Local branch `card/S5` off the base named by `lineage` (the primary
head); no pushes before gates pass; rebased onto the primary. The
board owner sets the `commit-range` frontmatter at In Review and
repeats the final range in the Done log entry.

## Log

- 2026-07-11 Filed by S0 from the approved plan.
- 2026-07-16 Promoted to Ready by the Fable session preparing the
  next attended GLM opencode wave (planner prep per the
  attended/unattended policy). Dependency S2 done; no active
  serialize-with conflict (S3, S4, S17 done; S6 still backlog).
  Reviewer pre-vet current: `rust-write` pins kimi-k2p7-code and
  `rust-reviewer` pins glm-5p2 (config verified 2026-07-16), so the
  author/reviewer families differ as Gate A requires.
- 2026-07-16 In Progress. Board owner (GLM 5.2 opencode, attended)
  created branch `card/S5` off primary head `65ea703c` in the
  orchestration-simplification worktree. Dispatching `rust-write`
  (kimi-k2p7-code) as executor; Gate A reviewer will be
  `rust-reviewer` (glm-5p2). Parallel with S27 (independent repo,
  no serialize-with conflict).
- 2026-07-17 Implementation complete by `rust-write` (kimi-k2p7-code).
  Consolidated artifact runtime into
  `crates/aura/src/orchestration/persistence/artifacts/`
  (`mod.rs` 16, `storage.rs` 679, `spill.rs` 168, `read_tool.rs` 641
  lines) with `persistence.rs` as facade and thin
  `tools/read_artifact.rs` re-export. Updated `orchestrator.rs` and
  `context/evidence.rs` imports. Tracked-file delta: 49 insertions,
  1768 deletions. Board owner verified directly: `cargo fmt --check`
  clean, `cargo clippy --package aura --lib -- -D warnings` clean,
  `INSTA_UPDATE=no cargo test --package aura --lib` all pass
  (golden-frame envelope identity holds). LOC measurement
  pending commit (script reads commit range via `Card: S5` trailer).
- 2026-07-17 Gate S PASSED. Board owner committed as `183f1934` on
  `card/S5` (commit range `65ea703c..183f1934`). LOC script output:
  product 12744→12642 (-102), template 367→367 (+0), test
  12695→12582 (-113), doc 932→932 (+0); reduction target
  (product+template) = -102, net-negative. No defect-pinned golden
  snapshots were changed. In Review; review packet generated.
- 2026-07-17 Gate A PASSED. Reviewer glm-5p2 (rust-reviewer), author
  kimi-k2p7-code (rust-write), families differ. Verdict PASS, 5
  MINOR, 0 BLOCKING. All 5 findings fixed in commit `5fdbdd3f`:
  (1) lock guard moved before lock_persistence, (2) four manifest
  tests restored, (3) dead Err fallback removed, (4) TOCTOU comment
  and # Errors rustdoc restored, (5) module doc reworded. Board
  owner re-verified: all lib tests pass, fmt/clippy clean. LOC over
  full range: product+template -91 (net-negative).
- 2026-07-17 Done. Final commit range `65ea703c..5fdbdd3f`, two
  commits (`183f1934` + `5fdbdd3f`), every gate passed and verified
  by the board owner directly. S6 unblocked (depends S3, S4, S5 all
  done).
- 2026-07-17 Codex frontier review (GPT-5.6-sol) found 2 BLOCKING:
  (1) fix commit `5fdbdd3f` not Gate A reviewed (only `183f1934`
  was); (2) [S27-specific, see S27 card]. Also 2 MINOR: stale review
  packet (omitted fix commit), stale storage.rs line count (679 vs
  745). All accepted: packets regenerated over full range, line count
  corrected, fresh Gate A re-review dispatched on the full final
  range. Author of all commits: kimi-k2p7-code (rust-write); fix was
  delegated to kimi-k2p7-code, not authored by the GLM board owner
  (codex's assumption corrected). Fresh Gate A re-review on full range
  `65ea703c..5fdbdd3f` by glm-5p2 (rust-reviewer): PASS, 0 findings.
  All 5 original fixes verified correct; no new issues introduced.
- 2026-07-17 Promoted onto the primary by the Fable vetting session:
  `mshearer/orchestration-simplification` fast-forwarded
  `65ea703c..5fdbdd3f` and checked out in the epic worktree. The
  session re-ran the full lib suite at this sha before promotion
  (green, no failures) and updated the PROCESS.md topology pin (which had
  gone stale at `3136fe19`) in the same turn per the repo-map duty.

## LOC script output

```
LOC report for S5 (183f1934^ -> 5fdbdd3f)
bucket        before     after     delta
product        12744     12653       -91
template         367       367        +0
test           12695     12669       -26
doc              932       932        +0
product+template delta (the reduction target): -91
```

## Residual risks

- Artifact I/O ordering is filesystem-dependent (the production trace
  loader's within-iteration file order); this card does not change
  that behavior but the consolidation surfaces it as a named risk
  outside the S2 manifest.
- `persistence/artifacts/storage.rs` (745 lines including restored
  tests) is large but focused on `ExecutionPersistence` I/O; a future
  card could split it further if it grows.

## Gate A findings ledger

Reviewer: glm-5p2 (rust-reviewer). Author: kimi-k2p7-code (rust-write).
Families differ. Verdict: PASS, 5 MINOR, 0 BLOCKING.

1. MINOR - Lock acquired on inline-fit path (control-flow change).
   `maybe_create_artifact` now calls `lock_persistence` before the
   `allows_inline` check, changing trace shape. Disposition: fix -
   move the guard before the lock.
2. MINOR - Four manifest tests deleted, not relocated (coverage loss).
   `test_manifest_serde_roundtrip`, `test_write_manifest`,
   `test_write_manifest_disabled`, `test_run_status_serde` removed
   from persistence.rs and not moved to storage.rs. Disposition: fix
   - restore them in the appropriate module.
3. MINOR - Speculative fallback for unreachable failure mode
   (`spill.rs:129-132`). `SpilledArtifact::new` only errors on empty
   filename, which `write_result_artifact` guarantees non-empty.
   Disposition: fix - remove the dead Err branch.
4. MINOR - Move stripped "why" comments and rustdoc `# Errors`
   sections. The `drain` TOCTOU comment, `# Errors` docs on
   `SpilledArtifact::new` and `ArtifactRef::new`, and the
   `TrailingFooter` domain-invariant doc were dropped. Disposition:
   fix - restore at minimum the TOCTOU comment and `# Errors` docs.
5. MINOR - Change narration in module doc (`mod.rs:3-5`).
   "consolidates", "previously split" goes stale. Disposition: fix
   - reword to describe what the module is.

All 5 findings fixed in commit `5fdbdd3f` on `card/S5`. Board owner
re-verified directly: `cargo fmt --check` clean, `cargo clippy
--package aura --lib -- -D warnings` clean, `INSTA_UPDATE=no cargo
test --package aura --lib` green (852 original + 4 restored
manifest tests).
