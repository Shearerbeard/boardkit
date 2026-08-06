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
