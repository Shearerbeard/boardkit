---
id: S27
title: Maintained architecture flowchart of the kit and its skills
status: backlog
depends: []
serialize-with: []
lineage: primary
executor: any
gates: "S -> A"
user-gates: []
---

# S27: Maintained architecture flowchart of the kit and its skills

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Drain record:
[2026-08-09-feedback-drain-7.md](../../plans/2026-08-09-feedback-drain-7.md)
(part (f) of the dotdir entry). Standing stretch goal in RULE-1 of the
aura plan of record, wanted for the future OSS project.

## Scope

A new `docs/ARCHITECTURE.md` (or sibling name) with the Mermaid
flowchart, `plugins/board/skills/board-hygiene/SKILL.md` (the
session-close currency line), docs links, tests only if a doctor check
lands.

## Deliverable

A standing Mermaid flowchart of how boardkit works and how it
interacts with the claude-skills transport and plugin skills, with
each node linked to the piece it names. Skill-to-skill-to-script
relationships are hard to follow today. Currency is a session-close
discipline: board-hygiene gains a checklist line that the flowchart is
updated when the session changed any pictured seam, which gives the
discipline the kit-side home consumers can be held to.

Backlog on purpose: it wants the post-Session-B architecture (store
seam, registry, dag) to draw, so it is not prioritized this sitting.

## Acceptance

- The flowchart renders (mermaid-view or equivalent) and every node
  link resolves.
- board-hygiene names the currency step; its contract stamp stays
  consistent.
- A cold reader can trace a dispatch from `delegating-work` through
  `resolve-route` to a transport skill using the chart alone.

## Gate checklist

- [ ] Gate S: load skill `gate-probes`, then `vale` on touched
  markdown; render the Mermaid and check links.
- [ ] Gate A: fresh-agent review, focus: does the chart match the
  code's actual seams, and will the currency line actually fire at
  session close?

## Branch

direct

## Log

- 2026-08-09 Minted by the seventh feedback drain from part (f) of the
  dotdir entry; deliberately backlog until the Session B architecture
  lands.
