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

## 2026-08-09 review-artifact-audit-trail

```yaml
date: 2026-08-09
harness: claude-code
agent: claude-fable-5
workstreams: [boardkit, wiki-system]
repo: aura-session-docs (Gate A of the board-consolidation plan)
source: aura-session-docs reports/gate-a-adjudication-list-2026-08-09.md (D4 section) and DECISIONS.md "Gate A rulings - board consolidation (2026-08-09)"
```

At Gate A, Mike ruled the wiki-side D4 question keep-ephemeral: review
packets stay gitignored and machine-local, the card log stays the durable
record. He attached a standing direction for the kit: the eventual version
of boardkit must carry a full audit trail of review artifacts as a
first-class feature, with the machine-local arrangement accepted only as
an interim state. Evidence of the gap: 159 review files (Gate A ledgers, review
packets with full diffs, secvet reviews, design-panel rounds) exist only on
one machine's disk across three untracked copies, while an archived board's
README claims them as part of the record; a wiki clone does not have them.
Two candidate shapes when the maintainer takes this up: a durable
artifact store under the store seam - a blob concern beside CardStore,
per the 2026-08-09 rulings - or a tracked-archive convention that covers
frozen boards only.
Proposes; the maintainer disposes.
