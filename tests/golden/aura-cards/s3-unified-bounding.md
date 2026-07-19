---
id: S3
title: Unified bounding module
status: done
depends: [S2]
serialize-with: [S4, S5, S6, S17]
lineage: primary
executor: smart
gates: "S -> A"
user-gates: []
commit-range: 3136fe19..3f75a68f
---

# S3: Unified bounding module

Plan section: Stage 3 (S3 bullet) in
[2026-07-11-orchestration-redesign.md](../plans/2026-07-11-orchestration-redesign.md).
Mechanics: [PROCESS.md](../PROCESS.md). Required reading:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md).

## Scope

Experiment worktree, bounding code in
`crates/aura/src/orchestration/` only. Pure consolidation: behavior
on every S2 manifest surface stays byte-identical. The fail-open
spill defect is NOT fixed here; it is a behavior change and moves to
S14.

## Deliverable

One source of truth for every truncate/summarize/spill decision -
today spread across char-based artifact spill, token-based scratchpad
budget, byte-based observability caps, and ad-hoc `safe_truncate`
literals - behind a typed budget config.

## Acceptance

- Golden-frame envelope identity over the S2 coverage manifest; a
  card that cannot keep it is misfiled and moves to Track B.
- `cargo fmt --check`, `cargo clippy -- -D warnings`, and `cargo test
  --package aura --lib` pass.
- LOC script output for the card's commit range is pasted on this
  card.
- Residual risks outside the manifest are named on this card.
- The fail-open spill defect, plus any siblings found, is recorded on
  S14 rather than fixed here.
- The production seams the S2 harness defers to S3+ are added here,
  and the harness's re-stated builders are retired to direct
  production calls: DESIGN.md R3 (the worker-side append order is
  re-stated test-side because a real seam needs product code) and
  DESIGN.md R8 (conversation-growth and tool-registration order are
  shape-only for the same reason). The matching MANIFEST re-stated
  rows flip to production-emitted. (Amended 2026-07-15, user-approved
  at the step-6 ratification, to the state the codex Gate A
  adjudicated: the R3 rows are production-emitted; the R8
  conversation-growth rows are partially production-emitted - shared
  push helpers, sequence test-side; the R8 tool-registration rows are
  shape-asserted, with a real tool-order seam left as follow-up-card
  scope. MANIFEST and both DESIGN.md files document the same state,
  so the record is in sync.)
- If this card lands the HashMap-to-BTreeMap ordering change that
  DESIGN.md defers to S3/S4, normalization pass 2 (the worker-order
  sort) is retired in the same commit.

## Gate checklist

- [x] Gate S: fmt, clippy, full lib tests, golden-frame envelope
      identity, LOC script output pasted on the card.
      Passed 2026-07-14 (Phase B complete, board-owner re-verified:
      fmt clean, clippy --workspace -D warnings clean, 851/851 lib
      tests, 26/26 golden tests under INSTA_UPDATE=no).
- [x] Gate A: fresh-agent diff review against this card's acceptance;
      rust-review skill applied.
      Codex leg passed 2026-07-14 (codex GPT-5.6 adversarial pass: 4
      BLOCKING + 3 MINOR found, all repaired.
      Finding 1: DuplicateCallPolicy nudge_threshold unwrap_or(0) behavior
      change, fixed to unwrap_or(block). Findings 2-3: R8 tool-order gates
      downgraded to shape-asserted, conversation-growth to partially
      production-emitted, generic-worker R3 test added. Finding 4: residual
      risk list completed. Findings 5-7: LOC explanation, stale prose, Vale
      issues fixed. Re-verify: 851/851 lib tests, 26/26 golden, clippy/fmt
      clean). Code leg passed 2026-07-15: fresh-context Claude (Fable 5)
      Claude Code subagent, gate-probes + rust-review, over the final
      range 3136fe19..3f75a68f; verdict PASS (0 blocking, 6 MINOR, each
      numbered with its disposition in the 2026-07-15 Log entry). The
      2026-07-14 tick was corrected and re-ticked; see the Log.

## Branch

Local branch `card/S3` off the base named by `lineage` (the primary
head); no pushes before gates pass; rebased onto the primary. The
board owner sets the `commit-range` frontmatter at In Review and
repeats the final range in the Done log entry.

## Log

- 2026-07-11 Filed by S0 from the approved plan.
- 2026-07-13 In Progress. Board owner created branch `card/S3` off the
  primary head `3136fe19` in the epic worktree
  `/Users/mshearer/workspace/orchestration-simplification`. Dispatched
  in the S3+S4+S5+S17+S7 wave with S7 as the parallel WIP-2 slot (S7
  is file-disjoint and on an isolated lineage off `9df96382`).
  Executor: opencode `rust-write` subagent (kimi-k2.7-code) per the
  user's session choices. Gate A reviewer: GLM-5.2 `rust-reviewer`
  subagent (user waived the REVIEW-TOOLING Claude-family rule for this
  wave; waiver logged here). Type-discipline cycle applies: skeleton
  with `todo!()` bodies and a co-located DESIGN.md pass the design
  panel (adversarial type reviewer + second-model logic reviewer)
  before implementation. Skeleton phase dispatched first.
- 2026-07-13 Skeleton landed: `bounding.rs` (569 lines, todo!() bodies)
  + `bounding/DESIGN.md` + one `mod bounding;` line in `mod.rs`. cargo
  fmt/check/clippy clean, 842 lib tests pass, zero production call
  sites rewired. Bounding inventory: 28 truncate/summarize/spill sites
  across char/token/byte/ad-hoc mechanisms. 17 public types in the
  skeleton. Design panel returned FAIL (codex GPT-5.6: 8 blocking + 1
  minor; Claude Opus 4.8: 8 blocking + 3 minor - strongly convergent).
  Core defect: the skeleton's strict validation rejects
  production-reachable configs (zero thresholds, nudge >= block,
  summary > threshold, max_tools=0) - a behavior change, not pure
  consolidation. Secondary: unit erasure (bare usize at decision
  boundaries allows byte/char mixing), LogPreviewWidths incomplete
  (missing 5 sites, single task_description for two different widths),
  ScratchpadBudget::new unimplementable (private context_window, no
  error variant), DESIGN.md inventory inaccuracies (char/byte
  mislabel, 4 wrong visibility rows, BoundingError missing from
  inventory).   All findings ACCEPTED; repair brief dispatched to the
  rust-write subagent. Re-review will use codex + GLM-5.2 subagent
  (user paused Claude Code usage for cost).
- 2026-07-13 Repair round 1: subagent applied 8 repairs (ResultSummaryWidth
  enum, DuplicateCallPolicy semantic enums, SizePromotion/DurationPromotion
  split, unit-erasure fix via &str methods, LogPreviewWidths completion,
  ScratchpadBudget infallible, generic widths made private, DESIGN.md fixes).
  Re-review: codex FAIL (5 new blocking - phantom states/errors from the
  repair), GLM-5.2 PASS (2 minor). The empty-result opencode hang hit once;
  subagent partially completed repair round 2 before returning empty.
- 2026-07-13 Repair round 2 (board owner direct): finished remaining repairs
  - removed NudgeOnly (phantom), made DuplicateCallPolicy variant fields use
  private NudgeThreshold/BlockThreshold newtypes (variants matchable but not
  constructable with invalid orderings), added truncate_to_summary method
  (separate from decide for the replan-error site), removed BoundingError
  entirely (no phantom error paths), fixed DESIGN.md R4/R7/type
  inventory/visibility claims. Final codex re-check: PASS (all 6 findings
  resolved, no new blocking). Build: fmt/check/clippy clean, 842/842 lib tests
  pass (flake did not fire). Design panel complete: codex PASS + GLM-5.2
  PASS. Implementation phase dispatched next.
- 2026-07-13 Implementation phase A complete: all 74 todo!() bodies
  implemented in bounding.rs by the board owner (opencode rust-write
  subagent returned empty on 3 attempts - the known MCP-client hang;
  board owner completed the implementation directly). Method bodies
  reproduce exact production behavior: byte-width truncate methods
  use safe_truncate (some with "..." suffix matching truncate_query,
  some without matching direct safe_truncate); char-width methods use
  char_indices/truncation matching FailureHandle/ErrorPreview/truncate_reasoning
  patterns; BoundingConfig::from_orchestration reads OrchestrationConfig
  fields and constructs the typed budget. truncate_to_summary returns
  (String, bool) to serve the replan error site. Build: fmt/clippy clean,
  842/842 lib tests pass, 22/22 golden-frame tests pass (envelope
  identity holds - module is additive, no production call sites rewired).
  Phase B (production call-site wiring) remains for full S3 Done.
- 2026-07-13 In Review. Committed as `b9402edb` on `card/S3`
  (commit range `3136fe19..b9402edb`, 1 commit, 1247 insertions).
  Review packet generated at `docs/redesign/reviews/S3/`
  (REVIEW.md + per-commit diff + full-range.diff). User is reviewing the Phase A
  implementation (the bounding module itself) before the implementation
  Gate A runs and before Phase B (call-site wiring) starts. This is an
  informal user review, not a card-defined U gate (S3 gates are S -> A);
  the user inserted it as a review checkpoint. After the user's review:
  run implementation Gate A (codex review of the implemented bounding.rs),
  then Phase B (wire production call sites to BoundingConfig, golden-frame
  tests must stay green), then S3 Gate S + Gate A for the full card.
- 2026-07-13 User review completed. User approved the module as
  "some of the best rust code we have ever produced" and requested six
  improvements: (1) TruncateMarker primitive to collapse ~13 duplicated
  truncate bodies, (2) typed `pub const DEFAULT: Self` instead of
  `usize`-then-`new`, (3) `TruncatedSummary` implementing
  `std::fmt::Display` instead of a bare `(String, bool)` tuple, (4) a
  bounding unit-test module, (5) doc fixes (ToolReasoningWidth clarity,
  line-number anchor drift hazards), (6) DESIGN.md residual risks R8
  (SessionHistoryLimit compaction future) and R9 (marker inconsistency).
  Fix round dispatched to opencode `rust-write` subagent; all six
  implemented. Gate S: fmt/clippy clean, 849/849 lib tests, 22/22
  golden-frame. Gate A: `rust-reviewer` subagent PASS (0 blocking,
  8 MINOR). All 8 MINOR repaired (truncate_chars→char_indices().nth()
  single-pass, TruncatedSummary+TruncateMarker in DESIGN.md inventory,
  R10 was_truncated signal asymmetry, into_string to avoid double-alloc,
  marker-suppression test, emoji assertion strengthened, drop
  unused_variables from module allow). Gate S re-verify: fmt/clippy
  clean, 850/850 lib tests, 22/22 golden-frame. Committed as `efcafa17`
  (commit range `3136fe19..efcafa17`, 2 commits, 1402 insertions).
  Review packet regenerated. LOC report pasted below. Remaining: Phase B
  (call-site wiring), then full card Gate S + Gate A.
- 2026-07-14 Stage 0 of the Phase B bolus ratified (board-owner Opus
  4.8 session). D2: GLM 5.2 keeps the orchestrator seat; the user
  launches the Phase B GLM session directly and the board owner audits
  it at the card gates (executor-fallback rule covers the opencode
  MCP-client hang). D3: Phase B full-card Gate A runs as a codex
  adversarial pass plus a fresh-context Claude `rust-review` in-session
  subagent; the GLM-5.2 code-review waiver is NOT renewed for Phase B
  (GLM authored the diff, so review stays cross-family). D5: hold the
  wave at S3 (S4/S18 deferred). Phase B stays board-owner-supervised at
  full gate rigor per the S29 retro's GO condition.
- 2026-07-14 Drift fix (board-owner session, pre-Gate-D). The
  2026-07-13 Gate S and Gate A passes (850/850 lib tests, 22/22
  golden-frame, rust-reviewer PASS with 8 MINOR repaired) were Phase A
  (the bounding module itself), not the full card. Per PROCESS.md's
  multi-phase gate-box rule, the card-level Gate S and Gate A boxes
  remain unchecked pending Phase B (production call-site wiring) and
  the full-card gate pass.
- 2026-07-14 In Progress (Phase B). User launched GLM 5.2 session from
  `docs/redesign/plans/2026-07-14-phase-b-kickoff.md`; confirmed good
  reasoning output with the standalone CLI. Board owner flips S3 to
  In Progress and audits at the gates. Phase B: wire production call
  sites to BoundingConfig, golden-frame tests must stay green, then
  full-card Gate S + Gate A.
- 2026-07-14 Phase B complete. GLM 5.2 orchestrator session wired all
  11 consolidation rows to BoundingConfig and closed all three S2
  harness seams (R3 worker, R8 tool-order, R8 conversation-growth).
  Subagent delegations: 4 kimi-k2.6 `rust-write` tasks via opencode
  native `task` tool (1 empty return on first dispatch, succeeded on
  retry; no executor-fallback needed). Gate S (board-owner
  re-verified): `cargo fmt --check` clean, `cargo clippy --workspace
  -- -D warnings` clean, 851/851 lib tests pass, 26/26 golden tests
  green (22 envelope-identity + 4 new R3/R8 comparison gates), all
  under `INSTA_UPDATE=no`. R10 resolved: `truncate_with_flag` on
  char-cap types (option 1). Normalization pass 2 stays (no
  HashMap-to-BTreeMap change this card). LOC report updated below.
  Residual risks named below. No fail-open siblings found beyond R2
  (already on S14). In Review. Commit range
  `3136fe19..6f9a4ab7` (10 commits). Review packet regenerated.
  Gate A: codex GPT-5.6 adversarial pass found 4 BLOCKING + 3 MINOR;
  all repaired (nudge_threshold behavior fix, R8 claim downgrades,
  generic-worker R3 test, residual risk completion, prose fixes).
  Gate A re-verify: 851/851 lib tests, 26/26 golden, clippy/fmt clean.
- 2026-07-15 Gate A un-ticked (board-owner Claude Code session, dated
  correction per the gate-box discipline rule, S29 change 4). The
  2026-07-14 tick rested on the codex leg alone: the D3 code leg (a
  fresh-context Claude `rust-review` subagent as THE code Gate A; codex
  never signs off Rust) never produced a review. The "rust-reviewer
  subagent returned empty" in that tick was the opencode agent of that
  name - config-pinned to GLM-5.2, the family whose code-review waiver
  was NOT renewed for Phase B - and it returned empty after its bash
  allowlist (cargo-only) blocked `git diff` and five agy attempts to
  fetch the diff timed out. It was also pointed at `..5ee5e101`, before
  the repair commit, so the final range has had no code-leg review.
  Session evidence: opencode ses_09ce4b2a5ffeNCcVqGdEJL9O78 (GLM 5.2
  board-owner seat) and child ses_09c4f196dffe4RZ8q1Lw4fRc8o (the empty
  reviewer). Codex findings 1-7 and repair commit 6f9a4ab7 stand; Gate S
  stands. Remediation: Gate D drift fixes land first, then one
  fresh-context Claude Code `rust-review` subagent reviews the final
  full range; the box re-ticks only with that verdict logged.
- 2026-07-15 Gate D drift audit (runbook step 5) run: a fresh-context
  audit agent sampled both DESIGN.md files, the MANIFEST, and
  docs/redesign/ARCHITECTURE.md against card/S3 head `6f9a4ab7`. All
  seam-table rows, gate claims, residual risks, and the type inventory
  verified against code; four prose-only drifts found (D1 MANIFEST
  intro contradicting its flipped rows, D2/D3 stale
  "only-the-accessors" claims in both DESIGN.md files, D4
  "runs scratchpad-disabled" phrasing) and fixed in doc-only commit
  `3f75a68f` on card/S3. ARCHITECTURE.md line anchors have drifted
  (~10 stale, partly pre-dating S3) but its behavioral claims hold;
  by its own update rule (behavior-changing cards only) that is not an
  S3 obligation - logged here as an explicit divergence for a future
  anchor re-verification pass. Commit range extended to
  `3136fe19..3f75a68f` (11 commits); review packet regenerated; LOC
  report updated above. Gate S re-verified at the new head: fmt clean,
  clippy --workspace -D warnings clean, 851/851 lib tests (26 golden
  included) under INSTA_UPDATE=no.
- 2026-07-15 Gate A code leg run and PASSED; Gate A box re-ticked in
  this same turn. Reviewer: fresh-context Claude (Fable 5) subagent
  spawned from the board-owner Claude Code session, skills gate-probes
  + rust-review, over the regenerated packet at the final range
  `3136fe19..3f75a68f`. Verdict: PASS (0 blocking, 6 MINOR). The
  reviewer independently re-ran Gate S (fmt/clippy clean, 851/851 lib,
  26/26 golden, INSTA_UPDATE=no) and byte-compared every consolidation
  site against baseline `3136fe19` (unwrap_or(block) equivalence,
  truncate_chars vs all three baseline char-cap bodies, marker styles
  per site, zero-value semantics on all five zero-capable knobs,
  fail-open path unchanged). Numbered minors with dispositions (full
  ledger: reviews/S3/GATE-A-LEDGER.md, working material; dispositions
  avoid extending the reviewed range):
  1. bounding.rs:9 module doc still calls the wiring future work -
     defer to S6 doc sweep.
  2. evidence.rs:375 rustdoc cites MAX_CHARS but the width parameter
     caps; MAX_CHARS pairs duplicate the bounding DEFAULTs - defer to
     S6 (pairs agree today; rustdoc+tests are the only consumers).
  3. types.rs:698 three new required serde fields on IterationContext
     without #[serde(default)]; no production persistence path today -
     latent hazard, candidate for S14.
  4. orchestrator.rs:543 whole-config clone avoidable with a let
     binding - defer to S6.
  5. orchestrator.rs:135-161 CoordinatorTools duplicated under
     cfg(test)/cfg(not(test)) can silently diverge - defer to S6.
  6. Acceptance bullet 6 still reads "flip to production-emitted" while
     the adjudicated landed state is R3 production-emitted, R8 growth
     partial, R8 tool-order shape-asserted - bullet NOT amended; user
     decides at step-6 ratification (amend, or file the real
     tool-order seam as a follow-up card).
  Runbook steps 1-5 are complete; step 6 (present diff, findings, and
  LOC delta; rebase onto the primary and push) awaits the user's
  explicit go.
- 2026-07-15 Done. User ratified step 6 with three decisions: (1) GO
  on integration; (2) amend acceptance bullet 6 to the adjudicated
  seam state, keeping card/MANIFEST/DESIGN.md in sync (amendment
  applied above, dated); (3) the ARCHITECTURE.md anchor
  re-verification is scheduled as its own card (S30) rather than
  folded into this ratification. Integration executed: the primary
  `mshearer/orchestration-simplification` fast-forwarded
  `3136fe19 -> 3f75a68f` (card/S3 was a direct descendant; no rebase
  rewrite) and pushed to origin; the epic worktree switched back to
  the primary. Final commit range `3136fe19..3f75a68f` (11 commits).
  Gates: S and A both passed and ticked with verifiable output logged
  above; Gate D sampled with findings fixed (`3f75a68f`); the R8
  tool-order seam and the six Gate A minors carry dispositions in the
  2026-07-15 entries (five to S6, serde hazard noted for S14,
  acceptance amendment landed here).

### LOC report (3136fe19..3f75a68f)

```
bucket        before     after     delta
product        11348     12699     +1351
template         204       204        +0
test           12711     13128      +417
doc              695       913      +218
product+template delta (the reduction target): +1351
```

The `product+template` delta rose from +1094 to +1339 between Phase A
and Phase B, then to +1351 with the Gate A repair commit (`6f9a4ab7`:
the nudge-threshold fix, the generic-worker R3 branch, and the R8
claim downgrades; the Gate D fix commit `3f75a68f` is doc-only). Phase B added typed accessor calls, `truncate_with_flag`
methods, the golden-frame seam accessors
(`worker_preamble_for_golden`, `coordinator_tool_order_for_golden`,
`push_user_turn_for_golden`, `push_assistant_turn_for_golden`), and the
`CoordinatorTools` test constructor. The deletion of `truncate_query`
and the removal of `safe_truncate` imports offset some of that growth,
but not all. The 16 `#[allow(dead_code)]` items introduced on the
bounding API surface are a candidate for retirement in a future card.

### Residual risks named on this card

#### Bounding module risks

- **R1 (byte/char mismatch)**: `safe_truncate` operates on UTF-8 bytes
  while several config fields and comments describe "characters." The
  bounding types keep the byte mechanism for byte-bounded surfaces and
  the character mechanism for char-bounded surfaces; aligning the units
  would be a behavior change.
- **R2 (fail-open spill defect)**: deferred to S14. `maybe_create_artifact`
  returns the full unbounded result when persistence fails to write the
  artifact. Not fixed here.
- **R3 (SSE-handler truncation)**: the actual byte caps for SSE fields live
  in the web-server SSE handlers, outside `orchestration/`, so this module
  cannot unify them.
- **R4 (token-counter approximations)**: the prior-work frame uses a
  4-char-per-token heuristic, while the scratchpad budget uses a real
  tokenizer. The two token budgets are not colocated or unified.
- **R5 (HashMap ordering)**: consolidation did not change any iteration
  order; S2 normalization pass 2 (worker-order sort) remains required.
- **R6 (config-load boundary behavior change)**: the repaired skeleton
  models zero thresholds, misordered duplicate-call thresholds,
  `max_tools_per_worker = 0`, and summary wider than threshold as valid;
  any future tightening is a behavior change requiring its own card.
- **R7 (token budgets not colocated)**: `BoundingConfig` centralizes the
  byte/char bounding decisions, display limits, and session-history limit,
  but does not own the scratchpad `ContextBudget` or the prior-work
  `TokenBudget`. `ScratchpadBudget` in bounding.rs is `#[allow(dead_code)]`
  API surface for a future seam.
- **R8 (SessionHistoryLimit compaction future)**: `SessionHistoryLimit`
  models only Disabled or a positive turn count; a future compaction-budget
  option would be a behavior change.
- **R9 (marker inconsistency)**: three marker styles (none, `"..."`, `"…"`)
  preserved byte-identically from production; unifying them would be a
  behavior change.
- **R10 (`was_truncated` signal asymmetry)**: closed in Phase B. Added
  `truncate_with_flag` methods to `FailureHandleWidth` and `ErrorPreviewWidth`
  so the constructors can gate their own markers.

#### Context fixture risks

- **R1 (rig-fork mapping)**: the final provider request is assembled in the
  pinned rig fork (rev `8908530`). Envelope identity at the aura seam is a
  necessary but not sufficient condition for request identity.
- **R2 (timing)**: timestamps are normalized away; time-dependent behavior
  is unverified.
- **R3 (re-stated append orders)**: the coordinator-side preamble append
  order is closed by `gate_r3_coordinator_preamble_matches_create_coordinator`.
  The worker-side order is closed by `gate_r3_worker_preamble_matches_create_worker`
  with scratchpad enabled in config but unwired (the test environment
  has no MCP, so production cannot wire scratchpad tools); the
  scratchpad append position remains a conditional residue. The coordinator vector-store append position is also
  re-stated because the gate runs vector-disabled.
- **R4 (event side effects)**: persistence writes, journal records, stream
  events, and artifact I/O ordering are outside the envelope and unverified.
- **R5 (trace-merge re-statement)**: `gate_r5_trace_merge_matches_persistence_loader`
  closes the production disk-scan merge; the trivial per-task wrapper loop
  around the scan is still reproduced test-side.
- **R6 (MCP-sourced inventory content)**: Summary/Full roster fixtures run
  with `mcp: None`; MCP-sourced tool names/descriptions differ per live
  deployment. Config-derived inventory content is covered.
- **R7 (escape hatch)**: the corpus pins `AURA_ESCAPE_HATCH` unset; the
  stripped-preamble branch is uncovered.
- **R8 (conversation-growth and tool-registration-order)**:
  - *Conversation-growth* is partially closed: `push_user_turn` and
    `push_assistant_turn` are shared with production, but the SEQUENCE (how
    many iterations, in what order) is still constructed test-side.
  - *Tool-registration-order* is a SHAPE ASSERTION, not a production
    comparison: `gate_r8_coordinator_tool_order` mirrors
    `build_agent_with_tools` without calling it directly, so a production
    reordering could false-pass; `gate_r8_worker_tool_order` asserts against
    a hard-coded vector.
