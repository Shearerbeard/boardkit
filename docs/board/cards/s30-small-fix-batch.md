---
id: S30
title: Wave-2 small-fix batch with the ignore and doctor truthing items
status: done
depends: []
serialize-with: []
lineage: primary
executor: smart
gates: "S -> A -> D -> U(code-review)"
user-gates: [code-review]
commit-range: "f8488de..23dea92"
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

- [x] Gate S: load skill `gate-probes`, then `uv run pytest -q`,
  `uv run ruff check`, `boardkit check`, `boardkit render --check`,
  `boardkit doctor`; `vale` on touched markdown.
- [x] Gate A: opencode-lane review of the diff, fresh context, packet
  staged per the working-dir contract.
- [x] Gate D: drift audit of the living documents before the user gate.
- [x] Gate U (code-review): batched packet to Mike; stop.

## Branch

direct

## Log

- 2026-08-23 Gate U (code-review) passed: Mike reviewed the batched
  Phase 2 window and accepted the batch. Two notes from his read are
  logged at the gate: the repeated path literals across `src/boardkit`
  consolidate into a constants hierarchy (minted as S44), and dispatch
  instruction volume gets a watch over the next runs (FEEDBACK.md,
  dispatch-briefs-may-over-instruct). Card done.
- 2026-08-22 Entered in-review for the batched user gate: commit-range
  f8488de..23dea92 recovered by the trailer search (the prior session
  committed the card's work without setting the range) and the review
  packet generated. The single commit bundles S14's landed process
  prose, so the packet shows that too; S14 is done with its own
  acceptance verified on its card.
- 2026-08-22 Gate D passed via the batched Phase 2 drift audit: a
  fresh small-class Claude auditor checked the living documents'
  claims and anchors against the repo and board and returned DRIFT
  AUDIT: CLEAN with zero findings. Evidence:
  [2026-08-22-phase2-gate-d.md](../evidence/2026-08-22-phase2-gate-d.md).
  The card now waits at its batched U(code-review) gate.
- 2026-08-22 Session close canary evidence filed at
  [2026-08-22-s30-s14-session-close.md](../evidence/2026-08-22-s30-s14-session-close.md);
  S30 remains in-progress at Gate D for the planned batched user gate.
- 2026-08-22 Gate A passed after three GLM-family reviewer rounds over
  the S30 diff. Round 1 returned PASS with five MINOR findings: dead
  optional-key constant, missing `[board] wip` override/validation tests,
  missing `cmd_check --config` cwd-regression coverage, unescaped `Card:`
  trailer grep, and silent git warning-probe failures. All five were
  fixed. Round 2 returned PASS with one MINOR finding, a duplicated
  `commit.gpgsign` test-helper line; it was removed. The focused final
  re-review verified the removal and returned VERDICT: PASS with zero
  findings. Reviewer unverified checks: git-diff reconstruction, pytest,
  boardkit commands, and Vale were unavailable in its sandbox, so the
  board owner supplied the passing Gate S outputs.
- 2026-08-22 First executor dispatch returned empty, so the board owner
  treated it as a failed delegation, audited the S30-scoped dirty diff,
  and completed the remaining Gate S repair directly. Gate S passed:
  `uv run pytest -q` (375 passed), `uv run ruff check` (clean), targeted
  `uv run ruff format --check` on touched Python files (clean),
  `boardkit render --check` (views current), `boardkit check` (valid;
  expected S30 range warnings over historical R-wave cards), `boardkit
  doctor` (20 passed, warnings only for the new next-id-race note and
  dirty tree), and `vale docs/board/REVIEW-TOOLING.md
  docs/board/cards/s30-small-fix-batch.md` (clean).
- 2026-08-22 Board owner pulled S30 for wave-2 Phase 1 execution after
  the user approved the batched user-gate plan.
- 2026-08-22 Minted at the wave-2 Gate U (Phase 0) per the plan's
  card map; Mike approved the plan and its dispositions that day.
