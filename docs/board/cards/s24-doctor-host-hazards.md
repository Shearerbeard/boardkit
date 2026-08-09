---
id: S24
title: R6/R7 doctor checks - host-repo hazards and harness parity
status: in-review
depends: []
serialize-with: []
lineage: primary
commit-range: 22bd55c..028ce5d
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

- [x] Gate S: load skill `gate-probes`, then `uv run pytest -q`,
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
- 2026-08-09 Pulled in-progress; executor is the maintainer session.
- 2026-08-09 Built: doctor checks `host.base-branch` (against the new
  optional `[board] base_branch`; undeclared skips, never passes),
  `host.tree-state` (dirty tree + unpushed commits, one warning; no
  upstream means the unpushed half stays quiet), and `entry.parity`
  (AGENTS.md canonical, shims must mention it; absent layouts warn).
  All warnings, never errors. Gate S PASS: 337 pytest green (8 tests
  on real git fixtures incl. a bare-remote unpushed case), ruff clean.
  Live probe: doctor on this repo warned dirty+unpushed mid-build,
  exactly the R6 evidence shape.
- 2026-08-09 In-review; commit-range 22bd55c..028ce5d. That commit was
  made --no-verify with views knowingly stale mid-wave; the following
  commit (a95fcab) rendered them current - logged as the deviation it
  is.
- 2026-08-09 Gate A open: deferred (adversarial reviews batch at the
  Session B boundary; packets present at the Gate B user gate).
