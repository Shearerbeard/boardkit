---
id: S36
title: rust-holes adopts the docking convention as second consumer
status: backlog
depends: [S31]
serialize-with: []
lineage: none
executor: smart
gates: "S -> A -> U(code-review)"
user-gates: [code-review]
epic: S41
---

# S36: rust-holes adopts the docking convention as second consumer

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Minting record:
[2026-08-19-wave-2-plan.md](../../plans/2026-08-19-wave-2-plan.md)

## Scope

External repo `~/dev/rust-holes` (the hole ledger's docking); this
board carries the card and the logged sha range.

## Deliverable

rust-holes adopts the S31 docking spec for its ledger. Divergence from
the spec is the trigger for library extraction, which would be its own
card.

## Acceptance

- rust-holes resolves its ledger through the documented order with no
  stored-link fragility; the adoption commits are logged here with
  their shas.

## Gate checklist

- [ ] Gate S: the rust-holes repo's own checks green; `vale` on
  touched markdown.
- [ ] Gate A: adversarial review over the external-repo packet
  (`--repo` and `--commit-range` per PROCESS).
- [ ] Gate U (code-review): packet to Mike; stop.

## Branch

direct

## Log

- 2026-08-22 Minted at the wave-2 Gate U (Phase 0) per the plan's
  card map; Mike approved the plan and its dispositions that day.
