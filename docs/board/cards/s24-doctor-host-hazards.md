---
id: S24
title: R6/R7 doctor checks - host-repo hazards and harness parity
status: ready
depends: []
serialize-with: []
lineage: primary
executor: smart
gates: "S -> A -> U(code-review)"
user-gates: [code-review]
---

# S24: R6/R7 doctor checks - host-repo hazards and harness parity

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Drain record:
[2026-08-09-feedback-drain-7.md](../../plans/2026-08-09-feedback-drain-7.md)
(same-sitting mints); requirements R6/R7 in the aura requirements doc,
evidence: the tb board lives on a feature branch of an adapter repo,
the wiki hosting the aura board sits dirty with unpushed commits, and
the aura repo runs two harnesses under different instruction files.

## Scope

`src/boardkit/doctor.py`, `src/boardkit/config.py` (an optional
declared base branch for the board's host repo), docs, tests.

## Deliverable

R6: doctor checks on the resolved board's host repo. One check
compares the current branch against a declared base branch, read from
an optional config key whose absence skips the check rather than
passing it. Two more warn on a dirty tree and on unpushed commits.
Warnings, never errors: a session that knows can proceed deliberately.

R7: a doctor check that the consumer repo has one real agent entry
file with the others as shims, per the kit's own AGENTS.md-canonical
convention. A repo with divergent full-text AGENTS.md and CLAUDE.md
warns; a repo with no entry file at all warns.

## Acceptance

- `uv run pytest -q` green; tests cover the branch mismatch, dirty and
  unpushed warnings, the skipped-when-undeclared base branch, and the
  parity check on shim, divergent, and absent layouts.
- `boardkit doctor` on a fixture repo parked on a feature branch with
  a declared base warns and still exits by its existing error rules.

## Gate checklist

- [ ] Gate S: load skill `gate-probes`, then `uv run pytest -q`,
  `uv run ruff check`, `vale` on touched markdown.
- [ ] Gate A: adversarial review, focus: false calm (a hazard the
  check silently skips) and false alarm (a legitimate layout the
  parity check flags).
- [ ] Gate U (code-review): present the review packet; stop.

## Branch

direct

## Log

- 2026-08-09 Minted by the seventh feedback drain from standing
  requirements R6/R7, riding the Session B wave per the build order.
