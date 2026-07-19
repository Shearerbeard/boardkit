---
id: S37
title: Bound operator task scope and terminal pane observation on hard tasks
status: backlog
depends: []
serialize-with: []
lineage: none
executor: smart
gates: "scope at promotion -> S -> A"
user-gates: []
---

# S37: Bound operator task scope and terminal pane observation on hard tasks

Follow-up on a shared latent fault the MILESTONE rep-1 dissection and the
accept investigation found in BOTH builds (baseline and head), so it is
not a refactor regression but a standing quality issue that caps
convergence on budget-boundary tasks such as tune-mjcf. Mechanics:
[PROCESS.md](../PROCESS.md).

## Scope

Two coupled faults observed on tune-mjcf and conda-env, present in the
baseline too:

1. The coordinator sometimes dispatches an over-scoped operator task
   embedding a multi-attempt playbook ("iterate up to 5 times..."),
   violating the single-action task contract in the system prompt, so one
   worker consumes the whole agent budget across its turn-depth cap
   instead of returning for the coordinator to compress context and route
   to a debugger.
2. Worker tool results relayed through the terminal are bounded by the
   ~1015-char tmux capture-pane window, so a worker that floods the pane
   (a large heredoc write) cannot see its own subsequent command output
   (an `eval.py` timing line), driving blind and wasteful retries.

Evidence:
[the rep-1 dissection](../evidence/2026-07-18-tune-mjcf-rep1-timeout-dissection.md)
and
[the accept investigation](../evidence/2026-07-18-milestone-accept-flip-investigation.md).

## Deliverable

Scoped at promotion into one mechanism at a time (this card names two).
Candidate directions: tighten the coordinator's single-action-task
adherence so operator tasks return after one validated attempt; and give
workers a scrollback-aware or artifact-based read of their own command
output instead of the raw pane clip. The promotion step picks one
mechanism and pre-registers its measurement.

## Acceptance

Set at promotion. At minimum, a before/after on tune-mjcf-class
convergence (or a golden-frame check for the chosen mechanism) against a
pre-registered threshold.

## Gate checklist

- [ ] Scope at promotion: one mechanism and its pre-registered
      measurement.
- [ ] Gate S: checks named at scoping.
- [ ] Gate A: fresh-agent review.

## Branch

Named at promotion once the mechanism is chosen.

## Log

- 2026-07-18 Filed on MILESTONE acceptance as the shared-latent-fault
  follow-up. Not a refactor regression (present in both builds); a
  standing reliability issue on budget-boundary tasks.
