---
id: S11
title: Tier the vale prose gate by artifact class
status: done
depends: []
serialize-with: []
lineage: primary
executor: any
gates: "S -> A"
user-gates: []
---

# S11: Tier the vale prose gate by artifact class

Mechanics: [PROCESS.md](../PROCESS.md). Grounding: the VerbTricolon
churn evidence collected across the chore-lottery S7 wave and two
boardkit maintainer sessions, and the codex adversarial review of the
rule (VERDICT: FAIL; per-instance matching is over-broad, the density
sibling carries the defensible tell). Filed to the marketplace inbox as
`feedback/2026-08-05-claude-code-verbtricolon-rule-churn/`.

## Scope

`.vale.ini` in this repo only, plus the same tier applied to the
claude-skills docs tree by the marketplace maintainer's approval
(recorded below). No rule files change on this card; disabling the
per-instance rule at the package level is the marketplace maintainer's
separate disposal of the inbox entry.

## Problem

One flat vale config lints every artifact class at the same severity.
The ai-tells rules earn their strictness on external prose, where an AI
tell costs reputation. On internal factual prose - board cards, process
docs, inbox entries - the per-instance VerbTricolon rule fired eight-plus
times across three sessions on legitimate enumerations, each costing a
rewrite pass or an inline suppression comment. The corpus inbox is worse
than churn: linting sample bodies would corrupt the S10 bench's raw
artifacts, and the no-lint rule lives only in a README today.

## Deliverable

Path-tiered vale config:

- Internal docs tier (`docs/**`, `FEEDBACK.md`): `VerbTricolon` off,
  `VerbTricolonDensity` still at error, everything else unchanged.
- Corpus tier (`bench/prose/corpus-inbox/`): no styles at all, encoding
  the README's verbatim-body rule in the gate itself.
- External tier (shipped templates, commit messages where wired):
  unchanged and strict.

## Acceptance

- `vale` clean over `docs/` without inline suppression comments.
- A probe file in the corpus inbox with a deliberate tricolon lints
  clean; the same text under `docs/` trips only the density rule when
  clustered.
- `uv run pytest -q` green (the templates-prose test still enforces the
  strict tier on shipped templates).

## Gate checklist

- [x] Gate S: load skill `gate-probes`, then `uv run pytest -q`,
  `uv run ruff check`, `vale` over the repo docs, `boardkit check`.
- [x] Gate A: adversarial review of the diff, focus: does any tier
  accidentally weaken the external-prose gate?

## Branch

direct

## Log

- 2026-08-05 Authored from the VerbTricolon churn finding; user
  approved the tiering proposal verbatim ("I like the proposed vale
  fix") and ruled the same tier applies to the claude-skills docs tree.
  Card opened in-progress; executor is the maintainer session.
- 2026-08-05 Gate S PASS: 269 pytest green, ruff clean, vale clean over
  32 doc files, boardkit check clean after render. Acceptance probes:
  a deliberate tricolon lints clean in the corpus inbox (no styles) and
  under docs/ (per-instance off); a syndetic two-tricolon paragraph
  under docs/ still errors via VerbTricolonDensity. Observed limit,
  inherited from the package: the density rule matches syndetic forms
  only, so asyndetic clusters pass - noted in the marketplace inbox
  entry's territory, not this card's.
- 2026-08-05 Gate A PASS (codex lane, author Fable maintainer session).
  Zero findings; the reviewer ran its own vale 3.14.2 probes confirming
  section layering, corpus exclusion, density enforcement, and that
  templates and commit messages stay strict. Companion claude-skills
  tier committed there as 952e5ad. Card DONE.
