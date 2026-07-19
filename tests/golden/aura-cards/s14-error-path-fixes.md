---
id: S14
title: Error-path defect fixes
status: backlog
depends: [S3, MILESTONE]
serialize-with: []
lineage: accepted-head
executor: any
gates: "S -> A -> U(run-decision)"
user-gates: [run-decision]
---

# S14: Error-path defect fixes

Plan section: Stage 7 in
[2026-07-11-orchestration-redesign.md](../plans/2026-07-11-orchestration-redesign.md).
Mechanics: [PROCESS.md](../PROCESS.md). Required reading:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md).

## Scope

Error-path behavior only, from adversarial-review finding 2: the
fail-open unbounded return in `maybe_create_artifact` plus any
sibling defects the S3 defect inventory surfaces. Split out of S3
because it changes behavior, where S3 is pure consolidation.

## Deliverable

Fixes for the fail-open error paths, each verified by fault-injection
unit tests, plus a run-decision record: the user gate decides whether
the change also needs a benchmark run before joining the accepted
head.

## Acceptance

- Fault-injection unit tests exercise each fixed error path and
  pass.
- `cargo fmt --check`, `cargo clippy -- -D warnings`, and `cargo
  test --package aura --lib` pass.
- The run-decision gate records whether a benchmark run is required
  before the fix joins the accepted head, and that decision is
  honored.

## Gate checklist

- [ ] Gate S: fmt, clippy, lib tests, and the fault-injection tests.
- [ ] Gate A: fresh-agent diff review against the S3 defect
      inventory.
- [ ] Gate U (run-decision): user decides whether a benchmark run is
      needed before the fix joins the accepted head.

## Branch

Local branch `card/S14` off the ACCEPTED HEAD: this card changes
behavior (error paths), so it never lands before the MILESTONE
equality replication. No pushes before gates pass; rebased onto the
primary only after the run-decision gate; commit range recorded here
at Done.

## Log

- 2026-07-11 Filed by S0 from the approved plan.
