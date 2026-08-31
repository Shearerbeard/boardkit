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

Prerequisites: Python 3.12 or newer and
[uv](https://docs.astral.sh/uv/getting-started/installation/). boardkit is
not published to a package index; it runs from this checkout:

```sh
export BOARDKIT_HOME=/path/to/boardkit   # its own line, before uv run
uv run --project "${BOARDKIT_HOME:-../boardkit}" boardkit check
```

`boardkit init` scaffolds a new board in the current repo; `check`
validates an existing one; `boardkit doctor` diagnoses the installation.
Running a board end to end also takes an agent harness with the board
skills installed. Claude Code:

```sh
claude plugin marketplace add Shearerbeard/boardkit
claude plugin install board@boardkit
```

OpenCode or Codex:

```sh
cp -R plugins/board/skills/* ~/.agents/skills/
```

`boardkit doctor` names each piece still unwired.
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

## Development

The code lives in `src/boardkit/`, one module per concern: `cli.py` (the
command surface), `config.py` (board discovery and `boardkit.toml`),
`board.py` and `dag.py` (the card registry and graph queries), `doctor.py`
(installation diagnosis), and `review_packet.py`, `receipts.py`, `store.py`
(review evidence). The board-bound skills ship in `plugins/board/`; the docs
`boardkit init` scaffolds live in `src/boardkit/data/templates/`. Tests sit
in `tests/`, with golden fixtures under `tests/golden/`.

```sh
uv run pytest -q        # the suite is the count of record
uv run ruff check       # lint; config in pyproject.toml
vale <changed docs>     # prose lint; run `vale sync` once per checkout
uv run boardkit check   # board validity; also what the pre-commit hook runs
```

pytest and ruff install with uv's dev dependency group; vale is a system
tool - `brew install vale`, then `mkdir -p .vale/styles && vale sync` once
per checkout (the styles dir must exist first, or vale syncs to its global
path instead).

There is no CI pipeline; the gates are local.
`docs/board/pre-commit.sample` runs `boardkit check` on every commit - copy
it into `.git/hooks/` to opt in. Commits follow conventional-commit form
(`type(scope): summary`, as in the git history). Bugs and process friction
go to GitHub issues; planned work is tracked as board cards under
`docs/board/cards/` and advanced through the gates in
`docs/board/PROCESS.md`. There is no changelog while the kit is
unpublished - the board and the git history are the record.

On this repo's own board, `boardkit check` prints two benign warning
classes: commit-range warnings on old cards whose review trailers name
commits a later rebase moved outside the recorded range (historical, and
discharged at those cards' gates), and unresolvable ranges pointing into
the external rust-holes repo, which resolve only on machines that have
that checkout. A freshly scaffolded board prints neither.

Code changes arrive as pull requests against `master` from a fork; open an
issue first for anything larger than a typo fix.

See `EXTRACTION.md` for where every piece of this kit comes from and what
remains to build.
