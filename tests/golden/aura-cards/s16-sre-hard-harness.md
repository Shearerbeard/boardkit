---
id: S16
title: sre-hard regression harness
status: done
depends: []
serialize-with: []
lineage: none
executor: smart
gates: "S -> A"
user-gates: []
---

# S16: sre-hard regression harness

Plan section: Stage 4 in
[2026-07-11-orchestration-redesign.md](../plans/2026-07-11-orchestration-redesign.md).
Mechanics: [PROCESS.md](../PROCESS.md). Required reading:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md).

## Scope

Adapter and ai-experiments repos; no Aura code. Make the
ai-experiments sre-hard benchmark repeatable against an experiment
binary. Scoped small; no code dependencies, so it may run early,
parallel with Stage 3. Needed before the Track A milestone gate.

## Deliverable

The reference score at `9df96382`, the exact run command, pass
criteria (what counts as a regression), and where results land. If
the suite turns out heavyweight, the card proposes a subset with the
user instead.

## Acceptance

- The documented command reproduces the reference score at
  `9df96382`.
- Pass criteria and the results location are written down. After
  this card, the Track A milestone and every behavior-card baseline
  gate run the sre-hard check alongside the TerminalBench
  comparison.

## Gate checklist

- [ ] Gate S: the documented command reproduces the reference score.
- [ ] Gate A: fresh-agent review of the command, pass criteria, and
      results location.

## Branch

Adapter repo, direct; no Aura code.

## Log

- 2026-07-11 Filed by S0 from the approved plan.
- 2026-07-12 In Progress, pulled in the four-card bolus (WIP-2
  deviation authorized; see S2 log). Scoping vetted: the harness is
  `ai-experiments/aura-e2e/run-sre-hard-e2e.sh` plus
  `uv run aura-eval <dir> --prompt-set sre-hard --skip-scratchpad`,
  5 prompts per iteration (~15-25 min), binary-targetable via BINARY=.
  No reference score exists at `9df96382`; establishing it is this
  card's work. Reference cell user-decided: gpt-5.2 config
  (`configs/sre/sre-hard-e2e-gpt52.toml`), N=3 (matches the 221-epic
  x3 practice), Mac host (full scorer tooling). Results go to fresh
  directories; the dirty `results-index.json` and untracked reports in
  the ai-experiments clone are not touched. Not heavyweight, so the
  card's subset-negotiation clause is unneeded.
- 2026-07-12 In Review. Reference established at N=3 against binary
  `1e471f4e` (Mac build of `9df96382`, sha matches the W15a-era
  record), config `bf3c8b8b`, harness ai-experiments `751fdc2`:
  quality 25/26, 22/26, 26/26 (band 22-26, median 25); diagnostic
  42/42, 42/42, 41/42. Config validated against the binary with zero
  API spend before the x3. Evidence:
  `evidence/2026-07-12-s16-sre-hard-reference.md` (vale clean) with
  the executable floor rule (any iteration under 22/26 blocks), the
  second-x3 escalation rule, the diagnostic consumption rule, and the
  exit-code caveat (gate on the printed score line, not exit codes).
  Gate S verified by the board owner directly: re-ran aura-eval on
  run 3 and reproduced 26/26 and 41/42 exactly; binary sha
  re-checked. Gate A: fresh reviewer signed off after re-deriving run
  2 and both shas (two minors, applied or noted); codex found five
  blocking precision gaps in the pass-criterion logic (no terminal
  rule for the second x3, unpinned harness, diagnostic-consumption
  ambiguity, two overgeneralizations), all repaired by the board
  owner in the evidence file. One iteration's run-2 watcher died
  silently during execution; the run itself was validated complete
  and double-scored identically before counting. Done flip awaits
  morning ratification.
- 2026-07-12 Done. User ratified the reference cell at morning
  ratification. The pinned-binary scores (quality band 22-26, median
  25; diagnostic 41-42/42) and the pass-criterion rules stand as the
  sre-hard regression reference for the Track A milestone and every
  behavior-card baseline gate. S26 will re-run this same cell with
  timing-SSE capture to co-measure latency.
