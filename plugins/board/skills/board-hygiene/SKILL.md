---
name: board-hygiene
description: |
  Use before ending any session that touched a card on a boardkit board,
  before a handoff, and after any card status change. Also use when the user
  says "board hygiene", "close out the board", "run the orientation canary",
  "check the board before we stop", or "is the board clean". Enforces the
  registry rules: card frontmatter is the source of truth, a log line lands
  in the same turn as the state change it records, generated views never
  drift, and the orientation canary clears before the session closes. Every
  path and command comes from `boardkit.toml` and the boardkit CLI, so this
  skill carries no repo-specific paths. Pair with `delegating-work` for the
  dispatches the checklist needs.
metadata:
  boardkit-contract: 2
---

# Board hygiene

The card registry that `boardkit.toml` names is the program's work state.
A wrong board is worse than no board, so this checklist runs before a
session ends, before a handoff, and after any card status change.

## Step one: run boardkit doctor

Before anything else in this skill, and before acting on anything the
board documents claim, resolve the invocation from the repo's agent
entry file first: bare `boardkit` is never on PATH, because the kit
runs from a local checkout. The checkout-based form is

```sh
uv run --project "${BOARDKIT_HOME:-../boardkit}" boardkit doctor
```

If the resolved invocation fails to run, **stop and tell the user the
board CLI is not reachable**. Do not fall back to a bare `boardkit`,
and do not work the checklist from the process docs alone. A
session that has read the rules but cannot run `boardkit check` or
`boardkit render` leaves a board that looks tended and is not, and the
next session cannot tell the difference. Doctor is the one diagnostic that
cannot report its own absence, so catching that absence is this step's
whole job.

When it does run, read what it says. Doctor names every check by a stable
id and exits 1 on any error, 0 on warnings alone. Errors such as
`roles.filled`, `views.current`, and `review-tooling.filled` block the
checklist below; warnings such as `skills.installed`, `worktrees.stray`,
and `env.boardkit-home` each map onto a step. Doctor also reports the
checks it skipped, because silence must not read as success. It never runs
a route's preflight commands for you; it prints them and you run them.

`boardkit check` and `boardkit doctor` answer different questions. Check is
board validity, and it is what a pre-commit hook runs. Doctor is
installation readiness. Both belong in a session close, and neither
substitutes for the other.

## Preconditions

Two conditions must hold or the rest of this skill does not apply. Missing
either one is a hard stop, not a thing to route around.

- **A resolvable board.** The CLI resolves one itself, in the order
  `${BOARDKIT_HOME:-../boardkit}/docs/DOCKING.md` specifies. Honor a
  board the user names, and let resolution run before concluding no
  board exists. Two of doctor's report lines confirm the target, and it
  takes both: the `boardkit doctor:` header names the `boardkit.toml`
  that answered, which is what identifies the board, and the
  `resolved via:` line names the step that chose it. Read the header
  before trusting that this is the board the session means to tend, and
  the step line when the answer is a surprise. Only when nothing
  answers, tell the user and offer `boardkit init`, which writes the
  config, the card directory, and the board documents, then prints the
  fill-in work still to do. A repo with cards but no entry files is a
  repair (point the manifest or a `--board` flag at it), not a silent
  init-over.
- **A compatible `boardkit --version`.** The board documents carry a
  contract stamp, the config declares the same version, and board-bound
  skills declare it in frontmatter metadata. Doctor compares all of them.
  An unknown version or a stamp mismatch means the kit and the repo have
  moved apart; report it and stop rather than guessing which side is
  right.

Boardkit runs from a local checkout, not a package index, so the repo's
agent entry file carries a bootstrap. Follow it exactly: export
`BOARDKIT_HOME` on its own line, before the `uv run` line. A same-line
assignment prefix expands the fallback default while the command is being
built, before the assignment lands, so the run targets the wrong checkout
and either fails oddly or succeeds against the wrong kit.

**Resuming a dead or interrupted session is a different procedure.** This
checklist tidies a session that ran; it does not recover one that did not
finish. Cold start belongs to the recovery protocol in the repo's process
document, which owns those steps. Three markers tell you that you are in
it. The repo's files are the state, not the chat transcript. Any active
card counts as suspect until someone re-runs its acceptance checks. And a
user gate the card log does not record as approved stays uncrossed. Run
that protocol first, then come back here.

## The hygiene checklist

Work these in order. Each one is a duty of the board owner, and none of
them is a later cleanup task.

1. **A log line for every state change, written in the same turn as the
   change.** This covers status changes, gate passes, deferrals, and
   takeovers. A status change without its log line is a hygiene defect the
   moment it happens. The card's gate-checklist box is ticked in the same
   turn its log records that gate as passed; an unticked box over a
   passing log line is drift in the other direction. A card worked in
   phases logs the phase-scoped pass and leaves the box unticked until the
   gate has covered the card's full scope.
2. **Status reflects reality.** A card is `done` only when its acceptance
   checks have passed and the log names who verified them and how. Never
   mark a card done on a subagent's claim alone: re-run at least one
   acceptance check yourself first. Blocked or partial work stays at
   `status: in-progress` with a log line naming the blocker. Choose
   accuracy over volume.
3. **The session respected the board mechanics its process document
   binds.** That document owns those rules, so check them there rather
   than from memory: the cap on how many cards may sit at
   `status: in-progress` at once and the terms of any side-quest
   exemption the user declared, the card-reference convention that a card
   id in prose carries a human-readable qualifier, and the rule that the
   checkout holding the board stays on its base branch. Each one is a
   defect at close, not a later cleanup.
4. **Read every card back after editing it.** After any multi-step edit
   sequence over a card, scripted edits, a stream editor, or a render
   pass, read the file back from disk before committing and before
   presenting any gate over it. An edit that reports success can still
   fail to persist, and when it does so silently the loss surfaces only
   after a gate was approved over stale text. The tick you show the user
   is the one you re-read, not the one you believe you wrote.
5. **Regenerate and validate the views.** Run `boardkit render`, then
   `boardkit check`. A check failure on a generated view means the card is
   wrong, not the view: fix the card frontmatter that produced it and
   regenerate. Views are never hand-edited. A drag-and-drop kanban tool
   editing a board view is the common source of this failure, and the fix
   is the same.
6. **New evidence is linked from the card that produced it.** Review
   output, canary records, benchmark results, and audit reports are
   findable from the card or they are lost.
7. **Every code card that reached review this session carries its commit
   range and its packet.** Set the card's commit-range frontmatter field,
   then generate the packet with `boardkit review-packet <id>`. For an
   external-repo card, pass `--repo <path>`, and for a card spanning more
   than one repo generate one packet per repo with `--suffix <name>` and
   that repo's own `--commit-range <a>..<b>`, so a second repo's diff
   never lands in a directory that reads as primary-repo content. A code
   card at `status: in-review` without a packet is not in review.
8. **Prose lint passes on every markdown file this session created or
   edited.** Use the linter the repo's own review-tooling document names
   in its tools fill-in. Do not assume a particular linter; the fill-in is
   what binds one.
9. **Reconcile the worktree map, where the repo keeps one.** If the
   session created, moved, or removed a worktree or branch, check the
   repo map in its process document against `git worktree list` on each
   listed repo. A worktree may sit on a per-card fan-out branch, which is
   fine; what must hold is that the primary branch the map names exists
   and tips at the commit the map documents. Then update both the table
   and the topology diagram beside it, or log the divergence on the card.
   Doctor's `worktrees.stray` warning catches job worktrees a delegation
   left behind; remove those with `git worktree remove` before close.
10. **Sweep the deferred gates.** Boardkit renders a deferred view
    whenever any gate is open-deferred; read it when it exists.
    Cross-check it with the canonical shape, a
    `Gate <X> open: deferred (<reason>)` bullet in a card's own log
    section:

    ```sh
    grep -rn 'open: deferred' <cards-dir>/*.md
    ```

    Open each hit and keep it only if that gate's checklist box is still
    unticked; a later tick means the deferral was resolved. Every
    surviving deferral is surfaced at the next user gate rather than
    quietly absorbed there.
11. **Run the documentation bus test when the wave touched
    documentation.** A wave that wrote or changed a README, process docs,
    templates, or onboarding files closes with this as a defined step,
    not an audit the user has to ask for. Where the `docs-bustest` skill
    is installed, load it by name. Where it is not, the repo's process
    document carries the method inline: the six scoring areas, the
    one-fact-one-place rule, and the P1/P2/P3 severities. Either way, P1
    findings are fixed or logged as explicit divergences on the board
    before the wave's user gate is presented, and the report is filed as
    evidence the board links.
12. **Run the orientation canary**, below. It is a hard stop.
13. **Commit the session's board and doc writes.** Once the canary
    clears, commit under the repo's commit standards: a conventional
    lowercase first line, a card trailer naming the card, and no AI
    attribution or sign-off trailers, because the human is the author.
    The board owner owns git. Board state is never left uncommitted
    across sessions.

## Orientation canary (hard stop)

Hygiene checks prove the board is consistent. The canary proves it is
legible to a session that was not here.

Dispatch a cheap model, ideally from a family or harness other than the
one the board owner ran in, so the proof covers cross-harness legibility
rather than the board owner's own reading. The board's contract binds a
route to this: resolve it rather than picking a model by hand. Give the
canary only the cold-start surface a fresh board owner reads: the
registry's `INDEX.md`, the board view, the deferred view where it exists,
and the process document's delegation and recovery sections. Add the cards
behind any open deferral, since the generated views carry no log detail.

Have it answer four questions:

1. Which cards are at `status: in-review`, and which are at
   `status: in-progress`, right now?
2. Which card is the next pull? If the ready column is non-empty, it is
   the top ready card. If ready is empty, name every backlog card whose
   dependencies are all done, and flag the empty ready column with
   eligible backlog cards behind it as a promotion gap to fix.
3. Which gates are open and deferred, and what does each one wait on?
4. Who is the board owner right now, and at which points must it stop for
   the user?

**Grade against a key, never against the canary's own confidence.** Compute
the key before dispatch:

```sh
uv run --project "${BOARDKIT_HOME:-../boardkit}" boardkit canary-key
```

That answers the first three questions deterministically from the cards,
reading frontmatter for the first two and the log entries plus
gate-checklist state for the third. The fourth question's key is static,
taken from the roles section of the repo's process document.

Two miss classes, two responses:

- **A board miss** is where the canary diverges from the key and the true
  answer is not objectively derivable from the surface it was given. That
  is a hard stop. The session does not close until whatever made the board
  ambiguous is fixed, in the frontmatter, the log, or the wording, and the
  views regenerate over the fix.
- **A model-weakness miss** is where the true answers are derivable and a
  second, slightly stronger cheap model orients correctly. The board is
  fine: swap the canary model and clear it rather than blocking. Re-run
  once first to rule out nondeterminism.

The hard stop is on board ambiguity, never on the frailty of one cheap
model.

File the computed key, the canary's verbatim answers, and the graded
verdict as an evidence record the board links, an evidence file or the
closing handoff. A canary that ran and left no key, no answers, and no
grade has not run for audit purposes, because the next session cannot tell
it from a skipped one.

**Degraded close, for an outage only.** When every route the board's
`canary` role declares is unreachable, the session may close degraded rather
than block. Compute the key with `boardkit canary-key` anyway and file it in
the close evidence. Log the canary as a deferred gate whose reason carries
the outage evidence: each route tried, and how it failed. The next session
start owes the canary and runs it before pulling new work. A degraded close
is an exception with a record, never a silent skip. Only an unreachable route
grounds one; a canary that ran and missed is graded by the two miss classes
above.

## Dispatching from this checklist

Several steps here need a dispatch. The canary is one. A deferred gate that
a later session resolves is another, as is the drift audit before a user
gate. Route each of them through `delegating-work`. That skill owns lane
selection: it resolves the role against the board's own delegation
contract, then loads only the child skill the resolution names.

Where `delegating-work` is not installed, do not improvise a lane. Read the
repo's own review-tooling document and its model-classes document instead.
The first pins the tools this repo uses and the invocation each one needs,
along with the transport rule. The second holds the capability taxonomy,
the reviewer pre-vet checklist, and the invariant that a reviewer's model
differs from every model that authored the work under review. Both live at
fixed board-document paths, and both override generic delegation guidance a
harness might load on its own.

## Feeding friction back

Friction with the process itself, a rule that fought the work, a gate that
misfired, a template claim that turned out wrong, is signal for the kit
rather than only for this repo. Record it as it happens in the repo's own
friction log, and append kit-relevant items to the boardkit checkout's
feedback inbox, which states its own entry format. Never edit the kit's
templates or code from a consumer repo.
