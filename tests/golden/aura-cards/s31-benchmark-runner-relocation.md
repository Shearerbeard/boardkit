---
id: S31
title: Record benchmark-runner relocation to aura-bench-runner
status: done
depends: []
serialize-with: []
lineage: none
executor: any
gates: "S -> A"
user-gates: []
---

# S31: Record benchmark-runner relocation to aura-bench-runner

Plan section: none - filed 2026-07-16 as the tracking card for the
runner-tooling migration. Turnkey spec and full detail:
[2026-07-16-runner-tooling-to-aura-bench-runner.md](../migrations/2026-07-16-runner-tooling-to-aura-bench-runner.md).
Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md).

## Scope

Adapter repo, direct (tracking/record card, no code).

## Deliverable

Durable board pointer to the relocated runner tooling.

## Acceptance

- The runner lives in `~/workspace/aura-bench-runner/`.
- No tracked live file in this repo references the moved runner
  scripts (frozen evidence, archive, and run-journal are intentionally
  left as historical record).
- `cards_index.py --check` passes.

## Gate checklist

- [x] Gate S: migration verified in the migration session - ruff check
      and format clean, full pytest suite (62) passing, vale 0 errors
      on all changed docs, `dump_*.py` fail loud without `PHOENIX_URL`,
      driver re-verified from the new location.
- [x] Gate A: independent context-isolated review of the sanitization
      signed off (`base_url` threaded through every call site,
      fail-loud confirmed); discoverability trace confirmed every
      front-door doc routes a reader to `~/workspace/aura-bench-runner`.

## Branch

Adapter repo, direct (migration commit `3393717` on
`mshearer/coordinator-context-program`).

## Log

- 2026-07-16 Migration executed (commit `3393717`): benchmark runner
  shell tooling (trace-verified driver, resource probe, remote launch
  and status wrappers, per-host env files) moved verbatim to the
  local-only `~/workspace/aura-bench-runner/`; terminalbench-aura is
  now adapter-only and host-neutral. Kept adapter code (`phoenix.py`,
  `trace_receipt.py`, `dump_all_traces.py`, `dump_task_trace.py`) now
  reads endpoints from env (`PHOENIX_URL`,
  `OTEL_EXPORTER_OTLP_ENDPOINT`), required and fail-loud, no baked
  defaults. README, RUNBOOK (slim stub), AGENTS, and scripts/README
  repointed at the runner and de-personalized. Verification: ruff +
  ruff-format clean, 62 pytest pass, vale 0 errors on changed docs,
  independent context-isolated Gate A review signed off, and a
  discoverability trace confirmed front-door docs route to the runner.
  Spec: [migration doc](../migrations/2026-07-16-runner-tooling-to-aura-bench-runner.md).
- 2026-07-16 Board rewiring (this card's own work): card filed as
  done with Gates S and A recorded from the migration session's
  verification; the two dangling script-path references repointed
  (`s26-sre-hard-timing-remeasure.md` lines 108/129,
  `plans/2026-07-11-orchestration-redesign.md` line 95); the migration
  doc's grep confirms no other live card or plan references the moved
  paths. Views regenerated; `cards_index.py --check` passes.
