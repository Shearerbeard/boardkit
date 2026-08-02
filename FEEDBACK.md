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

## 2026-08-02 docs-bustest-wave-close

```yaml
date: 2026-08-02
harness: opencode
agent: claude-fable-5
workstreams: [boardkit, chore-lottery]
repo: chore-lottery
source: chore-lottery docs/board/retro/scratchpad.md (PROCESS FEEDBACK, 2026-08-02)
```

The docs bus test should be a defined step at phase or wave close, not an
ad-hoc audit. The chore-lottery bootstrap wave wrote docs to the standard,
but no cold-read audit ran until the user asked for one; boardkit's
session-close hygiene listed prose lint but no docs audit. A candidate fix
landed in the PROCESS template on 2026-08-02, in the same wave that
created this inbox; the draining maintainer verifies that fix covers this
finding and closes the entry rather than re-planning it.

## 2026-08-02 card-edit-readback

```yaml
date: 2026-08-02
harness: opencode
agent: claude-fable-5
workstreams: [boardkit, chore-lottery]
repo: chore-lottery
source: chore-lottery docs/board/retro/scratchpad.md (TOOLING SLIP, 2026-08-02)
```

A card's gate ticks and log entries written mid-session silently failed to
persist through a multi-step card-edit, sed, and render sequence, and the
loss surfaced only when the user approved a gate over stale state. The
board state had to be reconstructed from git history. Candidate fix: the
PROCESS session-close hygiene names a read-back duty, after any multi-step
edit sequence over a card, read the card file back before committing and
before presenting a gate over it.

## 2026-08-02 no-hardcoded-model-ids

```yaml
date: 2026-08-02
harness: claude-code
agent: claude-fable-5
workstreams: [boardkit, typed-holes]
repo: terminalbench-aura
source: claude-skills feedback/2026-07-28-claude-code-boardkit-transport-wave/skill-retro.md (finding 6b)
```

A program doc's working recipe hardcoded a reviewer model id that later
became the writer's pin, so following the recipe literally violated the
same file's reviewer-differs-from-author invariant. Kit relevance: the
templates instruct dispatch briefs and design records but never warn
against pinning model ids in them. Candidate fix: MODEL-CLASSES or
REVIEW-TOOLING template rule, resolve models from harness configuration at
dispatch time; the ledger records models actually used (a fact about the
past), a recipe naming a future model is a drift hazard.

## 2026-08-02 lint-suppression-disposition

```yaml
date: 2026-08-02
harness: claude-code
agent: claude-fable-5
workstreams: [boardkit]
repo: terminalbench-aura
source: claude-skills feedback/2026-07-28-claude-code-boardkit-transport-wave/skill-retro.md (finding 2)
```

An always-on editor linter substituted acceptably for prose-lint detection
but silently absorbed the disposition step: a promote-to-config decision
(exempting an archive directory from a prose hook) was made ad hoc with no
recorded justification. Kit relevance: the PROCESS commit standards
require prose lint to pass but say nothing about recording why a rule was
suppressed or exempted. Candidate fix: one sentence in the commit
standards, a lint suppression or exemption carries a recorded reason where
it lands (the config comment or the commit body).

## 2026-08-02 per-gate-skill-loads

```yaml
date: 2026-08-02
harness: claude-code
agent: claude-opus-4-8
workstreams: [boardkit, hitl]
repo: aura-orchestration-mode
source: claude-skills feedback/2026-06-17-claude-code-hitl-typed-holes/skill-retro.md (corrective 1)
```

A one-time "load gate-probes first at gate boundaries" imperative stated
once in planning prose did not fire at the commit boundary or the review
gate; mid-flow imperatives decay. Kit relevance: gate checklists that
restate the load per gate (the shape boardkit's plan files already use)
fired reliably; prose that states it once did not. Candidate fix: the
PROCESS Gates section notes that per-gate checklists restate their
deterministic steps rather than referring to an earlier statement.

## 2026-08-02 boardkit-home-export

```yaml
date: 2026-08-02
harness: claude-code
agent: claude-fable-5
workstreams: [boardkit]
repo: terminalbench-aura (upstream-wave session)
source: claude-skills feedback/2026-08-02-claude-code-upstream-wave/process-feedback.md
```

The AGENTS template's bootstrap line only works with an exported
BOARDKIT_HOME or the default `../boardkit` layout: a same-line
environment prefix (`BOARDKIT_HOME=... uv run ... "${BOARDKIT_HOME:-../boardkit}"`)
expands the parameter before the assignment lands, so the command
silently targets the default path. Found while smoke-testing the
2026-08-02 template change. Candidate fix: one sentence in the AGENTS
template noting the variable must be exported.
