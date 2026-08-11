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

## 2026-08-09 info-exclude-invisible-consumers

```yaml
date: 2026-08-09
harness: claude-code
agent: claude-fable-5
workstreams: [boardkit]
repo: aura-orchestration-mode + ~/workspace/aura (mezmo/aura clones)
source: claude-skills feedback/2026-08-09-claude-code-info-exclude-invisible-consumers/process-feedback.md
```

Session C initially committed the manifest plus a .gitignore line to both
mezmo/aura clones; Mike caught it before any push - that repo is work OSS
and the personal workflow must leave zero traces in its history, ruling
out even the .gitignore edit. The landed fix: manifests untracked,
`.boardkit/` ignored per-clone via `.git/info/exclude`; worktree
resolution re-verified unaffected (the common-dir fallback stats the
filesystem, never git). Proposal: R5' docs name three consumer postures -
committed, gitignored, and invisible (info/exclude, for repos that must
not know boardkit exists) - plus the scale-up note that a second adopter
promotes invisible to a tracked .gitignore line as a deliberate step.
Proposes; the maintainer disposes.

## 2026-08-09 commit-range-excludes-first-commit

```yaml
date: 2026-08-09
harness: kimi-code
agent: kimi-k3
workstreams: [boardkit]
repo: aura-sandbox
source: docs/board/cards/sb8-serve-fault.md (log, 2026-08-09 in-review entry)
```

Setting `commit-range` for card SB8 as `1a18aa2..0611563` (first..last
of the card's commits, the natural reading of "A..B shas of the card's
commits") produced a review packet covering only the config-flip
commit: `git` range semantics exclude A, so the implementation commit
never reached the reviewer. Caught by inspecting the generated
packet's commit count before Gate A dispatch; corrected to
`192cbed..0611563`. Nothing in the card template or the review-packet
output warns when a `Card: <ID>`-trailer commit sits just outside the
range. Candidate kit fix: `boardkit review-packet` could cross-check
`git log --grep '^Card: <ID>$'` against the range and warn on card
commits it excludes, or the template could state the A-is-exclusive
convention outright.

## 2026-08-11 dotname-docking-generalization

```yaml
date: 2026-08-11
harness: claude-code
agent: claude-fable-5
workstreams: [boardkit, wiki-system, typed-holes]
repo: aura-orchestration-mode
source: claude-skills feedback/2026-08-11-claude-code-dotname-docking-generalization/process-feedback.md
```

Direction from Mike after the board-consolidation close: move the wiki
and rust-holes to the `.<name>` docking structure `.boardkit/` proved
out. What generalizes: resolution is computed, not stored; consumer
posture is per-repo (committed / gitignored / invisible via
info/exclude); the resolution order (flag, env, walk-up, common-dir
fallback, legacy) is kit-agnostic. Candidates: a wiki docking dir
replacing the CLAUDE.local.md symlink + render-script reach (same
stored-link fragility the board symlinks had), and a rust-holes docking
dir for the hole ledger. Proposal: extract the resolver into a documented
docking convention or small shared library the sibling kits vendor - one
spec, not three divergent walk-ups. A planned notanton bootstrap will
cold-test the setup recipe against whatever shape this takes. Proposes;
the maintainer disposes.

## 2026-08-11 wip-limit-config-in-code

```yaml
date: 2026-08-11
harness: claude-code
agent: claude-fable-5
workstreams: [boardkit]
repo: boardkit (found at Mike's S13/S24 U(code-review))
source: docs/board/cards/s13-board-discovery.md 2026-08-11 Gate U log entry
```

Review finding from Mike at the S13/S24 code review: board.py carries
`WIP_LIMIT = 2` as a code constant citing PROCESS.md prose - config
living in code. R1 gave per-lane `wip` a boardkit.toml home; the global
cap never migrated. Proposal: a `[board] wip` key defaulting to 2, with
the constant retired. The adjacent `X | None` optionality in config.py
was reviewed and judged correct (file-may-omit semantics R4 requires).
Proposes; the maintainer disposes.
