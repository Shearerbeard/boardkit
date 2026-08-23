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

## 2026-08-22 serialize-with-misses-in-review-fix-rounds

```yaml
date: 2026-08-22
harness: claude-code
agent: claude-fable-5
workstreams: [boardkit]
repo: boardkit (its own board, wave-2 Phase 2)
source: docs/board/cards/s29-shim-classification-hardening.md log, S29 executor report 2026-08-22
```

Two live collisions from one session. S29 (shim convention) and S31
(docking spec) both edit the AGENTS.md doc pair; neither card declared
`serialize-with`, and the board owner dispatched S31's executor while
S29's Gate A fix round was still writing the tree. The letter of the
WIP rule held - S29 was `in-review` when S31 went `in-progress` - but a
fix round is live authoring the serialize-with rule does not cover, so
two executors interleaved on shared files: one executor's vale gate
failed on the other's uncommitted sentence, and the byte-identical
doc-pair sync (a whole-file copy) was one timing window away from
silently reverting the other card's edit. Two candidate fixes, either
sufficient: the serialize-with rule extends to any card with a live fix
round, not just `in-progress` status; or entry-file doc pairs get a
kit-side sync check so a pair edit collision surfaces as a
deterministic failure instead of a silent revert. Proposes; the
maintainer disposes.

## 2026-08-23 dispatch-briefs-may-over-instruct

```yaml
date: 2026-08-23
harness: claude-code
agent: claude-fable-5
workstreams: [boardkit]
repo: boardkit (its own board, wave-2 Phase 2 user gate)
source: docs/board/cards/s43-phase2-residue-canary-fallback.md log; the Phase 2 Gate A round prompts (regenerable, packet directories)
```

At the Phase 2 U(code-review) gate Mike read the batch output and
flagged verbosity: the process may be over-instructing its agents.
The observable shape: Gate A dispatch prompts this wave ran about
sixty lines each, restating cycle state, materials, duties, and a
report contract, and executor briefs restated card content the card
already states. The cost signature is real - a full three-round cycle
ran 304k to 383k reviewer tokens per card, and every round's prompt
rebuilds context a pointer could carry. Candidate fix, to be tested
over the next runs rather than ruled now: briefs and review prompts
point at the card, the packet, and the canonical docs instead of
restating them, keeping only the report contract and the round's
delta inline; measure prompt size and reviewer spend against review
quality over a few cards before changing any template. Proposes; the
maintainer disposes.
