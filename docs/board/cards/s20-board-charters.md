---
id: S20
title: R10 board charters with the bk dogfood charter
status: backlog
depends: [S18]
serialize-with: []
lineage: primary
executor: smart
gates: "S -> A -> U(code-review)"
user-gates: [code-review]
---

# S20: R10 board charters with the bk dogfood charter

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Drain record:
[2026-08-09-feedback-drain-7.md](../../plans/2026-08-09-feedback-drain-7.md)
(part (d) of the dotdir entry, plus part (e) folded here). The ruling is
RULE-6 of the aura plan of record.

## Scope

`src/boardkit/config.py` (`[charter]` block), `src/boardkit/board.py`
(view header), `src/boardkit/brief.py` (brief injection),
`src/boardkit/data/templates/PROCESS.md` and `docs/board/PROCESS.md`
(charter prose and the one-board-per-family guidance), this repo's
`boardkit.toml` (the bk charter, the dogfood), tests.

## Deliverable

A `[charter]` block in the board-root `boardkit.toml` with `owns`,
`not`, and `route`: `owns` is the one-liner mirrored into the S18
registry row, `not` names what the board refuses, `route` maps refused
work to board short-codes resolvable via the registry. The admission
test is one question: where does the diff land. Charters render at the
top of both generated views and are injected into every dispatch brief.
Enforcement is prose-level in v1; `boardkit check` validates presence
of the three keys and that every `route` target resolves to a registry
short-code, nothing more.

Docs guidance ships beside it (folded part (e)): one board per family;
epics and lanes group initiatives; a new board is justified only by a
different source-of-truth repo or lifecycle owner, because cross-board
refs are informational and splitting coupled initiatives removes their
edges from the schedulable DAG.

bk authors its own charter on this card as the dogfood: owns the kit
family (boardkit, rust-holes, the bench), not consumer-repo process
fixes, routes aura-family work to the wiki board.

## Acceptance

- `uv run pytest -q` green; tests cover charter parsing, the
  route-resolvability check, view-header rendering, and brief
  injection.
- Both generated views of this board open with the bk charter, and
  `boardkit dispatch-brief S19` carries it.
- The shipped PROCESS template and this board's copy state the charter
  schema and the one-board-per-family guidance in the same sections and
  agree.

## Gate checklist

- [ ] Gate S: load skill `gate-probes`, then `uv run pytest -q`,
  `uv run ruff check`, `vale` on touched markdown.
- [ ] Gate A: adversarial review, focus: can a charter mislead a
  dispatch (route target that resolves but is wrong, owns line drifting
  from the registry mirror)?
- [ ] Gate U (code-review): present the review packet; stop.

## Branch

direct

## Log

- 2026-08-09 Minted by the seventh feedback drain from part (d) of the
  dotdir entry, with part (e) folded in and check-level validation
  accepted at the interview.
