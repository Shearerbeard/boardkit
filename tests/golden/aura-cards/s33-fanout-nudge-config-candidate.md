---
id: S33
title: Discover-then-fan-out planning + nudge fold-in decision (ai-experiments PR 17)
status: backlog
depends: []
serialize-with: []
lineage: none
executor: any
gates: "S -> A -> U(decision)"
user-gates: [decision]
---

# S33: Discover-then-fan-out planning + nudge fold-in decision (ai-experiments PR 17)

External evidence, filed for board-planning awareness. Mechanics:
[PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Full data:
[2026-07-17-e2e-fanout-nudge-config.md](../evidence/2026-07-17-e2e-fanout-nudge-config.md).

## Scope

Not a code change. `ai-experiments` PR #17 (`trogers/aura-e2e-skills`,
open) carries a discover-then-fan-out coordinator planning skill plus
`mezmo/aura` PR #380's turn-limit nudging, scored 142/144 on the RCA
suite there, the best result recorded in that repo to date, beating
both its inline-skilled (140/144) and base (134/144) prior-best
variants. Our `ai-experiments` integration branch,
`mshearer/aura-e2e-canonical`, was rebased onto PR #17's tip on
2026-07-17 (11 own commits replayed onto PR #17's 4 new commits; one
expected append-only conflict in `results-index.json` resolved keeping
both sides) so this content is available there, not yet pushed pending
user sign-off.

[S32](s32-turn-limit-nudge-variable.md), filed concurrently by another
session, already tracks the narrower nudge-only half
(`configs/sre-shell-orchestrated-nudge.toml`) as a benchmark variable
candidate. S33 is the broader question: whether the fan-out planning
skill (which S32 does not cover) is also worth porting to this repo's
SRE-shell/TerminalBench shape, given it structurally eliminated the
single-task-per-cycle pattern S32's own config doesn't address. S33 is
evidence-only and does not gate on S32's benchmark cycle completing;
it's evaluable at the next board-planning session regardless of where
S32 stands.

## Deliverable

`docs/redesign/evidence/2026-07-17-e2e-fanout-nudge-config.md` (filed)
plus a user decision, recorded in this card's Log, on whether to scope
a fold-in effort and if so whether as an extension of S32 or separate
follow-on work. Not a decision to adopt the config as the next Phase B
variable; per `next-run-state.json`, that selection gate
(`next_variable`) stays open regardless of this card's outcome.

## Acceptance

- The evidence doc exists, is vale-clean, and its numbers are
  cross-checked against `ai-experiments` `results-index.json` and both
  PRs' live state (done at filing, see Log).
- The decision (scope fold-in / defer / close as not worth porting) is
  recorded in this card's Log after the next board-planning session.
- If the decision is to scope fold-in work, a follow-on card is filed
  for it before this card moves to done.

## Preconditions before any fold-in work could start

- `mezmo/aura` PR #380 needs a landed or explicitly-adopted prototype
  build here (same PR that gates S32).
- The RCA/mock-mcp harness shape the config was proven in
  (`aura-e2e/configs/rca/rca-e2e-gpt55-fanout-nudge.toml`, log-analysis
  coordinator over a k8s-sre-style MCP surface) is not this repo's
  SRE-shell/TerminalBench shape; porting the planning skill is separate
  work, not a drop-in.
- The 142/144 number is from Tony's own machine/environment, not
  reproduced on this program's benchmark host; it should not be read
  as directly comparable to this repo's six-task accuracy fractions
  without a run here.

## Gate checklist

- [x] Gate S: evidence doc numbers cross-checked against
      `ai-experiments` `results-index.json` and both PRs' live state
      (2026-07-17, see Log); re-verify if either PR's state changes
      before promotion.
- [x] Gate A: fresh-agent review confirmed the evidence doc and card
      state evidence and a decision point only, not a commitment to
      adopt (2026-07-17, see Log).
- [ ] Gate U (decision): user reviews at the next board-planning
      session and decides whether to scope fold-in work, defer, or
      close as not worth porting.

## Branch

No branch; evidence-only card. If the user scopes fold-in work, that
work gets its own card and branch at promotion.

## Log

- 2026-07-17 Filed after rebasing `mshearer/aura-e2e-canonical` onto
  `ai-experiments` PR #17 and compiling the fanout-nudge benchmark
  evidence. Discovered concurrently with a separate session's [S32](s32-turn-limit-nudge-variable.md)
  filing for the narrower nudge-only config; scoped as a prose
  cross-reference rather than a registry dependency, since S33 is
  evidence-only and evaluable independent of S32's benchmark cycle.
- 2026-07-17 Gate S: cross-checked every number in the evidence doc
  against `ai-experiments` `results-index.json` entries
  (`gpt55-rca-fanout-nudge-proto` and its comparison points) and
  confirmed both PR #17 and PR #380 are OPEN via `gh pr view`. Gate A:
  fresh-agent review of both the evidence doc and this card; findings
  were a stale card-link, a stale "untracked" claim (S32 had since
  tracked the nudge config), an over-strong `depends: [S32]`, and a
  missing Acceptance section: all fixed in this filing.
- 2026-07-17 Promoted to Ready by the board owner (Fable, Claude
  Code) during board close. Depends is empty, so the card was
  dependency-eligible from filing; the orientation canary caught that
  it sat in Backlog. Gate S and Gate A are already recorded above, so
  the card is ready to present at its U(decision) gate. Its scope
  relationship to S32 (narrower nudge-only variable) is noted in the
  Scope section and is a planning input for the user, not a merge.
- 2026-07-17 Gate U(decision): user reviewed the packet and chose
  DEFER. The evidence is compelling (142/144, a structural win on
  planning-cycle shape), but it is unreproduced on this program's
  host and on a different harness, so the user is running a separate
  concurrent scoring session against Tony's already-running nudge
  code plus this program's control to get comparable data. That
  data-gathering is detached from the main refactor process and its
  results are parked, not fed into the board's benchmark loop.
  Revive trigger: the concurrent notanton scoring data lands and is
  parked; a future board-planning session then re-presents this card
  with that data for the scope/close decision. Until then the card
  sits in backlog (removed from Ready), the U(decision) box stays
  unticked because the final scope-or-close call is still pending,
  and no follow-on card is filed. S32 is unchanged and stands alone
  as the nudge-only benchmark-variable candidate.
- 2026-07-17 Revive-trigger data landed and parked: the concurrent
  Nobara scoring session completed - N=3 nudge-on vs nudge-off control
  on this program's host and harness, evidence
  [2026-07-17-s32-nudge-n3-notanton.md](../evidence/2026-07-17-s32-nudge-n3-notanton.md),
  tracked on [S32](s32-turn-limit-nudge-variable.md). Key result for the
  eventual scope/close decision: the nudge-only half is INERT on this
  repo's SRE-shell cell at the current worker `turn_depth` (the nudge
  never fired; 10/18 vs 9/18 is variance). That neither confirms nor
  refutes the fan-out variant's 142/144, which was won on a different
  harness at a lower depth - but it does show the nudge alone buys
  nothing here without a depth change, sharpening the fan-out-vs-nudge
  attribution question. U(decision) box stays unticked; a future
  board-planning session re-presents with this data.
- 2026-07-17 The fan-out half now has this-host data too, closing the
  attribution question the prior entry raised. Ported the discover-then-
  fan-out planning skill to `configs/sre-shell-orchestrated-fanout-nudge.toml`
  (same PR 380 nudge keys as S32, plus a "discover, then batch"
  system_prompt section - necessarily sequential-dependency chaining, not
  concurrent dispatch, since this harness has no code-level lock on its
  shared terminal connection; see the config's own header) and ran N=3
  on the same six-task cell, same `aura-pr380` binary S32 used. Evidence:
  [2026-07-17-s33-fanout-nudge-n3-notanton.md](../evidence/2026-07-17-s33-fanout-nudge-n3-notanton.md).
  Result: 7/18 (38.9%), the LOWEST of the three cells now measured on
  this harness - below both S32's nudge-off control (9/18) and nudge-on
  (10/18) on the identical binary. `dna-insert` and
  `conda-env-conflict-resolution` both regressed. Reading: the
  142/144 RCA-harness win came from real concurrent dispatch across
  independent investigation surfaces, a property this single-shared-
  terminal harness cannot safely offer; porting the batching instruction
  without that property does not reproduce the win and may actively
  hurt by front-loading task sequences before evidence is confirmed.
  Combined with S32's inertness finding, both halves of the fanout-nudge
  config now have negative or neutral this-host evidence against them.
  Also surfaced a structural gap while setting this up:
  `AuraOrchestratedAgent` hardcodes its config filename with no
  override mechanism, so alternate-config runs need a checksummed
  swap/restore of the live file - filed as [S34](s34-config-override-gap.md).
  A mid-run AWS SSO expiry (same failure signature S32 already
  documented) invalidated one replication; it was discarded and redone
  after re-auth, verified via real tool-call activity in the SSE stream
  rather than trusting the credentials preflight. U(decision) box stays
  unticked - this is more data for the same open decision, not the
  decision itself.
- 2026-07-18 Gate U(decision) re-presented at a board-planning session
  (board owner: Opus 4.8, Claude Code). Gate D spot-check confirmed the
  this-host evidence matches this log (fan-out 7/18, nudge-on 10/18,
  nudge-off 9/18; all 18 runs trace-complete). Decision: DEFER, not
  close. The literal port did not help on this harness and the mechanism
  is understood - no safe concurrency here to carry the RCA win - but the
  user wants the broader question kept open, not shut. Framing recorded
  for the revive: this repo is a server-side agent harness that should
  ship defaults which work out of the box, tuned for its terminal/SRE
  shape rather than a coding agent, while still allowing system prompts
  and workers built from scratch. Converging with Tony's fan-out/nudge
  line toward that smart-default set is a deliberate future effort. The
  priority this session moved to the frame-based decisions (S12, S13) and
  coordinator simplification (S9, S10, S11, S15), which are the vehicle
  for those defaults and are gated behind MILESTONE -> S9. Revive
  trigger: take S33 up again as part of that coordinator-simplification /
  defaults wave, or when a turn_depth experiment is on the table (S32's
  nudge inertness was depth-conditional). Until then S33 stays backlog,
  the U(decision) box stays unticked, and no follow-on card is filed. S32
  is unchanged and stands alone as the nudge-only benchmark-variable
  candidate.
