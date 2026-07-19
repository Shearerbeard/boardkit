---
id: S32
title: Turn-limit nudge benchmark variable (PR 380)
status: backlog
depends: [MILESTONE]
serialize-with: []
lineage: none
executor: smart
gates: "scope at promotion -> S -> U(launch) -> M -> U(baseline)"
user-gates: [launch, baseline]
---

# S32: Turn-limit nudge benchmark variable (PR 380)

Config-only benchmark variable: workers approaching their turn-depth
limit get an in-conversation notice to submit partial results instead
of failing with MaxDepthError and being retasked from zero
(mezmo/aura PR 380, `teriyakichild/turn-limit-nudging`). Mechanics:
[PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md).

## Scope

Adapter repo, `configs/sre-shell-orchestrated-nudge.toml` only. The
config was verified byte-identical to the baseline
`configs/sre-shell-orchestrated.toml` outside the two `[agent]` keys
`nudge_last_turn = true` and `nudge_turns_remaining = 3` (Fable
vetting session, 2026-07-17), so a run of this file isolates the
nudge feature as the single variable.

## Deliverable

An N=3 comparison of the nudge config against the accepted baseline
cell under the standing quality gates, with a provenance-delta table
per the Gate M comparison-validity rule.

## Acceptance

Written at promotion. Standing preconditions the promotion scope must
carry:

- The launch binary demonstrably includes PR 380 (the `[agent]` nudge
  keys are silently inert on an older binary; provenance must pin a
  sha that contains the feature).
- The one-variable rule: no other prompt, config, or
  `max_planning_cycles` change rides along.
- Trace-receipt canary or an explicit user waiver, per the standing
  user gates.

## Gate checklist

- [ ] Scope at promotion: launch binary sha with PR 380, comparison
      targets, and pre-registered metrics written on this card.
- [ ] Gate S: config diff re-verified against baseline (two keys
      only); `--strict-readiness` provenance fresh.
- [ ] Gate U (launch): provenance, canary, pre-registered metrics.
- [ ] Gate M: N=3 trace-complete comparison with provenance-delta
      table.
- [ ] Gate U (baseline): accept or reject; the decision is the
      user's only.

## Branch

Adapter repo, direct (config plus card only); shas recorded here at
Done.

## Log

- 2026-07-17 Filed by the Fable vetting session. The config appeared
  untracked in the adapter working tree (created 03:03 local,
  provenance outside the GLM board session); content vetted as
  baseline-identical outside the two nudge keys and committed under
  this card per the user's disposition decision.
- 2026-07-17 Parked scoring data landed (detached Opus/Claude Code
  session on the Nobara host, outside the gated loop): N=3 nudge-on vs
  nudge-off control on the same PR 380 binary (commit `b4d44c13`, sha256
  `02c096d4...`), so the only variable is the two nudge keys. Scores
  10/18 vs 9/18, all reps trace-complete. Central finding: the nudge
  fired ZERO times and no worker hit `MaxDepthError`; worker `turn_depth`
  ceilings (24/24/30/16) sit far above the ~9 tool-calls/dispatch these
  tasks reach, so the feature is inert on this cell plus config and the
  resolved-rate delta is task variance, not a nudge effect. Evidence and
  full mechanism analysis:
  [2026-07-17-s32-nudge-n3-notanton.md](../evidence/2026-07-17-s32-nudge-n3-notanton.md).
  Re-scope implication for this card: to make the nudge a live variable,
  a future variant must lower worker `turn_depth` (~10) in both cells;
  as configured the variable measures nothing. Card stays backlog; this
  is parked evidence, not a gate pass (the run did not pass through this
  card's U(launch), M, or U(baseline) gates).
