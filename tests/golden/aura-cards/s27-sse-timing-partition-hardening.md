---
id: S27
title: Harden SSE timing partition invariants
status: done
depends: [S25]
serialize-with: []
lineage: none
executor: any
gates: "S -> A"
user-gates: []
commit-range: c993443..5432ff2
---

# S27: Harden SSE timing partition invariants

Mechanics: [PROCESS.md](../PROCESS.md). Required reading:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Follow-up filed from the
user's review of the S25 parser (ai-experiments `c993443`).

## Scope

ai-experiments repo, `aura-e2e/` only. Do not start while the
concurrent S25 verification session is active in that clone; the
board owner confirms the session is over before dispatch.

## Deliverable

The S25 aggregation guarantees its own partition invariants instead
of inheriting them from upstream stream behavior. Today
`aggregate_timings` adds every event to the totals but adds to
`by_worker` only when `worker_id` is present, and completed tool
events that never matched a `tool_call_started` land in an unnamed
`""` bucket of `by_tool`. A `task_completed` without `worker_id`, or
an unmatched `tool_call_id`, silently breaks the
`sum(by_worker) == total` property the tests assert. Such events are
valid input, not errors: they route to named unattributed buckets so
the gap is visible in the output. What fails loudly is the
reconciliation assertion: named buckets plus unattributed must equal
the totals, and the parser raises on violation instead of reporting
wrong per-worker numbers.
The timing test also gains a committed minimal SSE fixture so it
stops skipping on clean checkouts. The two pre-existing F841 dead
assignments (`benchmark_report.py:211,221`) and the missing ruff
line-length setting, both flagged out of scope on S25, are cleaned up
here.

## Acceptance

- Adversarial parser tests cover a `task_completed` without
  `worker_id` and a `tool_call_completed` with an unmatched
  `tool_call_id`; both route to named unattributed buckets and the
  partition reconciliation still holds.
- The timing tests run, not skip, on a clean checkout via a committed
  minimal fixture named in the test.
- `ruff check` reports no F841 in `benchmark_report.py`; the ruff
  line-length setting is present in the repo config.
- Full aura-e2e suite green; coverage stays above the repo's 80%
  gate.

## Gate checklist

- [x] Gate S: ruff check + ruff format clean; full suite green;
      acceptance output reported verbatim.
- [x] Gate A: fresh-agent review of the invariant tests against the
      failure modes named in the Deliverable above (missing
      `worker_id`, unmatched `tool_call_id`, skipping fixture).

## Branch

ai-experiments repo, direct (no Aura code); commit recorded here at
Done.

## Log

- 2026-07-12 Filed as backlog by the board owner from the user's S25
  review round. Execution deferred until the concurrent S25
  verification session in the ai-experiments clone is declared over.
- 2026-07-12 codex adversarial review (standing rule): unattributed
  events clarified as valid-but-visible with the reconciliation
  assertion as the fail-loud surface; Gate A retargeted at the
  Deliverable's named failure modes. Both findings accepted.
- 2026-07-16 Promoted to Ready by the Fable session preparing the
  next attended GLM opencode wave (planner prep per the
  attended/unattended policy). Dependency S25 done. Scope-note
  precondition stands: the board owner confirms the concurrent S25
  verification session in the ai-experiments clone is over before
  dispatch. Reviewer pre-vet current: `python-write` pins
  kimi-k2p7-code and `python-reviewer` pins glm-5p2 (config verified
  2026-07-16).
- 2026-07-16 In Progress. Board owner (GLM 5.2 opencode, attended)
  confirmed the S25 verification session is over: ai-experiments
  working tree clean at head `c993443` (the committed S25 parser),
  S25 status Done. Dispatching `python-write` (kimi-k2p7-code) as
  executor; Gate A reviewer will be `python-reviewer` (glm-5p2).
  Parallel with S5 (independent repo, no serialize-with conflict).
- 2026-07-17 Implementation complete by `python-write`
  (kimi-k2p7-code). Partition invariants hardened: unattributed
  events route to named buckets (`_unattributed`, `_unmatched`);
  fail-loud reconciliation assertion raises on violation. Committed
  minimal SSE fixture at `tests/fixtures/timings_minimal.sse`. F841
  dead assignments removed from `benchmark_report.py`. Ruff
  line-length setting added to `pyproject.toml`. Board owner
  verified directly: `ruff check .` clean, `ruff format --check .`
  clean, the full suite is green (including 7 new adversarial tests on the
  committed fixture), coverage 83.09% > 80% gate. Committed as
  `8f9f13c` on `mshearer/aura-e2e-tests`. Gate S PASSED. In Review.
- 2026-07-17 Gate A PASSED. Reviewer glm-5p2 (python-reviewer),
  author kimi-k2p7-code (python-write), families differ. Verdict
  PASS, 5 MINOR, 0 BLOCKING. Findings: (1) unrelated ruff cleanups
  inflate diff - advisory, deferred; (2) reconciliation missing
  `sum(by_worker.tool_count) == tool_count` - fixed in `5432ff2`;
  (3) fail-loud raise path uncovered by tests - fixed in `5432ff2`
  (new `test_reconciliation_raises_on_noncomparable_duration`);
  (4) no empty-input edge-case test - advisory, deferred; (5) no
  all-unattributed scenario test - advisory, deferred. Board owner
  re-verified: suite green with ruff clean and coverage above the gate.
- 2026-07-17 Done. Final commit range `c993443..5432ff2`, two
  commits (`8f9f13c` + `5432ff2`) on `mshearer/aura-e2e-tests`.
  Every gate passed and verified by the board owner directly.
- 2026-07-17 Codex frontier review (GPT-5.6-sol) found 2 BLOCKING:
  (1) fix commit `5432ff2` not Gate A reviewed (only `8f9f13c` was);
  (2) Gate S "verbatim output" requirement not met (log had summaries
  only). Also 2 MINOR: stale review packet, stale line count. All
  accepted: verbatim output pasted below, packets regenerated, fresh
  Gate A re-review dispatched on the full final range. Author of all
  commits: kimi-k2p7-code (python-write); fix was delegated to
  kimi-k2p7-code, not authored by the GLM board owner (codex's
  assumption corrected). Fresh Gate A re-review on full range
  `c993443..5432ff2` by glm-5p2 (python-reviewer): PASS, 0 findings.
  Findings 2 and 3 verified correct; no new issues introduced.

## Verbatim Gate S output

```
$ ruff check .
All checks passed!

$ ruff format --check .
16 files already formatted

$ uv run python -m pytest -v
============================= test session starts ==============================
platform darwin -- Python 3.13.5, pytest-9.0.3, pluggy-1.6.0
rootdir: /Users/mshearer/workspace/ai-experiments/aura-e2e
configfile: pyproject.toml
testpaths: tests
plugins: cov-7.1.0
collected 34 items

tests/test_sse_timings.py::test_fixture_is_discoverable_via_shared_helper PASSED [  2%]
tests/test_sse_timings.py::test_per_event_durations_are_extracted PASSED [  5%]
tests/test_sse_timings.py::test_aggregate_matches_per_event_sums PASSED  [  8%]
tests/test_sse_timings.py::test_parse_result_matches_direct_aggregation PASSED [ 11%]
tests/test_sse_timings.py::test_pinned_capture_shape PASSED              [ 14%]
tests/test_sse_timings.py::test_aggregate_reconciles_with_wall_clock PASSED [ 17%]
tests/test_sse_timings.py::TestMinimalFixture::test_committed_minimal_fixture_is_present PASSED [ 20%]
tests/test_sse_timings.py::TestMinimalFixture::test_per_event_durations_are_extracted PASSED [ 23%]
tests/test_sse_timings.py::TestMinimalFixture::test_aggregate_matches_per_event_sums PASSED [ 26%]
tests/test_sse_timings.py::TestMinimalFixture::test_unattributed_task_completed_routes_to_named_bucket PASSED [ 29%]
tests/test_sse_timings.py::TestMinimalFixture::test_unmatched_tool_call_completed_routes_to_named_buckets PASSED [ 32%]
tests/test_sse_timings.py::TestMinimalFixture::test_parse_result_matches_direct_aggregation PASSED [ 35%]
tests/test_sse_timings.py::TestMinimalFixture::test_partition_reconciliation_holds_on_minimal_fixture PASSED [ 38%]
tests/test_sse_timings.py::TestMinimalFixture::test_reconciliation_raises_on_noncomparable_duration PASSED [ 41%]
tests/test_stall_detector.py::TestHardStall::test_canonical_t2_zero_calls_timeout_is_attributed PASSED [ 44%]
tests/test_stall_detector.py::TestHardStall::test_t0_stall_is_not_attributed PASSED [ 47%]
tests/test_stall_detector.py::TestHardStall::test_no_submit_result_with_zero_calls_is_hard_stall PASSED [ 50%]
tests/test_stall_detector.py::TestHardStall::test_provider_failure_is_excluded PASSED [ 52%]
tests/test_stall_detector.py::TestParallelPlans::test_parallel_fanout_does_not_fabricate_chains PASSED [ 55%]
tests/test_stall_detector.py::TestReplanSegmentation::test_task_id_reuse_across_iterations_does_not_chain PASSED [ 58%]
tests/test_stall_detector.py::TestBrokenChain::test_planned_never_started_after_failure PASSED [ 61%]
tests/test_stall_detector.py::TestBrokenChain::test_no_broken_chain_without_failure PASSED [ 64%]
tests/test_stall_detector.py::TestGiveUpAndAnomaly::test_submit_result_only_at_gen2_is_give_up PASSED [ 67%]
tests/test_stall_detector.py::TestGiveUpAndAnomaly::test_synthesis_with_artifact_reads_is_not_give_up PASSED [ 70%]
tests/test_stall_detector.py::TestGiveUpAndAnomaly::test_zero_calls_with_success_is_anomaly_only PASSED [ 73%]
tests/test_stall_detector.py::TestRequery::test_exact_requery_of_non_direct_ancestor PASSED [ 76%]
tests/test_stall_detector.py::TestRequery::test_same_tool_different_args_is_possible_only PASSED [ 79%]
tests/test_stall_detector.py::TestRequery::test_direct_ancestor_overlap_is_not_requery PASSED [ 82%]
tests/test_stall_detector.py::TestSoftStall::test_slow_gen2_task_flags_soft_and_partial PASSED [ 85%]
tests/test_stall_detector.py::TestSoftStall::test_fast_ratio_below_floor_does_not_flag PASSED [ 88%]
tests/test_stall_detector.py::TestSummarize::test_headline_count_dedupes_multi_flag_instances PASSED [ 91%]
tests/test_stall_detector.py::TestSummarize::test_wasted_pct_against_total_task_time PASSED [ 94%]
tests/test_stall_detector.py::TestSummarize::test_analyze_sse_file_stamps_sse_key PASSED [ 97%]
tests/test_stall_detector.py::TestDuplicateTaskStarted::test_retry_restart_appends_record_without_losing_history PASSED [100%]

================================ tests coverage ================================
Name                             Stmts   Miss Branch BrPart  Cover
src/aura_e2e/stall_detector.py     233     32    110     12    83%
TOTAL                              233     32    110     12    83%
Required test coverage of 80.0% reached. Total coverage: 83.09%
============================== 34 passed in 0.13s ==============================
```
