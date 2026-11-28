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

At planning, agree which available models fill the roles in
`MODEL-CLASSES.md`. Record any approved reviewer substitution and whether
the plan or completed candidate gets a Frontier review.

## Fix-round packets

Use `boardkit review-packet` to capture the full candidate range. Stage
the material for each reviewer under the base repo's gitignored
`.review/<card>/<role>/`. Include the specification revision, source
worktree and range, actual authors, required checks and optional diagnostics.
For a repair, include the prior findings and dispositions. Keep prior
receipts when regenerating a packet. Use `--repo` for another worktree
and `--suffix` for a supplementary packet.

## Harness bindings

One row per board-owner harness this repo has actually run a board
session from. Live model pins resolve at dispatch time from the harness
configs listed below; per the no-model-ids rule,
none are copied here.

| Board owner (harness) | Executor pool | Gate A reviewer | Gate F route | Defers |
| --- | --- | --- | --- | --- |
| Claude Code | Claude subagents | code reviewer from different model family | frontier model via CLI | nothing |
| OpenCode | pinned agents | code reviewer independent of authors; optional plan review with user choice | user-approved Frontier review | when no independent model available |

Pin sources: `~/.config/opencode/opencode.json` and
`~/.config/opencode/agent/*.md` for the opencode lane;
`~/.codex/config.toml` for the codex lane. Provider constraints for a given run come from the
session-start provider question in the delegation inventory, not from
this table.

Doctor checks that every `pin_source` path exists and that its anchor
matches a heading; it stats the file, it never executes the route's
`preflight` commands. Preflight commands are printed for the caller to
run, per the rule that a diagnostic must not be a code-execution surface.

## Tools, in order of preference

1. `opencode run -m` with the plain provider/model path read from the pin
   sources above - code and technical plan/spec review at Gate A. Staged
   packet in a dedicated directory per the `working-dir` contract;
   invocation and validity rules in the `opencode-cli` skill. Binary on
   PATH; pins in `~/.config/opencode/`.
2. `codex exec --sandbox read-only` - code review fallback and Gate F
   frontier review. Repo-native paths, cwd at this repo, caller-owned
   deadline via `perl -e 'alarm N; exec @ARGV' --` (stock macOS has no
   `timeout`); rules in the `codex-cli` skill. Config in `~/.codex/`.

For the configured code-review order, run `boardkit resolve-route code-review`.

## Transport rule

Use native subagent dispatch inside the owner's harness. For an external
harness use a CLI with a caller-owned deadline, or a pre-vetted adapter
with a recoverable job handle. Run mechanical checks in the candidate
worktree. If a reviewer cannot read an input, give it a staged packet
and verify access before starting the review.

The coordinator keeps failed-run evidence with the card. At session close
account for delegated worktrees, including `.agy-mcp/worktrees/job-*`;
use `git worktree remove` once their commits and evidence are safe.

## Stall protocol

External CLI deadline on this board: 10 minutes. For a
background CLI, check liveness before the deadline. Native dispatch uses
harness completion notifications. Read the verdict from the reviewer's
final message. If delivery failed, keep the transcript and apply the
delivery rule in `PROCESS.md`.

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

Record the aggregate and per-model figures in the wave-close retro. If
per-session recovery fails mid-close, record what is recoverable and log
the failure as process feedback rather than dropping the record.

## Machine bootstrap appendix

What a second machine needs to reach a dispatch-ready board, stated as
kinds. The checkout mechanics live in the README quick start; the lane
verification procedure is the pre-vet checklist in MODEL-CLASSES.md.
This appendix owns the lane inventory between them.

- Per-harness config trees, by kind: the opencode config group (often
  dotfiles-managed), the sibling claude-skills install for the
  language skills and the codex config tree. None of these ship with a
  clone; each machine brings or rebuilds its own.
- Provider accounts, by kind - subscription, API key, cloud-role -
  matched to the routes this board's `boardkit.toml` declares.
  Credentials are the machine's own; nothing in a clone carries them,
  and account facts never appear as model ids.
- Verification, per lane, before a wave depends on it: the pre-vet
  checklist in `MODEL-CLASSES.md`, applied as written.

A machine that clears every bullet above and a green
`boardkit doctor` is dispatch-ready. This appendix carries no clone
URL; a machine records where it cloned from in its own notes.
