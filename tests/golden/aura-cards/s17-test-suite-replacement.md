---
id: S17
title: Orchestration test-suite replacement
status: done
depends: [S2]
serialize-with: [S3, S4, S5, S6]
lineage: primary
executor: smart
gates: "S -> A -> U(deletion-list)"
user-gates: [deletion-list]
commit-range: "a40173d6..76bc66e8"
---

# S17: Orchestration test-suite replacement

Plan section: Stage 3 in
[2026-07-11-orchestration-redesign.md](../plans/2026-07-11-orchestration-redesign.md).
Mechanics: [PROCESS.md](../PROCESS.md). Required reading:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md).

## Scope

Test-only, envelope-neutral by construction: the roughly 1,140 inline
orchestrator.rs test lines, the remaining `frame_validation_tests.rs`
stragglers, and the live integration targets. Serializes with S3 and
S6, which share the orchestrator.rs inline-test lines, per the
fan-out policy.

## Deliverable

An audit classifying each existing orchestration test as necessary
coverage or brittle, and frame-per-state verification tests built on
the S2 harness replacing the brittle set, so editing a frame and its
code IS editing the tests. Net test-LOC reduction reported.

Design principle (user, 2026-07-12, at the S2 schema gate): the
replacement tests follow the expect-test discipline (Minsky, "Now
more than ever: building reliable software in the age of agents",
Bug Bash 2026). Every test's artifact is a complete, human- and
agent-readable render of the final state the model receives, not
assertion fragments; the corpus mirrors the current rendering and
rolls forward only through intentional, ledgered snapshot re-pins in
the same commit as the behavior change.

## Acceptance

- Every existing orchestration test is classified; the deletion list
  (especially any live integration test) is presented at Gate U
  before removal.
- fmt, clippy, full lib tests, and golden-frame envelope identity
  pass; the LOC script output pasted on this card shows a net
  test-LOC reduction.

## Gate checklist

- [x] Gate S: fmt, clippy, full lib tests, golden-frame envelope
      identity, LOC script output pasted on the card.
- [x] Gate A: fresh-agent diff review against this card's
      acceptance; rust-review skill applied.
- [x] Gate U (deletion-list): user reviews the deletion list,
      especially any live integration test, before removal.

## Branch

Local branch `card/S17` off the primary; no pushes before gates pass;
rebased onto the primary; commit range recorded here at Done.

## Log

- 2026-07-11 Filed by S0 from the approved plan.
- 2026-07-16 Promoted to In Progress by board owner (GLM-5.2/opencode).
  User approved 3-card bolus (S17 + S23 parallel, S4 after). Gate A
  waiver: code leg run by opencode rust-reviewer (glm-5p2) per user
  waiver 2026-07-16; implementer is rust-write (kimi-k2p7-code),
  different model family. Branch card/S17 off primary head 311b7598.
- 2026-07-16 Implementation complete on worktree
  `/Users/mshearer/workspace/orchestration-simplification` (branch
  `card/S17`). Classification: 5 brittle tests deleted (no live
  integration tests removed), 3 golden-frame fixtures added, coverage
  remapped in `MANIFEST.md`. `cargo fmt --check`, `cargo clippy -- -D
  warnings`, and `cargo test --package aura --lib` pass (839/839; one
  flaky `openinference_exporter` failure on first run, passed on clean
  re-run). Manual line-count estimate: net test-LOC reduction of ~374
  lines (frame_validation_tests.rs 1164 -> 692; orchestrator.rs test
  region ~1140 -> 1112; golden_tests.rs 1647 -> 1773). Official
  `scripts/loc_measure.py` output pending because the board owner owns
  git commits and the script requires a commit range. Temporary
  `.cargo/config.toml` (used to set `INSTA_UPDATE=always` for snapshot
  generation) is now empty but still present in the worktree; needs
  removal by the board owner.
- 2026-07-16 Board owner: committed as `3d3dbb6c` on `card/S17`
  (trailer `Card: S17`). Removed empty `.cargo/config.toml`. Gate S
  re-verified by board owner: `cargo fmt --check` clean, `cargo clippy
  -- -D warnings` clean, `cargo test --package aura --lib` 839/839
  passed. LOC script output:
  ```
  LOC report for 311b7598..3d3dbb6c
  bucket        before     after     delta
  product        12462     12462        +0
  template         204       204        +0
  test           12919     12552      -367
  doc              915       919        +4
  product+template delta (the reduction target): +0
  ```
  Net test-LOC reduction: 367. Product+template delta: 0 (envelope
  neutral). Gate S box checked. Status moved to In Review;
  commit-range frontmatter set: 311b7598..3d3dbb6c.
- 2026-07-16 Gate A (opencode rust-reviewer, glm-5p2): FAIL, 1
  blocking + 3 minor. All 4 accepted and fixed in commit `59f2794f`.
  Ledger:
  (1, BLOCKING): MANIFEST row 147 falsely claimed
  `test_continuation_all_failure_categories` was deleted when it
  still existed. Resolution: deleted the test (golden fixture covers
  all 10 FailureCategory variants vs 8 in the unit test).
  (2, MINOR): `test_continuation_full_scenario` and
  `test_session_history_full_scenario` not named in MANIFEST remap.
  Resolution: added explicit rows naming both tests and their
  coverage distribution.
  (3, MINOR): `test_vector_store_tool_name_format` and
  `test_artifact_threshold_below_does_not_create` lack per-test
  classification. Resolution: classified here —
  `test_vector_store_tool_name_format` was tautological (tested
  `format!` macro output, not production logic);
  `test_artifact_threshold_below_does_not_create` was a noop (created
  fresh persistence, never exercised the threshold code path, only
  asserted empty list). Both genuinely zero-value.
  (4, MINOR): stale cross-reference in `catch_all_manifest` doc
  comment. Resolution: updated to reflect the catch-all is now
  covered by `session_history_catch_all`.
  Gate S re-verified after fixes: fmt clean, clippy clean, 838/838
  passed. Updated LOC: test 12919 -> 12521 (-398), product+template
  +0. Commit range updated to 311b7598..59f2794f. Gate A box
  checked. Reviewer: opencode rust-reviewer (glm-5p2), per user
  waiver 2026-07-16.
- 2026-07-16 Gate U (deletion-list): APPROVED. User approved the
  6-test deletion list. No live integration tests in the list; all 6
  are inline unit tests replaced by golden-frame coverage or
  genuinely zero-value. Gate U box checked.
- 2026-07-16 Done. Rebased `card/S17` onto primary (now at
  `a40173d6` after S23 merge); rebase clean. Primary branch
  `mshearer/orchestration-simplification` fast-forwarded from
  `a40173d6` to `76bc66e8` (2 S17 commits). Final commit range:
  a40173d6..76bc66e8. Gate S re-verified after rebase: fmt clean,
  clippy clean, 838/838 lib tests passed. LOC: test 12919 -> 12521
  (-398), product+template +0. Verified by board owner
  (GLM-5.2/opencode): Gate S, Gate A ledger, Gate U approval all
  recorded. S17 Done.
