---
id: S13
title: R5' .boardkit resolution with the CardStore seam
status: in-progress
depends: []
serialize-with: []
lineage: primary
executor: smart
gates: "S -> A -> U(code-review)"
user-gates: [code-review]
---

# S13: R5' .boardkit resolution with the CardStore seam

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Drain records:
[2026-08-05-feedback-drain-4.md](../../plans/2026-08-05-feedback-drain-4.md)
(final entry, the original discovery scope) and
[2026-08-09-feedback-drain-7.md](../../plans/2026-08-09-feedback-drain-7.md)
(the R5' rewrite; the ruling is RULE-2 of the aura plan of record, the
store-seam constraint is RULE-3).

## Scope

`src/boardkit/config.py` (resolution), a new `src/boardkit/store.py`
(CardStore seam), `src/boardkit/board.py` and `src/boardkit/cli.py`
(store construction and the `--board` flag), `src/boardkit/doctor.py`
(resolution reporting), `plugins/board/skills/board-hygiene/SKILL.md` and
`plugins/board/skills/delegating-work/SKILL.md` (the precondition prose),
tests. This repo's own `.boardkit/` lands on S18 with the registry rows,
not here.

## Deliverable

A harness-neutral `.boardkit/` directory convention, superseding both the
R5 `.claude/board` sketch and this card's earlier pointer-file design:

- `manifest.toml`, committed: boards this repo participates in, keyed by
  short-code, each with a `location`; a `default` key.
- `boards/<code>/`, in-repo board homes; per-board commit-or-gitignore is
  the repo's choice (ruled).
- `local.toml`, gitignored: machine overlay resolving `external` boards
  to absolute paths (a wiki checkout, a directory outside git).

Resolution order, first hit wins: `--board <code-or-path>` flag,
`BOARDKIT_BOARD`, walk-up `.boardkit/` (manifest plus overlay), git
common-dir fallback (in a linked worktree, resolve
`git rev-parse --git-common-dir` to the main checkout and read its
`.boardkit/`), then the legacy `boardkit.toml` walk-up so unported
consumers keep working. A resolved location must hold `boardkit.toml` at
the board root; board-level config stays there.

Store-seam constraints (RULE-3) bind the shape: `location` values are
scheme-prefixed store refs (`dir:` today; a bare string means `dir:`;
`linear:` reserved; an unknown scheme is a loud error). The CLI core
talks to a CardStore interface (list/get plus board metadata, with
put/transition/append_log defined on the seam); the markdown-dir layout
is driver #1, not the data model; card identity is the `id` frontmatter,
never the filename. One source of truth per board, views stay
non-authoritative renders, gates/WIP/routing stay kit-side. append_log
ships on the seam with driver-level tests only; no CLI command calls it
yet, and the card log says so.

## Acceptance

- `uv run pytest -q` green; tests cover every step of the resolution
  order, the overlay, the common-dir fallback from a linked-worktree
  fixture, the legacy fallback, and the unknown-scheme error.
- With a `.boardkit/manifest.toml` naming an external board resolved via
  `local.toml`, `boardkit check` runs from a repo with no root
  `boardkit.toml`.
- From a linked worktree with no per-worktree setup, resolution lands on
  the main checkout's `.boardkit/`.
- Both board skills drop the init-first precondition in favor of the
  resolution order, and their contract stamps stay consistent.

## Gate checklist

- [x] Gate S: load skill `gate-probes`, then `uv run pytest -q`,
  `uv run ruff check`, `vale` on touched markdown.
- [ ] Gate A: adversarial review, focus: can the resolution order
  silently target the wrong board (stale `BOARDKIT_BOARD`, overlay
  pointing at a moved checkout, common-dir fallback in a submodule or
  bare-repo layout)?
- [ ] Gate U (code-review): present the review packet; stop.

## Branch

direct

## Log

- 2026-08-05 Minted by the fourth feedback drain from the Epoch
  split-layout discovery findings.
- 2026-08-09 Rewritten by the seventh drain to the R5' ruling (RULE-2)
  with the RULE-3 store seam folded in; the pointer-file design is
  superseded. U(code-review) gate inserted per PROCESS (card predates
  the standing gate).
- 2026-08-09 Pulled in-progress; executor is the maintainer session
  (Session B of the aura plan of record).
- 2026-08-09 Built: resolution order in `config.py` (manifest, overlay,
  common-dir fallback, legacy), `store.py` CardStore seam (list/get/
  transition/append_log; `put` deferred - no caller and no
  format-preserving serialization), `--board` flag wired through the
  CLI and doctor, both board skills re-worded. Gate S PASS: 291 pytest
  green (14 new resolution tests incl. a real linked-worktree fixture,
  8 new store tests), ruff clean, vale clean on the two skill files.
