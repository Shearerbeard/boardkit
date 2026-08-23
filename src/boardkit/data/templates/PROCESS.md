# Process

<!-- boardkit-contract: v2 -->

This file states how work on this board is tracked, delegated, verified, and
recovered. It is stable: it changes only when the rules change, not when the
work changes. The work itself lives in the card registry (see `boardkit.toml`
for its path), never here.

Model-class delegation policy (who runs what, and the harness bindings for
this repo) lives in `MODEL-CLASSES.md` and `REVIEW-TOOLING.md`, not here.
Read both before dispatching a card.

## Card schema

The card registry is one markdown file per card, with YAML frontmatter.
Generated views sit alongside it: `INDEX.md` and `board.md` always, plus
`deferred.md` whenever any gate is open-deferred; `boardkit
render` writes them and `boardkit check` validates them against the cards
and fails on drift. Never hand-edit a generated view. If a view looks wrong,
fix the card frontmatter that produced it and regenerate.

Frontmatter fields, all required except the last two: `commit-range`, which
is added at the moment the card enters `in-review`, and `side-quest`, which
is absent unless the user has declared the flow a detached side quest (see
their entries below):

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
  branch-per-card workflows. One of `primary`, `accepted-head`,
  `isolated-branch`, or `none`; `none` means the card is not tied to a
  branch lineage in this repo.
- `executor`: `smart` or `any`. See `MODEL-CLASSES.md` for what each class
  may own.
- `gates`: a human-readable string naming the gate order for this card, for
  example `S -> A`.
- `user-gates`: a list of named user stops on this card, like
  `[mockup, launch]`. Empty when the card needs no user gate.
- `commit-range`: the card's commit shas, set by the board owner once the
  card enters `in-review`. Absent before then. Feeds `boardkit
  review-packet`.
- `side-quest`: `true` or `false`, defaulting to `false` when absent. Marks
  a card as part of a flow the user has declared a detached side quest, so
  it does not count against the WIP limit. See the WIP-limit bullet under
  "Board mechanics" for when this may be set.
- `lane`: optional; the lane this card belongs to, from the board-declared
  vocabulary (`[[board.lanes]]` in `boardkit.toml`). A board that declares
  no lanes accepts no `lane` keys. Lanes are how one board carries more
  than one family of work legibly: the generated views group by lane, and
  a lane may carry its own WIP cap or a board-wide WIP exemption in config
  rather than in process prose.
- `refs`: optional; qualified cross-board references, `<code>/<id>` (as in
  `tb/S91`), resolved against the family registry. Informational only:
  the scheduler never blocks on another board's state, so a ref never
  affects readiness. Bare ids stay valid inside a single board; a
  cross-board mention without a short-code qualifier is not resolvable.
- `kind`: optional; `card` (the default) or `epic`. An epic is itself a
  card that names an initiative: it holds the goal prose and may carry
  gates like any card. It may not be a member of another epic.
- `epic`: optional; the id of the same-board epic card this card serves.
  Membership is grouping, not dependency: it feeds the per-epic rollup in
  the views, the epic clusters in the graph, and `boardkit dag --to
  <epic>`, and it never blocks scheduling on its own.

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
  review packet is generated with `boardkit review-packet <id>`. An
  external-repo code card (`lineage: none`) records its external commit shas
  in the card log as work lands, then copies the logged range into
  `commit-range` when it enters this status, so
  `boardkit review-packet <id> --repo <path>` can generate the packet its
  gates present. A card whose work spans more than one repo gets one packet
  per repo, each output directory named for the repo it covers: pass
  `--suffix <name>` alongside `--repo <path>` and the packet lands in
  `reviews/<id>-<name>`, so a diff from a second repo never sits in a
  directory that reads as primary-repo content. `commit-range` names shas
  in the primary repo, which a second repo has never seen, so the packet
  for that repo also takes `--commit-range <a>..<b>` with its own shas.
- `done`: every gate on the card has passed, and the log records who
  verified the acceptance criteria and how.

## Board charter

A board may declare a `[charter]` block in `boardkit.toml`: `owns` (the
one-liner mirrored into the board's registry row), `not` (what this board
refuses), and `[charter.route]` mapping registry short-codes to the work
that belongs there. The admission test is one question: where does the
diff land. The charter renders at the top of the generated views and rides
every dispatch brief; enforcement is prose-level, and `boardkit check`
validates only that route targets resolve to registry short-codes and that
the registry mirror matches.

One board per family is the bright line: initiatives group inside a board
with epics and lanes. Only a different source-of-truth repo or a different
lifecycle owner justifies a new board, because cross-board references are
informational by design - split coupled initiatives across two boards and
their edges silently drop out of the schedulable DAG.

## Board mechanics

- WIP limit: at most two cards `in-progress` at once. A lane declared
  `exempt = true` in `boardkit.toml` keeps its cards out of this count
  (the config home for a spike-lane exemption); a lane with its own
  `wip = <n>` caps that lane's in-progress cards separately, and the
  lane cap counts every card in the lane, exemptions included. This forces the board
  owner to finish or hand off before starting more work than one session
  can track. One exemption: a flow the user explicitly declares a detached
  side quest does not count against the limit. Such a flow must not
  interrupt the mainline and shares only test resources with it,
  coordinated at its own launch gates. The exemption is recorded on the
  flow's own cards as `side-quest: true` in frontmatter, so a fresh session
  can see why the count looks high, and `boardkit check` counts those cards
  out of the limit. The board owner sets the flag only on the user's
  explicit declaration, never on its own judgment that work is a side
  quest. The flag exempts a card from the count and from nothing else: two
  cards that list each other in `serialize-with` still may not both be
  `in-progress`, side quest or not.
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
- Card-reference prose convention: a card id in prose (card logs, evidence
  files, process docs) carries a short human-readable qualifier alongside
  the id: S12 (retry-budget accounting), S31 (packet naming for multi-repo
  cards). A bare id is acceptable only in frontmatter
  `depends` lists and in inline code, where the qualifier would be
  redundant. Prose that names ids without qualifiers costs every later
  reader a lookup.
- The checkout that holds the board stays on its base branch. A card that
  touches code takes its own worktree; parking the board's checkout on a
  card branch strands the board state a fresh session reads.
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

A brief names the role it dispatches and the pin source where that role's
live model pins are read. It never names a model id. Models resolve from
harness configuration at dispatch time, so an id written into a brief is a
copy that starts going stale immediately, and a stale one can invert the
reviewer-differs-from-author invariant by naming the very model that
authored the diff. Where the record needs to say which model ran, that
fact lands after the run, in the cost ledger.

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

Per-gate checklists restate their deterministic steps in full - the skill
loads, the commands, the order - rather than pointing at a statement made
earlier in the plan or the session. A load-this-first imperative stated
once in planning prose has decayed by the time the gate arrives; the
checklist that repeats it at the gate is the one that fires.

- Gate S, self: run the deterministic checks the card names (lint,
  typecheck, test, `boardkit check`, or whatever the card's own tooling
  provides). Fix failures before proceeding. When a card's gate checklist
  says acceptance output is reported verbatim, paste the full command
  output, not a summary. Gate S also carries the doc-sync duty: the card's
  report names which living documents its diff affects, or states none
  (the duty itself is described under Gate D below).
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
  from the record itself. A check the reviewer cannot execute, or one
  that fails for reasons peculiar to the reviewer's sandbox (a denied
  command, a missing tool, no network), is reported as unverified, never
  as a finding against the diff: the board owner runs the check itself
  or routes it to Gate S, and the review record says which checks the
  reviewer actually ran. Never
  read an empty or failed reviewer return as a pass: a review with no
  verdict has not run. Zero findings is recorded as an explicit PASS, not
  silence. Two cases defer: self-review (the same model authored and would
  review), and a reviewer that pre-vet finds unreachable, unvetted, or
  under-permissioned (see `MODEL-CLASSES.md`). Fix-commit re-review duty:
  when Gate A findings are fixed in a new commit, the card's `commit-range`
  extends to include the fix commit, the review packet regenerates over the
  full range, and a fresh Gate A review covers the fix commit. Marking a
  card done without this leaves the fix commit unreviewed. An external-repo
  card (`lineage: none`) carries the same duty: the fix commit extends the
  logged sha range and the card's `commit-range`, and the packet regenerates
  over the full range with `--repo <path>` for a fresh Gate A. Convergence
  rule: each re-review round verifies the prior round's dispositions with
  evidence, re-raises findings whose fixes failed, and re-raises any
  regression the fix introduced in the reviewed diff. It does not expand
  scope past ground already accepted. Round bound: after two fix rounds,
  the board owner writes a ruling that names the next action: continue,
  card, or escalate. The ruling may not pass Gate A while unresolved
  in-scope findings remain; failed fixes and fix-introduced regressions
  stay in cycle or escalate, never carded as new scope. A FAIL whose
  findings are all new scope - none re-raise a prior round's failed fix,
  and none are regressions the fix introduced - triggers the user
  escalation, taking the disagreement to the user with it recorded on the
  ledger, never a silent stop or an unbounded loop. The dispatch brief for
  a re-review round carries this discipline into the reviewer prompt. The
  ledger records per-round finding counts, cumulative reviewer spend, and
  per-finding disposition verification evidence as required fields, so the
  cycle's shape is auditable from the record.
- Gate M, manual: the agent exercises the behavior end to end and reports
  what happened.
- Gate D, drift audit: before any user gate opens, a fresh lower-cost agent
  checks the living documents' claims (and any code anchors they cite)
  against the current state of the repo and the board, and reports drift.
  Findings are fixed, or logged as explicit divergences on the board, before
  the user gate is presented.

  Gate D's inputs are the repo's living contract documents, and two duties
  keep them audit-ready. A repo that keeps living contracts (design docs, type
  plans, PROCESS.md, the card registry) stamps each with the commit its code
  anchors were last verified against; re-verifying bumps the stamp. And every
  implementation card's dispatch brief and report names which living documents
  its diff affects, or states none: when the behavior a living document
  describes changes, the same card updates the document and its anchor, or the
  board owner logs the divergence explicitly on the card before it can reach
  done.
- Gate F, frontier review: before a wave-level user gate (one that accepts
  work spanning more than one card), an adversarial review by a frontier
  model over the accumulated diff. It is expensive and never auto-fires:
  the board owner proposes it, and the user pre-approves it or skips it by
  judgment. A skip is logged on the card with its reason. A user gate that
  decides a single card is local and does not trigger Gate F unless that
  card is itself the milestone.
- Gate U, user: stop. Present diffs, findings, and risks. Do not proceed
  without explicit user approval.
- Gate T, user testing: stop. The user exercises the behavior by hand;
  the board owner's deliverable is the handout that makes that possible:
  the exact run commands, a reference prompt or script, the expected
  observations in order (observable behaviors, never "verify it works"),
  the failure signatures, and the revert steps. The user's observations
  are recorded as evidence, pass or fail. A test the user cannot run
  from the handout alone is a failed handout, not a failed test, and it
  reopens the gate.

### Deferrals

When a gate must defer, the board owner logs it
open with a `Gate <X> open: deferred (<reason>)` log line and leaves its
checklist box unticked, then continues with other eligible cards. The line
is a bullet in the card's own `Log` section, and it states the deferral
plainly rather than quoting it in inline code: that is the only shape
`boardkit` reads as a deferral, so prose elsewhere on the card may discuss
the convention without recording one.

The log line records the deferral; the checklist tick is what clears it.
`boardkit` holds a deferred gate open until the gate's checklist box is
ticked, so a later `Gate <X> passed` log line on its own does not close
the deferral, and `boardkit check` warns when it finds that shape: a pass
logged after a deferral with the box still unticked. Tick the box in the
same turn the log records the resolving pass, per the board mechanics
above. Log a pass with the verdict directly after the gate name -
`Gate A passed` or `Gate A PASS` - since that is the shape the warning
reads; a wording that puts other words between the gate and its verdict
is not legible to it. A
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

Code-review packets go to the user. Every code card (any `lineage`,
including external-repo code cards) carries a U(code-review) gate after its
Gate A and before its launch leg or done, at which the board owner presents
the review packet generated by `boardkit review-packet` and stops. A card
spanning more than one repo presents one packet per repo, generated with
`--repo <path> --suffix <name> --commit-range <a>..<b>` into
`reviews/<id>-<name>`, since the card's `commit-range` frontmatter holds
primary-repo shas that do not resolve in the second repo. When
pulling a code card that lacks the gate, or on encountering any already-active
(`in-progress` or `in-review`) code card without it, the board owner inserts
the gate into the card's frontmatter and checklist and logs the insertion.

## Type discipline

This board does not describe a type-design discipline in detail. Domain
type design, the compile-clean skeleton step, and the adversarial
design-review panel between skeleton and fill ship as the `typed-holes`
skill, which installs for both Claude Code and agent-skills harnesses. Load
it by name when a card's deliverable is new domain types. Where the skill
is not installed, a card whose deliverable is new domain types carries the
type-discipline rules directly in its dispatch brief. In short: design the
domain types first, so invalid states are unrepresentable and constructors
return errors rather than trusting input; land the type skeleton with
unimplemented bodies as its own compile-clean commit; run an adversarial
design review of the types between the skeleton and the first filled-in
body.

## Commit standards

- Conventional-style first line: `<type>(<optional scope>): <description>`,
  entirely lowercase, under 72 characters, with no trailing punctuation. The
  body explains what changed and why. A repo that runs commitlint takes its
  own config as the authority over this wording.
- Card trailer: every commit carrying a card's work ends with a
  `Card: <ID>` trailer on a line of its own. This is what makes a card's
  commit range recoverable later. When a card reaches `in-review` without
  `commit-range` set, `boardkit review-packet` tells the board owner to
  find the range with
  `git log --oneline --grep '^Card: <ID>$' <primary-branch>`, and that
  search only finds anything because every card commit carries the trailer.
  A repo that skips the trailer has to reconstruct ranges by hand.
- No AI attribution and no sign-off: never add a `Co-Authored-By` trailer
  for an AI assistant, and no `Signed-off-by` trailers. The human is the
  author of every commit. These rules override any default footer a harness
  adds on its own.
- Prose lint: every checked-in markdown file passes the repo's prose linter
  before it is committed. A lint suppression or exemption carries its
  recorded reason where it lands: a comment beside the config line, or the
  body of the commit that adds it.

## Session close

Before a session ends, the board owner runs board hygiene: every card the
session touched has a dated log line for each state change, statuses reflect
reality, the views regenerate and `boardkit check` passes, new evidence is
linked from the card that produced it, every code card that entered
`in-review` has its `commit-range` set and its packet generated, and prose
lint passes on every markdown file the session created or edited. Then the
board owner commits the session's board and doc writes under the commit
standards above. Board state is never left uncommitted across sessions.

Read a card back after editing it. After any multi-step edit sequence over
a card - scripted edits, `sed`, a render pass - read the card file back
from disk before committing and before presenting any gate over it. An
edit that reports success can still fail to persist. The failure is
silent: nothing surfaces until a gate has been approved over stale state
and the board needs rebuilding from git history. The tick
you are about to show the user is the one you re-read, not the one you
believe you wrote.

### Wave close: documentation bus test

A wave that wrote or changed documentation (a README, process docs,
templates, onboarding files) closes with a documentation bus test, as a
defined step, not an ad-hoc audit the user has to ask for. The test asks
whether two cold readers could pick the repo up if the maintainer
disappeared: a human contributor who knows the domain but not this project,
and a fresh agent session with zero prior context.

The method, where the `docs-bustest` skill is installed, is that skill;
load it by name. Where it is not, apply the same method directly:

- Score the entry docs pass/fail across six areas: orient (one-line
  purpose, quick start, structure, architecture), operate (setup, build
  and test commands, config surface, deploy path where one applies),
  decide (decision log, constraints, changelog), contribute (workflow,
  tests, CI, quality commands), agent discoverability (agent entry file
  present and current, handoff docs not stale, one canonical roadmap,
  links resolve, no facts restated across audience files), and content
  quality (no stale claims, no undefined jargon, dated).
- One fact, one place: when a human doc and an agent doc need the same
  fact, the public doc states it and the agent doc references it.
  Duplicated facts drift apart; a fact stated in two places with two
  values is a blocking finding.
- Report findings by severity: P1 (docs contradict code, a required step
  is missing, or one fact carries two values), P2 (info exists but is
  hard to find, outdated, or scattered), P3 (polish).

P1 findings are fixed, or logged as explicit divergences on the board,
before the wave's user gate is presented. The report is filed as evidence
the board links, like any other gate output.

### Orientation canary (hard stop)

Once the hygiene checks pass, prove the board is legible to a session that
was not here. Dispatch a cheap model, ideally from a family or harness other
than the one the board owner ran in, so the proof covers cross-harness
legibility and not just the board owner's own reading. Give it only the
cold-start surface a fresh board owner reads: the registry's `INDEX.md`,
this file's recovery protocol and roles sections, `board.md`, and
`deferred.md` with the cards it names. Include `deferred.md` in the brief
unconditionally. When the view is absent, the brief says so and states
that absence reads as "no deferred gates" - then the canary answers the
deferral question outright instead of abstaining. The generated views
carry no log detail.

Have it answer four questions:

1. Which cards are `in-review`, and which are `in-progress`, right now?
2. Which card is the next pull? If `ready` is non-empty, it is the top
   `ready` card. If `ready` is empty, name every `backlog` card whose
   dependencies are all `done`, and flag an empty `ready` column that has
   eligible `backlog` cards behind it as a promotion gap to fix.
3. Which gates are open and deferred (a `Gate <X> open: deferred (<reason>)`
   log line whose checklist box is still unticked), and what does each one
   wait on?
4. Who is the board owner right now, and at which points must it stop for
   the user?

Grade against a key, never against the canary's own confidence. Compute the
key before dispatch: `boardkit canary-key` answers the first three questions
deterministically from the cards, reading frontmatter for the first two and
the Log entries and gate-checklist state for the deferred gates in the
third. The fourth question's key is static, taken from the Roles section
above.

The canary is evidence, not just a ritual: file the computed key, the
canary's verbatim answers, and the graded verdict as an evidence record the
board links (an evidence file, or the closing handoff). A canary that ran
but left no key, answers, or grade on record has not run for audit
purposes; the next session cannot distinguish it from a skipped one.

Two miss classes, two responses. A board miss, where the canary diverges
from the key and the true answer is not objectively derivable from the
surface it was given, is a hard stop. The session does not close until
whatever made the board ambiguous is fixed, in the frontmatter, the log, or
the wording, and the views regenerate over the fix.
A model-weakness miss, where the true answers are derivable and a second,
slightly stronger cheap model orients correctly, means the board is fine;
swap the canary model and clear it rather than blocking. Re-run once to rule
out nondeterminism. The hard stop is on board ambiguity, never on the
frailty of one cheap model.

## Process feedback

Friction with the board process itself, a rule that fought the work, a gate
that misfired, a template claim that turned out wrong, is signal for the
kit, not just for this repo. Record it as it happens in this repo's own
friction log (a retro scratchpad or the closing handoff), and route the
kit-relevant items to the boardkit checkout's `FEEDBACK.md` inbox
(`${BOARDKIT_HOME:-../boardkit}/FEEDBACK.md`), which states its own entry
format. Append an entry there; never edit the kit's templates or code from
a consumer repo. A maintainer session drains the inbox into the kit's
plans.

## Recovery protocol

A fresh session recovers board state from the cards and this file, never
from chat memory:

1. Read this file.
2. Read the registry's `INDEX.md`. The registry is the state; do not
   reconstruct it from chat history or git log first.
3. Take the delegation inventory, before promoting a card or planning a
   wave. It opens with a question to the session driver - which providers
   are in play for this run - because that constraint is a session fact no
   config file records; the answer filters every pin read that follows and
   lands in the session log, never in a card or brief. Then read the
   harness's own agent configuration and record which
   executors and reviewers exist, what model each is pinned to, and whether
   the ones this session will depend on are reachable. `MODEL-CLASSES.md`
   carries the capability taxonomy and the pre-vet checklist;
   `REVIEW-TOOLING.md` carries the review procedure and the harness
   transports. The pins constrain what can be planned: the
   reviewer-differs-from-author invariant decides which executor may author
   which card and which reviewer can close its gate, so a wave allocated
   before the pins are known can hand work to an author no available
   reviewer is allowed to review.
4. Treat any card `in-progress` as suspect: re-run its acceptance checks and
   inspect the repo's status before trusting its log.
5. Guard against unlogged work: before dispatching a card, check whether its
   scope already contains partial work. If it does, treat that card as
   `in-progress` and verify it per step 4.
6. Continue with the highest-priority `ready` card, or finish verifying the
   suspect card first.
7. Never cross a user gate that the card log does not show as approved.

All recovery-critical state lives in the repo's files: the cards, this
document, and git state. Nothing recovery-critical lives only in chat
history or a scratch file.
