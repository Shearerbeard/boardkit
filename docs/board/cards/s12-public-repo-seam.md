---
id: S12
title: Public-repo seam for contract docs and generated views
status: ready
depends: []
serialize-with: []
lineage: primary
executor: smart
gates: "S -> A"
user-gates: []
epic: S41
---

# S12: Public-repo seam for contract docs and generated views

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Drain record:
[2026-08-05-feedback-drain-4.md](../../plans/2026-08-05-feedback-drain-4.md),
entries one and two.

## Scope

`src/boardkit/data/templates/` (PROCESS.md, the entry-file templates,
and a new outsider-safe board README template), `src/boardkit/board.py`
(view-header strings), `src/boardkit/doctor.py`, `src/boardkit/cli.py`
(init), tests.

## Deliverable

The kit owns the public/private split the Epoch bootstrap resolved by
hand. A shipped outsider-safe board README template covers how to read
a card (frontmatter and statuses), a contributor path needing only the
repo's own toolchain, and a condensed statement of the gates, with the
contract docs documented as local-only for public repos. `boardkit
doctor` warns when a public remote is configured and contract docs are
tracked. `boardkit init --public` writes the gitignore lines for the
contract docs and `boardkit.toml`. The generated view headers stop
pointing at "PROCESS.md, Delegation protocol": neutral wording or a
pointer derived from a `boardkit.toml` key, so an untracked PROCESS.md
never leaves the views dangling. The PROCESS.md template gains the
"outside contributors do not need this tooling" paragraph
unconditionally.

## Acceptance

- `uv run pytest -q` green; tests cover the doctor warning (public
  remote plus tracked contract docs) and the `--public` gitignore
  writes.
- Rendered `INDEX.md` and `board.md` headers no longer name PROCESS.md
  unconditionally; regenerating this repo's own views stays clean.
- The shipped board README template exists and the template docs state
  which files are outsider-safe versus local-only.

## Gate checklist

- [ ] Gate S: load skill `gate-probes`, then `uv run pytest -q`,
  `uv run ruff check`, `vale` on touched markdown.
- [ ] Gate A: adversarial review, focus: does the header change break
  `views.current` for existing consumer boards, and does the contract
  digest move correctly with the template edits?

## Branch

direct

## Log

- 2026-08-05 Minted by the fourth feedback drain from the Epoch
  public-repo bootstrap findings.
- 2026-08-22 Joined epic S41 (co-worker consumption readiness) at
  the wave-2 Gate U (Phase 0). Grouping only; readiness unchanged.
