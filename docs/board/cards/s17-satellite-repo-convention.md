---
id: S17
title: Satellite-repo convention - no canonical-looking TODO beside a board
status: ready
depends: []
serialize-with: []
lineage: primary
executor: smart
gates: "S -> A"
user-gates: []
---

# S17: Satellite-repo convention - no canonical-looking TODO beside a board

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Drain record:
[2026-08-07-feedback-drain-6.md](../../plans/2026-08-07-feedback-drain-6.md),
third entry.

## Scope

`src/boardkit/data/templates/PROCESS.md` and `docs/board/PROCESS.md`
(the convention prose), `plugins/board/skills/board-hygiene/SKILL.md`
(the canary surface and a sweep step), tests only if a doctor check
lands.

## Deliverable

A stated convention for repos inside a boarded workstream that carry
their own roadmap files: the repo either gets a real board, or its
TODO.md is demoted with a header that names the driving goal, points
at the owning board, and marks its entries as a pull-only-when-blocking
enhancement backlog. The premise to protect: card frontmatter is the
only surface that may read as canonical work state. The orientation
canary's question set gains a probe for canonical-roadmap claims found
outside the board, so the next self-declared "canonical active
roadmap" in a satellite repo surfaces at session close instead of
steering a cold session's DAG.

## Acceptance

- The convention appears in the shipped PROCESS.md template and this
  board's copy, in the same section, and both copies agree.
- board-hygiene names the satellite-repo sweep and the canary probe;
  its contract stamp stays consistent.
- Applied once: agent-driver-rs TODO.md (the motivating case) is
  demoted per the convention, or the divergence is logged where the
  owning workstream records it.

## Gate checklist

- [ ] Gate S: load skill `gate-probes`, then `vale` on touched
  markdown; `uv run pytest -q` if a doctor check lands.
- [ ] Gate A: adversarial review, focus: does the convention leak
  session vocabulary into public satellite repos, and can a demoted
  TODO still read as canonical to a cold model?

## Branch

direct

## Log

- 2026-08-07 Minted by the sixth feedback drain from the agent-driver
  satellite-repo finding.
