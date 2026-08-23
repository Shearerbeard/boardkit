---
id: S44
title: Consolidate the repeated path literals into a constants hierarchy
status: backlog
depends: []
serialize-with: []
lineage: primary
executor: smart
gates: "S -> A -> U(code-review)"
user-gates: [code-review]
---

# S44: Consolidate the repeated path literals into a constants hierarchy

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Minted from Mike's finding at
the wave-2 Phase 2 U(code-review) gate (2026-08-23): the Python modules
repeat path strings that belong in one constants hierarchy.

## Scope

`src/boardkit/` modules holding the repeated literals (`cli.py`,
`config.py`, `board.py`, `contract.py`, `doctor.py`, `brief.py`,
`review_packet.py`), the module that ends up owning the hierarchy
(`contract.py` grows it or a new module joins it), tests.
Behavior-preserving: no path or CLI-surface change, and the scaffolded
config shape stays as it is.

## Deliverable

One definition per structural path fact, following the pattern Mike
named from aura-session-docs (`scripts/wiki_frontmatter.py` there): a
module owns each concept family as named module-level constants, its
docstring names the diverging copies it replaced, and callers import
rather than restate. The duplication sites verified at minting:

- `docs/board/cards` appears in `INIT_CONFIG_TEMPLATE` and is rebuilt
  segment-by-segment in `cmd_init`; the review `output_dir` default and
  the twice-repeated `pin_source` anchor live in the same template.
- The `docs/board/...` doc destinations exist as `CONTRACT_DOCS` tuples
  in `contract.py` and again as loose literals in `cli.py` messages and
  `doctor.py` checks.
- `board.py` half-lifts the view filenames: `graph.md` has a constant
  while `INDEX.md` and `board.md` are literals in both the `GENERATED`
  set and the render map.
- Entry-file and template names (`AGENTS.md`, `PROCESS.md`,
  `_template.md`, the `SKILL.md` probe triple) repeat across
  `contract.py`, `doctor.py`, `cli.py`, and `brief.py`.

Structural facts consolidate; one-off message strings stay where they
are. The init config template may interpolate the constants so the
scaffolded text keeps reading as plain TOML.

## Acceptance

- `uv run pytest -q` green with no test semantics changed.
- Each canonical path segment, filename, and anchor has one definition
  site in `src/boardkit/`, proven by grep in the packet.
- `boardkit check`, `boardkit render --check`, and `boardkit doctor`
  behave identically on this repo before and after.

## Gate checklist

- [ ] Gate S: load skill `gate-probes`, then `uv run pytest -q`,
  `uv run ruff check`, `boardkit check`, `boardkit render --check`,
  `boardkit doctor`.
- [ ] Gate A: adversarial review, focus: did any path fact silently
  change while moving, and does the hierarchy invent structure the
  code does not need?
- [ ] Gate U (code-review): packet to Mike; stop.

## Branch

direct

## Log

- 2026-08-23 Minted by the board owner from Mike's U(code-review)
  finding on the Phase 2 window: repeated copy-paste path strings
  across the Python modules belong in a constants hierarchy, shaped
  like the aura-session-docs consolidation he named as the model. The
  duplication sites in the deliverable were verified by grep at
  minting.
