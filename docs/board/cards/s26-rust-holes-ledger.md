---
id: S26
title: rust-holes HOLES ledger with a hook-grade check
status: ready
depends: []
serialize-with: []
lineage: none
executor: smart
gates: "S -> A -> U(code-review)"
user-gates: [code-review]
---

# S26: rust-holes HOLES ledger with a hook-grade check

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Drain record:
[2026-08-09-feedback-drain-7.md](../../plans/2026-08-09-feedback-drain-7.md)
(second drained entry). Source finding: claude-skills
`feedback/2026-08-09-opencode-hole-inventory-drift/process-feedback.md`,
from the chore-lottery S22 session open.

## Scope

The rust-holes repo (external): a `templates/HOLES.md` or `.toml`
ledger template and a hook-grade check script; rust-holes docs naming
the convention. Nothing in this repo's `src/` changes.

## Deliverable

The typed-holes marker convention gains its missing half, enumeration:
a ledger whose rows record each hole's site, marker id, owning card,
and fill bound, plus a check that fails on a `todo!()` without a
registered marker and on a ledger row whose hole is gone. Today the
inventory is a convention line ("tracked by grep"), so an unowned hole
passes every gate silently; chore-lottery S5's Gate A caught exactly
that shape once and it took a human adversarial reviewer.

## Acceptance

- In the rust-holes repo: the check fails on a fixture with an
  unregistered `todo!()`, fails on a stale ledger row, and passes when
  ledger and holes agree; its test or demo run is recorded.
- The ledger template ships beside the existing marker convention and
  the docs cross-reference both.

## Gate checklist

- [ ] Gate S: run the rust-holes repo's own checks on the touched
  files; `vale` on touched markdown where configured.
- [ ] Gate A: adversarial review, focus: can a hole evade the check
  (macro-generated `todo!()`, cfg-gated code, marker id reuse)?
- [ ] Gate U (code-review): present the review packet; stop.

## Branch

direct

## Log

- 2026-08-09 Minted by the seventh feedback drain from the kimi-k3
  hole-inventory finding; accepted at the interview with building
  explicitly out of Session B scope.
