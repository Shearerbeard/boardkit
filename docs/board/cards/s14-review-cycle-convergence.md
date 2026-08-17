---
id: S14
title: Bound the adversarial review cycle with a convergence rule
status: ready
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

- [ ] Gate S: load skill `gate-probes`, then `uv run pytest -q`,
  `uv run ruff check`, `vale` on touched markdown.
- [ ] Gate A: adversarial review, focus: can the convergence rule be
  gamed to close a cycle early (dispositions marked verified without
  evidence, real regressions dismissed as "new scope")?

## Branch

direct

## Log

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
