# Process

This file states how work on this board is tracked, delegated, verified, and
recovered. It is stable: it changes only when the rules change, not when the
work changes. The work itself lives in the card registry (see `boardkit.toml`
for its path), never here.

Model-class delegation policy (who runs what, and the harness bindings for
this repo) lives in `MODEL-CLASSES.md` and `REVIEW-TOOLING.md`, not here.
Read both before dispatching a card.

## Card schema

The card registry is one markdown file per card, with YAML frontmatter. Two
generated views sit alongside it, `INDEX.md` and `board.md`; `boardkit
render` writes them and `boardkit check` validates them against the cards
and fails on drift. Never hand-edit a generated view. If a view looks wrong,
fix the card frontmatter that produced it and regenerate.

Frontmatter fields, all required except `commit-range`, which is added at
the moment the card enters `in-review` (see its entry below):

- `id`: the card's identifier, matching the id scheme in `boardkit.toml`.
- `title`: a short imperative title.
- `status`: one of the five statuses below.
- `depends`: card ids that must be `done` before this card can become
  `ready`. This is the full ordering DAG, not just the immediate
  prerequisite.
- `serialize-with`: card ids that share files or resources with this one.
  Two serialized cards may not both be `in-progress` at once, and the
  relationship must be reciprocated on the other card.
- `lineage`: where this card's work branches from, for repos that use
  branch-per-card workflows. A value of `none` means the card is not tied to
  a branch lineage.
- `executor`: `smart` or `any`. See `MODEL-CLASSES.md` for what each class
  may own.
- `gates`: a human-readable string naming the gate order for this card, for
  example `S -> A`.
- `user-gates`: a list of named user stops on this card, like
  `[mockup, launch]`. Empty when the card needs no user gate.
- `commit-range`: the card's commit shas, set by the board owner once the
  card enters `in-review`. Absent before then. Feeds `boardkit
  review-packet`.

Filename rule: `<id-lowercase>-<slug>.md`, with a unique lowercase slug per
card.

Statuses and their lifecycle:

- `backlog`: not yet eligible. Waiting on a dependency, or not yet
  prioritized.
- `ready`: every card in `depends` is `done`; the card is eligible for
  dispatch.
- `in-progress`: an executor is actively working the card. At most two
  cards may hold this status at once (the WIP limit).
- `in-review`: the work is complete and awaiting gate review. A card with a
  branch lineage enters this status only once `commit-range` is set and its
  review packet is generated with `boardkit review-packet <id>`.
- `done`: every gate on the card has passed, and the log records who
  verified the acceptance criteria and how.

## Board mechanics

- WIP limit: at most two cards `in-progress` at once. This forces the board
  owner to finish or hand off before starting more work than one session
  can track.
- Update the card's log in the same turn as the status change it records.
  A status change without a matching log line the same turn is a hygiene
  defect, not a later cleanup task.
- A card's gate-checklist box is ticked in the same turn its log records
  that gate as passed. An unchecked box sitting over a passing log line is
  drift, exactly like an unlogged status change. A card worked in phases
  logs interim, phase-scoped gate passes as log lines only; the checklist
  box stays unticked until the gate has passed over the card's full scope.
- A card is `done` only when its acceptance checks have passed and the log
  names who verified them and how. The board owner never marks a card done
  on a subagent's claim alone: it re-runs at least one acceptance check
  itself before the status changes.
- Choose accuracy over verbosity. A card that says less but is correct beats
  one that says more but drifted from reality. A wrong board is worse than
  no board.
- Generated views are never hand-edited. `boardkit check` catches drift
  between the cards and the views, including drift introduced by a
  drag-and-drop kanban tool; treat any such failure as a signal to fix the
  card frontmatter, then regenerate with `boardkit render`.

## Roles

- Board owner: the session the user has put in charge of the board, in any
  harness. There is no role question to ask: a session the user tells to
  run the board is the board owner from that moment. Exactly
  one session owns the board at a time. It sequences work, promotes
  dependency-eligible cards, runs every gate, performs the board's git
  operations, and is the only session that talks to the user at a gate. It
  dispatches its own executors and reviewers.
- Planner: a session that vets, specs, and delegates a wave of cards before
  another session runs them. Planning confers no standing authority. Once
  the user hands the board to another session, that session is the board
  owner, and the planner holds no live role until the user re-engages it.
- Executor: a subagent the board owner dispatches to work one card. An
  executor makes no board writes and runs no git operations; it reports
  back to the board owner, which is the only role that commits, updates
  card status, or regenerates views. An executor may itself dispatch worker
  subagents at most one nesting level below it; those workers delegate to
  no one further.
- Reviewer: a fresh-context agent the board owner dispatches for a gate. A
  reviewer is never nested inside another delegation: the board owner
  dispatches every gate review directly, or the gate defers rather than
  being routed through an executor. The reviewer's model must differ from
  every model that authored the diff under review (the
  reviewer-differs-from-author invariant, see Gate A below and
  `MODEL-CLASSES.md`).

A dispatch brief for a subagent contains the full card text, paths to any
required reference material (not summaries of it), the scope rule ("only
modify what the card names; if the task needs anything else, stop and
report instead"), and the expected report format: what changed as
file:line, acceptance-check output verbatim, open questions, and anything
discovered but not fixed.

Decision authority stays with the board owner. When a card allows an
either-or outcome, the subagent reports the evidence and stops; the board
owner decides and writes the log entry.

Executor-fallback rule: a delegation tool can fail to deliver. After three
failed delegation attempts on one unit of work, the board owner has two
options: author the unit directly and log the takeover on the card, or
name a second executor and redispatch. A card that needs a different
threshold sets and logs its own. The board still owns git, gates, and board writes; only the
authoring hand changes, and the switch is always logged, never silent. This
rule covers authoring executors only. It does not excuse a Gate A reviewer
from the reviewer-differs-from-author invariant: if the board owner's
takeover means it authored the diff and its harness holds no other model
family, that card's Gate A stays open rather than self-reviewing.

## Gates

- Gate S, self: run the deterministic checks the card names (lint,
  typecheck, test, `boardkit check`, or whatever the card's own tooling
  provides). Fix failures before proceeding. When a card's gate checklist
  says acceptance output is reported verbatim, paste the full command
  output, not a summary.
- Gate A, agent: a fresh subagent with no implementation context reviews the
  diff against the card's acceptance criteria and either finds issues or
  signs off explicitly. The reviewer's model must differ from every model
  that authored the diff (the reviewer-differs-from-author invariant); for a
  multi-commit range, the reviewer must differ from every model that wrote
  any commit in it, and a range whose authorship cannot be established
  defers rather than being reviewed blind. Findings are numbered, each with
  its resolution, recorded to the card's log or review directory so the
  record is auditable finding-by-finding, not as an aggregate count. The
  ledger also names the model that authored the diff and the model that
  reviewed it, so the reviewer-differs-from-author invariant is checkable
  from the record itself. Never
  read an empty or failed reviewer return as a pass: a review with no
  verdict has not run. Zero findings is recorded as an explicit PASS, not
  silence. Two cases defer: self-review (the same model authored and would
  review), and a reviewer that pre-vet finds unreachable, unvetted, or
  under-permissioned (see `MODEL-CLASSES.md`). Fix-commit re-review duty:
  when Gate A findings are fixed in a new commit, the card's `commit-range`
  extends to include the fix commit, the review packet regenerates over the
  full range, and a fresh Gate A review covers the fix commit. Marking a
  card done without this leaves the fix commit unreviewed.
- Gate M, manual: the agent exercises the behavior end to end and reports
  what happened.
- Gate D, drift audit: before any user gate opens, a fresh lower-cost agent
  checks the living documents' claims (and any code anchors they cite)
  against the current state of the repo and the board, and reports drift.
  Findings are fixed, or logged as explicit divergences on the board, before
  the user gate is presented.
- Gate F, frontier review: before a wave-level user gate (one that accepts
  work spanning more than one card), an adversarial review by a frontier
  model over the accumulated diff. It is expensive and never auto-fires:
  the board owner proposes it, and the user pre-approves it or skips it by
  judgment. A skip is logged on the card with its reason. A user gate that
  decides a single card is local and does not trigger Gate F unless that
  card is itself the milestone.
- Gate U, user: stop. Present diffs, findings, and risks. Do not proceed
  without explicit user approval.

### Deferrals

When a gate must defer, the board owner logs it
open with a `Gate <X> open: deferred (<reason>)` log line and leaves its
checklist box unticked, then continues with other eligible cards. A
deferred gate stays open on the card until a later session resolves it, and
the next user gate surfaces it rather than silently absorbing it. Resolving
a deferred gate means running it properly: the resolving session's reviewer
must be pre-vetted, reachable, and must satisfy the
reviewer-differs-from-author invariant, or the gate stays open.

Standing user gates apply independent of any single card. Architecture and
type-design decisions need user approval before implementation cards that
build on them start. Acceptance decisions, a baseline, a launch, a
milestone, belong to the user alone. A repo may add its own standing user
gates; record them here or in a repo-specific addendum.

## Type discipline

This board does not describe a type-design discipline in detail. Domain
type design, the compile-clean skeleton step, and the adversarial
design-review panel between skeleton and fill ship as the `typed-holes`
skill. Load that skill when a card's deliverable is new domain types.

## Recovery protocol

A fresh session recovers board state from the cards and this file, never
from chat memory:

1. Read this file.
2. Read the registry's `INDEX.md`. The registry is the state; do not
   reconstruct it from chat history or git log first.
3. Treat any card `in-progress` as suspect: re-run its acceptance checks and
   inspect the repo's status before trusting its log.
4. Guard against unlogged work: before dispatching a card, check whether its
   scope already contains partial work. If it does, treat that card as
   `in-progress` and verify it per step 3.
5. Continue with the highest-priority `ready` card, or finish verifying the
   suspect card first.
6. Never cross a user gate that the card log does not show as approved.
