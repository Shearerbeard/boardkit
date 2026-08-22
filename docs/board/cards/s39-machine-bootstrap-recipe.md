---
id: S39
title: Machine-bootstrap recipe and account inventory
status: ready
depends: []
serialize-with: []
lineage: primary
executor: smart
gates: "S -> A -> D -> U"
user-gates: [review]
epic: S41
---

# S39: Machine-bootstrap recipe and account inventory

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Minting record:
[2026-08-22-spread-readiness-hypothesis.md](../../plans/2026-08-22-spread-readiness-hypothesis.md)

## Scope

`docs/board/REVIEW-TOOLING.md` template appendix,
`src/boardkit/data/templates/`, `src/boardkit/doctor.py` (pointer
only), README.

## Deliverable

What a second machine needs and where each piece comes from: the
dotfiles opencode group, the claude-skills install, codex and agy
config, provider accounts by kind (never model ids), and the kit's
own clone URL. Cards EXTRACTION.md's never-shipped Phase 4
sibling-install obligation. The planned notanton bootstrap is the
cold-test.

## Acceptance

- A fresh machine can reach a dispatch-ready state from the recipe
  plus its own credentials; the notanton cold-test passes or its
  failures become findings here.

## Gate checklist

- [ ] Gate S: `boardkit check`, `boardkit render --check`,
  `boardkit doctor`, `vale` on touched markdown.
- [ ] Gate A: adversarial prose review per the roster.
- [ ] Gate D: drift audit before the user gate.
- [ ] Gate U: Mike reviews the recipe; stop.

## Branch

direct

## Log

- 2026-08-22 Minted at the wave-2 Gate U (Phase 0) from the approved
  spread-readiness action list.
