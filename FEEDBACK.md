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
