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

## 2026-08-04 board-worktree-colocation

```yaml
date: 2026-08-04
harness: claude-code
agent: claude-fable-5
workstreams: [terminalbench, boardkit]
repo: terminalbench-aura
source: ~/dev/claude-skills/feedback/2026-08-04-claude-code-board-worktree-colocation/process-feedback.md
```

Board state colocated with the governed repo's worktrees produced two
recorded failures in the consumer program. First, the S59 branch-state
split (a standing terminalbench blocker): a decided cell's board docs
landed only on the held `card/S59` branch while the program base still
shows the card as backlog, so a fresh session reading the base could
re-run four hours of decided work. Second, reference fragility: review
packets live in a gitignored `reviews/` directory, so packet paths
resolve only in the checkout that generated them, and any fresh worktree
dangles them - the 2026-08-03 batch-1 guide had to embed regeneration
commands to survive this. The consumer mitigates by discipline (pinned
program-control checkout, card worktrees carry no board writes) and the
discipline failed anyway under concurrent sessions. Kit-relevant because
`boardkit.toml` resolves `cards_dir` and the review `output_dir` relative
to the toml inside the consumer repo, reproducing the colocation for
every consumer. Candidate fixes, for the maintainer to weigh: a
machine-dir board root outside any consumer worktree (the user floated
`~/workspace/boards/<name>`; machine-anchored program state has local
precedent in `~/workspace/aura-bench-runner` and the session wiki);
kit-resolved reference anchors instead of checkout-relative paths; packet
references that resolve from any checkout or fail detectably. Full
grounding in the source record.
