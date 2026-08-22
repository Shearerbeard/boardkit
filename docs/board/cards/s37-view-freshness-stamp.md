---
id: S37
title: Recomputable freshness stamp on the generated views
status: backlog
depends: [S28]
serialize-with: []
lineage: primary
executor: smart
gates: "S -> A -> U(code-review)"
user-gates: [code-review]
epic: S41
---

# S37: Recomputable freshness stamp on the generated views

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Minting record:
[2026-08-22-spread-readiness-hypothesis.md](../../plans/2026-08-22-spread-readiness-hypothesis.md)

## Scope

`src/boardkit/board.py` (view headers), `src/boardkit/cli.py`
(`check`), golden tests.

## Deliverable

Generated views carry a stamp a reader can verify without the CLI:
a content digest of the card sources or the last commit touching the
cards dir, never the view's own commit sha (unknowable at render
time), plus render-time tree state. `check` recomputes and validates
it. Lands after S28's golden-view work, or regenerates the goldens
with it.

## Acceptance

- A stale render is detectable from the view text alone; `check`
  fails on a stamp mismatch; goldens updated deliberately.

## Gate checklist

- [ ] Gate S: load skill `gate-probes`, then `uv run pytest -q`,
  `uv run ruff check`, `boardkit check`, `boardkit render --check`,
  `boardkit doctor`; `vale` on touched markdown.
- [ ] Gate A: opencode-lane review, fresh context.
- [ ] Gate U (code-review): packet to Mike; stop.

## Branch

direct

## Log

- 2026-08-22 Minted at the wave-2 Gate U (Phase 0) from the approved
  spread-readiness action list.
