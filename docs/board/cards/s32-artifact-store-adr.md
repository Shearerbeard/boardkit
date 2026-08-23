---
id: S32
title: ArtifactStore ADR - receipts, postures, sidecar mechanics
status: in-progress
depends: [S28]
serialize-with: []
lineage: primary
executor: smart
gates: "S -> A -> D -> U"
user-gates: [adr-approval]
epic: S41
---

# S32: ArtifactStore ADR - receipts, postures, sidecar mechanics

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Minting record:
[2026-08-19-wave-2-plan.md](../../plans/2026-08-19-wave-2-plan.md)

## Scope

A new ADR under `docs/`; no storage code.

## Deliverable

Wave-2 decision 2 as a reviewed ADR before any storage code exists:
the ArtifactStore interface beside CardStore, the per-board posture
key (`ephemeral`, `in-repo`, `sidecar`), the receipt format (verdict,
numbered findings ledger, author and reviewer models, content
digests), sidecar mechanics and failure modes, and the outside-vetter
validation path. Ruled inputs: R-wave backfill is start-fresh plus one
receipt for the 2026-08-16 ruling (Mike, 2026-08-22 Gate U); the
per-harness machine-local pointer pattern is weighed here beside S12.

## Acceptance

- ADR accepted with its adversarial-review ledger appended; S33 cites
  it.

## Gate checklist

- [ ] Gate S: `adr-review` structure checks, then `uv run pytest -q`,
  `uv run ruff check`, `boardkit check`, `boardkit render --check`,
  `boardkit doctor`, `vale` on the ADR prose.
- [ ] Gate A: adversarial prose review per the roster, ledger appended
  to the ADR.
- [ ] Gate D: drift audit before the user gate.
- [ ] Gate U: Mike approves the ADR; S33 does not start without it.

## Branch

direct

## Log

- 2026-08-23 Board owner pulled S32 for wave-2 Phase 4 on S28's close
  (the dependency's user gate passed the same day). Board owner
  ruling at pull: the ADR home is `docs/adr/`, numbered from 0001,
  since the gate-probes routing already names that path and future
  ADRs join it. Gate A runs on the codex lane (GPT 5.6-sol) per this
  session's provider authorization; the metered lane is not proposed.
  The executor dispatch continues the leaner point-at-the-card brief
  under the dispatch-verbosity watch.
- 2026-08-22 Minted at the wave-2 Gate U (Phase 0) per the plan's
  card map; Mike approved the plan and its dispositions that day.
