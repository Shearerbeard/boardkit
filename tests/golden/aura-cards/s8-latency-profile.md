---
id: S8
title: Latency profile investigation
status: done
depends: []
serialize-with: []
lineage: none
executor: smart
gates: "S -> A"
user-gates: []
---

# S8: Latency profile investigation

Plan section: Stage 4 (S8 bullet) in
[2026-07-11-orchestration-redesign.md](../plans/2026-07-11-orchestration-redesign.md).
Mechanics: [PROCESS.md](../PROCESS.md). Required reading:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md).

## Scope

Investigation, no code: Phoenix span analysis of an orchestrated run,
written up as one dated evidence file in `docs/redesign/evidence/`.
Fix candidates become new cards, not edits under this one.

## Deliverable

A dated evidence file that breaks an orchestrated run's wall clock
into Phoenix span buckets and names the top latency contributors with
spans cited. Named suspects to measure: whether Bedrock calls use
prompt caching (the re-rendered continuation defeats prefix caching,
per the web finding), the no-backoff planning retry
(orchestrator.rs:1463-1470), the serialized `Mutex<Persistence>`
hops, and `per_call_timeout_secs=0`.

## Acceptance

- The evidence file ranks contributors with numbers and cites the
  spans behind each.
- Each named suspect is measured or explicitly ruled out.
- Fix candidates are filed as new cards.

## Gate checklist

- [ ] Gate S: the evidence file is vale-clean.
- [ ] Gate A: fresh-agent review of the measurement method.

## Branch

No branch (no code); the deliverable is a dated evidence file.

## Log

- 2026-07-11 Filed by S0 from the approved plan.
- 2026-07-12 In Progress, pulled in the four-card bolus (WIP-2
  deviation authorized; see S2 log). Feasibility vetted: Phoenix at
  fedora-cube retains all three Nobara baseline runs (verified by live
  query), Phoenix 6/6 on each, and all four named suspects confirmed at
  their cited lines. Scope disposition: the dump scripts fetch
  startTime only, so `scripts/dump_all_traces.py` gets an
  endTime/latencyMs query extension; that is adapter measurement
  tooling, not Aura code, so the card's no-code rule holds. Spans are
  snapshotted to disk before analysis against the retention risk.
  Mutex-persistence and retry-backoff suspects are bounded indirectly
  via span gaps; the evidence file names that limitation.
- 2026-07-12 In Review. Evidence delivered:
  `evidence/2026-07-12-s8-latency-profile.md` (vale clean), raw span
  snapshots under `runs/s8-span-snapshots/` (gitignored, cited by the
  file). Headline: 62.6 percent of wall clock is model-requested
  keystrokes blind sleep (7,976s over 436 calls; the 60s-plus tail is
  38.0 percent of wall); worker LLM streaming 26.2 percent; planning
  6.6 percent; explicit orchestration residue 0.7s. All four suspects
  verdicted (retry: no occurrence detected; Mutex: bounded under 0.5s
  where visible, within-turn blind spot named; timeout: unbounded
  confirmed, worst completed call 105.6s; caching: absent, idealized
  3.64x worker token model with assumptions stated). Gate A round 1:
  the method reviewer independently recomputed all 18 task rows and
  signed off with 5 minor prose findings; codex found 6 blocking
  overclaim/citation issues; a repair pass fixed every blocking and
  minor except card filing, and the board owner then re-verified vale,
  the 2-line script diff, and independently recomputed the 7,976s/436
  headline from the raw snapshots. Fix candidates filed as cards
  S19-S23 by the board owner, completing the last codex finding.
  Done flip awaits morning ratification.
- 2026-07-12 Done. User ratified the profile at morning ratification;
  no decisions outstanding. Fix candidates S19-S23 carry the
  follow-up work (S19 keystrokes bounding is the largest lever). The
  user also opened a re-measure follow-up: now that the SSE stream
  emits `duration_ms` upstream, re-profile the sre-hard cell from SSE
  ground truth to validate the 62.6 percent keystrokes-sleep headline
  and give S19 a precise before/after. Filed as S25 (parser) and S26
  (re-measure).
