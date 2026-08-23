---
id: S42
title: Fix doctor host checks that misfire on in-repo board homes
status: backlog
depends: []
serialize-with: []
lineage: primary
executor: smart
gates: "S -> A -> U(code-review)"
user-gates: [code-review]
---

# S42: Fix doctor host checks that misfire on in-repo board homes

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Minted as residue of the S31
(docking-convention spec) verification pass; the misfires are recorded
as Known limits in [DOCKING.md](../../DOCKING.md).

## Scope

`src/boardkit/doctor.py` (`config.repo-root`, `env.boardkit-home`),
`src/boardkit/config.py` only if selector handling moves, tests.

## Deliverable

Three verified misfires, each reproduced against a throwaway host repo
during S31:

- `config.repo-root` warns "the walk-up reached a parent repository's
  board" for a legitimately docked board under
  `.boardkit/boards/<code>/`. The layout is supported; the message
  describes a different failure. Compare against the docking
  directory's owner rather than the board root alone.
- `env.boardkit-home` computes its `../boardkit` default relative to
  the board root, so for a docked board the warning names a path under
  `.boardkit/boards/` that nobody would install to.
- `--board ""` is treated as a short-code and fails with `no board ''`
  while `BOARDKIT_BOARD=""` falls through to the walk-up. Decide
  whether the flag should match the variable's blank-skip or fail as
  it does today, and state the choice in DOCKING.md (a behavior change
  bumps the spec version per its own rule).

## Acceptance

- `uv run pytest -q` green with a regression test per misfire.
- `boardkit doctor` on a fixture host with a board at
  `.boardkit/boards/<code>/` raises neither misfiring warning.
- DOCKING.md's Known limits section updates to drop what this card
  fixes; if flag semantics change, the spec version bumps.

## Gate checklist

- [ ] Gate S: load skill `gate-probes`, then `uv run pytest -q`,
  `uv run ruff check`, `boardkit check`, `vale` on touched markdown.
- [ ] Gate A: adversarial review of the diff against the spec's
  resolution order.
- [ ] Gate U (code-review): packet to Mike; stop.

## Branch

direct

## Log

- 2026-08-22 Minted by the board owner as residue of S31's
  code-verification pass. All three misfires were reproduced against a
  throwaway host repo and are recorded in DOCKING.md's Known limits;
  this card exists so the fix is scheduled work rather than a spec
  footnote.
