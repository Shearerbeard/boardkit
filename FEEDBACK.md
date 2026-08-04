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

## v1 migration error presents as a raw traceback

```yaml
date: 2026-08-04
harness: claude-code
agent: claude-fable-5
workstreams: [boardkit]
repo: chore-lottery
source: maintainer session, entry-point canary
```

Running `boardkit check` against a v1 consumer config raises the
migration ValueError uncaught, so the consumer sees a Python traceback
with the remedy buried at the bottom instead of the clean `ERROR:` line
every other refusal uses. The message content is right; the
presentation is the defect. `cmd_check` (and any command that loads
config) should catch config-load ValueErrors and print them through the
normal error path with exit 1.
