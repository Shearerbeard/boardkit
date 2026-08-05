---
id: S5
title: Run the never-run Gate T on native opencode routing
status: done
depends: []
serialize-with: []
lineage: none
executor: any
gates: "M -> T"
user-gates: [live-review]
---

# S5: Run the never-run Gate T on native opencode routing

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Plan:
[2026-08-04-productionize-verification.md](../../plans/2026-08-04-productionize-verification.md),
stage 4 - the full handout lives there. Closes stage 4 of
`docs/plans/2026-07-27-opencode-self-knowledge.md`, unchecked since the
AGENTS.md fix shipped.

## Scope

No repo edits. One live native opencode session driven by the user in
~/dev/chore-lottery (venue set by user ruling 2026-08-04),
plus a transcript excerpt saved as evidence next to this card.

## Deliverable

Evidence that a native opencode board-owner session (a) greps its own
agent pins before routing, (b) dispatches the pinned reviewer subagent
through its in-session task tool, (c) never execs `opencode run`, and
(d) stages a `.review/` packet instead of escalating to agy when the
reviewer hits a permission wall. A dated evidence file under
`docs/board/evidence/` with the transcript excerpts.

## Acceptance

- The evidence file exists, shows all four behaviors, and names the
  session date and the model that ran.
- Any failure signature observed (CLI exec, silent agent fallback,
  agy escalation) is filed as a FEEDBACK entry instead of being
  smoothed over.

## Gate checklist

- [x] Gate M: agent-driven dry run per the plan's handout, transcript
  saved.
- [x] Gate T: user runs one real Gate A review from a native opencode
  session on a live card, per the handout.

## Branch

direct

## Log

- 2026-08-04 Authored; the fix this verifies shipped 2026-07-28 and has
  never been proven live.
- 2026-08-05 Gate M skipped by user ruling: the user went straight to
  the live run in their chore-lottery session ("I left the S5 as
  closed") and the live evidence subsumes what a dry run would have
  shown; the skip is recorded here rather than backfilled.
- 2026-08-05 Gate T PASS 🛑 user-run (2026-08-04, chore-lottery, board
  owner kimi-k3, reviewer DeepSeek-V4-Flash-0731). All four behaviors
  evidenced in
  [2026-08-05-s5-gate-t-native-opencode.md](../evidence/2026-08-05-s5-gate-t-native-opencode.md).
  One observation filed and adjudicated: the session had no Gate T
  concept - a kit vocabulary hole, not a session failure; fixed in the
  2026-08-05 drain (Gate T defined in shipped PROCESS.md, doctor
  gate-vocabulary check added). Card DONE.
