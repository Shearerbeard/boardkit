---
id: S13
title: Replan-boundary continuity decision
status: backlog
depends: [S9, S10]
serialize-with: []
lineage: none
executor: smart
gates: "S -> A -> U(decision)"
user-gates: [decision]
---

# S13: Replan-boundary continuity decision

Plan section: Stage 7 in
[2026-07-11-orchestration-redesign.md](../plans/2026-07-11-orchestration-redesign.md).
Mechanics: [PROCESS.md](../PROCESS.md). Required reading:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md).

## Scope

No code: a decision card following the S12 shape and artifact
convention, due after the S9 and S10 baseline gates. This is the
conda 0/3 lever. W12 proved a bare channel re-add changes nothing
([2026-07-08-w12-run1-traces/SYNTHESIS.md](../evidence/2026-07-08-w12-run1-traces/SYNTHESIS.md);
the replan rework detail is in
[2026-07-10-worker-delegation-contract-audit.md](../evidence/2026-07-10-worker-delegation-contract-audit.md)),
and the plan's non-goals bar re-adding the removed cross-iteration
channel as-is; the fix routes through contract or thread shape.

## Deliverable

A decision artifact under the S12 convention
(`docs/redesign/evidence/<date>-s13-replan-decision.md`) choosing how
replan-boundary continuity is handled, routed through the delegation
contract or the thread shape, with "keep as is" still delivered as a
decision. The chosen option then becomes a scoped card with its own
gates.

## Acceptance

- The decision artifact exists at the named path by its due gate
  (after the S9 and S10 baseline decisions) and is vale-clean.
- The decision honors the W12 evidence: no bare re-add of the
  removed cross-iteration channel.
- A scoped follow-on card is filed for the chosen option, or the
  keep decision is logged here.

## Gate checklist

- [ ] Gate S: vale on the decision artifact.
- [ ] Gate A: fresh-agent review of the decision against the W12/W13
      evidence and the S9/S10 baseline outcomes.
- [ ] Gate U (decision): user picks the continuity route or keep;
      the decision is logged either way.

## Branch

No code; the decision artifact lands in the adapter repo, direct.

## Log

- 2026-07-11 Filed by S0 from the approved plan.
