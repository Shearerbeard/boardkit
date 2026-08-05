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

## 2026-08-04 cost-recovery-recipe-bar

```yaml
date: 2026-08-04
harness: opencode
agent: kimi-for-coding/k3
workstreams: [boardkit]
repo: chore-lottery
source: docs/board/retro/2026-08-04-s7-retro.md (cost appendix)
```

<!-- vale ai-tells.VerbTricolon = NO -->
<!-- vale-reason: dense factual inbox prose; the rule fires context-free across whole paragraphs, so a legitimate finding cannot be phrased without tripping it -->
The kit's wave-close cost duty (MODEL-CLASSES.md) requires the closing
handoff to record per-session cost, duration, and token totals, deferring
recovery to the consumer's REVIEW-TOOLING.md. The chore-lottery recipe
failed: opencode export piped into a strict JSON sum broke on raw control
bytes in transcripts, leaving 12 of 14 sessions unextractable. The wave
record fell back to aggregates. The duty presupposes a recipe proven
against real transcripts. Candidate fix: pre-vet the recovery recipe
against one real session transcript, or document the raw-bytes failure
mode.
<!-- vale ai-tells.VerbTricolon = YES -->

## 2026-08-04 canary-read-list-phrasing

```yaml
date: 2026-08-04
harness: opencode
agent: kimi-for-coding/k3
workstreams: [boardkit]
repo: chore-lottery
source: docs/board/retro/2026-08-04-orientation-canary.md
```

The canary procedure in the kit-shipped PROCESS.md lists the cold-start
surface as "the registry's INDEX.md, this file's recovery protocol and
roles sections, board.md, and the cards named in `deferred.md` when that
view exists". Built from that sentence, the S7-session canary brief
omitted deferred.md entirely; the canary abstained on the deferred-gates
question with a correct explanation, and the absence of the view was
itself the answer (the key says "none"). The inspection still passed, but
the conditional phrasing invites the omission and a canary that abstains
leaves a weaker audit record. Candidate fix: the template should name
deferred.md unconditionally and state that an absent view reads as "no
deferred gates".
