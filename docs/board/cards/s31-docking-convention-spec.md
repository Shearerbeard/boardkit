---
id: S31
title: Versioned docking-convention spec with the three consumer postures
status: in-progress
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

- [x] Gate S: load skill `gate-probes`, then `uv run pytest -q`,
  `uv run ruff check`, `boardkit check`, `boardkit render --check`,
  `boardkit doctor`; `vale` on touched markdown.
- [ ] Gate A: adversarial review of the spec against the shipped
  resolver's actual behavior.
- [ ] Gate D: drift audit before the user gate.
- [ ] Gate U (code-review): packet to Mike; stop.

## Branch

direct

## Log

- 2026-08-22 Gate S passed, run by the board owner over the combined
  Phase 2 tree: `uv run pytest -q` (416 passed), `uv run ruff check`
  (clean), `vale` on all six touched markdown files (clean),
  `boardkit check`, `boardkit render --check`, and `boardkit doctor`
  all green, the AGENTS.md doc pair byte-identical, and the spec read
  in full by the board owner. The spec follows the shipped resolver
  where prose disagreed with code; the executor's eight divergence
  notes are stated inside the spec itself (the `--config` bypass, the
  flag/variable asymmetry, the manifest-not-directory walk-up rule,
  init scaffolding nothing under `.boardkit/`, the shorter
  registry-lookup path, the common-dir acceptance conditions, and the
  two doctor misfires recorded under Known limits). Board owner
  ratifications: `docs/DOCKING.md` as the spec's home (the
  consumer-scaffolded contract set is a fixed tuple in `contract.py`,
  so `docs/board/` would be a code change and posture shift);
  version-in-heading plus a `docking-spec: v1` stamp with an
  unversioned filename; and the two board-skill pointer clauses as the
  one-fact-one-place duty. Whether the spec joins `CONTRACT_DOCS` is
  deferred to the batch user gate. The doctor misfires on in-repo
  board homes are carded as S42 rather than fixed in-cycle.
- 2026-08-22 Board owner pulled S31 for wave-2 Phase 2 (the last
  Phase 2 card) and dispatched a Claude executor. WIP holds at two
  with S30 parked at Gate D; S15 and S29 sit in-review at the batched
  window.
- 2026-08-22 Minted at the wave-2 Gate U (Phase 0) per the plan's
  card map; Mike approved the plan and its dispositions that day.
