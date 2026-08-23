# Docking convention v1

<!-- boardkit-contract: v2 -->
<!-- docking-spec: v1 -->

Docking is how a tool finds the state it owns from wherever a session is
standing. boardkit docks at `.boardkit/`: a directory at a repository's root
naming the boards that repo participates in and where each one lives. Every
step of the lookup is computed at run time from the filesystem, so there is
no symlink or pointer file to go stale when a checkout moves.

This document states the convention as a contract, so a second tool can
implement it without reading boardkit's source and a reviewer can check an
implementation against a written order. It describes what
`src/boardkit/config.py` ships today. Where the two disagree the code is the
truth and this document is the defect; fix the document.

Covered here: the resolution order, the docking directory's contents, the
common-dir fallback, the postures a consuming repo may take, and what a
second consumer has to implement. Covered elsewhere: the family-registry
fields a manifest row may carry beyond `location` (`README.md`, "Board
resolution and the family registry"), board-level configuration
(`boardkit.toml` at each board root), and the gate process
(`docs/board/PROCESS.md`).

## Version

This is docking spec v1. The version bumps when what an adopter must
implement changes - a step added or removed, a changed precedence, a renamed
file, a rewritten posture rule - and stays put for wording. The
`boardkit-contract` stamp above names the delegation contract version this
document was written against, as every shipped doc in this repo does; the
two versions are independent of each other.

## The docking directory

By convention `.boardkit/` sits at the root of the host repository - the git
checkout a session works in, which is not always the board's own root. The
walk-up accepts one at any depth, and the common-dir fallback looks only
beside the main checkout's git directory, so the root is where a docking
directory reaches every worktree of the repo. It holds:

- `manifest.toml`, required. The boards this repo participates in, keyed by
  short-code, plus the `default` code. Its presence is what makes a
  directory a docking directory: a `.boardkit/` without it is invisible to
  resolution, and the walk-up continues past it.
- `local.toml`, optional and never committed. The machine overlay that
  resolves `external` boards to absolute paths on this machine.
- `boards/<code>/`, optional. In-repo board homes, committed or ignored per
  the repo's posture.

Board-level configuration stays in `boardkit.toml` at each board's root; the
docking directory holds none of it. Agent entry files (`AGENTS.md` and its
shims) live at the host repo root, which for a `.boardkit/boards/<code>/`
layout sits above the board root.

### manifest.toml

```toml
default = "bk"

[boards.bk]
location = "dir:."

[boards.aura]
location = "external"
```

`default` must name a `[boards.<code>]` table that the file also declares.
Unknown top-level keys and unknown row keys are errors, so a typo surfaces
instead of being ignored.

`location` is a scheme-prefixed store ref:

- `dir:<path>` is the only driver implemented. Relative values resolve
  against the directory that contains `.boardkit/`, not against the docking
  directory itself. An absolute value resolves to itself, but a path that is
  true of one machine belongs in the overlay rather than in a committed
  manifest.
- A bare string with no scheme means `dir:`, so a directory literally named
  `external` has to be written `dir:external`.
- The exact keyword `external` defers the location to `local.toml`.
- `linear:` is reserved and refused with a message saying so, rather than
  read as an unknown scheme.
- Any other scheme is an error naming the schemes that exist.

A malformed manifest fails loudly at whichever step reads it. It never falls
through to a later step: a manifest with a typo in it must not quietly
select a different board than the one its author meant.

### local.toml

```toml
[boards.aura]
path = "/absolute/path/to/board"
```

`path` is the only key a row may carry, and it must be absolute. A relative
path is refused with its reason, because it would resolve against the
process working directory and silently land on whatever board sits there.
Paths are expanded and resolved before use, so a symlinked or aliased
checkout compares equal to the board root it points at.

An absent `local.toml` is an empty overlay, which matters only when an
`external` row actually has to resolve. Then the error names the file, the
code, and the line to add.

## Resolution order

Five steps, first hit wins.

1. **`--board <short-code|path>`.** Honored whenever the flag is present.
2. **`BOARDKIT_BOARD`.** Same selector grammar as the flag. A variable set
   to the empty string is skipped rather than honored, so an unset-by-blank
   export falls through instead of failing.
3. **Walk-up `.boardkit/`.** From the working directory up through every
   parent, the first directory holding `.boardkit/manifest.toml` wins, and
   the board is that manifest's `default`.
4. **Git common-dir fallback.** The main checkout's `.boardkit/`, reached
   from a linked worktree. See below.
5. **Legacy `boardkit.toml` walk-up.** From the working directory up through
   every parent, the first `boardkit.toml` wins. This is what keeps a
   consumer that never adopted the docking directory working unchanged.

When no step answers, the failure names all five in one message rather than
reporting only the last thing tried.

**Selector grammar.** A selector is a path when it contains a path
separator, or is exactly `.`, `..`, or `~`, or starts with `~/`. Anything
else is a short-code. The test is on the string's shape and never on what
exists: a directory in the working directory that happens to share a
short-code's name must not hijack the code. A path selector resolves to a
`boardkit.toml` file or to a directory holding one, and anything else is an
error. A short-code selector needs a registry to resolve against, and finds
one through steps 3 and 4 - so those two steps serve twice, once as
resolution steps of their own and once as the registry search for steps 1
and 2.

**The winning step is reported, not discarded.** `boardkit doctor` prints
`resolved via: <source>`, and carries the same value as `resolution_source`
under `--json`. The source is `--board`, `BOARDKIT_BOARD`, the path of the
`.boardkit/` that answered, `git common-dir <path>`, or `legacy walk-up`. A
stale environment variable or a moved overlay can still select a board that
is not the one the session meant; naming the step that chose is what makes
that visible instead of silent.

**`--config <path>` bypasses the order.** It names a `boardkit.toml`
directly and wins over every step above, including the flag. Treat it as an
escape hatch for tooling that already knows the board root, never as a sixth
step: it carries no registry provenance, so registry validation then falls
back to searching from the board root.

**Registry lookups follow a shorter path.** Enumerating the family
(`boardkit boards`) searches steps 3 and 4 from the process working
directory only; the flag and the environment variable have no say in which
registry is read. The validations that `boardkit check` runs (registry row
drift, charter route targets, cross-board refs) are handed the `.boardkit/`
that resolved the board, so a board reached by short-code is judged against
the registry that chose it rather than against whatever sits above the
shell.

## The common-dir fallback

Step 4 runs `git -C <cwd> rev-parse --git-common-dir` and accepts the answer
only when it is absolute. A linked worktree answers with the main checkout's
git directory; the main checkout answers a relative `.git`, and step 3 has
already covered that case. The candidate is the sibling of that git
directory, `<common>/../.boardkit/`, and it is accepted only when it holds
`manifest.toml`.

Every other outcome yields nothing and resolution continues to step 5: git
missing from the host, a working directory outside any repository, a
non-zero exit.

Two properties earn this step its place:

- A linked worktree resolves its main checkout's board with zero
  per-worktree setup. No symlink to create, no manifest to copy, nothing to
  re-point when the worktree is thrown away and remade.
- The lookup stats the filesystem and never asks git what is tracked. The
  one git call reports a path, not a tracking state, so an untracked or
  excluded `.boardkit/` resolves exactly like a committed one. That is the
  property the three postures below depend on.

The step assumes the common git directory sits inside the main checkout, at
`<main>/.git`. A repository built with a separate git directory, or a bare
repository serving worktrees, puts the candidate somewhere that holds no
manifest; the step then finds nothing and falls through rather than guessing
where the checkout went.

## Consumer postures

A repo that docks chooses how much of the docking directory its history
carries. All three postures resolve identically, because resolution stats
the filesystem.

- **Committed.** `.boardkit/manifest.toml` is tracked; `.gitignore` carries
  `.boardkit/local.toml` so the machine overlay stays local. For a repo
  whose team shares the board. This repo is the worked example: see its
  `.boardkit/manifest.toml` and the ignore line `boardkit init` appends.
- **Gitignored.** The docking directory exists on disk and the repo's
  tracked `.gitignore` carries `.boardkit/`. For a repo that tolerates a
  boardkit-shaped line in its history but does not want the manifest in it -
  a board that is one contributor's working state rather than the project's.
- **Invisible.** Nothing about boardkit reaches the repo's tracked history
  at all: the docking directory is excluded per-clone through
  `.git/info/exclude`, which git never tracks. For a repo where the personal
  workflow must leave zero traces, such as a work OSS checkout where even a
  `.gitignore` edit would be a trace. This posture is the reason resolution
  may never consult git's tracking state.

**Promotion rule.** Invisible is a one-clone posture. `.git/info/exclude` is
per-clone state, so a second clone, a second machine, or a second person
repeats the exclusion by hand or has the directory show up as untracked
noise. When a second adopter appears, promote invisible to a tracked
`.gitignore` line as a deliberate step - a decision the repo's owners take
and record, never a silent upgrade by whoever notices first. Promoting again
from gitignored to committed is the same kind of step, taken when the board
stops being one person's working state and becomes shared state the repo
maintains.

Demotion is never automatic either. A repo that goes quiet on boardkit
leaves its posture where it is until someone decides otherwise; the CLI
reads no posture and enforces none.

## Adopting the convention in another tool

A second consumer implements the same order over its own dot-directory.
`boardkit init` scaffolds nothing under `.boardkit/`, so adoption is a
deliberate act in either tool: the directory and its manifest are written by
hand or by the adopting tool's own scaffolder.

Five names, three of them the adopter's to choose:

| Name | boardkit | Adopter |
| --- | --- | --- |
| Docking directory | `.boardkit/` | `.<tool>/` |
| Registry file | `manifest.toml` | `manifest.toml` |
| Machine overlay | `local.toml` | `local.toml` |
| Selector flag | `--board` | the tool's own noun |
| Selector variable | `BOARDKIT_BOARD` | `<TOOL>_<NOUN>` |

Keep the two filenames as they are. An adopter that renames them buys
nothing and costs every reader who has to learn which tool calls the overlay
what.

Then implement the order. These eight requirements define a conformant
implementation, and they are the checklist a reviewer runs against one:

1. Five steps in the stated precedence, first hit wins, with the flag above
   the variable above the walk-up above the common-dir fallback above the
   legacy walk-up. A tool with no legacy layout to support states that step
   as not applicable rather than renumbering the rest.
2. The walk-up accepts a directory only when the registry file is present
   inside it, and continues upward otherwise.
3. The common-dir fallback accepts only an absolute `--git-common-dir`
   answer, requires the registry file at the candidate, and returns nothing
   on every other outcome.
4. A malformed registry or overlay fails loudly at the step that read it and
   never falls through to a later step.
5. Overlay paths are absolute, and a relative one is refused with its
   reason.
6. Resolution carries which step answered, and the tool's diagnostic prints
   it.
7. Resolution reads the filesystem only. No step may consult git's index or
   tracking state, or the invisible posture breaks.
8. The three postures are the consuming repo's choice, and the promotion
   rule above is documented where that repo's contributors will read it.

A second consumer that satisfies all eight has adopted the convention; the
adoption card records where each requirement landed.

## Divergence and library extraction

The convention is duplicated on purpose. Two independent implementations of
an eight-point contract cost less than a shared library does at two
consumers, and the copies stay honest as long as they agree.

Divergence is the trigger. When a second consumer's copy has to differ on
any of the eight requirements - a step it cannot implement, a precedence its
host makes impossible, a posture that does not apply - that divergence is
recorded on the adopting card and becomes the case for extracting the
resolver into a library the consumers share. S36 (rust-holes docking
adoption) is the first such card. Until a divergence lands there, extraction
is not a card. Silently forking the order is the failure this rule exists to prevent:
one spec, not three walk-ups that drifted.

## Known limits

- **The walk-up is not bounded by the repository.** Step 3 climbs past a
  repository boundary, so a submodule or nested checkout with no docking
  directory of its own can select a superproject's board before the
  common-dir fallback runs. Confirmed behavior, raised at S13's Gate A
  (board discovery, finding 3) and open: whether the walk-up should stop at
  a repository boundary is the board owner's call.
- **`config.repo-root` warns on any board root below the git top level.**
  Doctor compares the two and warns when they differ. That catches the
  crossing above, and it also fires on a supported in-repo board home under
  `.boardkit/boards/<code>/`, where the message about reaching a parent
  repository's board misreads what happened. The layout is fine; the
  warning's wording predates it.
- **`env.boardkit-home` computes its default from the board root.** For a
  board under `.boardkit/boards/<code>/`, the `../boardkit` default in that
  warning resolves relative to the board root rather than the host repo
  root, so the path it names is not one anybody would install to. Export
  `BOARDKIT_HOME` and the warning goes away.
