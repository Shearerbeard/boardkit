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

One row per board-owner harness this repo has actually run a board
session from. Live model pins resolve at dispatch time from the harness
configs named in the Pin sources column; per the no-model-ids rule,
none are copied here.

| Board owner (harness) | Executor pool | Gate A reviewer | Gate F route | Defers |
| --- | --- | --- | --- | --- |
| Claude Code | Claude subagents (`general`, `Explore`) | opencode CLI reviewer, codex CLI as fallback (both author no Claude diffs, so the invariant holds for any Claude-authored card) | codex CLI frontier model | nothing |

Pin sources: `~/.config/opencode/opencode.json` and
`~/.config/opencode/agent/*.md` for the opencode lane;
`~/.codex/config.toml` for the codex lane; the agy doctor report for the
Antigravity lane. Provider constraints for a given run come from the
session-start provider question in the delegation inventory, not from
this table.

Doctor checks that every `pin_source` path exists and that its anchor
matches a heading; it stats the file, it never executes the route's
`preflight` commands. Preflight commands are printed for the caller to
run, per the rule that a diagnostic must not be a code-execution surface.

## Tools, in order of preference

1. `opencode run -m` with the plain provider/model path read from the pin
   sources above - code review at Gate A. Staged
   packet in a dedicated directory per the `working-dir` contract;
   invocation and validity rules in the `opencode-cli` skill. Binary on
   PATH; pins in `~/.config/opencode/`.
2. `codex exec --sandbox read-only` - code review fallback and Gate F
   frontier review. Repo-native paths, cwd at this repo, caller-owned
   deadline via `perl -e 'alarm N; exec @ARGV' --` (stock macOS has no
   `timeout`); rules in the `codex-cli` skill. Config in `~/.codex/`.
3. `agy` (Antigravity bridge) - prose, plan, and spec review. Detached
   jobs through the agy MCP tools; budget-gated, ask before spending.
   Config in `~/.config/agy-mcp/config.toml`.

Card and gate reviews go to the opencode lane first; ad-hoc adversarial
review and the post-stall fallback go to the codex lane. A bare request
for a second-model review resolves to the codex lane.

Route by what the artifact is judged on. Code review goes to the
code-specialized reviewers, in the harness where the diff was written. A
reviewer whose strength is natural language rather than code is reserved for
the artifacts judged on language: plans, prose, specs, architecture, product,
and marketing review. It is not the default code reviewer. If such a reviewer
runs on a metered or capped budget, record that here as a gate: no use
without explicit user approval in the current session.

Record the split explicitly rather than leaving it to inference: name
which reviewer takes card and gate reviews, and which takes ad-hoc
adversarial review and the post-stall fallback. A bare request for a
second-model review should resolve to one tool by reading this
section.

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

This repo has no evidence-dependent run types today (no traced sessions,
benchmark sweeps, or recordings that the analysis reads back). The rows
below stay commented out; un-comment and fill one only when a run type is
added whose value depends on captured evidence.

| Run type | Canary command | Receipt proven at |
| --- | --- | --- |
<!-- | benchmark sweep | `<command>` | `<path or query the analysis reads>` | -->
<!-- | traced session | `<command>` | `<path or query the analysis reads>` | -->

## Budget etiquette

Restate or tighten the budget etiquette from `MODEL-CLASSES.md` here if
this repo has repo-specific cost constraints (a shared quota, a per-wave
budget cap). Leave this section out if the generic guidance is enough.

## Wave-close cost record

At wave close the board owner records, for the orchestrator session and each
delegated session:

- model string (the provider/model path used for the session),
- session id or transcript path,
- duration,
- input, output, and total token counts,
- cost in USD if reported by the harness.

Recovery recipe by harness:

- **opencode (board owner and Gate A code-review fallback):** copy the
  figures from the session's close summary in the opencode transcript.
  There is no stable CLI export yet; if an export becomes available, prefer
  it and validate the totals against the live transcript before committing
  the record.
- **codex (code-review fallback and Gate F frontier review):** copy the
  figures from the codex session log printed at the end of `codex exec`.
- **agy (prose review):** copy the figures from the agy job summary shown
  by the agy MCP tools; the job id is the session id.

Record the aggregate and per-model figures in the wave-close retro. If
per-session recovery fails mid-close, record what is recoverable and log
the failure as process feedback rather than dropping the record.
