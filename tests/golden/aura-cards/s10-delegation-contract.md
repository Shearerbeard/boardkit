---
id: S10
title: Delegation-contract reconciliation (W18)
status: backlog
depends: [S9]
serialize-with: []
lineage: accepted-head
executor: smart
gates: "U(mockup) -> S -> A -> U(launch) -> M -> U(baseline)"
user-gates: [mockup, launch, baseline]
---

# S10: Delegation-contract reconciliation (W18)

Plan section: Stage 6 in
[2026-07-11-orchestration-redesign.md](../plans/2026-07-11-orchestration-redesign.md).
Mechanics: [PROCESS.md](../PROCESS.md). Required reading:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md).

## Scope

One behavior variable across exactly three layers, no others: the
`orchestrator_preamble.md` "Task Description Quality" section; the
config playbook TASK DESCRIPTIONS and EXACT-DATA HANDOFF blocks in
`configs/sre-shell-orchestrated.toml`; the `create_plan` `task` field
description in `routing_tools.rs` only if the mockup gate decides the
schema surface is in (historical guard: create-plan-task-sizing 2/6).
Base: the accepted head.

## Deliverable

Resolve the verified contradiction (preamble "replace references with
actual content" versus playbook "concise; path-not-paraphrase") in
favor of evidence-sourced contracts. Bulk data travels as references
to artifacts and paths; values are inlined only when short and
observed; a sourced-versus-asserted distinction stops the coordinator
baking unverified facts into contracts (the conda 0/3 mechanism).

## Acceptance

- Before/after contract mockups for two historical cases (the
  15,261-char reshard task and a conda replan task), rewritten under
  the new guidance.
- A contract-quality rubric (the five-element rubric of
  [2026-07-10-worker-delegation-contract-audit.md](../evidence/2026-07-10-worker-delegation-contract-audit.md)
  plus a sourced-facts check) applied to the N=3 run's task descriptions.
- A recorded baseline decision; rubric scores on file; lineage held.

## Gate checklist

- [ ] Gate U (mockup): the two rewritten contract mockups plus the exact
      wording diff of all changed layers; schema in-or-out decided here.
- [ ] Gate S: fmt, clippy, lib tests (if schema text changed), vale
      on config prose, golden frames re-snapshotted.
- [ ] Gate A: fresh strong-class agent review of the wording diff
      against the layer-contradiction finding in
      [2026-07-11-orchestration-redesign-orientation.md](../evidence/2026-07-11-orchestration-redesign-orientation.md);
      the golden-frame re-baseline checkpoint applies here too.
- [ ] Gate U (launch): provenance, canary, and pre-registered metrics
      and thresholds (as S9) plus the contract-rubric scoring plan.
- [ ] Gate M: N=3 trace-complete; comparison report with rubric scores
      for every task description in the run, conda-env and
      install-windows contracts quoted; S16 sre-hard run alongside.
- [ ] Gate U (baseline): accept or reject against the pre-registered
      thresholds; on rejection, commits move to `evidence/S10`.

## Branch

Local branch `card/S10` off the accepted head; no pushes before gates
pass; rebased onto the primary; commit range recorded here at Done.

## Log

- 2026-07-11 Filed by S0 from the approved plan.
