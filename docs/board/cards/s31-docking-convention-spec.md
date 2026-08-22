---
id: S31
title: Versioned docking-convention spec with the three consumer postures
status: ready
depends: []
serialize-with: []
lineage: primary
executor: smart
gates: "S -> A -> D -> U(code-review)"
user-gates: [code-review]
epic: S41
---

# S31: Versioned docking-convention spec with the three consumer postures

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Minting record:
[2026-08-19-wave-2-plan.md](../../plans/2026-08-19-wave-2-plan.md)

## Scope

A new versioned spec under `docs/`, the R5' docs it consolidates, and
`src/boardkit/data/templates/` where placement guidance ships; tests
only where template text is pinned.

## Deliverable

The `.boardkit/` docking convention as a versioned document: the
resolution order (flag, env, walk-up, common-dir fallback, legacy),
the three consumer postures (committed, gitignored, invisible via
`.git/info/exclude`) with the scale-up note that a second adopter
promotes invisible to a tracked line as a deliberate step, and the
common-dir fallback semantics. rust-holes adopts it as the second
consumer (S36); library extraction becomes a card only if the second
copy diverges.

## Acceptance

- The spec states all five resolution steps and all three postures
  with their promotion rule.
- `vale` clean; the spec carries a version and a contract stamp.
- S36 can execute from the spec alone.

## Gate checklist

- [ ] Gate S: load skill `gate-probes`, then `uv run pytest -q`,
  `uv run ruff check`, `boardkit check`, `boardkit render --check`,
  `boardkit doctor`; `vale` on touched markdown.
- [ ] Gate A: adversarial review of the spec against the shipped
  resolver's actual behavior.
- [ ] Gate D: drift audit before the user gate.
- [ ] Gate U (code-review): packet to Mike; stop.

## Branch

direct

## Log

- 2026-08-22 Minted at the wave-2 Gate U (Phase 0) per the plan's
  card map; Mike approved the plan and its dispositions that day.
