---
source: https://github.com/mezmo/aura/issues/475
date: 2026-08-09
artifact: ticket
note: "User flagged unreadable: wall-of-prose asymmetry analysis with inline path:line citations in place of structure; org-sourced: keep-or-purge at gate"
---

# Cross-instance cancel leaves the executing instance's subscribers without a terminal frame

In a two-instance deployment, cancel an A2A task through the instance that is not executing it and the executing instance's own subscribers never learn the outcome: their stream closes with no terminal frame, while subscribers relaying through the other instance receive `TASK_STATE_CANCELED` normally. The task store itself ends correct and terminal - only local stream delivery is affected.

The asymmetry is in the subscription paths. A subscriber on the executing instance is served by the local execution stream (`crates/aura-web-server/src/a2a/request_handler.rs:101-102` at `18a37458`); a subscriber on any other instance is served by the bus relay (`request_handler.rs:106-107`). When a cancel arrives at a non-executing instance, that instance drives the cancel and writes the terminal status to the shared store, and the bus carries it to relay subscribers. The executing instance's routed-cancel listener only stops the execution and discards the cancel's events (`bus_bridge.rs:294-310`, including the discard loop), so the local execution stream ends without a terminal frame.

A client that keys off the terminal frame (rather than polling the task store) never receives one, and cannot tell a cancelled task from a dropped connection.

Reproduced deterministically (12/12) on a 2-instance compose rig: send on instance A, subscribe on both, cancel through B; A's subscriber receives only non-terminal frames and a bare stream close.
