---
id: S13
title: R5' .boardkit resolution with the CardStore seam
status: in-review
depends: []
serialize-with: []
lineage: primary
commit-range: 8bd2624..deb9c2b
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
- [x] Gate U (code-review): present the review packet; stop.

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
- 2026-08-09 In-review; commit-range 8bd2624..deb9c2b (work commit
  deb9c2b; the drain commit carried this card's board writes).
- 2026-08-09 Gate A open: deferred (adversarial reviews batch at the
  Session B boundary so the reviewer sees the whole wave; packets
  present at the Gate B user gate).
- 2026-08-11 Gate U(code-review) passed: Mike reviewed the packet
  (batch 1 with S24), verdict pass with one finding. Finding: config
  values should come from the config file - the `X | None` manifest/
  registry fields were judged correct (the file may omit them; R4 needs
  heterogeneous rows), but board.py's `WIP_LIMIT = 2` code constant is
  config-in-code and should migrate to a `[board] wip` key defaulting
  to 2. Routed to the drain-8 inbox. Gate A batch deferral survives
  this gate (surfaced, not absorbed).
- 2026-08-16 Gate A ran (resolving the deferral): reviewer gpt-5.6-sol
  via codex exec, author claude-fable-5 (whole wave); dispatched on the
  codex fallback after the pinned opencode lane stalled its read probe
  on two models. Verdict FAIL, four findings.
  1. BLOCKING resolution computed which selector won and discarded it,
     so a stale BOARDKIT_BOARD or overlay could choose silently.
     Confirmed. Fixed in 1214b10: doctor carries the source through the
     report ('resolved via:' / resolution_source), per the card's
     doctor-scoped resolution-reporting promise.
  2. BLOCKING local.toml accepted relative paths, which resolve against
     the process cwd. Confirmed. Fixed in 1214b10: the loader refuses a
     non-absolute overlay path loudly.
  3. BLOCKING the .boardkit walk-up is unbounded by the repo, so a
     submodule without its own .boardkit can select a superproject's
     board before the common-dir fallback runs. Confirmed as behavior;
     disposition escalated: the walk-up shape is the R5' ruled order
     and doctor's config.repo-root already warns on the legacy variant
     of this crossing. Whether the .boardkit walk-up should stop at a
     repo boundary is Mike's call - surfaced at the next user gate
     with the batch-2 packets.
  4. BLOCKING the CardStore seam is unused by production code and lacks
     the board-metadata surface; put is absent. Split: the put half
     rejected as already ruled (deferral and reason logged 2026-08-09);
     the wiring and metadata halves confirmed and minted as S28 rather
     than patched mid-review.
  Reviewer-reported UNVERIFIED (sandbox): pytest and writable-fixture
  acceptance runs - run board-owner-side: 341 pytest green, ruff clean.
  Fix commit 1214b10 sits apart from the reviewed range with foreign
  commits between, so commit-range stays 8bd2624..deb9c2b and the
  fix-commit re-review runs over 1214b10^..1214b10 via the packet
  override; Gate A's box stays unticked until that re-review passes.
