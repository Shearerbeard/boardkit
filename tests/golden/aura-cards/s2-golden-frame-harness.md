---
id: S2
title: Experiment worktree and golden-frame harness
status: done
depends: [S0]
serialize-with: []
lineage: primary
executor: smart
gates: "S -> A -> U"
user-gates: [schema]
commit-range: 9df96382..3136fe19
---

# S2: Experiment worktree and golden-frame harness

Plan section: Stage 2 in
[2026-07-11-orchestration-redesign.md](../plans/2026-07-11-orchestration-redesign.md).
Mechanics: [PROCESS.md](../PROCESS.md). Required reading:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md).

## Scope

The new experiment worktree
(`/Users/mshearer/workspace/orchestration-simplification`, primary
branch off `9df96382`): a `context_fixture` test module, snapshot
tests, a checked-in coverage manifest, and consolidation of
`frame_validation_tests.rs`. Additive test code only.

## Deliverable

The typed-context backbone: a context fixture (a complex struct/enum
covering turn counts, prior results, artifacts, budgets, failure
history, and iteration state) plus snapshot tests rendering the
COMPLETE request envelope (system preamble, full message list, and
serialized tool definition JSON) for the coordinator initial planning
call, continuation calls at depths 1-3, and worker calls (frame
populated, empty, and spilled; recon and non-recon; final-iteration
urgency); a byte-identity assertion mode for refactor cards; a
coverage manifest naming every surface and branch the corpus covers
and, explicitly, what it does not.

## Acceptance

- All manifest surfaces render from fixtures; every `%%SLOT%%` and
  `{{slot}}` is exercised by at least one fixture.
- Byte-identity mode is proven by a no-op refactor.
- `frame_validation_tests.rs` cases the snapshots subsume are
  deleted, with a net test-LOC reduction reported.
- The coverage manifest is committed.

## Gate checklist

- [x] Gate S: `cargo fmt --check`, `cargo clippy -- -D warnings`,
      `cargo test --package aura --lib`; every slot exercised.
- [x] Gate A: fresh agent audits the manifest against the anatomy
      doc's block inventory, all 23 preamble blocks plus continuation
      slots ([2026-07-10-coordinator-thread-anatomy.md](../evidence/2026-07-10-coordinator-thread-anatomy.md)),
      and the tool-definition surfaces (create_plan schema included).
- [x] Gate U (schema): user reviews the fixture type design and the
      coverage manifest; this is the context schema the epic builds on.

## Branch

Local branch `card/S2` off the base named by `lineage` (the primary
head); no pushes before gates pass; rebased onto the primary; the
commit range is recorded here at Done.

## Log

- 2026-07-11 Filed by S0 from the approved plan.
- 2026-07-12 In Progress, pulled in the four-card bolus (S1+S2+S8+S16)
  per the approved bolus plan. WIP-2 deviation authorized by the user:
  all four cards are file-disjoint per the epic fan-out policy.
  Worktree `/Users/mshearer/workspace/orchestration-simplification`
  (primary branch off `9df96382`), card branch `card/S2`. The schema
  Gate U is pre-authorized for unattended execution with a user-approved
  decision packet (insta snapshots; test-side normalization, no product
  code changes; depths = continuation calls 2-4; replan-boundary as a
  distinct manifest branch; source-built session-history fixture;
  config-driven recon branch); the type skeleton still passes a
  two-layer rust-expert review before implementation, and the full
  design record goes to morning ratification.
- 2026-07-12 Type skeleton landed on card/S2 at worktree commit
  `710112b0` (initially `047652f3`, amended by the repair round):
  a #[cfg(test)] context_fixture module (facade + scenario.rs +
  envelope.rs + normalize.rs + DESIGN.md + MANIFEST.md, 1,606
  insertions, todo!() bodies), insta dev-dependency, and three
  #[cfg(test)] delegating accessors in orchestrator.rs as the only
  product-file delta. Adversarial design panel: the DMMF reviewer
  caught the fixture types encoding a production-unreachable state
  (generic-worker vector append; the append is role-branch-only at
  orchestrator.rs ~717) and codex found ten logic issues including
  false-pass coverage claims, synthetic append/tool combinations, a
  normalization design that could rewrite payload bytes, and a
  session-history ordering inversion; the coverage reviewer signed
  off with two minors. All findings repaired and dispositioned in
  DESIGN.md/MANIFEST.md; the repair promoted the R3/R5
  byte-comparison gates from mitigation candidates to REQUIRED
  implementation steps. Board owner re-ran cargo check, clippy -D
  warnings, and fmt --check directly (all clean) and verified the
  additive-only diff and Card trailer. Schema gate record staged for
  morning ratification per the pre-authorization; implementation
  proceeds against the repaired manifest.
- 2026-07-12 In Review. Implementation complete on card/S2 and
  fast-forwarded onto the primary: commit range
  `9df96382..99ab559e`, six commits from `710112b0` through
  `99ab559e` (skeleton, corpus+gates, subsumption, coverage records,
  panel repairs; every commit carries the Card: S2 trailer).
  Delivered: 18 complete-envelope insta snapshots over 27 corpus
  tests; both REQUIRED comparison gates landed (R3 coordinator
  preamble byte-equals real create_coordinator output; R5 trace merge
  equals the production persistence loader); byte-identity mode
  proven with a positive no-op refactor AND a one-byte negative
  control (coordinator snapshots failed, workers stayed green),
  transcript in DESIGN.md; 29 frame_validation_tests cases deleted
  (1,992 to 1,164 lines) with a named deletion ledger and two new
  owning tests for previously owner-less paths. Gate S verified by
  the board owner directly: fmt, clippy -D warnings, 842/842 lib
  tests under INSTA_UPDATE=no, 18 snapshots, zero pending. Gate A:
  rust reviewer and manifest auditor both signed off after
  independent re-verification; codex found 3 blocking record issues
  (non-discriminating slot witness, ledger gaps, C8 boundary), all
  repaired with dispositions. RATIFICATION ITEMS for the morning
  gate: (1) a fourth #[cfg(test)] pure-delegation accessor beyond
  the skeleton's three, needed by the R3 gate; (2)
  WorkerRosterFixture gained a vector-stores catalog argument beyond
  the approved schema; (3) ACCEPTANCE DEVIATION: net test-LOC
  reduction did not materialize, measured +2,391 test .rs lines over
  the fixed boundary (the corpus infrastructure outweighs the 828
  deleted lines); (4) scripts/loc_measure.py misclassifies harness
  .rs as product and markdown as template, needs fixing before C8
  sums card deltas. One unexplained single-test flake observed once
  then absent across 12 consecutive clean runs; watch during S3-S6.
- 2026-07-12 User dispositions at morning ratification. Card stays In
  Review pending the user's own code review, the schema Gate U, and
  the Aura primary push; only the LOC items are decided here. (3) The
  net test-LOC acceptance deviation is ACCEPTED for this card: the
  reduction target belongs to the epic cumulative (S17 deletes the
  brittle suite next), not to the card that builds the corpus infra.
  (4) `scripts/loc_measure.py` fixed in the adapter (fix commit
  `9d8f9da`): a general `#[cfg(test)] mod NAME;` detector routes
  harness .rs to the test bucket and a new doc bucket holds design
  records and ledgers, so the C8 target is trustworthy. Recomputed
  over `9df96382..99ab559e`: product +46, template +0 (reduction
  target +46, was falsely +3819), test +2396, doc +695 (DESIGN 368 +
  MANIFEST 247 + slot_coverage.sh 80). Residual: the +46 is ~+2
  release-compiled lines (mod.rs) plus ~44 cfg(test) accessor lines
  the tool conservatively books as product. Deviations (1) the fourth
  cfg(test) accessor and (2) the WorkerRosterFixture vector-stores
  argument still await the schema Gate U verdict.
- 2026-07-12 User code-review round dispositions. Tracker-speak
  comments stay for card-executor steering during the epic and are
  stripped by the new S28 sweep before the PR re-cut. Retirement of
  the harness scaffolding (re-stated builders, normalization pass 2,
  defect-pinned snapshots) moved into S3-S6 acceptance bullets. The
  cfg(test) gate at the mod.rs declaration site was confirmed
  sufficient; no per-file marker comment wanted. User ordered the
  corpus module renamed to golden_tests; rename lands as a repair
  commit this session. `commit-range` frontmatter added for the new
  review-packet tooling.
- 2026-07-12 Rename landed in the worktree working tree (corpus.rs to
  golden_tests.rs, facade mod decl, three envelope.rs doc refs,
  DESIGN.md/MANIFEST.md path refs; snapshots untouched by design
  since their names derive from the normalize module path). Gate S
  re-verified directly by the board owner: fmt clean, clippy
  --all-targets -D warnings clean, 842/842 lib tests under
  INSTA_UPDATE=no with zero pending, slot_coverage.sh PASS. Gate A
  fresh-agent grep review: PASS, zero module/file corpus references
  remain crate-wide. Committed as `3136fe19` on card/S2; the primary
  fast-forwarded to match and `commit-range` extended to
  `9df96382..3136fe19` (seven commits).
- 2026-07-12 Gate U (schema) PASSED. The user reviewed the type and
  function surface (signatures-only render of the fixture schema plus
  the coverage manifest) and approved, accepting both deviations: (1)
  the fourth cfg(test) accessor `coordinator_preamble_for_golden`
  (the R3 gate needs the real preamble) and (2) the
  `WorkerRosterFixture` vector-stores catalog argument (a real
  envelope input). The user set the standing design intent for the
  corpus: snapshots are complete, human- and agent-readable renders
  of the final state the model receives, in the expect-test
  discipline (Minsky, Bug Bash 2026); they mirror the current
  baseline rendering, defects pinned, and roll forward only through
  intentional ledgered re-pins. The principle is carried into S17's
  charter. Remaining before Done: the Aura primary push decision.
- 2026-07-12 Done. The user approved the push after commitlint
  verified the range clean (0 problems, 1 references-empty warning);
  the primary `mshearer/orchestration-simplification` is on the aura
  origin at `3136fe19`, no PR opened. Final commit range
  `9df96382..3136fe19`, seven commits, every gate passed and
  verified as logged above. S3, S4, S5, S17, S23, S24, and S7 are
  unblocked for the next wave.
