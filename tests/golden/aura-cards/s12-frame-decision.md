---
id: S12
title: Evidence-frame fix-or-remove decision (W19)
status: backlog
depends: [S9, S10]
serialize-with: []
lineage: none
executor: smart
gates: "S -> A -> U(decision)"
user-gates: [decision]
---

# S12: Evidence-frame fix-or-remove decision (W19)

Plan section: Stage 7 in
[2026-07-11-orchestration-redesign.md](../plans/2026-07-11-orchestration-redesign.md).
Mechanics: [PROCESS.md](../PROCESS.md). Required reading:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md).

## Scope

No code: the epic's committed W19 deliverable is a decision with a
named artifact, due after the S9 and S10 baseline gates. The chosen
option then becomes a scoped card with its own gates; this card does
not implement it.

## Deliverable

`docs/redesign/evidence/<date>-s12-frame-decision.md`, choosing fix,
remove-with-replacement, or keep, against the W19 falsifiable
statement (the W19 card in [BOARD.md](../BOARD.md); audit basis:
[2026-07-10-worker-delegation-contract-audit.md](../evidence/2026-07-10-worker-delegation-contract-audit.md)).
Removal requires a named replacement channel (web
counter-evidence: bare removal reproduces a known coupled-task
failure). "Keep as is" is still delivered as a decision, not by
letting the due gate lapse.

## Acceptance

- The decision artifact exists at the named path by its due gate
  (after the S9 and S10 baseline decisions) and is vale-clean.
- The decision answers the W19 falsifiable statement and names a
  replacement channel if the choice is removal.
- A scoped follow-on card is filed for the chosen option, or the
  keep decision is logged here.

## Gate checklist

- [ ] Gate S: vale on the decision artifact.
- [ ] Gate A: fresh-agent review of the decision against the W19
      falsifiable statement and the S9/S10 baseline evidence.
- [ ] Gate U (decision): user picks fix, remove-with-replacement, or
      keep; the decision is logged either way.

## Branch

No code; the decision artifact lands in the adapter repo, direct.

## Log

- 2026-07-11 Filed by S0 from the approved plan.
