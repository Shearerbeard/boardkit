---
source: https://github.com/mezmo/aura/issues/474
date: 2026-08-09
artifact: ticket
note: "User flagged unreadable: dense single-paragraph defect narration with inline path:line/sha citations burying the finding; org-sourced: keep-or-purge at gate"
---

# Approval decisions on the redis backend leave no durable record

When AURA runs with the Redis session store, resolving a HITL approval persists nothing. The Redis store's `resolve` ignores the decision it is given (the `_decision` parameter at `crates/aura-web-server/src/session_store/redis/approval_store.rs:101-112`, sha `18a37458`) and deletes the parked request record with an atomic `GETDEL` (`approval_store.rs:52-70`) as its at-most-once claim. The decision's only carrier is the wake publish, and that publish is fire-and-forget (`crates/aura/src/hitl/registry.rs:170-188`): if it is lost, the decision is gone, and the parked call waits out its timeout and fails closed even though an operator already approved it. A resolver crash after the `GETDEL` and before the publish loses the decision the same way.

This matters for any deployment that treats approvals as an audit surface: nothing records that a decision happened or what it was. An approval can be granted and never take effect. Cross-instance resolve itself works, and the fail-closed timeout backstop holds - the gap is durability, not routing.

Reproduced deterministically (10/10) on a 2-instance compose rig by suppressing the wake channel and observing the approval fail closed with no recoverable decision.

Durable approval state is in scope for #271; this issue tracks the defect on main until that work lands.

