---
id: MILESTONE
title: Track A replication gate
status: done
depends: [S6, S17, S16]
serialize-with: []
lineage: primary
executor: smart
gates: "U(launch) -> M -> U(acceptance)"
user-gates: [launch, acceptance]
---

# MILESTONE: Track A replication gate

Plan section: the Track A milestone in Stage 3 of
[2026-07-11-orchestration-redesign.md](../plans/2026-07-11-orchestration-redesign.md).
Mechanics: [PROCESS.md](../PROCESS.md). Required reading:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md).

## Scope

No code changes. The card produces one benchmark launch from the
refactored primary head plus the S16 sre-hard run, with the resulting
catalogs and comparison reports, and it records the accepted head on
the registry.

## Deliverable

Score-based empirical evidence that the refactored binary behaves
like the baseline: an N=3 trace-complete TerminalBench replication
compared against the Nobara lineage reference
([2026-07-09-w15f-nobara-baseline.md](../evidence/2026-07-09-w15f-nobara-baseline.md)),
plus the sre-hard regression check defined by S16.

## Acceptance

- Pre-registered comparison: equality against the Nobara baseline
  (mean and per-task flips under the variance reading rule), fixed at
  the launch gate before results exist. The spec is drafted and
  frozen at
  [2026-07-17-milestone-track-a-prereg.md](../evidence/2026-07-17-milestone-track-a-prereg.md);
  the launched binary sha and run ids are its only launch-time fields.
- All three runs pass SSE, parse, and Phoenix gates (driver RESULT
  lines are the record).
- sre-hard run meets the S16 pass criteria.
- On acceptance, the accepted head commit is recorded here and S9
  unblocks; on regression, bisect the serial Track A commit list and
  file the finding before any Track B work.

## Gate checklist

- [x] Gate U (launch): provenance, canary, standing rules, and the
      pre-registered comparison spec.
- [x] Gate M: the N=3 replication plus sre-hard, reports on file.
- [x] Gate U (acceptance): user reviews both results with a
      strong-class agent board review; decision logged either way.

## Branch

No branch; runs build from the primary head at the time of launch.

## Log

- 2026-07-11 Filed by S0 from the approved plan.
- 2026-07-17 Promoted to Ready by the board owner (Fable, Claude
  Code). S6 completion this session satisfied the last open
  dependency (S6, S17, S16 all Done). The Track A milestone is now
  unblocked and awaiting its user launch decision; the board-close
  orientation canary flagged the missed promotion, which this entry
  resolves.
- 2026-07-17 Pre-registered comparison spec drafted and frozen
  (`evidence/2026-07-17-milestone-track-a-prereg.md`) by the Fable
  board owner while notanton was busy: the host-free half of the
  `U(launch)` gate. It pins the comparison target (Nobara mean 3.0/6
  {2,3,4}), the provenance-delta validity condition (only the binary
  may differ from `9df96382`), the reading rule (stable-task flips are
  signal, boundary moves are noise), and the accept/regression/
  investigate decision rule, all before results exist. The `U(launch)`
  box stays unticked: provenance (`--strict-readiness`) and the
  trace-receipt canary still need notanton free at launch, and the
  launched sha plus run ids are recorded then. Confirmed the baseline
  ran on notanton (its driver log is on that host), so the
  replication on notanton has no host confound.
- 2026-07-18 Gate D drift audit before U(launch) (fresh sonnet
  subagent, board owner's harness). PASS on board consistency,
  primary-head identity (7a0f0651, clean worktree, descends from
  9df96382), pre-reg spec integrity, and config sha (b91b4ce3 matches
  the baseline pin). One drift finding, recorded here on the board as
  an explicit divergence per PROCESS.md rather than fixed now:
  ARCHITECTURE.md line anchors are pinned to 3f75a68f (S30) but the
  head under test is 7a0f0651, 12 commits ahead; build_continuation_wrapper
  is cited at orchestrator.rs:1346 but sits at ~1263 after the S4/S5/S6
  refactors (logging.rs off-by-one, types.rs:770 still resolves). The
  stale anchors do not affect this replication - its validity rests on
  the pre-reg spec and provenance, not on doc line numbers - and the
  correct re-anchor target is the accepted head, unknown until
  acceptance, so the S30-style re-anchor pass is deferred to Track A
  acceptance. Operational note: the baseline config is swap/restored
  for nudge runs (S34), so its sha256 is re-checksummed in the launch
  shell at provenance time, not trusted from this audit snapshot.
  U(launch) box stays unticked; no launch approved.
- 2026-07-18 Gate U(launch) PASSED; rep 1 of 3 launched. User approved
  the launch and pre-approved Gate F at this board-planning session
  (board owner: Opus 4.8, Claude Code). A provisioning gap was found and
  closed first: the RUNBOOK's default host paths point at the
  coordinator-context/baseline line, and 7a0f0651 was absent on
  notanton, so origin/mshearer/orchestration-simplification was fetched
  and built into a dedicated worktree (Linux binary sha256 779f6699...,
  release, CXXFLAGS=-include cstdint); the Mac sre-hard binary was built
  from the 7a0f0651 worktree (darwin sha256 15061d61...). Checkpoint-1
  preflight all green against the built binary: config
  sre-shell-orchestrated.toml sha256 b91b4ce3... (baseline-pin match,
  verified live plus git-clean, model sonnet-4-6, no nudge/fanout
  markers, no stray variant configs), creds valid (Bedrock account),
  docker ready (Nobara x86_64), OTEL and Phoenix ready, trace-receipt
  canary OK (span queried back in 4.0s), strict-readiness provenance
  exit 0 - only the binary differs from 9df96382, so the single-variable
  validity condition holds. One benign note: the TerminalBench repo is
  dirty only from an untracked harness-config/ dir, not a tracked
  change. Rep 1 launched on notanton in a detached tmux session with
  LABEL_TOTAL=3; run ids are recorded as each rep starts. Gate F (codex
  frontier review over the 30-commit 9df96382..7a0f0651 range) is
  running concurrently, to land before U(acceptance). Checkpoint model:
  an affirmative pause after rep 1 (verify real tool-call activity plus
  the SSE/parse/Phoenix gates) before rep 2, then guarded auto-continue
  for reps 2-3. The sre-hard N=3 cell (Gate M part 2) runs on the Mac
  next. ARCHITECTURE.md anchor re-verification stays deferred to
  acceptance per the Gate D entry above.
- 2026-07-18 Gate M rep 1 of 3 complete (run_id
  2026-07-18__14-33-22-milestone-tracka-1of3, resolved 3/6). Trace gates
  PASS: sse_present 6 of 6 with no missing spans and no parse errors,
  phoenix_matched 6/6; 181 worker tool calls; all tasks ran 9-15 min
  (hello-world 37s) -
  real engagement, not the SSO-expiry signature. Per-task vs baseline:
  resolved reshard-c4-data, dna-insert, hello-world; unresolved
  conda-env-conflict-resolution and install-windows-3.11 (both baseline
  stable failures, consistent) and tune-mjcf. tune-mjcf is a baseline
  STABLE-PASS task (3/3) that FAILED via agent_timeout/max_depth - a
  pre-registered stable-pass flip (regression signal) and the max_depth
  the quality gates name. Held at Checkpoint 2 for the user; rep 2 not
  started. Gate F (codex gpt-5.5, author of the reviewed range is the
  mixed executor set that wrote the 30 S-card commits) VERDICT 2 BLOCKING
  + 1 MINOR, recorded to this ledger: (F1) BLOCKING templates.rs chained
  .replace() re-substitutes any %%VAR%% appearing in already-substituted
  content - verified real (latent injection/behavior drift vs a format!
  baseline), but benchmark task text carries no %% markers, so NOT the
  likely tune-mjcf cause; queued as a fix regardless. (F2) BLOCKING
  orchestrator.rs AURA_PROMPT_JOURNAL inert - this is the INTENDED S24
  removal, dispositioned as a false positive. (F3) MINOR mod.rs dropped
  public re-exports of orchestration::fields/sections (S6 dead-code
  sweep). Disposition of F1/F3 rides to U(acceptance).
- 2026-07-18 Gate M part 2 (sre-hard N=3) complete on the Mac against
  the 7a0f0651 darwin build (sha 15061d61), config bf3c8b8b, harness
  751fdc2 - the same cell as the S16 reference, only the binary differs.
  Diagnostic 126/126 (100 percent), above the reference 125/126. Quality
  64/78 vs the reference 73/78, BUT the gap is confounded by mock-MCP
  data variance rather than a clean coordinator regression: on
  multi-category-findings, iter 1 found 8/9 categories while iters 2 and
  3 found only 4/9 because the k8s-sre-mcp returned unknown_metric
  placeholders and variant alert names (HighErrorRate-nginx,
  KubePodCrashLooping) that the exact-match answer_contains assertions
  reject. So sre-hard is weak, caveated evidence, not clean
  corroboration of the tune-mjcf timeout. Exact per-iteration quality/26
  and the executable floor are interpretable only after de-confounding
  the mock variance. Results at
  ai-experiments/aura-e2e/sre-hard-results-20260718-144338. Feeds
  U(acceptance) as supporting evidence with the confound labeled.
- 2026-07-18 tune-mjcf rep-1 timeout dissected in the background (4-agent
  workflow while rep 2 ran); evidence frozen at
  [2026-07-18-tune-mjcf-rep1-timeout-dissection.md](../evidence/2026-07-18-tune-mjcf-rep1-timeout-dissection.md).
  Verdict: LIKELY VARIANCE at N=1 (~75 percent). The refactored
  coordinator path is byte-identical to baseline (bounding caps,
  continuation and worker prompts, planning-cycle and turn-depth logic
  all verified unchanged); the only two non-identical deltas (dup-call
  policy, templates .replace) are provably inert at benchmark defaults
  and non-marker content. Baseline and milestone traces match
  structurally; the whole divergence is the iteration-2 operator's
  non-deterministic tuning search on a budget-boundary task. Decisive
  tell: the baseline's own tune-mjcf durations were 717/355/915s, so run
  3 also grazed the 900s wall and the task is knife-edge - rep 1 fell the
  other way. Decision rule: tune-mjcf resolving in rep 2 or rep 3
  confirms variance (close as noise); a timeout in both is a real
  regression to bisect (templates commit first, then dup-call). A shared
  latent fault (over-scoped operator task plus 1015-char pane clip,
  present in both builds) is flagged for a follow-up card. Loose thread:
  the rendered runtime-config sha changed (19dba59d to 00c6245f) on a
  byte-identical source config; confirm cosmetic before any bisect.
- 2026-07-18 Gate M rep 2 of 3 complete (run_id
  2026-07-18__16-35-55-milestone-tracka-2of3, resolved 2/6). Trace gates
  pass (sse_present 6 of 6, no missing spans, no parse errors, phoenix
  6/6). Per-task: resolved hello-world (stable pass, holds) and
  reshard-c4-data (boundary); unresolved dna-insert (boundary), conda-env
  and install-windows (stable failures, consistent), and tune-mjcf
  (agent_timeout again). tune-mjcf is now 0/2 across reps 1-2, both
  timeouts - the other stable pass (hello-world) holds, so the signal is
  isolated to tune-mjcf, the knife-edge task the dissection identified.
  Running mean 2.5/6 over reps 1-2, inside the [2,4] noise band. Rep 3
  launched as the decider per the pre-registered rule and the dissection
  rule: tune-mjcf resolving in rep 3 confirms variance (1/3, close as
  noise); a third timeout is 0/3 and a real regression to bisect
  (templates commit first, then dup-call) after confirming the 00c6245f
  config-sha delta is cosmetic. Guarded auto-continue: rep 2 tripped no
  infra guard.
- 2026-07-18 Config-sha loose thread resolved as cosmetic. The
  milestone's rendered runtime config differs from the baseline source
  config (b91b4ce3) in exactly one line - the MCP server URL
  (localhost:32904 vs the templated default) - the expected per-run
  _patch_mcp_url substitution. Model, turn depths, max_planning_cycles,
  prompts, and bounding config are byte-identical, so the
  00c6245f-vs-19dba59d rendered-sha delta is the per-run MCP port, not a
  behavioral toggle. Every mechanistic thread the dissection opened is
  now closed: the refactor cannot cause the tune-mjcf timeout by code,
  behavior, or config. The only open question is the empirical one -
  tune-mjcf 0/2 - and rep 3 decides it.
- 2026-07-18 Gate M rep 3 of 3 complete (run_id
  2026-07-18__18-03-05-milestone-tracka-3of3, resolved 4/6); trace gates
  pass (sse_present 6 of 6, no missing spans, no parse errors, phoenix
  6/6). Per-task: resolved hello-world (stable pass), dna-insert and
  reshard-c4-data (boundary), and conda-env-conflict-resolution;
  unresolved install-windows (stable fail, consistent) and tune-mjcf
  (agent_timeout, a third time). N=3 COMPLETE. Per-run scores rep 1/2/3 =
  3/2/4, so the distribution is {2,3,4}, mean 3.0/6, sample SD 1.0 -
  identical to the baseline distribution {2,3,4}. Per-task vs baseline:
  hello-world 3/3 holds; install-windows 0/3 holds; dna-insert 2/3 and
  reshard 3/3 (boundary noise). Two stable-task flips: tune-mjcf 3/3 to
  0/3 (stable-pass flip to failure, all agent_timeout) and conda-env 0/3
  to 1/3 (stable-fail flip to resolved, once). Against the pre-registered
  rule this is NOT a clean PASS: the tune-mjcf flip triggers REGRESSION
  and the conda-env flip triggers INVESTIGATE, even though the aggregate
  distribution matches baseline exactly. The dissection mechanistically
  exonerated the refactor (byte-identical code, behavior, config), and
  the two flips roughly cancel in aggregate. Escalated to U(acceptance)
  as a judgment call; no auto-accept.
- 2026-07-18 U(acceptance) deferred pending a flip investigation the user
  requested (leaning accept). Background workflow diagnoses both
  stable-task flips: whether tune-mjcf 0/3 is knife-edge variance (the
  operator-prompt diff plus a head-versus-baseline run comparison across
  all six tune-mjcf runs) and whether the conda-env 0/3 to 1/3 flip is
  variance or a refactor behavior change, then an accept-readiness
  synthesis. The verdict feeds the final decision.
- 2026-07-18 Flip investigation complete; verdict ACCEPT-SUPPORTED (high
  confidence). Evidence frozen at
  [2026-07-18-milestone-accept-flip-investigation.md](../evidence/2026-07-18-milestone-accept-flip-investigation.md).
  The pre-registered regression tripwire fired as designed (tune-mjcf
  0/3) and mandated diagnosis before acceptance; that diagnosis is now
  done on every pre-committed bisect target and clears the refactor.
  tune-mjcf 0/3 is stochastic knife-edge variance: the templates .replace
  delta is empirically closed on the actual operator prompts (no fixed
  frame to corrupt), the baseline itself grazed the 915s wall (B3), and
  the three head failures are three different dead ends. conda-env 0/3 to
  1/3 is variance on a hidden four-conflict chain: rep 3 won with the
  fewest tokens (113K vs 163K/193K) and the baseline reached the same
  import-test gate (2of3). The two flips cancel; aggregate {2,3,4} mean
  3.0 matches baseline. Residual risk: n=3, and the tune-mjcf reading
  leans on the single B3 data point. Conditions carried to acceptance: an
  F1 templates fix-forward card, F3/F2 disposition, the ARCHITECTURE.md
  re-anchor, a shared-latent-fault card, and optional confirmatory
  baseline reps. Presented to the user for the final accept call;
  baseline acceptance is a standing user gate.
- 2026-07-18 Gate U(acceptance): ACCEPTED by the user. 7a0f0651 recorded
  as the accepted Track A head (binary sha256 779f6699 Linux / 15061d61
  darwin). The N=3 distribution {2,3,4}, mean 3.0, matched baseline; the
  two stable-task flips (tune-mjcf 0/3, conda-env 1/3) were diagnosed as
  stochastic knife-edge variance that cleared the refactor
  ([flip investigation](../evidence/2026-07-18-milestone-accept-flip-investigation.md)) -
  the pre-registered regression tripwire fired and was discharged on
  every pre-committed axis. Gate M (N=3 plus sre-hard) and
  U(acceptance) ticked; card Done. S9 unblocks. Follow-ups carried: an
  F1 templates fix-forward card, S6/S24 disposition of F3/F2, the
  ARCHITECTURE.md re-anchor to 7a0f0651, and a shared-latent-fault card;
  wiki handoff to follow.
