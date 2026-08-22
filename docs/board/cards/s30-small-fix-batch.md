---
id: S30
title: Wave-2 small-fix batch with the ignore and doctor truthing items
status: ready
depends: []
serialize-with: []
lineage: primary
executor: smart
gates: "S -> A -> D -> U(code-review)"
user-gates: [code-review]
epic: S41
---

# S30: Wave-2 small-fix batch with the ignore and doctor truthing items

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Minting record:
[2026-08-19-wave-2-plan.md](../../plans/2026-08-19-wave-2-plan.md)

## Scope

`src/boardkit/board.py`, `src/boardkit/cli.py`, `src/boardkit/config.py`,
`src/boardkit/review_packet.py`, `src/boardkit/doctor.py`, this repo's
`.gitignore`, `docs/board/REVIEW-TOOLING.md` (two fill-ins), tests.

## Deliverable

The mechanical inbox items from drain 8 plus the approved A8 batch,
none of them design-bearing:

- A `[board] wip` key defaulting to 2; the `board.py` constant retires.
- `--config`-bearing commands stop resolving the registry from the
  process cwd.
- `review-packet --commit-range` accepts git revision expressions.
- A warning when `Card:`-trailer commits fall outside a card's recorded
  range (covers the rebase hazard and the excluded-first-commit trap).
- Deferral supersession per wave-2 decision 4: newest-wins plus the
  `superseded <date>` marker parsed as a terminator.
- Entity-name collision lint; a doctor note for the next-id race.
- A check-level warning for a recorded `commit-range` touching `src/`
  paths on a card without a U(code-review) gate.
- A8: `.boardkit/local.toml` and `.claude/settings.local.json` join
  this repo's `.gitignore`; `init` scaffolds all four ignore lines;
  doctor's required-fill sections extend to every heading the template
  calls mandatory; this board's wave-close cost recipe and
  evidence-receipt canary row get filled; decide whether doctor stats
  the pin-source config paths (existence only, never execution).

## Acceptance

- `uv run pytest -q` green with a test per fix.
- The R-wave's annotated deferral lines parse as resolved without
  hand-editing.
- `boardkit doctor` on this repo reports the two previously-unfilled
  sections truthfully.

## Gate checklist

- [ ] Gate S: load skill `gate-probes`, then `uv run pytest -q`,
  `uv run ruff check`, `boardkit check`, `boardkit render --check`,
  `boardkit doctor`; `vale` on touched markdown.
- [ ] Gate A: opencode-lane review of the diff, fresh context, packet
  staged per the working-dir contract.
- [ ] Gate D: drift audit of the living documents before the user gate.
- [ ] Gate U (code-review): batched packet to Mike; stop.

## Branch

direct

## Log

- 2026-08-22 Minted at the wave-2 Gate U (Phase 0) per the plan's
  card map; Mike approved the plan and its dispositions that day.
