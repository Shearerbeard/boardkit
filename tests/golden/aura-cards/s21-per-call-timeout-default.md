---
id: S21
title: Real default for per_call_timeout_secs
status: backlog
depends: [MILESTONE]
serialize-with: []
lineage: accepted-head
executor: any
gates: "S -> A -> U(run-decision)"
user-gates: [run-decision]
---

# S21: Real default for per_call_timeout_secs

Fix candidate filed from the S8 latency profile
([2026-07-12-s8-latency-profile.md](../evidence/2026-07-12-s8-latency-profile.md)).
Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md).

## Scope

One default in `aura-config/src/orchestration.rs:580-582` (0 =
unbounded today; the consumer at `orchestrator.rs:879-882` skips the
timeout wrap entirely) plus a retry-once-on-timeout decision at the
same consumer. Error-path behavior change, so it follows the S14
shape: fault-injection tests, and its user gate decides whether a
benchmark run is needed before joining the accepted head.

## Deliverable

A bounded per-call default (about 300s; the worst observed completed
call in the S8 profile is 105.6s, so 300s carries roughly 3x margin)
converting a hung provider call from a 900s task loss into a bounded
retryable failure.

## Acceptance

- Fault-injection unit tests exercise the timeout and retry paths and
  pass.
- `cargo fmt --check`, `cargo clippy -- -D warnings`, and `cargo test
  --package aura --lib` pass.
- The run-decision gate records whether a benchmark run is required
  before the change joins the accepted head, and that decision is
  honored.

## Gate checklist

- [ ] Gate S: fmt, clippy, lib tests, fault-injection tests.
- [ ] Gate A: fresh-agent diff review.
- [ ] Gate U (run-decision): user decides whether a benchmark run is
      needed before the change joins the accepted head.

## Branch

Local branch `card/S21` off the accepted head; no pushes before gates
pass; rebased onto the primary only after the run-decision gate;
commit range recorded here at Done.

## Log

- 2026-07-12 Filed as backlog by the board owner from S8 fix
  candidate 3.
