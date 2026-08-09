---
id: S18
title: R4 boards registry - the manifest is the registry
status: in-review
depends: [S13]
serialize-with: []
lineage: primary
commit-range: deb9c2b..bb2d0f8
executor: smart
gates: "S -> A -> U(code-review)"
user-gates: [code-review]
---

# S18: R4 boards registry - the manifest is the registry

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Drain record:
[2026-08-09-feedback-drain-7.md](../../plans/2026-08-09-feedback-drain-7.md)
(first drained entry, plus interview decision 5).

## Scope

`src/boardkit/config.py` (manifest row schema), `src/boardkit/cli.py`
(the `boards` command), `src/boardkit/doctor.py` (row-vs-board
verification), this repo's own `.boardkit/manifest.toml` (the bk
dogfood rows), docs, tests.

## Deliverable

The `.boardkit/manifest.toml` from S13 grows into the family registry.
Each `[boards.<code>]` row carries `location` (scheme-prefixed),
`engine`, `id_prefix`, and `scope` (one line; the charter `owns` mirror
once S20 lands). Optional `status` marks a row `transitioning`,
`external`, or `archived`. Engine heterogeneity is data: pre-boardkit,
hand-maintained, and TODO-file surfaces are first-class rows, so the
registry can describe a family before it is uniform.

`boardkit boards` enumerates from the resolved manifest plus
`local.toml`: one row per board with short-code, home, engine, prefix,
scope, and whether the home currently resolves on this machine.
Uniqueness: short-codes are unique by TOML table semantics; a new row
claiming an id prefix another row already holds fails validation unless
the collision is marked known on the row, because the aura family's
existing S-prefix collisions must remain describable while new ones are
refused. For `dir:` rows, cached fields are verified against the
board's own `boardkit.toml`; a mismatch fails `boardkit check`. A
second hand-maintained family copy is forbidden: prose indexes generate
from these rows.

## Acceptance

- `uv run pytest -q` green; tests cover row parsing, the known-collision
  refusal for new prefix claims, `dir:` row verification, and an
  external row with and without an overlay path.
- `boardkit boards` run in this repo answers from
  `.boardkit/manifest.toml` and lists the bk board without reading any
  hand-written index.
- A cross-board resolution test exists: from a fixture repo whose
  manifest names two boards, resolving each short-code lands on the
  right `boardkit.toml`.

## Gate checklist

- [x] Gate S: load skill `gate-probes`, then `uv run pytest -q`,
  `uv run ruff check`, `vale` on touched markdown.
- [ ] Gate A: adversarial review, focus: can the registry lie (cached
  row drifting from the board config, an overlay masking the committed
  location, collision marks papering over a real new collision)?
- [ ] Gate U (code-review): present the review packet; stop.

## Branch

direct

## Log

- 2026-08-09 Minted by the seventh feedback drain from the 2026-08-07
  registry entry, shaped by the manifest-is-registry interview decision
  and the RULE-3 store-seam constraints.
- 2026-08-09 Pulled in-progress straight from backlog: S13 is in-review
  in the same sitting and the dependency is on S13's diff, not its done
  state (same-hand build order per drain 7). Executor is the maintainer
  session.
- 2026-08-09 Built: registry fields on manifest rows (optional per the
  RULE-2 minimal shape; `dir:` boards self-describe and cached fields
  verify against them), `registry_rows` validation with the marked-
  collision rule, `boardkit boards` (+ `--json`), row drift wired into
  `check` via `board_row_errors`, the bk dogfood manifest, README
  section. Maintainer adjustment vs the card text: row verification
  landed in `boards` + `check`, not doctor - check is where drift
  fails; doctor stays installation-level. Gate S PASS: 302 pytest
  green (10 registry tests + the named Gate B cross-board resolution
  test), ruff clean, vale clean on README.
- 2026-08-09 Acceptance run: `boardkit boards` in this repo answers
  from `.boardkit/manifest.toml` (bk row, default-marked, reachable);
  `--json` emits stable fields; cross-board test
  `test_cross_board_resolution_lands_each_code_on_its_own_config`
  passes.
- 2026-08-09 In-review; commit-range deb9c2b..bb2d0f8.
- 2026-08-09 Gate A open: deferred (adversarial reviews batch at the
  Session B boundary; packets present at the Gate B user gate).
