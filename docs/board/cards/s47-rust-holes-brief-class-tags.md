---
id: S47
title: model-class tags in the rust-holes dispatch brief
status: in-progress
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

- [ ] Gate S: rust-holes `bin/check` green (S45 ships it); vale on
  touched markdown; the no-model-id grep recorded.
- [ ] Gate A: second-model review, focus: do the tags contradict
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
