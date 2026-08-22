---
id: S33
title: Receipts and sidecar implementation per the ADR
status: backlog
depends: [S32]
serialize-with: []
lineage: primary
executor: smart
gates: "S -> A -> M -> D -> U(code-review)"
user-gates: [code-review]
epic: S41
---

# S33: Receipts and sidecar implementation per the ADR

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Minting record:
[2026-08-19-wave-2-plan.md](../../plans/2026-08-19-wave-2-plan.md)

## Scope

`src/boardkit/store.py` (ArtifactStore seam and posture backends),
gate-close logging, `boardkit.toml` here (`posture = sidecar`), tests.

## Deliverable

Gate closes write a compact receipt into the tracked repo and the
packet into the configured store, in the same commit as the log line.
This board flips to `posture = sidecar`.

## Acceptance

- A gate close on this board produces a tracked receipt and a sidecar
  packet without hand steps.
- Gate M ran from a clean clone: receipt digests validate against
  fetched packets, and a deliberately tampered packet fails.

## Gate checklist

- [ ] Gate S: load skill `gate-probes`, then `uv run pytest -q`,
  `uv run ruff check`, `boardkit check`, `boardkit render --check`,
  `boardkit doctor`; `vale` on touched markdown.
- [ ] Gate A: opencode-lane review, fresh context.
- [ ] Gate M: the clean-clone digest validation and tamper test, plus
  the wave smoke test on one of this wave's own cards.
- [ ] Gate D: drift audit before the user gate.
- [ ] Gate U (code-review): Mike reads the receipt as an outside
  vetter would; stop.

## Branch

direct

## Log

- 2026-08-22 Minted at the wave-2 Gate U (Phase 0) per the plan's
  card map; Mike approved the plan and its dispositions that day.
