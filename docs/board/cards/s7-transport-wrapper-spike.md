---
id: S7
title: Thin transport wrapper spike with a canary harness
status: backlog
depends: [S2]
serialize-with: []
lineage: none
executor: smart
gates: "S -> A -> U"
user-gates: [adopt-or-drop]
---

# S7: Thin transport wrapper spike with a canary harness

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Plan:
[2026-08-04-productionize-verification.md](../../plans/2026-08-04-productionize-verification.md),
stage 6. New standalone repo, per the codex-reviewed ownership
boundary: not in boardkit (which never executes delegations), not in a
skills repo (scripts there do not resolve for consumers).

## Scope

A new repo for the wrapper; boardkit changes limited to naming the
wrapper as an adapter behind a versioned interface once it exists.

## Deliverable

Per the codex REVISE verdict - a thin wrapper first, no MCP surface:

1. One command that runs a delegation with bridge-owned staging (per
   the route's staging contract), a hard deadline with process-group
   kill (no `timeout` binary dependency), a strict result protocol
   (terminal output present, explicit verdict present, no
   auto-rejection markers), and a `mode:`-aware refusal of `--agent`
   for subagent-only opencode agents. Liveness signals are telemetry,
   never automatic kill criteria.
2. A per-job record (id, status, exit, output paths) so stalls and
   empty returns are visible after the fact - today a stalled run
   costs zero and vanishes from budget review.
3. The canary harness: replay one fixed review packet through each
   transport on demand, recording verdict-rate over time - the
   measurement bed that decides whether the wrapper grows toward the
   agy-mcp shape or stays thin.

## Acceptance

- Ten replayed dispatches per transport with recorded outcomes; the
  wrapper's failure classification matches manual inspection on each.
- An empty exit-0 return and a forced stall both produce structured
  failures, not silence.

## Gate checklist

- [ ] Gate S: the wrapper's own test suite; `uv run pytest -q` in
  boardkit if the adapter naming lands.
- [ ] Gate A: adversarial review, focus: staging immutability, crash
  cleanup, and whether the result protocol can pass a verdict-free run.
- [ ] Gate U: adopt-or-drop on the canary numbers against the 63%
  CLI-lane baseline.

## Branch

direct; external commits recorded in the Log as they land.

## Log

- 2026-08-04 Authored from the transport forensics and the codex REVISE
  verdict (thin wrapper, measure, then decide).
