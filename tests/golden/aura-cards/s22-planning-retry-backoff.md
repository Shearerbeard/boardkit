---
id: S22
title: Backoff and visibility for the transient planning retry
status: backlog
depends: [MILESTONE]
serialize-with: []
lineage: accepted-head
executor: any
gates: "S -> A -> U(run-decision)"
user-gates: [run-decision]
---

# S22: Backoff and visibility for the transient planning retry

Fix candidate filed from the S8 latency profile
([2026-07-12-s8-latency-profile.md](../evidence/2026-07-12-s8-latency-profile.md)).
Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md).

## Scope

The transient planning retry arm (`orchestrator.rs:1463-1470`, bare
`continue` today; transient classes at `:4366-4371`): a jittered
sleep plus a span or event marking each retry. Error-path behavior
change on a path with no occurrences detected in the S8 profile, so
the expected latency effect in calm runs is near zero; the value is
not hot-looping against an overloaded provider and making future
occurrences measurable (the path emits nothing today).

## Deliverable

A retry arm with jittered backoff and per-retry observability,
verified by fault-injection tests.

## Acceptance

- Fault-injection unit tests exercise the retry arm (backoff applied,
  span or event emitted) and pass.
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

Local branch `card/S22` off the accepted head; no pushes before gates
pass; rebased onto the primary only after the run-decision gate;
commit range recorded here at Done.

## Log

- 2026-07-12 Filed as backlog by the board owner from S8 fix
  candidate 4.
