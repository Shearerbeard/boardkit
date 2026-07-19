---
id: S7
title: Stream assistant text deltas
status: done
depends: [S2]
serialize-with: []
lineage: isolated-branch
executor: any
gates: "S -> A -> M"
user-gates: []
commit-range: 9df96382..7800f00b
---

# S7: Stream assistant text deltas

Plan section: Stage 4 (S7 bullet) in
[2026-07-11-orchestration-redesign.md](../plans/2026-07-11-orchestration-redesign.md).
Mechanics: [PROCESS.md](../PROCESS.md). Required reading:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md).

## Scope

Experiment worktree, isolated branch off the accepted head: the
`event_tx` forwarding sites (orchestrator.rs:1149, 954) and
an adapter SSE-compat integration test. NOT score-neutral by
construction: new SSE events change stream timing and could affect
the adapter's parser, a hard dependency of the catalog gates. Ships
in NO benchmark binary until a decision card promotes it.

## Deliverable

Coordinator and worker `Text` deltas forwarded to `event_tx`, with
reasoning forwarding kept as-is, plus an integration test proving the
adapter SSE parser and the catalog gates pass with the new events.

## Acceptance

- The adapter SSE-compat integration test passes with the new events
  (parser plus catalog gates).
- A local manual streaming check is performed and logged here.
- Reasoning forwarding is unchanged.
- The branch feeds no benchmark binary until a decision card promotes
  it.

## Gate checklist

- [x] Gate S: fmt, clippy, full lib tests, adapter SSE-compat
      integration test green.
- [x] Gate A: fresh-agent diff review against this card's acceptance;
      rust-review skill applied.
- [x] Gate M: adapter-compat run plus the manual SSE check.

## Branch

Local branch `card/S7` off the base named by `lineage` (isolated
branch off the accepted head); no pushes before gates pass; rebased
onto the primary only when a decision card promotes it; the commit
range is recorded here at Done.

## Log

- 2026-07-11 Filed by S0 from the approved plan.
- 2026-07-13 In Progress. Board owner created an isolated-branch
  worktree `/Users/mshearer/workspace/orchestration-simplification-s7`
  on branch `card/S7` off the accepted head `9df96382` (NOT the
  primary head; S7 is a behavior candidate that ships in no benchmark
  binary until a decision card promotes it). Repo map updated in
  PROCESS.md this turn (repo-map duty). Dispatched in parallel with S3
  as the WIP-2 slot; S7 is file-disjoint from the S3-S5-S17 chain
  (separate worktree, separate base). Executor: opencode `rust-write`
  subagent (kimi-k2.7-code). Gate A reviewer: GLM-5.2 `rust-reviewer`
  subagent (user waived the REVIEW-TOOLING Claude-family rule for this
  wave; waiver logged here). Will pause at Gate M for the user's
  manual SSE check plus the adapter-compat run.
- 2026-07-13 Rust implementation complete: Text deltas forwarded at
  worker (orchestrator.rs:954) and coordinator (orchestrator.rs:1149)
  paths, following the existing reasoning-forwarding pattern. Reasoning
  forwarding unchanged. Adapter SSE-compat integration test written
  (tests/test_s7_sse_compat.py, 8 tests, 59 total suite tests pass).
  Gate A: codex GPT-5.6 found 1 blocking (unnecessary t.clone() in both
  forwarding arms) + 2 minor (comment noise, test order-dependence).
  Clone fixed: t moved into StreamedAssistantContent::Text(t) after
  content.push_str(&t). Re-verify: codex PASS. Build: fmt/clippy clean,
  842/842 lib tests pass.   Pausing at Gate M for user.
- 2026-07-13 In Review. Committed as `7800f00b` on `card/S7`
  (commit range `9df96382..7800f00b`, 1 commit, 15 insertions / 1
  deletion). Review packet generated at `docs/redesign/reviews/S7/`
  (REVIEW.md + per-commit diff + full-range.diff). Adapter test
  committed separately in the adapter repo at `04a5e64`
  (tests/test_s7_sse_compat.py, 429 insertions, 8 tests). User is
  reviewing the Rust diff and the adapter test before Gate M. Gate A
  passed (codex GPT-5.6, clone fix applied, re-verify PASS). Remaining:
  Gate M (user's manual SSE check + adapter-compat run), then S7 Done.
  The branch feeds no benchmark binary until a decision card promotes
  it.
- 2026-07-14 Gate D drift fix (board-owner session). Scope code anchor
  corrected: `orchestrator.rs:1142-1144, 954-956` was stale; the
  coordinator Text forwarding arm begins at line 1149, the worker arm
  at line 954 (per codex GPT-5.6 Gate D audit, finding D7).
- 2026-07-14 Gate M (packet review, user). User reviewed the review
  packet at `docs/redesign/reviews/S7/` (1 commit, 15 insertions / 1
  deletion) and the adapter test at `tests/test_s7_sse_compat.py` (8
  tests). Packet passes. Remaining Gate M items: manual SSE streaming
  check and adapter-compat run, using a Fireworks GLM 5.2 orchestrated
  config for richer reasoning output. E2E launching on notanton with
  the S7 binary.
- 2026-07-14 Gate M (manual SSE check + adapter-compat, user). E2E run
  on notanton with S7 binary (`card/S7` branch, sha `d43f2123`) and a
  Fireworks GLM 5.2 orchestrated config
  (`mezmo-orchestrated-glm52-fireworks.toml`). Findings:
  1. Reasoning deltas stream well: both `aura.reasoning`
     (coordinator planning) and `aura.orchestrator.worker_reasoning`
     (worker turns) produce live SSE events. The CLI handles them.
  2. Text deltas do NOT stream in practice. The orchestration
     architecture routes coordinator output as tool calls (routing
     decisions: create_plan, respond_directly, etc.), and worker text
     is collected as the worker response rather than streamed live.
     The final synthesized response goes through a different path that
     does not pass through the `StreamItem::StreamAssistantContent::Text`
     arms the S7 patch wires. The forwarding code is correct but
     dormant under the current architecture; it would activate if the
     orchestration streaming model changes to emit coordinator or
     worker text directly.
  3. The adapter SSE-compat integration test (8 tests) passes,
     confirming the parser handles Text delta events if they do
     appear.
  Gate M passes: the code is correct, reasoning is unchanged, the
  adapter is compat-safe, and the manual check is logged. The Text
  forwarding is infrastructure for a future architecture change, not
  a live feature today. S7 Done.
