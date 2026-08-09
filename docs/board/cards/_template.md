---
id: SX
title: Short imperative title
status: backlog
depends: []
serialize-with: []
lineage: none
executor: any
gates: "S -> A"
user-gates: []
---

# SX: Short imperative title

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). If this card implements part of
a larger plan or design doc, link that doc here.

## Scope

The exact files the executor may touch. If the work needs
anything else, stop and report instead.

## Deliverable

The artifact this card produces.

## Acceptance

Commands or named files with pass criteria. Every criterion verifiable
by running something or reading a named file.

## Gate checklist

- [ ] Gate S: named deterministic checks.
- [ ] Gate A: fresh-agent review focus.

## Branch

Worktree cards: local branch `card/<id>` off the base named by
`lineage`; no pushes before gates pass; rebased onto the primary. The
board owner sets the `commit-range` frontmatter when the card enters
In Review (it feeds `boardkit review-packet`, PROCESS.md board
mechanics) and repeats the final range in the Done log entry. Cards
with no branch of their own: state "direct" instead. External-repo
cards (`lineage: none`) keep no branch; they state "direct" and record
their external commit shas in the Log as work lands.

## Log

- YYYY-MM-DD One-line dated entries, appended in the same turn as the
  state change they record.

<!-- Frontmatter contract (all keys required except commit-range and
side-quest; validated by `boardkit check`):
id: <prefix><number> or a sentinel id, per boardkit.toml; unique.
status: backlog | ready | in-progress | in-review | done.
  "ready" requires every depends entry to be done (validated).
depends: card ids that must be Done first. Includes lineage-ordering
  edges (a behavior card depends on the decision that mints its
  base), so this list is the complete ordering DAG; the lineage key
  below names only the base ref.
serialize-with: cards sharing files; may not be In Progress together
  (validated); must be reciprocated on the other card (validated).
lineage: primary | accepted-head | isolated-branch | none.
executor: smart | any. See MODEL-CLASSES.md for the class each allows.
gates: human-readable gate order string.
user-gates: list of named user stops, for example [mockup, launch].
commit-range: A..B shas of the card's commits, set by the board owner
  when the card enters In Review; absent until then. Feeds
  `boardkit review-packet` (in-review lineage cards without it fail
  `boardkit check`). A card spanning two repos generates the second
  repo's packet with `--repo <path> --suffix <name> --commit-range
  <a>..<b>`, since these shas exist in the primary repo only.
side-quest: true | false, absent meaning false. True marks the card as
  part of a flow the user has declared a detached side quest, which
  PROCESS.md exempts from the WIP limit. Set it only on the user's
  explicit declaration. It exempts the card from the WIP count alone:
  serialize-with still applies.
lane: optional; a lane name from [[board.lanes]] in boardkit.toml. Only
  valid on boards that declare lanes (validated).
refs: optional; qualified cross-board references (<code>/<id>, e.g.
  tb/S91), informational only; never affects readiness (validated
  against the family registry by boardkit check).
kind: optional; card (default) or epic. An epic card names an
  initiative and may not itself carry the epic key.
epic: optional; id of the same-board epic card this card serves
  (validated: target exists and is kind epic). Grouping, never
  dependency.
File naming: <id-lowercase>-<slug>.md, unique lowercase slugs. -->
