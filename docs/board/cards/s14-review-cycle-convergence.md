---
id: S14
title: Bound the adversarial review cycle with a convergence rule
status: done
depends: []
serialize-with: []
lineage: primary
executor: smart
gates: "S -> A"
user-gates: []
---

# S14: Bound the adversarial review cycle with a convergence rule

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Drain record:
[2026-08-05-feedback-drain-5.md](../../plans/2026-08-05-feedback-drain-5.md),
first entry.

## Scope

`src/boardkit/data/templates/PROCESS.md` (the Gate A / fix-commit
re-review paragraph), `docs/board/PROCESS.md` (this board's copy),
`src/boardkit/brief.py` and its data (the dispatch brief must carry
the discipline), `plugins/board/skills/delegating-work/SKILL.md`,
tests.

## Deliverable

The re-review duty gains a convergence rule stated beside it: each
re-review round verifies the prior round's dispositions, re-raises
only findings whose fixes failed, and does not expand scope past
ground already accepted. A round bound with a named escalation: a FAIL
that is all new scope after the bound goes to the user with the
disagreement recorded on the ledger, never a silent stop or an
unbounded loop. The dispatch brief for a re-review round must carry
the discipline into the reviewer prompt. On the ledger, per-round
finding counts and cumulative reviewer spend become required fields,
so the cycle's shape is auditable from the record.

## Acceptance

- `uv run pytest -q` green; a test asserts the re-review dispatch
  brief contains the convergence instruction.
- The template and this board's PROCESS.md state the convergence rule,
  the round bound, and the escalation in the same section as the
  fix-commit re-review duty, and both copies agree.
- The ledger format prose names per-round finding counts and
  cumulative spend as required fields.

## Gate checklist

- [x] Gate S: load skill `gate-probes`, then `uv run pytest -q`,
  `uv run ruff check`, `vale` on touched markdown.
- [x] Gate A: adversarial review, focus: can the convergence rule be
  gamed to close a cycle early (dispositions marked verified without
  evidence, real regressions dismissed as "new scope")?

## Branch

direct

## Log

- 2026-08-22 Session close canary evidence filed at
  [2026-08-22-s30-s14-session-close.md](../evidence/2026-08-22-s30-s14-session-close.md);
  the canary passed 4/4.
- 2026-08-22 S14 done. Acceptance verified by the board owner: tests pin
  the dispatch-brief convergence clause and the template Gate A bullet;
  the live and template PROCESS copies are byte-identical for the new rule;
  the ledger fields require per-round counts, cumulative spend, and
  per-finding disposition verification evidence; Gate S and Gate A both
  passed.
- 2026-08-22 Gate A passed via Codex fallback for prose/process review
  after Antigravity was skipped for lack of fresh spend approval. Round 1
  failed with three BLOCKING findings: fix-induced regressions could be
  mislabeled new scope, dispositions could be marked verified without
  evidence, and the two-round ruling could pass Gate A while unresolved
  in-scope work remained. The board owner fixed all three in both PROCESS
  copies, the delegating-work skill, and the brief/template tests. Focused
  re-review returned VERDICT: PASS, with pytest and ruff unverified in the
  reviewer sandbox; the board owner supplied `uv run pytest -q` (383
  passed) and `uv run ruff check` (clean).
- 2026-08-22 Gate S passed for S14 after board-owner correction to match
  wave-2 decision 6's two-fix-round bound: `uv run pytest -q` (383
  passed), `uv run ruff check` (clean), targeted `uv run ruff format
  --check` on touched Python files (clean), and `vale docs/board/PROCESS.md
  src/boardkit/data/templates/PROCESS.md
  plugins/board/skills/delegating-work/SKILL.md
  docs/board/cards/s14-review-cycle-convergence.md` (clean). Board
  validation also remained current with `boardkit check` and `boardkit
  render --check`.
- 2026-08-22 Board owner pulled S14 for wave-2 Phase 2 process
  scaffolding after the user approved batching S30 with Phase 2 for the
  next code-review gate.
- 2026-08-05 Minted by the fifth feedback drain from the Epoch
  five-round review-cycle finding.
- 2026-08-16 Second worked example, on this board's own R-wave:
  [2026-08-16-gate-a-review-cycle.md](../evidence/2026-08-16-gate-a-review-cycle.md).
  Five rounds again. Rounds 1 and 2 found defects in the reviewed diffs;
  rounds 3 to 5 each returned one further evasion of a single text
  heuristic living in a fix commit, each narrower than the one before,
  and the cycle ended by a board-owner ruling rather than by a rule.
  Two candidate termination conditions the session would have used, both
  checkable from the review records this card already has to read: stop
  when a round's findings no longer touch the reviewed diff, and stop
  when round N+1's findings are strictly narrower instances of round N's
  class. The ruling also had to answer what happens to the gate when a
  cycle ends without a pass, which is the half the Epoch example did not
  reach: it stays open-deferred and the user decides at the user gate.
