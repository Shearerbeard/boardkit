# boardkit

**Status: unpublished; runs from a local checkout.** In daily use by its
own board and the consumer repos that point `BOARDKIT_HOME` at this
checkout; not on any package index.

boardkit is a process kit for AI-assisted software development. It packages
three practices that were proven on a live project and extracts them into a
form any repository can adopt:

1. **A gated card board.** Work is tracked as one markdown card per task with
   validated frontmatter (dependencies, serialization constraints, executor
   class, review gates). A CLI validates the board, generates index and kanban
   views, and detects drift. A gate ladder (self-check, agent review, manual
   exercise, drift audit, frontier review, user gate) controls when work may
   advance and when a human must be pulled in.
2. **The typed-holes dev flow.** Domain types are designed first (in the style
   of *Domain Modeling Made Functional*), landed as a compile-clean skeleton
   with `todo!()` bodies, adversarially design-reviewed, and only then filled
   in - often by smaller, cheaper models.
3. **Model-class delegation.** A written policy for which class of model
   handles which size of job (frontier orchestrators, mid-class writers,
   small-class explorers), with the invariant that a reviewer never shares a
   model with the author of the diff it reviews.

You can run the board from Claude Code or OpenCode. Codex support is a named
deferral, not an omission (see `EXTRACTION.md`).

## Quick start

boardkit is not published to a package index; it runs from this checkout
via [uv](https://docs.astral.sh/uv/):

```sh
export BOARDKIT_HOME=/path/to/boardkit   # its own line, before uv run
uv run --project "${BOARDKIT_HOME:-../boardkit}" boardkit check
```

`boardkit init` scaffolds a new board in the current repo; `check`
validates an existing one; `boardkit doctor` diagnoses the installation.
The `export` must be its own line: a same-line prefix expands the
`../boardkit` default before the assignment lands and silently targets
the wrong checkout.

## Diagnostics and routing

A board declares a delegation contract in `boardkit.toml`: one `[routes.*]`
table per transport you can dispatch to, and one `[roles.*]` table per
required role (executor, code review, prose review, frontier review, drift
audit, canary). Three commands read it.

- `boardkit doctor` diagnoses the whole installation from cold and reports
  every check by a stable id, with `--json` for tooling.
- `boardkit resolve-route <role>` answers which transport serves one role,
  and fails rather than guessing when that route is unfilled.
- `boardkit dispatch-brief <card-id>` generates a card's brief: the card
  verbatim, its reference links, the resolved routes, and the process clauses
  quoted from your own docs rather than restated.

Every shipped doc carries a stamp (`<!-- boardkit-contract: v2 -->`) naming
the contract version it was written against, and `boardkit.toml` declares the
same version under `[contract]`. Doctor compares them, so a kit that has
moved ahead of a repo says so instead of behaving strangely.

## Board resolution and the family registry

The CLI computes which board it targets from the filesystem instead of
reading a stored pointer, so a linked worktree or a moved checkout needs no
per-clone setup. `docs/DOCKING.md` is the versioned spec: the five-step
resolution order, what `.boardkit/` holds, the git common-dir fallback, and
the three postures a consuming repo may take (committed, gitignored, or
invisible through `.git/info/exclude`). Board-level config stays in
`boardkit.toml` at each board's root.

`boardkit dag --to <id|epic>` answers goal-directed questions over one
board. Its output has four parts - the goal's ancestor closure, the
unblocked frontier, a wave partition over the remaining work, and which
gates sit on which edges - and `--render` emits the plan as Mermaid. A
standing `graph.md` view (status-colored, epic and lane clusters)
regenerates with the other views.

`.boardkit/manifest.toml` is also the family registry: rows may carry
`engine`, `id_prefix`, `scope`, and `status`, so pre-boardkit,
hand-maintained, and TODO-file surfaces are first-class rows. `boardkit boards` (with `--json`
for tooling) enumerates the family from it, fills a `dir:` board's prefix
from that board's own config, verifies cached row fields against it, and
refuses an id-prefix collision unless every colliding row is marked
`prefix_collision_ok = true`. Prose indexes generate from these rows; a
second hand-maintained family copy is forbidden.

`check` and `doctor` answer different questions. `check` is board validity:
are the cards well-formed and the generated views current? It is what the
pre-commit hook runs. `doctor` is installation readiness: is this repo wired
up to actually dispatch work? A freshly scaffolded repo passes `check` and
fails `doctor`, by design - `boardkit init` writes placeholders instead of
pretending a transport is configured, and doctor names each one still to
fill in.

The language skills the flow's writers and reviewers load (rust-*, python-*,
docs-*) are not part of this kit; they install alongside it from
[claude-skills](https://github.com/Shearerbeard/claude-skills).

See `EXTRACTION.md` for where every piece of this kit comes from and what
remains to build.
