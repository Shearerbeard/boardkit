---
id: S28
title: Wire the CLI core through the CardStore seam
status: in-progress
depends: []
serialize-with: []
lineage: primary
executor: smart
gates: "S -> A -> D -> U(code-review)"
user-gates: [code-review]
---

# S28: Wire the CLI core through the CardStore seam

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Minted from S13's Gate A
finding 4 (2026-08-16): the seam landed as an interface with driver-level
tests, but no production module imports it - `build_board` still walks
markdown directly, the protocol lacks the board-metadata surface the S13
deliverable names, and `put` stayed deferred (no caller, no
format-preserving serialization; S13 log, 2026-08-09).

## Scope

`src/boardkit/store.py` (board metadata on the protocol; `put` if and
only if a caller lands with it), `src/boardkit/board.py` and
`src/boardkit/cli.py` (route card traversal through a store constructed
from the resolved config), tests. No behavior change to views, check
output, or the resolution order.

## Deliverable

The CLI core reads cards through a CardStore constructed at resolution
time, with the markdown-dir layout as driver #1 behind the seam rather
than beside it. Board metadata (the config surface a second driver would
need) is defined on the protocol. `put` lands only with its first real
caller; if it stays deferred, this card's log says so and why.

## Acceptance

- `uv run pytest -q` green; a test constructs the store from a resolved
  config and `build_board` (or its successor path) consumes it.
- `grep -rn "from boardkit.store" src/` shows at least one production
  import; the golden views stay byte-identical.
- `uv run ruff check` clean.

## Gate checklist

- [ ] Gate S: load skill `gate-probes`, then `uv run pytest -q`,
  `uv run ruff check`, `boardkit check`, `boardkit render --check`,
  `boardkit doctor`; golden-view comparison.
- [ ] Gate A: adversarial review, focus: does the seam actually
  invert the dependency (could a second driver be written without
  touching board.py), or does every caller still reach the markdown
  traversal directly?
- [ ] Gate D: drift audit of the living documents that describe the
  store seam before the user gate.
- [ ] Gate U (code-review): packet to Mike; stop.

## Branch

direct

## Log

- 2026-08-23 Board owner pulled S28 for wave-2 Phase 3 and aligned the
  card with the plan's phase ladder: Gate D and the standing
  U(code-review) gate joined the checklist, and Gate S extended to the
  plan's probe list with the golden-view comparison. Gate A runs on
  the codex lane (GPT 5.6-sol) per this session's provider
  authorization; the plan's opencode naming predates it. The executor
  dispatch uses the leaner point-at-the-card brief under the
  dispatch-verbosity watch (FEEDBACK.md).
- 2026-08-16 Minted by the board owner from S13 Gate A finding 4
  (reviewer gpt-5.6-sol via codex): seam unused by production code,
  board metadata absent from the protocol. The put-deferral half of the
  finding was rejected as already ruled - the S13 log records the
  deferral and its reason; this card carries the wiring and the
  metadata surface.
