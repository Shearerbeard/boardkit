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

## 2026-08-12 consumer-seam-and-canary-patterns

```yaml
date: 2026-08-12
harness: opencode
agent: opencode-go/deepseek-v4-pro
workstreams: [boardkit, aura]
repo: mezmo/aura (board-consistency program, reports/board-consistency-program-2026-08-12.md)
source: reports/canary-consistency-evidence-2026-08-12.md
```

Four findings from the board-consistency program (a P19 epic-repair and
before/after orientation-canary run across the aura board family):

1. **Consumer seam for non-opencode harnesses.** opencode gets a full
   machine-local board bootstrap via AGENTS.md (`.git/info/exclude`);
   the tracked repo stays clean ("no process-tooling traces in tracked
   files"). Claude Code's local channel was the wiki render's
   permanent `Memory:` index line pointing at a
   never-created `memory/MEMORY.md`. Creating that file activated a
   persistent above-the-fold seam with zero renderer changes. Parallel
   thought for S12 (public-repo seam): the kit's entry-file templates
   could ship a per-harness machine-local pointer pattern (a permanent
   index line to a curated consumer file) rather than expecting
   tracked-file edits.
2. **Entity-name collisions escape the qualify-ids rule.** Three
   "agent-driver" entities (library / prototype spike / epic) live on
   three boards; only canary probes caught the conflation. Card-id
   collisions are linted; entity-name collisions are not. Candidate
   check, adjacent to S13 board-discovery / S21 cross-board-refs.
3. **Before/after canary pattern.** The orientation canary grades a
   single key; measuring surface improvements over edits needed:
   per-question grading atoms (surface-support x code-truth), surface
   manifests pinned by commit shas, sealed-key immutability with dated
   pre-run amendments, defect-probe questions (either canary outcome
   evidences the defect), and an "inventing an answer when none is
   derivable = miss" rule that classed a real model-weakness incident.
   Offered as a reusable extension for the canary section of the kit's
   PROCESS.md templates.
4. **Next-id allocation raced the host repo's card minting.** Doctor's
   `host.tree-state` warning was present, but the next free id was
   still taken by garden-minted commits not yet pulled (P20 collision).
   A doctor check or documented gotcha for consumers whose host repo
   has an autonomous minting process would have caught it.

Proposes; the maintainer disposes.

## 2026-08-13 review-artifact-locations

```yaml
date: 2026-08-13
harness: claude-code
agent: claude-opus-5
workstreams: [boardkit]
repo: aura-orchestration-mode (aura#496 fill wave, cards P16-P18)
source: claude-skills feedback/2026-08-13-claude-code-review-artifact-locations/process-feedback.md
```

Mike's finding at the wave's code-review gate: he does not know where the
review artifacts live canonically, and the diffs plus the guided read order
are not in one place he can go back through. He asked for the locations
twice. This wave's material landed in four directories: generated per-card
packets in the board's gitignored `reviews/P16|P17|P18`, four hand-built
wave-level files in `reviews/496-fill-wave/`, reviewer verbatims in
`evidence/`, and staged prompts plus the original GitHub drafts in the
worktree's `.review-staging/`. The hand-written consolidated packet shows the
gap from the inside: it points at "the board's reviews dir" and a handout
"filed alongside this packet" without paths, and its one real path names a
stale copy. Seams: `render_review()` already writes a header carrying Card,
Repo, and Range, and it holds the output directory and the diffed repo
(including a `--repo` worktree override) at that point; `cmd_review_packet`
prints those paths to a stdout the reviewer never sees; the template
PROCESS.md names `reviews/<id>-<name>` in passing and nowhere states where
review artifacts live. Four more findings from the same wave. (1) Wave-level
artifacts have no generator: `review-packet` is per-card, so the consolidated
packet, findings ledger, Gate T handout, and guided review are hand-built
every wave and their shape drifts. (2) A rebase onto a new base rewrote every
sha and three cards' `commit-range` was hand-patched; a range whose shas
survive as unreferenced objects still produces a packet over abandoned
history, silently. The trailer search the missing-range error already
recommends would support a cross-check. (3) The standing rule that every code
card carries a `U(code-review)` gate is enforced by editing frontmatter,
checklist, and log on each card at pull time; boardkit's own board shows seven
cards carrying the same hand-insertion. `cmd_check` already accumulates
findings of this class. (4) `boardkit check --config <board>/boardkit.toml`
fails from `~/dev/boardkit` with `[charter.route]: 'adr' is not a registry
short-code (known: aura, bk)` and passes from the aura repo: `--config` wins
for the config load, but `charter_route_errors`, `board_row_errors`, and
`card_ref_findings` each resolve the registry from `Path.cwd()`. Nothing in
`--help` says so. Overlaps are cross-referenced in the source record rather
than restated here. The gitignored packet-retention half belongs to the
2026-08-09 review-artifact-audit-trail entry and drain 7's decision 3. The
range-field fragility is adjacent to the 2026-08-09
commit-range-excludes-first-commit entry. The ranked read order is S15 and the
dangling-reference half is S8. Proposes; the maintainer disposes.

## 2026-08-16 packet-carries-no-review-scope-guide

```yaml
date: 2026-08-16
harness: opencode
agent: kimi-for-coding/k3
workstreams: [boardkit]
repo: chore-lottery
source: docs/board/reviews/S8/REVIEW.md plus the hand-written REVIEW-GUIDE.md companion
```

At S8's U(code-review) the user opened the generated packet and asked
where "the auto 80/20 guide" was: they could not tell what the scope of
their review was. The packet (REVIEW.md plus per-commit diffs) is
complete as evidence but carries no orientation: what to read closely,
what the gates already covered, what is skim-safe. The board owner
hand-wrote a REVIEW-GUIDE.md companion (the risky 20%, the skim-safe
rest, the parked decisions) to unblock the review. Adjacent to the
existing entry's "guided review is hand-built every wave" finding, but
this one is per-card and user-facing: the reader at a U gate is the
user, not an agent, and the packet is their only map. A generated
"review focus" section (risky files from the diff stats, gate coverage
from the card, open questions from the log) would remove the
hand-writing. Proposes; the maintainer disposes.

## 2026-08-16 parallel-same-crate-fills-see-each-others-mid-flight-state

```yaml
date: 2026-08-16
harness: opencode
agent: kimi-for-coding/k3
workstreams: [boardkit]
repo: chore-lottery
source: docs/board/retro/2026-08-16-s8-implementation-close.md
```

Five rust-write fills dispatched in parallel against disjoint files of
one new crate each reported the siblings' half-written files as compile
errors and lint failures, and their reports cross-described transient
states that no longer existed at collection time. Every fill landed
clean in the end; the cost was report noise and one wasted round of
"is my file the broken one" per executor. The briefs scoped cargo test
with name filters, which helped, but cargo still compiles the whole
crate. Candidate directions: a dispatch-brief note that parallel fills
in one crate should expect cross-file interference and report it as
such, or a sequencing rule (skeleton-critical files first, leaf fills
parallel). Proposes; the maintainer disposes.

## 2026-08-16 review-cycle-had-no-termination-rule

```yaml
date: 2026-08-16
harness: claude-code
agent: claude-fable-5
workstreams: [boardkit]
repo: boardkit (its own board, the R-wave Gate A)
source: docs/board/evidence/2026-08-16-gate-a-review-cycle.md
```

The batched Gate A over ten cards ran, then its fix commits were
re-reviewed four more times. Rounds 1 and 2 found real defects in the
cards' diffs. From round 3 on, every finding was in one text heuristic
inside a fix commit, and each round returned exactly one new evasion
narrower than the last. A bare mention of the target file counted as
proof; the next round got past that with a directive wearing heading
syntax; the round after that used prose trailing a mid-line comment
close. All of them were real and all were fixed, with nothing in the kit
saying when to stop. The
board owner ended it by writing a ruling and carding the residue as S29.
The three-attempt cap in REVIEW-TOOLING governs dispatch attempts against
a stalled transport, not iteration depth against a reviewer that is
working correctly. S14 owns the convergence rule and now has a worked
example to build from; two shapes the session would have used: stop when
a round's findings no longer touch the reviewed diff, and stop when
round N+1's findings are strictly narrower instances of round N's class.
Proposes; the maintainer disposes.

## 2026-08-16 deferral-reason-cannot-be-superseded

```yaml
date: 2026-08-16
harness: claude-code
agent: claude-fable-5
workstreams: [boardkit]
repo: boardkit (its own board, closing the R-wave)
source: docs/board/cards/deferred.md and src/boardkit/board.py deferred_gates
```

A gate can stay open for a new reason after its original deferral
condition is met, and the card log has no way to say so. `deferred_gates`
collapses repeat deferrals by reason and treats a new reason as a new
entry, so logging the current reason rendered two rows per card in
`deferred.md` - one of them a condition that had already been satisfied.
Only ticking the box clears the old row, and ticking asserts a pass the
reviewer never gave. The board owner annotated the ten resolved markers
in place (`Gate A open: deferred (` became `Gate A deferred, superseded
<date>:`), which keeps the historical text and date while removing the
shape boardkit reads as live. That worked, but it is an invented
convention: the kit has no supersession vocabulary, and a false row in the
deferred view is exactly the ambiguity the orientation canary is supposed
to catch. Candidate fixes: a `resolved`/`superseded` marker the parser
understands, or letting the newest deferral for a gate win with the older
ones kept as history. Proposes; the maintainer disposes.

## 2026-08-16 canary-role-has-no-fallback-route

```yaml
date: 2026-08-16
harness: claude-code
agent: claude-fable-5
workstreams: [boardkit]
repo: boardkit (its own board, session close)
source: boardkit.toml [roles.canary] and docs/board/evidence/2026-08-16-gate-a-review-cycle.md
```

`board-hygiene` calls the orientation canary a hard stop before session
close, and the scaffolded contract binds `roles.canary` to a single route
with no fallback. When that transport went down - four failed read probes
across three models, while `opencode models` still answered - the canary
could not run, and the only contract-conformant move was to defer a step
the hygiene skill calls a hard stop. `code-review` survived the same
outage because it declares a fallback. Two candidates, not exclusive:
scaffold `roles.canary` with the same fallback shape the review roles get,
and have `board-hygiene` say what a session close looks like when the
canary transport is unreachable, so the answer is not improvised at the
one moment the board is about to be left alone. Related: a board owner
must not substitute a transport the contract does not name, so the gap
cannot be closed session-side. Proposes; the maintainer disposes.

## 2026-08-16 review-packet-range-and-verdict-reading-hazards

```yaml
date: 2026-08-16
harness: claude-code
agent: claude-fable-5
workstreams: [boardkit]
repo: boardkit (its own board, the R-wave Gate A)
source: docs/board/evidence/2026-08-16-gate-a-review-cycle.md
```

Three smaller frictions from the same wave. First, `review-packet
--commit-range` rejects anything that is not two hex shas, so the natural
`<sha>^..<sha>` for a single fix commit fails and the caller has to
pre-resolve the parent with `git rev-parse`; git revision expressions
would cost nothing to accept. Second, the fix-commit re-review duty says
the card's `commit-range` extends to include the fix commit, but a fix
commit separated from the reviewed range by other cards' commits cannot be
expressed as `A..B` at all; this wave reviewed each fix through its own
`--suffix` packet instead, which works and is undocumented. Third, a
reviewer that reads other cards' review outputs quotes their verdict lines
into its own transcript, so the obvious `grep 'VERDICT:' <output> |
tail -1` reports a verdict belonging to a different review - it misread one
FAIL as this review's own mid-session. A packet-side verdict field, or a
documented rule to read the reviewer's own final message, would remove the
trap. Proposes; the maintainer disposes.
