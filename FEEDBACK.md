# FEEDBACK.md - process-feedback inbox

This file is boardkit's intake for process friction found while using the
kit from a consumer repo. Consumers append entries here; nobody edits the
kit's templates or code from a consumer repo. A maintainer session drains
entries into `docs/plans/` (or rejects them with a recorded reason) and
deletes them from this file; the plans are the durable record, this file is
a queue.

This inbox is the canonical intake (affirmed 2026-08-09, drain 7). A
maintainer drain MAY also sweep claude-skills `feedback/` for entries that
name boardkit and were never mirrored here; when it does, the drain record
names that source explicitly.

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

## 2026-08-22 opencode-exit0-truncation-not-in-stall-protocol

```yaml
date: 2026-08-22
harness: claude-code
agent: claude-fable-5
workstreams: [boardkit, claude-skills]
repo: boardkit (its own board, the spread-readiness review panel)
source: claude-skills feedback/2026-08-22-claude-code-opencode-exit0-truncation/process-feedback.md
```

REVIEW-TOOLING's stall protocol names one stall signature (a quiet
process at near-zero CPU) plus the empty-return rule, but the failure
this session hit four times is neither: `opencode run` exited 0
mid-review with the trace cut at a tool call and no final message,
after minutes of real, billed work - the three failed runs on one
provider lane cost more than the successful review on another. The
template carries no probe ladder (nonce read-back, then a bounded
dispatch-shaped smoke, then the full run) and no
second-truncation-switch-lanes rule, and the pre-vet's read probe
cannot catch a failure that only appears at full run length. Candidate
fix: the stall protocol names this second signature with its
discriminator (real tokens billed, versus the hang's zero), and the
pre-vet section gains the ladder with the caveat that a passing smoke
does not clear a lane for long runs. Proposes; the maintainer
disposes.
