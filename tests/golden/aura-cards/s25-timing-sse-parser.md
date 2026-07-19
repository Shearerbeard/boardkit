---
id: S25
title: Parse timing SSE events in aura-e2e
status: done
depends: []
serialize-with: []
lineage: none
executor: any
gates: "S -> A"
user-gates: []
---

# S25: Parse timing SSE events in aura-e2e

Mechanics: [PROCESS.md](../PROCESS.md). Required reading:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Prerequisite for the S26
sre-hard latency re-measure; filed from the S8 ratification follow-up.

## Scope

ai-experiments repo, `aura-e2e/src/aura_e2e/` only. The SSE stream now
emits per-event `duration_ms` upstream (aura
`crates/aura/src/orchestration/stream_events.rs:60`, asserted in
`stream_events.rs:175` as `"duration_ms":1234`), but the e2e tooling
never parsed it: `sse_parser.py` ignores the field and
`benchmark_report.py:82` (`_sse_duration_secs`) falls back to file
mtime as a wall-clock proxy.

Touch `sse_parser.py` and its test only. Do not touch the dirty
`results-index.json` or any untracked reports in the clone.

## Deliverable

`sse_parser.py` extracts per-event `duration_ms` (and any sibling
timing fields the stream carries) and exposes a per-phase / per-tool
timing aggregation that a latency profile can consume directly from
the SSE, replacing the mtime proxy. A test parses a captured SSE
stream and asserts both per-event and aggregate durations. The parser
documents which event types carry timing.

## Acceptance

- The parser test passes against a real captured sre-hard SSE file
  (name the fixture path in the test).
- Aggregate timing reconciles against a known run's wall clock within
  a stated tolerance; the tolerance and its cause (untimed gaps) are
  documented in the parser or the test.
- `_sse_duration_secs`'s mtime fallback is either replaced by the
  parsed total or explicitly retained with a comment saying why.

## Gate checklist

- [x] Gate S: ruff check + ruff format clean; the parser test passes;
      report the acceptance output verbatim.
- [x] Gate A: fresh-agent review of the parser change and its
      reconciliation against a real run.

## Branch

ai-experiments repo, direct (no Aura code); commit recorded here at
Done. Board owner re-runs one acceptance check before Done.

## Log

- 2026-07-12 Filed and dispatched to a subagent in the same turn
  (board-owner authorized) from the S8 ratification follow-up. In
  Progress. Dispatch brief carries this card, the aura-side emission
  anchors, and the scope rule. Board owner verifies the parser test
  output directly before Done; decision authority stays with the
  board owner.
- 2026-07-12 Gate S verified by the board owner directly: re-ran the
  new test (6/6) and the full suite green (26/26), coverage above the
  repo's 80% gate, in `~/workspace/ai-experiments/aura-e2e`; scope
  confirmed clean (only `sse_parser.py`, the `benchmark_report.py`
  `_sse_duration_secs` seam, and `tests/test_sse_timings.py`;
  `results-index.json` was pre-dirty). Committed at ai-experiments
  `c993443`. `duration_ms` confirmed on exactly two SSE variants:
  `task_completed` and `tool_call_completed`. Flagged out-of-scope:
  pre-existing F841 dead code (`benchmark_report.py:211,221`), the
  repo's missing ruff line-length config, and that the timing test
  skips when no local `.sse` capture is present (captures are
  untracked, so the test is environment-dependent). Gate A
  (fresh-agent diff review) still pending before Done.
- 2026-07-13 Gate A passed. Fresh subagent (no impl context) ran
  `python-review` over `c993443` and signed off with no blocking
  findings; all three acceptance criteria verified PASS (real named
  fixture, tests do not skip, 6/6; reconciliation ratio 0.940 inside a
  documented band; mtime fallback explicitly retained with rationale;
  sole `_sse_duration_secs` caller updated, no NamedTuple leak to other
  `parse_sse_file` callers). Board owner re-ran acceptance directly:
  `test_sse_timings.py` 6/6 and full suite 26/26 green at 83.09%
  coverage (>80 gate) in `~/workspace/ai-experiments/aura-e2e`. Non-
  blocking findings recorded for the S27 partition-hardening card that
  reuses this parser: (a) `test_aggregate_matches_per_event_sums` over-
  asserts `sum(worker.tool_ms) == total_tool_ms`, but `total_tool_ms`
  counts every completed tool event while `worker_tool_ms` only accrues
  when `worker_id` is truthy, so a capture with a coordinator-level tool
  call (empty worker) would fail the test; 0 such events on the pinned
  fixture. (b) reconciliation lower bound `0.75` is looser than the
  measured 0.940 warrants (~0.85 would still flag a silent large drop).
  Both left as-is
  for S25; Done. Commit stays `c993443` (ai-experiments, external repo,
  `lineage: none`).
