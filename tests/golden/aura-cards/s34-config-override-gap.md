---
id: S34
title: No config-path override in AuraOrchestratedAgent
status: backlog
depends: []
serialize-with: []
lineage: none
executor: any
gates: "S -> A -> U(run-decision)"
user-gates: [run-decision]
---

# S34: No config-path override in AuraOrchestratedAgent

Fix candidate filed from the S33 fan-out+nudge N=3 run
([2026-07-17-s33-fanout-nudge-n3-notanton.md](../evidence/2026-07-17-s33-fanout-nudge-n3-notanton.md)).
Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md).

## Scope

`aura_terminalbench/agent.py`: `_AuraAgentBase` reads `config_path =
CONFIGS_DIR / self._CONFIG_FILENAME`, where `_CONFIG_FILENAME` is a
hardcoded class attribute (`AuraOrchestratedAgent` = always
`sre-shell-orchestrated.toml`, `AuraSingleAgent` = always
`terminalbench-single.toml`). There is no `-k config_path=...` kwarg,
environment variable, or per-run override. Running any alternate config
through `tb run --agent-import-path aura_terminalbench:AuraOrchestratedAgent`
today requires physically overwriting the live file at that fixed path
for the run's duration, then restoring it, since there's no other way in.

This has already happened twice outside the gated loop (S32's and S33's
detached scoring sessions both needed a checksummed swap/restore of
`configs/sre-shell-orchestrated.toml`). It works, but it's a real
liability: a run that's interrupted mid-swap (crash, killed session,
dropped SSH) can leave the tracked baseline config silently replaced by
whatever variant was being tested, with no automated signal that it
happened.

## Deliverable

A `-k config_filename=...` kwarg (or equivalent) on `_AuraAgentBase` /
`AuraOrchestratedAgent`, defaulting to the current hardcoded filename
when unset, so `tb run` invocations can select a config without touching
the live file at all. Update `scripts/remote/nobara-launch.sh` (and its
forwarded-var list) and `scripts/trace-verified-benchmark.sh` to pass it
through alongside `BINARY`, `AURA_SOURCE_ROOT`, etc.

## Acceptance

- A `tb run` invocation can select `configs/sre-shell-orchestrated-nudge.toml`
  (or any other file in `configs/`) via kwarg/env without modifying
  `configs/sre-shell-orchestrated.toml`.
- Existing behavior with no override set is unchanged (still resolves to
  today's hardcoded filenames).
- `nobara-launch.sh` forwards the new var; its `--help` documents it.
- Unit test covering the override path in `agent.py`.

## Gate checklist

- [ ] Gate S: adapter unit tests, `nobara-launch.sh` help text updated.
- [ ] Gate A: fresh-agent diff review.
- [ ] Gate U (run-decision): user decides whether a verification run is
      needed before this joins the accepted head.

## Branch

Local branch `card/S34` off the accepted head; no pushes before gates
pass; commit range recorded here at Done.

## Log

- 2026-07-17 Filed as backlog from the S33 fan-out+nudge N=3 run, which
  needed a manual checksummed config swap/restore to work around this
  gap.
