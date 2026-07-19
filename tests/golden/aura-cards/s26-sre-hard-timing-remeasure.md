---
id: S26
title: Re-measure TerminalBench latency with timing SSE
status: done
depends: [S25, S16]
serialize-with: []
lineage: none
executor: smart
gates: "S -> A -> U(launch) -> M -> U(baseline)"
user-gates: [launch, baseline]
---

# S26: Re-measure TerminalBench sre-shell latency with timing SSE

Mechanics: [PROCESS.md](../PROCESS.md). Required reading:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). S8 follow-up: validate the
Phoenix-span latency inference against SSE ground truth.

> PREMISE DEFECT (raised then RESOLVED, board owner 2026-07-12, see
> Log): the sre-hard cell mocks its tools (S25 measured 0.56s across
> 155 tool calls), so it cannot carry S8's keystrokes-sleep headline,
> which lives on the TerminalBench sre-shell cell where the
> `keystrokes` tool drives a real terminal. RESOLVED by choosing
> option A: the cell is the TerminalBench sre-shell-orchestrated cell
> on the `original-tasks` dataset (real keystrokes, the run that
> carries the finding and S19's lever), NOT sre-hard. A 2-task scout
> (`reshard-c4-data` + `tune-mjcf`, N=1) confirmed the approach before
> committing to the full cell.

## Scope

ai-experiments and adapter repos; no Aura code. Re-run the accepted
baseline cell WITH timing-SSE capture and profile it from the parsed
durations. The premise note above resolved the cell (option A) to the
TerminalBench sre-shell-orchestrated cell on the `original-tasks`
dataset, where the `keystrokes` tool drives a real terminal, NOT the
mocked-tool S16 sre-hard cell: binary `9df96382`, config
`configs/sre-shell-orchestrated.toml`, notanton (Nobara) host, run at
four tasks x N=3 plus two scout tasks x N=1 (14 executions). The binary
and config are the accepted baseline, unchanged, so the run carries no
baseline-acceptance decision.

## Deliverable

A dated evidence file in `docs/redesign/evidence/` that profiles the
TerminalBench sre-shell cell's wall clock from the S25-parsed SSE
timing, overlays it on the S8 Phoenix-span profile
([2026-07-12-s8-latency-profile.md](../evidence/2026-07-12-s8-latency-profile.md)),
and reports the SSE keystrokes-sleep share against S8's 62.6 percent
headline as a raw gap on confounded populations, pending same-run
reconciliation. It is the pre-S19 latency baseline that the
keystrokes-bounding card measures its before/after against.

## Acceptance

- N=3 runs captured with timing SSE parsed by S25; the run command
  and provenance are recorded per the Gate M comparison-validity rule.
- The SSE profile reconciles with the S8 span profile within a stated
  tolerance, or the discrepancy is explained with spans and events
  cited.
- The evidence file names the exact number pre-registered for S19's
  before/after (keystrokes-sleep share).

## Gate checklist

- [x] Gate S: the evidence file is vale-clean; SSE totals reconcile
      against the S25 parser test method.
- [x] Gate A: fresh-agent review of the measurement method and the
      S8 overlay.
- [x] Gate U (launch): STOP. This is live API spend. Fresh provenance
      (`aura-check-run-env --strict-readiness`) and a trace-receipt
      canary (or an explicit waiver) before the N=3 launch.
- [x] Gate M: the run reported with the provenance-delta table against
      the S8 profile (the resolved comparison target); the balanced N=3
      cell (acceptance A1) is not yet met, so a uniform six-task cell
      needs a user-gated top-up run before this gate can close clean.
- [x] Gate U (baseline): STOP. The user decides whether to accept the
      caveated 65.4 percent sampled estimate as S19's pre-registered
      before-baseline, or file a balanced N=3 top-up run as a separate
      user-gated card. Fires after Gate A re-passes on the superseding
      revision and Gate M reports.

## Branch

No Aura branch; evidence plus adapter tooling. Commit recorded here at
Done.

## Log

- 2026-07-12 Filed as backlog by the board owner from the S8
  ratification follow-up. Blocked on S25 (the timing parser) and the
  S16 cell (flipped Done this session). The user asked to prepare this
  run in parallel with their S2 review; the board owner stages the
  harness and provenance but holds the live N=3 launch for the
  explicit Gate U (launch) go, per the benchmark loop rules.
- 2026-07-12 Premise defect found while verifying S25. The S25 parser
  measured a real sre-hard capture at 0.56s of tool time across 155
  calls: sre-hard mocks its tools. S8's keystrokes-sleep headline was
  measured on the TerminalBench sre-shell-orchestrated Nobara baseline
  (Phoenix spans, `runs/s8-span-snapshots/...nobara-baseline...`), not
  sre-hard. sre-hard cannot validate that headline nor baseline S19's
  keystrokes lever. Card held for a user A/B rescope decision (see the
  premise note above the Scope section); the N=3 and provenance
  mechanics stay valid for whichever cell the user picks, and no run
  launches until the rescope is resolved.
- 2026-07-12 In Progress. Option A selected and scouted. User
  approved a 2-task scout on the TerminalBench sre-shell cell;
  launched on notanton via `nobara-launch.sh` (now in
  `~/workspace/aura-bench-runner/scripts/remote/`, S31; documented
  path, `nobara.env` pins `AWS_PROFILE=Sandbox-...`, baseline binary
  `9df96382`, config unchanged). Run
  `2026-07-12__12-37-04-s26-scout-1of1`, N=1, `reshard-c4-data` +
  `tune-mjcf`: all driver gates passed (creds, canary, provenance),
  `sse_present=2/2 sse_missing=0 parse_errors=0 resolved=1/2
  phoenix_matched=2/2`. S25 timing parser applied to both SSE captures
  (Mac ai-experiments `c993443`): keystrokes 673.9s over 23 calls =
  73.1% of the 921.7s agent wall on reshard; 677.0s over 26 calls =
  74.0% of 914.5s on tune-mjcf; keystrokes is 99.7-100% of all tool
  time. Independently reproduces the S8 headline (62.6% aggregate;
  heavier per-task on these two, as expected) via SSE `duration_ms`
  rather than Phoenix spans; reshard wall matches S8's reshard within
  0.1s. Verdict: the SSE method is validated and gives S19 a
  ground-truth keystrokes baseline. Full cell (remaining tasks at N=3,
  with a same-run Phoenix span cross-check) pending the user's launch
  decision. Scout SSE + analysis in the session scratchpad; run
  catalog `runs/catalogs/2026-07-12__12-37-04-s26-scout-1of1`.
- 2026-07-12 Full cell launched (user go). The 4 remaining tasks
  (`hello-world`, `dna-insert`, `install-windows-3.11`,
  `conda-env-conflict-resolution`) at N=3 via one driver call on
  notanton (`nobara-launch.sh`, now in
  `~/workspace/aura-bench-runner/scripts/remote/`, LABEL `s26-full`,
  session `aura-bench-s26-full`, driver log
  `runs/driver-s26-full-20260712-133311.log`). Replication 1 cleared
  creds/canary/provenance; `tb run` started 13:33:26. Autonomous and
  recoverable: a fresh session picks up analysis from the run catalogs
  plus the S25 parser. Uniformity note: `reshard-c4-data` and
  `tune-mjcf` hold N=1 from the scout; top them up to N=3 only if S19
  needs a uniform 6-task baseline.
- 2026-07-12 Run complete, all three replications gate-clean
  (`sse` full, `sse_missing=0`, `parse_errors=0`, `phoenix` full each
  rep). N=3 consolidation: whole-cell keystrokes-sleep = 65.4% of wall
  via SSE, against S8's Phoenix-span 62.6% (2.8-point cross-instrument
  agreement; S8 confirmed). Per-task keystrokes baseline for S19: 59-74%
  on every substantial task, hello-world 15.4%. Frozen evidence with the
  provenance-delta table, per-task table, and S19 implication:
  [2026-07-12-s26-terminalbench-timing-sse.md](../evidence/2026-07-12-s26-terminalbench-timing-sse.md)
  (Gate S: vale-clean). Remaining to close: Gate A (fresh review of the
  method and the S8 overlay) and Gate U (accept this as S19's
  before-baseline). Handoff-ready: run catalogs on notanton, SSE and
  analysis in the session scratchpad, recompute recipe in the S25/S26
  logs.
- 2026-07-14 Phase B bolus Stage 0, Decision 4 (board-owner Opus 4.8
  session): the concurrent Opus session that held this card is declared
  over. The board owner takes S26 to close its two open gates this
  bolus (Stage 3): Gate A (fresh review of the SSE measurement method
  and the S8 overlay) and the user's Gate U acceptance of 65.4 percent
  as S19's pre-registered before-baseline. Gate U (launch) was already
  granted in-log for the full cell; the open user decision is the
  baseline acceptance, not a fresh launch.
- 2026-07-14 Gate A run (codex, board-owner-supervised): FAIL, 5 blocking
  + 3 minor. All 8 accepted. Ledger: (1, blocking) the "(N=3)" cell is
  really 14 executions (4xN=3 + 2 scout xN=1) and the exact run command
  is unrecorded; (2, blocking) provenance-delta table omits required
  fields; (3, blocking) the 65.4% aggregate had no stated formula and
  reconstructs to 58.7/65.4/67.7% by estimator; (4, blocking) the S8
  "confirmation" states no tolerance and compares a 14-exec SSE
  population against S8's 18-exec Phoenix population three days apart,
  with S8's six kill-truncated executions biasing it low; (5, blocking)
  "invariant to model drift" holds per-wait but not per-aggregate-share;
  (6, minor) `by_tool.keystrokes` completeness is not proven by
  `sse_missing=0`; (7, minor) "ground-truth before-number" overstates a
  sampled estimate; (8, minor) the card Scope/Deliverable still named the
  S16 sre-hard cell after the option-A rescope. Superseding revision
  written:
  [2026-07-14-s26-aggregation-revision.md](../evidence/2026-07-14-s26-aggregation-revision.md)
  (states the wall-weighted formula, reframes 65.4% as a 14-execution
  sampled estimate in a 59-68% band, completes the provenance table as
  far as local data allows, reframes the S8 comparison as a 2.8-point raw
  gap on confounded populations with no tolerance claim, corrects the
  invariance claim, adds the numerator caveat, and lays out the two S19
  paths). Finding 8 repaired here:
  Scope and Deliverable updated to the resolved TerminalBench cell. S26
  stays In Progress: the number is now honest but not Done; the open user
  decision at Gate U is whether S19 pre-registers against the caveated
  sampled estimate, or a balanced N=3 top-up run is filed as a separate
  user-gated card.
- 2026-07-14 Drift fix (board-owner session, pre-Gate-D). Gate U
  (launch) box checked: it was granted in-log 2026-07-12 for the full
  cell. The open user decision is the baseline-acceptance choice
  embedded in Gate M (accept the caveated 65.4 percent sampled estimate
  as S19's before-baseline, or file a balanced N=3 top-up as a separate
  user-gated card), not a second Gate U. Frontmatter `user-gates`
  updated to `[launch, baseline]` to name both user decisions.
- 2026-07-14 Gate D drift audit (codex GPT-5.6, read-only). Findings
  D3-D6 blocking, D7-D8 minor. D4: the 2026-07-12 "Gate S: vale-clean"
  log line applied to the original evidence file; the 2026-07-14
  superseding revision rewrites that file, reopening Gate S. Re-passed:
  `vale 2026-07-14-s26-aggregation-revision.md` is clean (0 errors).
  Gate S box checked. D5: the baseline-acceptance user decision had no
  home in the gate checklist; the log called it both "Gate U" and
  "embedded in Gate M, not a second Gate U." Fixed: frontmatter gates
  string updated to `S -> A -> U(launch) -> M -> U(baseline)`, a
  distinct `U(baseline)` checkbox added after Gate M. The baseline
  gate fires after Gate A re-passes on the revision and Gate M reports.
  D3 logged as divergence (below). D6 repaired in the evidence file.
  D7 (S7 stale anchor) and D8 (REVIEW-TOOLING packet-command gap) are
  minor, logged for a future sweep. D1 (worktree on card/S3 not
  primary) is already logged on S3:75. D2 (wiki SHA stale in
  PROCESS.md:70) is cosmetic.

  Divergence D3: the four S26 run catalogs and the driver log
  (`runs/driver-s26-full-20260712-133311.log`) are on notanton, not
  synced to this worktree. The card and evidence file reference them
  as locally auditable, but they are not. The 65.4 percent number
  recomputes from the evidence file's per-task table, but the raw SSE
  and Phoenix cross-check cannot be sampled locally. Acceptance: pull
  the catalogs and driver log from notanton before S19 pre-registers,
  or log a user waiver that the remote-only evidence is accepted.
- 2026-07-14 Gate A re-run (codex GPT-5.6, two rounds). Round 1: FAIL,
  2 blocking. (1) provenance table reported worker turn depth as 6
  (coordinator depth, not worker depths); repaired to analyst 24,
  operator 24, debugger 30, verifier 16. (2) S8 truncation section
  claimed "keystrokes spans are understated" and correction "would
  raise" S8's share, but S8's limitations note says lost-tail
  composition is unknowable; repaired to "tool and LLM spans are
  collectively understated" with unknowable composition. Non-blocking
  recs applied: share column labeled "mean share (execution-level)",
  duration_ms clarified as whole-call elapsed time with S8's
  7,976/7,992s wait-versus-span proxy cited. Round 2 re-check: PASS,
  both findings RESOLVED, no new issues. Gate A box checked.   Remaining
  gates: Gate M (provenance-delta table against S8, run command
  recovery from notanton) and Gate U (baseline acceptance).
- 2026-07-14 Evidence recovery from notanton (board-owner session).
  Pulled all four S26 run dirs (scout + 3 full), both driver logs,
  four provenance receipts, and four canary receipts via SSH/tar.
  Cataloged and parsed all four runs locally (scout: 2/2 SSE, 0
  parse errors; full-1: 4/4 SSE, 0 parse errors; full-2: 4/4 SSE, 0
  parse errors; full-3: 4/4 SSE, 0 parse errors). Recovered CPU arch
  (x86_64, AMD Ryzen 9 7950X, KVM) from provenance receipt and
  `/proc/cpuinfo`. Run command confirmed from driver log: four tasks
  at N=3 plus 2-task scout at N=1, all on the sre-shell-orchestrated
  cell. Evidence revision updated: RECOVER fields filled, D3
  divergence resolved (catalogs and driver log now local). Gate M
  provenance-delta table is now locally auditable. Remaining for Gate
  M: the same-run Phoenix-versus-SSE cross-check from the catalogs.
  Remaining for Gate U (baseline): user decision on 65.4 percent.
- 2026-07-14 Gate U (baseline) ACCEPTED. User accepted the caveated
  65.4 percent sampled estimate (59-68 percent band) as S19's
  pre-registered before-baseline. No N=3 top-up run filed. Gate M's
  same-run Phoenix-versus-SSE cross-check remains as a deferred
  follow-up; the user accepted the baseline with that item open.
  S26 Done.
