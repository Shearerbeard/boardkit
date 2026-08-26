---
id: S47
title: model-class tags in the rust-holes dispatch brief
status: done
commit-range: 605056b..0f0311c
depends: []
serialize-with: [S4]
lineage: none
executor: any
gates: "S -> A"
user-gates: []
---

# S47: model-class tags in the rust-holes dispatch brief

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Drain record:
[2026-08-23-feedback-drain-8.md](../../plans/2026-08-23-feedback-drain-8.md).
External repo: `~/dev/rust-holes` (private; never publish). Source:
two unchecked items in the aura board's executor cost plan
(2026-08-05). Serialized with S4 because both touch
`templates/dispatch-brief.md`.

## Scope

The rust-holes repo (external), one file:
`templates/dispatch-brief.md`. No doctrine-prose edit anywhere; the
PLAYBOOK already states the class split, and after S4 that section
has one owner whose own process takes any guidance change. Classes,
never model ids.

## Deliverable

The skeleton and fill brief blocks each carry a model-class tag. The
skeleton is the design step and takes the strongest available class.
Fills execute against green-when-done criteria and take a smaller
class. A reviewer's class matters less than the invariant that it
never shares a model with the unit's author.

## Acceptance

- The first 2026-08-05 cost-plan checkbox (brief tags) is checked
  with a pointer to the landed sha; the second (Delegating prose) is
  either closed as already-satisfied with the S4 record as evidence,
  or routed to the section's owner, not edited here.
- The brief still instantiates by fill-the-brackets alone; grep
  proves no model id landed anywhere in the templates.

## Gate checklist

- [x] Gate S: rust-holes `bin/check` green (S45 ships it); vale on
  touched markdown; the no-model-id grep recorded.
- [x] Gate A: second-model review, focus: do the tags contradict
  MODEL-CLASSES.md?

## Branch

direct; external commits recorded in the Log as they land.

## Log

- 2026-08-23 Minted by feedback drain 8 from the rust-holes
  second-dev audit (adopted RH4 draft, adversarially reviewed and
  narrowed to the template there).
- 2026-08-26 Pulled to in-progress under the cleanup execution plan
  while S45 sits at Gate A (WIP 2 of 2). Executor lane: opencode on
  bedrock, write-only dispatch from the rust-holes worktree (shell
  steps stall headless, see S45's log); reviewer lane: codex. S4 is
  not in progress, so the serialize-with holds.
- 2026-08-26 Executor (bedrock lane, write-only) landed the two class
  tags and the explanatory sentence in one pass. Board-owner repairs
  before Gate S: wrapped two lines to 72 columns, removed one
  trailing-space quote line. Gate S passed: `bin/check` exits 0; grep
  for model or provider ids across `templates/` returns nothing; the
  brief still instantiates by fill-the-brackets alone; vale clean.
  Commit `9d6f6f9` on rust-holes master; commit-range set; packet
  generated; Gate A dispatched to the codex lane.
- 2026-08-26 Gate A round 1 (codex lane): FAIL, 3 BLOCKING, all
  ACCEPTED and repaired in `0f0311c` by the board owner: the tags now
  use the model-classes taxonomy names (skeleton: smart
  writer-reviewer; fill: small explorer; reviewer: smart class with
  frontier fallback, never the author), and the restated
  green-criteria clause is gone. The range now spans S45's fix commit
  `4511add` as well, which touches no template; round 2's prompt
  names it out of scope. Round 2 dispatched to the same lane.
- 2026-08-26 Gate A round 2 (codex lane): PASS, zero findings, all
  three round-1 fixes verified against the diff and MODEL-CLASSES.md.
  Acceptance re-run by the board owner: `bin/check` green, no model or
  provider id under `templates/`, the five angle-bracket slots intact,
  both tag lines present. Done. Cost-plan disposition: the brief-tags
  checkbox is satisfied by `0f0311c`; the Delegating-prose checkbox
  is closed as already-satisfied, the split now living in the skill's
  delegation text (S4 record). Ticking the boxes in the aura board's
  cost-plan note is a wiki edit left to the next handoff.
- 2026-08-26 Intent validation (codex lane, finding 3) held the
  deferred cost-plan tick against this card's acceptance. Both boxes
  in the aura board's executor-cost-plan note are now ticked with
  their pointers (`0f0311c` for the tags; the prose item closed as
  already satisfied via S4 `fac496c`); the edit sits uncommitted in
  the wiki checkout for its own board owner to commit.
