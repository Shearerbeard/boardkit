---
source: https://github.com/mezmo/aura/issues/383
date: 2026-08-09
artifact: ticket
note: "S10 card names this the one ticket that escaped verbose drift (hand-tuned against exemplar #310 plus voice profile); detail stays concrete without narration; org-sourced: keep-or-purge at gate"
---

# [FEATURE]: A2A visibility in server status + a first-party A2A client in aura-cli

## Problem

Two gaps make our own A2A hard to see and hard to exercise.

1. No first-class A2A visibility server-side. A2A is opt-in behind `AURA_ENABLE_A2A`, but
   nothing surfaces whether it's on, its endpoints, or its task-store state the way
   `aura.mcp_status` / the startup banner do for MCP. Today you confirm it by curling
   `/health` or reading the agent card.

2. aura-cli can't drive A2A. The CLI isn't just a client-facing tool, it's our primary dev and
   testing harness against the deployed server, so this gap hurts development and ops, not just
   end users. To send or inspect tasks against our own server we fall back to the external
   `a2acli`, which is a dependency risk on its own: older builds panic before sending anything
   (`rustls: No provider set`), and only newer builds work.

## What we want

- Surface A2A the way we surface MCP: enabled/disabled, endpoints, task store, in the startup
  banner and/or a status event, so it's visible without curl.
- First-party A2A client commands in aura-cli (card / send / stream / get-task / list-tasks /
  cancel), so we can drive and inspect A2A with our own tooling.
- Treat the CLI as an A2A task-management surface too, not just send/inspect: list tasks and
  cancel them, e.g. kill a stuck task against a running deployment.

## Tools and libraries

- `a2a-client-lf` (a2aproject/a2a-rs, import `a2a_client`): the Rust A2A client library. Gives
  `AgentCardResolver`, `A2AClientFactory`, and send/stream/get/list/cancel. CLI driving builds
  on this, so no new transport code.
- `a2a-lf` / `a2a-server-lf` (a2aproject/a2a-rs): what the server already runs on. We track a
  pinned git tag; upstream is active, so worth checking whether to move the pin.
- `a2acli` (package `a2a-cli`, a2aproject/a2a-rs): external A2A CLI, prior art for the command
  surface. Caveat: older builds panic against a plain-HTTP server (`rustls: No provider set`),
  newer builds fix it. That fragility is part of why we want first-party.
- Broader A2A verification tooling we looked at: the A2A TCK (official conformance harness) and
  A2A Inspector (external task-shape web UI). Neither replaces first-party CLI driving (TCK
  checks protocol conformance, not our memory semantics; Inspector is pre-1.0 and blocked by our
  missing CORS layer), but they're the landscape.
- Related: #368 (A2A history omits assistant turns), #330 (A2A streaming/cancel over the bus).
