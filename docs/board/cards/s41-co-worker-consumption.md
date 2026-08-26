---
id: S41
title: Co-worker consumption readiness
status: backlog
depends: []
serialize-with: []
lineage: primary
executor: smart
gates: "S -> U"
user-gates: [acceptance]
kind: epic
---

# S41: Co-worker consumption readiness

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Minting record:
[2026-08-22-spread-readiness-hypothesis.md](../../plans/2026-08-22-spread-readiness-hypothesis.md)

## Goal

A co-worker can clone boardkit, orient from the repo alone, reach a
dispatch-ready machine from the written recipe, read the board
visually, and trust its gate decisions without access to this
machine. The 2026-08-22 spread-readiness assessment is the baseline
evidence; the agent-driver conversion run is the acceptance test the
user offers when this epic's members land.

## Acceptance scenario

The target, stated as a run a second developer performs on a machine
that has never seen this repo, carrying only the repo URL and their
own agent subscriptions. Each step names the member that makes it
passable; a step that needs Mike to answer a question is a finding,
not a pass.

1. Install: clone the kit, follow the bootstrap recipe to a working
   CLI, and stand up provider lanes from the account-kind inventory
   (S39).
2. Orient: their agent reads AGENTS.md and the read order, then
   reports board state correctly with no human explanation (the
   orientation canaries prove this today); the human path through the
   README is S40.
3. Verify: `boardkit check` and `boardkit doctor` run green, or with
   warnings the docs themselves explain (S8, S12).
4. See: the board's visual surface opens and agrees with the views'
   freshness stamp (S38, S37).
5. Trust: they audit one past gate decision from receipts tracked in
   the repo, with no access to this machine's transcripts (S32, S33).
6. Run: they pull a ready card and land it through the S and A gates
   with their own agents, on this board or a docked consumer board
   (S15, S30, S31; S36 proves the second consumer).
7. No lifeline: the run completes without asking Mike anything.

The Phase 7 documentation bus test grades the docs cold against this
script, and the agent-driver conversion run is its live form, offered
at Mike's call when the members land.

## Members

S8, S12, S15, S30, S31, S32, S33, S36, S37, S38, S39, S40, S48 carry
`epic: S41`. Membership is grouping, not dependency; `boardkit dag
--to S41` computes the schedulable plan.

## Gate checklist

- [ ] Gate S: `boardkit dag --to S41` shows an empty remaining set;
  members all done.
- [ ] Gate U: Mike accepts consumption readiness against the
  acceptance scenario, and decides the conversion-run offer; stop.

## Branch

direct

## Log

- 2026-08-25 S48 (document stores overlay and close-review) added to
  the member list; minted at S33's Gate U close with `epic: S41` in
  frontmatter, this prose list catching up. Membership is grouping;
  the card's own depends stay [S33].
- 2026-08-23 Board owner wrote the acceptance scenario onto the epic
  at Mike's direction: the second-developer target stated as a
  seven-step pass/fail run, each step mapped to the member that makes
  it passable, with the Phase 7 bus test grading the docs against
  exactly this script. Gate U now reads against it. Grounding: the
  epic's prior goal prose and the three-axis analysis in the
  spread-readiness hypothesis plan.
- 2026-08-22 Minted at the wave-2 Gate U (Phase 0) from the approved
  spread-readiness action list.
- 2026-08-22 Phase 0 close evidence linked:
  [2026-08-22-phase0-close.md](../evidence/2026-08-22-phase0-close.md)
  (Gate D 2 findings fixed; orientation canary 4/4; dag frontier
  recorded).
