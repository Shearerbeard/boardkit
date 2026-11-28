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
  duties around a dispatch; each transport skill explains its invocation.
  Pair with `board-hygiene` at session close.
metadata:
  boardkit-contract: 2
license: MIT
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

- **A resolvable board with a delegation contract.** Without one there
  are no roles, no routes, and no pin sources, so there is nothing to
  resolve. The CLI resolves the board itself, in the order
  `${BOARDKIT_HOME:-../boardkit}/docs/DOCKING.md` specifies, so honor a
  user-named board and let resolution run before concluding the repo
  has none. Before dispatching against it, read both of doctor's
  identifying lines: the `boardkit doctor:` header names the
  `boardkit.toml` that answered, so it is what says which board a
  dispatch will land on, and the `resolved via:` line names the step
  that chose it. Remedy when it truly has none: `boardkit init`
  scaffolds the config and the board documents, then prints the
  fill-in work that remains.
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

Before allocating cards, inventory the available models and providers with
the operator. Use the reviewer pre-vet in `MODEL-CLASSES.md` and record
the agreed roles in the DAG. Resolve the actual route and model again
at dispatch.

For OpenCode, pass the dispatch directory explicitly in API queries and verify the returned
location before comparing effective agents/skills with approved sources.
Record source hashes in the run receipt. Local definitions can override a
global installation; an unqualified API request uses the server default location.

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
staging: working-dir (stage the packet into the transport's working directory and name the staged paths; reads outside the working directory are refused)
preflight: opencode --version
fallback: codex-cli
```

The `staging` line is the transport's read contract, and the dispatch
honors it before anything else: `working-dir` stages the packet into the
transport's working directory and names the staged paths; `repo-native`
runs with cwd at the repo under review and names repo-native paths. The
two contracts are opposites and both fail as silence when crossed, which
is why the resolution prints the rule with the route.

Add `--json` for the same content as a parseable object. A transport that
loads no child skill says so explicitly, as
`skill: none (this transport loads no child skill)`, and an absent
preflight or fallback prints `none` rather than being omitted, so a
missing line always means a missing value rather than an oversight.

Then, in order:

1. Resolve the role; an invalid review configuration goes to the operator.
2. Use the selected transport and load its named child skill, if any.
3. Read the live pin at its declared source and run the printed preflight.

## The roles

Six roles, and the board's config binds a route to each. These are the
vocabulary of a dispatch; no model name belongs here or in any brief.

- **executor**: authors one card's work in its own worktree and reports back.
  Follows repo commit rules. Board writes stay with the coordinator.
- **code-review**: reviews a code diff at Gate A, in the harness where the
  diff was written where possible.
- **prose-review**: reviews a non-code artifact when its agreed task gates
  require it.
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

## Choosing the reviewer

Use the agreed DAG and the eligibility rules in `MODEL-CLASSES.md`. Code
review checks behavior and scope. For a prose review, name the audience
and the argument or wording to assess. An editorial assignment returns
revised text; the technical owner decides changes to the underlying claims.

## The metered lane and its preflight

For a metered transport, obtain session spend approval and follow the
preflight in the selected transport skill before its first dispatch.

**The adapter must report ready before dispatch.** Funding or configuration
failures require an operator ruling under PROCESS.md. Other preflight
failures use the declared approved route or defer; they do not authorize
an unapproved model switch.

An approval carried over from an earlier session does not count. Neither
does an inference from the user asking for a review.

## Execution worktree

Give each writer its assigned worktree; reuse it for review at the exact
candidate revision. If the transport creates worktrees itself, record
the actual location. The coordinator tracks them through integration and
cleanup under the board's `PROCESS.md`.

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
  in, each with its adapter, child skill, pin source, staging contract,
  preflight, and fallbacks. A role that cannot resolve prints in place as unresolved
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

Give the worker the complete brief, inline or at a readable path named in
the kickoff. Add the assignment scope and expected return if the card does
not supply them. The owner resolves the route; the worker receives the
card and the assignment.

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
- `codex-cli` drives the codex CLI for a second-model read, with no
  per-session spend approval in its way. Where it is not installed, the
  review-tooling document carries the sandboxed invocation and the
  caller-owned deadline.

In every degrade case the rule is the same: read the repo's own
review-tooling and model-classes documents rather than improvising, and
say in the card log which document you routed from.

## Returning a review

Use `REVIEW-TOOLING.md` for the packet location and transport controls.
Return findings and the explicit verdict to the coordinator. The review-slot
and delivery rules in `PROCESS.md` govern repairs, verification and escalation.
