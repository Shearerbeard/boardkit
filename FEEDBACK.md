# FEEDBACK.md - process-feedback inbox

This file is boardkit's intake for process friction found while using the
kit from a consumer repo. Consumers append entries here; nobody edits the
kit's templates or code from a consumer repo. A maintainer session drains
entries into `docs/plans/` (or rejects them with a recorded reason) and
deletes them from this file; the plans are the durable record, this file is
a queue.

## Entry format

One `##`-level section per entry, newest last, opening with a fenced YAML
block that matches the claude-skills `feedback/` retro frontmatter, then
the finding in prose:

````markdown
## 2026-08-02 short-slug

```yaml
date: 2026-08-02
harness: claude-code
agent: <model id>
workstreams: [boardkit]
repo: <consumer repo the friction arose in>
source: <path or record the finding is grounded in>
```

What happened, why it is kit-relevant, and the candidate fix if one is
apparent. Ground it in a real session; do not assert from memory.
````

- `harness` uses the claude-skills vocabulary: `claude-code`, `opencode`,
  `codex`, or `antigravity`.
- An entry proposes; the maintainer disposes. Do not pre-commit the kit to
  a fix inside an entry.

## Entries

## 2026-08-05 public-repo-seam-for-contract-docs

```yaml
date: 2026-08-05
harness: claude-code
agent: claude-fable-5
workstreams: [boardkit]
repo: Epoch (github.com/Shearerbeard/Epoch, public OSS)
source: epoch-postgres docs/adr/0009-private-tooling-seam.md and the
  codex adversarial review recorded in that session
```

Bootstrapping the kit into a PUBLIC repo surfaced a seam the templates
do not address: the contract docs (PROCESS.md, MODEL-CLASSES.md,
REVIEW-TOOLING.md) read as the maintainer's AI-orchestration manual to
an outside reader, and an adversarial review graded a tracked
PROCESS.md as a publication blocker (model routing, cost ledger,
session-recovery protocol are maintainer-operational, not a
contribution process). The consumer repo resolved it by gitignoring
all three contract docs plus boardkit.toml, and adding a small
repo-owned docs/board/README.md covering: how to read a card
(frontmatter and statuses), a contributor path that needs only cargo
and git, and a condensed statement of the type-discipline gates.
Candidate kit fixes: (a) a public/private split in the templates - a
shipped BOARD-README.md.template holding the outsider-safe subset, with
the contract docs documented as local-only for public repos; (b) a
`boardkit doctor` check that warns when a public remote is configured
and contract docs are tracked; (c) init writing gitignore lines for
the contract docs behind a --public flag. Also worth folding into the
PROCESS.md template regardless: a short "outside contributors do not
need this tooling" paragraph.

## 2026-08-05 generated-view-headers-assume-process-doc

```yaml
date: 2026-08-05
harness: claude-code
agent: claude-fable-5
workstreams: [boardkit]
repo: Epoch (github.com/Shearerbeard/Epoch, public OSS)
source: codex adversarial review round 2 over the epoch board bootstrap
```

The header prose `boardkit render` writes into INDEX.md and board.md
points readers at "PROCESS.md, Delegation protocol" and "the session
running the board". In a public repo where PROCESS.md is untracked
(see the prior entry), the generated views ship an unresolvable
pointer plus session vocabulary, and the never-hand-edit rule means
the consumer cannot fix it locally. Candidate fix: make the generated
header text configurable or neutral ("see the board README"), or
derive the doc pointer from a boardkit.toml key.

## 2026-08-05 board-hygiene-step-one-assumes-path-install

```yaml
date: 2026-08-05
harness: claude-code
agent: claude-fable-5
workstreams: [boardkit]
repo: epoch-board (private board for github.com/Shearerbeard/Epoch)
source: epoch-board docs/board/retro/2026-08-05-bootstrap-canary.md
```

A codex orientation canary loaded the board-hygiene skill from
~/.agents/skills and obeyed step one literally: it ran bare `boardkit
doctor`, got command-not-found (the kit runs via `uv run --project
"$BOARDKIT_HOME" boardkit ...` from a checkout, never PATH), and
hard-stopped per the skill's own stop rule without reading the board.
The skill's step-one text names the bootstrap ("the repo's agent entry
file carries a bootstrap") but the fenced command block still shows
bare `boardkit doctor`, which is what a literal-minded model executes.
Candidate fix: make every fenced command in the skill use the
checkout-based invocation, or add one line before the first block:
"resolve the invocation from the repo's entry file first; bare
`boardkit` is never on PATH."

## 2026-08-05 skills-prescribe-init-over-sibling-board

```yaml
date: 2026-08-05
harness: claude-code
agent: claude-fable-5
workstreams: [boardkit]
repo: epoch-postgres (public code repo; private board in ../epoch-board)
source: claude-skills feedback/2026-08-05-claude-code-board-discovery-init/process-feedback.md
```

A session in the code repo of a split layout (private board in
`../epoch-board` with `[review].repo = "../epoch-postgres"`; the public
code repo carries no tracked pointer by design) tried to bootstrap a
fresh board even after the user named the existing board's path. The
board-hygiene and delegating-work skills state "`boardkit.toml` at the
repo root" as a hard precondition and prescribe offering `boardkit
init` when it is missing; discovery is cwd-only, so a user-stated
sibling path loses to the precondition. Aggravating: the
hand-bootstrapped board repo lacked the entry files init writes, so
even the right repo offered no CLI bootstrap. Candidate fix: before
offering init, honor a user-named board, a local pointer, or an env
var such as `BOARDKIT_BOARD`, and treat a missing root `boardkit.toml`
as "check for a sibling board" rather than "no board exists"; in split
layouts, remind that the code repo needs an untracked pointer back.
