---
source: chore-lottery@0b0330e87bf8aca2e059c633665d17603a6be13a:docs/board/REVIEW-TOOLING.md
date: 2026-08-09
artifact: doc-draft
note: board review-tooling doc, frozen as cleanup-task input
---

# Review and delegation tooling for this repo

<!-- boardkit-contract: v2 -->

This file is a per-project fill-in, not a generic doc. It pins the actual
tools and harness bindings this repo uses for review and delegation, so a
board owner does not have to rediscover tool mechanics every session. Cards
cite this file instead of repeating it.

A repo's `REVIEW-TOOLING.md` overrides any generic delegation-skill guidance
a harness might load by default. If a skill's default instructions conflict
with what is pinned here, this file wins.

## The standing rule

Every final artifact (a plan, a card, an evidence write-up, an architecture
decision) gets one adversarial review by a model from a different family
than its author, before it reaches a user gate. For code, that is the Gate
A review defined in `PROCESS.md` and `MODEL-CLASSES.md`. Run it in the
board owner's own harness when a reviewer there satisfies the
reviewer-differs-from-author invariant, and reach outside that harness
when none does: the invariant decides, convenience does not. A harness
whose only reviewers share the author's family cannot close its own
Gate A. For prose and design artifacts,
pick a reviewer from a different family than the author using the
harness-bindings table below.

An adversarial review of a standalone prose artifact that is not a card (a
plan, an ADR, a design doc) appends a numbered findings ledger to the
artifact itself, so the record travels with it. The ledger carries an
explicit verdict and names both the author model and the reviewer model.
Each finding records its disposition: the fix applied, or the reason the
finding was rejected. An empty or verdict-less return is a failed review,
never a clean pass. Zero findings is recorded as an explicit PASS,
distinguishable from a tool that silently returned nothing.

## Harness bindings

One row per board-owner harness. Model pins are read at dispatch time from
the pin sources named in `boardkit.toml`; this table names roles and agent
handles, never model ids.

| Board owner (harness) | Executor pool | Gate A reviewer | Gate F route | Defers |
| --- | --- | --- | --- | --- |
| OpenCode | pinned subagents via the in-session task tool: `rust-write`, `rust-write-fast`, `python-write`, `general`, `explore` | code diffs: the pinned `rust-reviewer` or `python-reviewer`; prose and process docs: the `general` agent, provided its current pin differs in family from the author | the codex route below; the agy route as the budget-gated fallback | nothing |
| Claude Code | Claude subagents (`general`, `Explore`) | a non-Claude reviewer through the codex route, or the OpenCode reviewer agents driven through the opencode CLI from outside | the codex route; the agy route as the budget-gated fallback | nothing |

## Tools, in order of preference

1. In-harness OpenCode subagent dispatch (the task tool): executors, Gate A
   reviewers, drift audits, and orientation canaries. The board owner
   dispatches its own pinned agents and never invokes the opencode CLI from
   inside a session. Subagent definitions live at
   `~/.config/opencode/agent/*.md` (user scope) and `.opencode/agent/*.md`
   (project scope); the primary agents (`general`, `explore`, `build`,
   `plan`) are defined and pinned in the `agent` block of
   `~/.config/opencode/opencode.json`. Read the pins at dispatch time:
   agent names do not imply model families.

   Executor allocation (the routing table adopted from the bootstrap
   retro, proposal 1):

   | Work | Agent |
   | --- | --- |
   | Rust implementation | `rust-write` |
   | Mechanical single-file Rust fills | `rust-write-fast` |
   | Python machinery | `python-write` |
   | Gate A on Rust or Python diffs | `rust-reviewer` / `python-reviewer` |
   | Gate A on prose, plans, process docs | `general`, when its pin differs in family from the author |
   | Gate D drift audits, orientation canaries | `explore` or `general` |

   Brief sizing (bootstrap retro, proposal 3): `rust-write` gets
   single-file fill briefs until evidence says otherwise. A multi-file or
   new-module brief goes to the board owner's own class or is split into
   single-file units. Watch `rust-write-fast`'s first briefs before
   trusting it with larger ones.

   Reviewer permission constraint: the pinned code reviewers run with a
   bash allowlist that denies `git show` and `git diff` over commits, so a
   reviewer pointed at raw git history grades its own sandbox as a
   blocker. Point reviewers at a pre-generated packet from `boardkit
   review-packet S5`, or stage the material into `.review/` inside the
   working directory. A reviewer brief must instruct the reviewer to
   report checks it cannot run, never to grade an unrunnable check as a
   finding.

2. codex CLI (`codex exec`): the post-stall fallback for prose and process
   review, and the first Gate F route. Driven per the `codex-cli` skill:
   stage the packet into `.review/` inside the working directory (codex
   trusts only git repos and can hang silently on unstaged paths), wrap
   every invocation in a caller-owned deadline of `timeout 900`, and run
   the contract-shaped read probe from the Reviewer pre-vet section
   (a staged-file nonce readback, never a bare echo) before a gate
   depends on the route.

3. agy MCP (`agy_start` plus `agy_status` / `agy_result` polling):
   language-class review when the user wants a second frontier read.
   Budget-gated: no agy spend without explicit user approval in the
   current session. Prefer the detached job form over a
   work-inside-the-call path for anything long.

The split, explicitly: in-harness OpenCode agents (tool 1) take card and
gate reviews. The codex route (tool 2) is where ad-hoc adversarial review
and the post-stall fallback go. Frontier language review uses the agy route (tool 3) only
after the user approves the spend. A bare request for
a second-model review resolves to tool 1 when a different-family reviewer
exists in-harness; otherwise it resolves to tool 2.

Hard routing exclusions: agy is never a deterministic shell proxy and
never a workaround for another reviewer's permission failure. The pinned
code reviewers never review prose or process docs. No reviewer whose pin
shares the author's model family closes that author's gate.

## Transport rule

This rule covers an EXTERNAL harness reaching into a different agent
harness. Prefer CLI invocations over MCP transports for that:
`opencode run` or `codex exec` rather than an MCP
tool call into the same harness. The principle behind the preference is
recoverability. Prefer a transport that returns a job handle immediately
and runs the work behind that handle, because the caller can then poll it,
bound it with a deadline, and reconnect after a client-side failure. A
transport that completes the work inside the tool call leaves the caller
nothing to hold. With no deadline the wait is unbounded, and a client that
gives up has no way back to work the server has not finished. Judge a
transport on that property rather than on which protocol it speaks. Use CLI invocations as the default; treat a
work-inside-the-call path to another harness as a fallback that needs its
own contract-shaped read probe (see Reviewer pre-vet) before a wave
depends on it. If this repo has no
such transport installed, delete the preceding sentence when filling
this file in, so a filled-in copy never advertises a path nothing here
can take.

The rule does not apply within a harness. A board owner running natively
inside a harness dispatches that harness's own pinned reviewer and
executor agents through its in-session subagent dispatch, and never
invokes its own harness's CLI from inside a session: the nested server
breaks per-session cost capture and the "a review is never launched from
inside another delegation" invariant. When a subagent cannot read a path
the review needs - several harnesses reject reads outside the working
directory - stage the packet (card, spec, diff, prompt) into a `.review/`
directory inside the working directory and name those staged paths.
Falling back to a CLI self-invocation is not the remedy. Read the agent
config for the current model pins before routing either way; agent names
do not imply model families.

A metered language-review harness is reserved for language-shaped review:
judgment about a plan, a diff, or prose. It is never a deterministic shell
proxy - anything a shell command answers exactly, run in a shell - and
never a workaround for another reviewer's permission failure. A permission
failure produces a locally staged packet, per the paragraph above. Work
that only reads asks for no write mode and no worktree.

Cap repeated dispatch attempts on one unit of work at three, matching the
executor-fallback rule in `PROCESS.md`. Past three, the approach changes
rather than the attempt count. The ways out: a re-staged packet the
transport can actually read; a different transport; a deferred gate. Session close accounts for every worktree a delegation created:
list them, and remove the strays (`.agy-mcp/worktrees/job-*` and whatever
your own transports leave behind) with `git worktree remove`. A retry loop
that burns a weekly budget and returns no verdict, leaving a dozen
registered worktrees behind, is the recorded failure these three rules
exist to prevent.

## Stall protocol

Agent CLIs commonly ship without a timeout flag, so the caller owns the
deadline: wrap every delegated invocation in one (`timeout <seconds> <the
delegation command>`) and treat the wrapper's exit as the delegation's
outcome. On a stall, switch tools rather than retrying blind; the same
prompt through the same stalled tool usually stalls again. An empty
return, a zero-exit run with no final text, and any run without an explicit
verdict are each a failed delegation, never a pass. Record the deadline this
repo uses per tool alongside the invocations above.

A dispatched review also carries a liveness convention, so the harness
detects a stall instead of the user asking about one. Run the delegation
in the background and check it mid-deadline. Growing output or CPU burn
counts as alive; a quiet process at near-zero CPU minutes before the
deadline is the recorded stall signature (two field
cases: 17 and 10 minutes of silence at ~0.1s CPU). On that signature,
kill it, retry once at most, then switch transports or defer - the
bounded retry-then-switch above, triggered by the harness's own check
rather than by waiting out the full deadline.

## Reviewer pre-vet

Before a wave or gate depends on any reviewer named above, run the pre-vet
checklist in `MODEL-CLASSES.md`: reachability, usage headroom, permission
profile, and model identity. The reachability step is a contract-shaped
read probe, never a bare echo: stage one small file where the route's
`staging` contract says the packet will sit and have the reviewer read a
nonce back from its content. Two recorded stalls sat behind a passing
echo pre-vet - the echo probed the model, not the read path the review
would actually take. An unvetted, quota-exhausted, or
under-permissioned reviewer defers per `PROCESS.md`.

## Evidence-receipt canary

Fill this in when this repo has runs whose value depends on captured
evidence: traces, metrics, transcripts, recordings, anything the analysis
reads back after the run. Before any expensive run of that kind, a named
canary command must prove end-to-end receipt in the launch shell: the
evidence lands, readable, at the place the analysis will later read it from.
Endpoint reachability is not receipt. A collector that accepts a connection
can still drop every span it is handed. Where the canary cannot run, the
card records an explicit user waiver before the run starts, naming what
evidence the run is risking.

This repo has no such runs today; the rows stay commented out.

| Run type | Canary command | Receipt proven at |
| --- | --- | --- |
<!-- | benchmark sweep | `<command>` | `<path or query the analysis reads>` | -->
<!-- | traced session | `<command>` | `<path or query the analysis reads>` | -->

## Budget etiquette

The agy route runs on a constrained budget. No agy spend without explicit
user approval in the current session, recorded on the card that spends it.
In-harness dispatch and the codex route need no per-session approval.
Escalate reviewer class on failure, not by default, per
`MODEL-CLASSES.md`.

## Wave-close cost record

A delegated wave's closing handoff records the orchestrator model string,
every delegated session id, and per-session cost, duration, and token
totals. Recovery recipe for the OpenCode session store:

1. Record each delegated session id at dispatch time; the task tool
   returns it, and `opencode session list` maps titles to ids after the
   fact.
2. Per session, export and sum:

   ```sh
   opencode export ses_0362bb944ffeX0t8kVAcRToK0p | python3 -c "
   import json, sys
   d = json.load(sys.stdin)
   cost = sum(m['info'].get('cost', 0) for m in d['messages'])
   toks = sum(m['info'].get('tokens', {}).get('total', 0) for m in d['messages'])
   t = [m['info']['time'] for m in d['messages'] if 'time' in m['info']]
   end = max(x.get('completed', x['created']) for x in t)
   dur = (end - min(x['created'] for x in t)) / 1000
   print(f\"cost=\${cost:.4f} tokens={toks} duration={dur:.0f}s model={d['info']['model']['id']} agent={d['info'].get('agent')}\")"
   ```

   Verified 2026-08-03 against an `explore` subagent session:
   `cost=$0.0124 tokens=248428 duration=131s`.
3. Cross-check the wave total with `opencode stats --days 7
   --project ""`, which reports aggregate cost and token totals.
