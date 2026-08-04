---
name: delegating-work
description: |
  Use when dispatching any board work to another model: "delegate this
  card", "get a second-model review", "who reviews this", "run Gate A",
  "dispatch an executor", "send this to a reviewer", "which tool should
  review this plan". The router for a boardkit board. It resolves the role
  to a transport with `boardkit resolve-route`, picks exactly one lane,
  loads only the child skill that resolution names, and generates the brief
  with `boardkit dispatch-brief`. It owns lane selection and the process
  duties around a dispatch; how each transport is driven stays in the child
  skills `opencode-cli`, `collaborating-with-antigravity`, and `codex-cli`.
  Pair with `board-hygiene` at session close.
metadata:
  boardkit-contract: 2
---

# Delegating work

This is the router for a board that declares a delegation contract in
`boardkit.toml`. It decides which lane a piece of work takes and what the
board owes around that dispatch. It does not drive any transport: the
mechanics of each one live in its own child skill, and this file names
which child to load rather than repeating what the child says.

For board work it supersedes the older per-tool snapshots that each
described their own routing. Those snapshots are now transport children
with no say over lane selection.

## Fail closed before the first dispatch

Two things must be present. If either is missing, stop and say so rather
than dispatching on a guess.

- **`boardkit.toml` with a delegation contract.** Without it there are no
  roles, no routes, and no pin sources, so there is nothing to resolve.
  Remedy: `boardkit init` scaffolds the config and the board documents,
  then prints the fill-in work that remains.
- **A filled-in review-tooling document.** The repo's review-tooling file
  is a per-project fill-in, and boardkit ships it with two sections
  deliberately empty. A copy whose tools section or harness-bindings
  section is still byte-identical to the shipped template is unfilled, and
  a route resolved against it points at nothing. Remedy: fill those
  sections, then re-run doctor.

Both conditions are checks doctor already knows how to report, as
`config.present`, `review-tooling.filled`, `review-tooling.placeholders`,
`roles.filled`, and `routes.pin-source`. So on the first dispatch of a
session, if nothing has run it yet:

```sh
boardkit doctor
```

If that command is not found, stop and tell the user the board CLI is not
installed; never route from the documents alone. On a board session
`board-hygiene` has already run this as its first step, and one run per
session is enough.

## Take the delegation inventory at session start

Resolution answers which transport serves a role. It does not answer
whether that transport can be reached today, and it runs at dispatch time,
which is too late to shape a wave. Take the inventory before planning a
wave or promoting a card, not at the gate the reviewer serves.

Read the harness's own agent configuration and record which executors and
reviewers exist and what model each is pinned to. Then, for every external
reviewer the plan will lean on, run the pre-vet checklist the repo's
model-classes document defines:

- **Reachability and auth**: the binary, server, or API answers right now,
  rather than merely being configured.
- **Usage headroom**: budget or quota is left for this review. An
  exhausted cap found mid-gate is worse than one found before dispatch.
- **Permission profile**: the reviewer can read the material it is being
  asked to review. A reviewer whose allowlist blocks the diff it was sent
  is a recorded failure, not a hypothetical one.
- **Model identity**: the configured model is what the agent or persona
  name implies. Names drift out of sync with the pin underneath them, so
  check the harness's agent-definition file rather than the label.

The pins constrain the plan. Under the reviewer-differs-from-author
invariant, they settle which executor may author a given card and which
reviewer may close its gate. So a wave allocated before the pins are known
can hand work to an author that no available reviewer is allowed to
review, and that surfaces only once the work is already written by the
wrong hand. An unvetted, quota-exhausted, or under-permissioned reviewer
counts as unreachable, and its gate defers.

Dispatch-time resolution complements this inventory; it does not replace
it.

## Route mechanically, not by reading prose

The prose tables in the repo's review-tooling and model-classes documents
are for humans and for doctor. Never route by interpreting them at
dispatch time: that is four hops across three documents, and every hop is
a place to guess wrong.

Resolve the role instead, with a single command:

```sh
boardkit resolve-route <role>
```

The output is flat `key: value` lines, one line per value:

```
role: code-review
route: opencode-reviewer (1 of 2)
adapter: opencode
skill: opencode-cli
pin source: docs/board/REVIEW-TOOLING.md#harness-bindings
preflight: opencode --version
fallback: codex-cli
```

Add `--json` for the same content as a parseable object. A transport that
loads no child skill says so explicitly, as
`skill: none (this transport loads no child skill)`, and an absent
preflight or fallback prints `none` rather than being omitted, so a
missing line always means a missing value rather than an oversight.

Then, in order:

1. **Resolve first.** Resolution is lazy and fails closed: it validates
   only the role you asked for, so one half-written binding elsewhere on
   the board cannot block this dispatch, and it refuses rather than
   dispatching to a route that still carries template placeholders or a
   pin source that points nowhere. A refusal is a real answer; take the
   declared fallback or defer the gate.
2. **Select exactly one transport.** The route line names it. Do not
   fan out across transports because two look plausible.
3. **Load only the child skill the resolution names.** Not all three, not
   the one you used last time.
4. **Read the pin at dispatch time from the resolution's pin source.**
   That field is a pointer to where live model pins are recorded, never a
   pin itself. Model ids go stale, and a stale id copied into a brief can
   invert the reviewer-differs-from-author invariant by naming the very
   model that authored the diff. Never write a model id into a card, a
   brief, or this kind of doc; the cost ledger records which model
   actually ran, after the fact.
5. **Run the preflight commands the resolution printed.** Boardkit prints
   them and never runs them, because a diagnostic that shells out to repo
   config is a code-execution surface. Running them is the caller's job.

## The roles

Six roles, and the board's config binds a route to each. These are the
vocabulary of a dispatch; no model name belongs here or in any brief.

- **executor**: authors one card's work and reports back. Makes no board
  writes and runs no git operations.
- **code-review**: reviews a code diff at Gate A, in the harness where the
  diff was written where possible.
- **prose-review**: reviews a language-shaped artifact at Gate A, a plan,
  spec, architecture note, product or marketing text. See the roster
  below.
- **frontier-review**: the wave-scope adversarial review at Gate F, over
  an accumulated diff, before a wave-level user gate.
- **drift-audit**: the Gate D pass that checks living documents' claims and
  code anchors against the current repo and board state. It runs on a
  lower-cost model inside the board owner's own harness and loads no
  review skill, so there is no reason for it to spend smart-class or
  frontier-class budget.
- **canary**: the cheap cross-family orientation check `board-hygiene`
  runs before a session closes.

Gate A is an honest limit in the contract. A card records the gates it
must pass but not whether it produced code or prose, so a generated brief
prints both Gate A routes and quotes the repo's own rule for choosing
between them. The board owner picks; the brief does not guess.

## The language-shaped-review lane is a role with a roster

Prose review is a role with a named default and named alternates, not a
hardcoded tool. Whatever the board's own `roles.prose-review` routes list
declares is the roster. Its first entry is the primary; the rest are the
fallback chain, in declared order. That ordering is itself contract, which
is why reordering it moves the contract digest.

The customary shipping arrangement, for a repo that has not decided
otherwise: the Antigravity transport is the primary, driven by the child
skill `collaborating-with-antigravity`, because that lane handles human
language more naturally than the families tuned for diffs, and these
artifacts are judged on exactly that. Behind it come the frontier
alternates the repo's harness-bindings table records, the codex transport
among them. That is a customary chain and nothing more: where the repo's
own `roles.prose-review` declaration differs from this paragraph, the
declaration wins, and no model name belongs in either.

A session whose primary is unapproved or unreachable takes the next route
in the chain instead of stalling, and logs the switch on the card. Four
ordinary reasons a primary is unavailable: the session lacks the spend
approval a metered transport needs; a probe reports the transport
unhealthy; quota is exhausted; or the primary's family authored the
artifact under review, so the reviewer-differs-from-author invariant closes
that route. Walk the chain. Only once it is exhausted does the gate defer.

The same shape governs every role. Prose review gets its own section
because it is the lane most often written down as a tool name.

## The metered lane and its preflight

Some transports are metered and gated. When a resolution's route points at
the Antigravity transport, its skill line names
`collaborating-with-antigravity`, and that child owns the ordered
preflight, both steps before the session's **first** dispatch and in this
order:

1. An explicit per-session spend approval, recorded in the session.
2. The `agy_doctor` probe, run before the first dispatch rather than after
   a failure. Its report names the agy version, the auth state, whether
   the fallback CLI is present, and the session-store path.

Load the child and follow its steps. It owns running the probe and reading
the report; they are not repeated here.

What this router states is the interface. **The adapter must report ready
before the first dispatch. Otherwise take the declared fallback route, or
defer.** A probe reporting auth trouble, an exhausted quota, or missing
config means the reviewer is unreachable under the pre-vet rule. The
dispatch does not happen. Instead the gate it would have served stays open
as a deferral, for the next user gate to surface.

An approval carried over from an earlier session does not count. Neither
does an inference from the user asking for a review.

## Execute-mode dispatch leaves a worktree behind

Where a route dispatches execute-mode work rather than a review, isolation
is opt-in and cleanup is manual.

- Keep the transport's worktree default **off** unless a run actually
  needs isolation, and turn it on per call when it does. A machine-wide
  default-on leaves a branch and a directory behind after every execute
  run, wanted or not.
- Nothing auto-cleans a job worktree. Remove strays with
  `git worktree remove` before the session ends.
- Session close accounts for every worktree a delegation created: list
  them, then remove the ones nothing still needs. Doctor's
  `worktrees.stray` warning surfaces the leftovers it knows the shape of,
  which complements this duty rather than replacing it.
- Work that only reads asks for no write mode and no worktree at all.

The recorded failure behind these rules is a retry loop that burned a
weekly budget and returned no verdict, leaving a dozen registered worktrees
behind it.

## Briefs come from the generator

Never hand-assemble a dispatch brief and never paste policy text into one.
Restated policy goes stale silently. Generate it:

```sh
boardkit dispatch-brief <card-id>
```

The brief is deterministic and carries no timestamp, so two runs over an
unchanged board produce identical bytes and a brief can be diffed. Its
schema:

- **Header**: the card id and path, the contract version, the contract
  digest, and the source files the brief was built from.
- **The card, verbatim**, in a fenced block. It is the specification, and
  nothing below it overrides it.
- **Reference material** as repo-relative paths, the card's own links
  resolved. The brief prints paths rather than summaries of what is at
  them, so the executor reads the source.
- **Routes**: the executor plus every role the card's declared gates pull
  in, each with its adapter, child skill, pin source, preflight, and
  fallbacks. A role that cannot resolve prints in place as unresolved
  rather than aborting the brief, because a broken reviewer binding is
  exactly what the board owner should see.
- **Contract clauses**, quoted out of the repo's own process and
  model-classes documents: the dispatch-brief paragraph, the
  decision-authority paragraph, and the bullet for each gate the card
  declares. A missing anchor is a loud failure, not a quietly shorter
  brief.
- **Provenance footer**: regenerate rather than edit, plus the digest.

**Staleness rule**: a brief whose digest differs from the digest doctor
prints was built against a contract that has since moved. Regenerate it.
Editing a brief forks the contract into a copy that nothing re-checks.

For an executor that loads no skills, the generated brief is its entire
context. Send it whole. Add only what the card cannot know, such as the
scope rule for this dispatch and the expected report shape, and never
trim the clauses out to save room.

## The router picks the lane; the children drive

Each child skill declares the artifact class it serves and hands work
outside that class back here. Naming a destination is not the same as
picking the lane, and picking the lane is this skill's job alone. A child
never routes around a resolution.

- `opencode-cli` drives OpenCode from an external harness for code writing
  and second-model code review. Where it is not installed, take the
  invocation, the model-selection rule, the staging recipe, and the
  subagent-flag caveat from the repo's review-tooling document, which
  pins them for this repo.
- `collaborating-with-antigravity` drives the Antigravity CLI for
  language-shaped review, and owns the spend-approval and probe preflight
  above. Where it is not installed, the gate does not simply proceed: the
  repo's review-tooling document carries the raw invocation and the budget
  gate, and both still apply. Without a way to run the probe, treat the
  transport as unvetted and take the fallback route.
- `codex-cli` drives the codex CLI for a second-model read, with no
  per-session spend approval in its way. Where it is not installed, the
  review-tooling document carries the sandboxed invocation and the
  caller-owned deadline.

In every degrade case the rule is the same: read the repo's own
review-tooling and model-classes documents rather than improvising, and
say in the card log which document you routed from.

## Validity floor for any delegated review

These bind every review dispatch, whatever the transport.

- **Every final artifact gets one adversarial review before its user
  gate**, by a model from a family other than its author's. A plan, a
  card, an evidence write-up, and a decision record all count, not code
  alone. There is no artifact class that reaches a user gate unreviewed.
- **The reviewer starts with fresh context.** No implementation context
  from the authoring session comes along: a reviewer that already holds
  the author's reasoning is checking its own work with extra steps.
- **An empty return is a failed delegation, never a pass.** So is a
  zero-exit run with no final text, and so is any run without an explicit
  verdict. A review with no verdict has not run.
- **Zero findings is recorded as an explicit pass**, so it stays
  distinguishable from a tool that silently returned nothing.
- **Findings are numbered and each carries its own disposition**, the fix
  applied or the reason it was rejected, recorded to the card's log or its
  review directory. For a standalone prose artifact that is not a card,
  append that ledger to the artifact itself so the record travels with it.
- **The reviewer's model differs from every model that authored the work
  under review.** For a multi-commit range that means every commit in the
  range, and a range whose authorship cannot be established defers rather
  than being reviewed blind. The ledger names the authoring model and the
  reviewing model so the invariant is checkable from the record.
- **A review is never nested inside another delegation.** The board owner
  dispatches every gate review directly, or the gate defers.
- **Cap repeated attempts on one unit of work at three.** Past three the
  approach changes rather than the attempt count: stage the packet, switch
  transports, or defer. Wrap every delegated invocation in a deadline,
  since agent CLIs commonly ship without a timeout flag, and treat the
  wrapper's exit as the delegation's outcome. On a stall, switch tools;
  the same prompt through the same stalled tool usually stalls again.
- **Deferral semantics come from the repo's process document.** Log the
  gate open with the deferral shape that document defines, leave its
  checklist box unticked, continue with other eligible work, and surface
  the deferral at the next user gate. Resolving it later means running it
  properly, with a pre-vetted, reachable reviewer that satisfies the
  invariant above.
- **Permission failures produce a staged packet, not a transport switch.**
  Where a reviewer cannot read the path under review, stage the card,
  spec, diff, and prompt into a review directory inside the working
  directory and name the staged paths. Point reviewers at a packet from
  `boardkit review-packet <id>` rather than assuming they can run a diff
  themselves.

## Budget etiquette

Use the cheapest class that can do the job correctly, and escalate only on
failure rather than by default. The ladder has rungs: a search task a
small explorer-class model failed goes to a smart-class model next, not
straight to frontier on the first miss. Frontier-class calls stay reserved
for board ownership and for the wave-scope Gate F review, where the
reviewer-differs-from-author invariant requires that class.

A metered language-review transport stays reserved for language-shaped
judgment: never a deterministic shell proxy for something a shell command
answers exactly, and never a workaround for another reviewer's permission
failure.
