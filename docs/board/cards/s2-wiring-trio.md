---
id: S2
title: Wire pre-vet, deferrals, and packet staging into the CLI
status: ready
depends: []
serialize-with: []
lineage: primary
executor: smart
gates: "S -> A"
user-gates: []
---

# S2: Wire pre-vet, deferrals, and packet staging into the CLI

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Plan:
[2026-08-04-productionize-verification.md](../../plans/2026-08-04-productionize-verification.md),
stage 2.

## Scope

`src/boardkit/cli.py`, `src/boardkit/contract.py`,
`src/boardkit/board.py`, `src/boardkit/review_packet.py`, new module(s)
under `src/boardkit/`, tests. No template prose changes beyond pointing
existing recipes at the new commands.

## Deliverable

Three subcommands whose inputs boardkit already holds:

1. `boardkit pre-vet <role>`: generate a nonce, stage it per the
   resolved route's staging contract, print the probe prompt, and
   verify a pasted readback. Replaces the echo probe.
2. `boardkit deferrals`: the open-deferral sweep board-hygiene
   currently does with a raw grep plus hand filtering, computed from
   `deferred_gates()`.
3. `boardkit stage-packet <card-id> --route <name>`: materialize the
   review packet into the transport's working directory per the
   route's staging contract, printing the staged paths for the prompt.

The kit still never executes a delegation: these commands stage, sweep,
and verify, and stop at the boundary `contract.py` draws for preflights.

## Acceptance

- `uv run pytest -q` green with new tests per subcommand, including a
  crossed-staging-contract refusal case.
- `boardkit deferrals` output matches the hand-filtered grep on the
  golden fixture board.
- board-hygiene and the REVIEW-TOOLING template name the commands where
  their prose recipes stood.

## Gate checklist

- [ ] Gate S: `uv run pytest -q`, `uv run ruff check`, `vale` on touched
  markdown.
- [ ] Gate A: adversarial review, focus: does any new command cross into
  executing repo-configured commands, and is staging crash-safe?

## Branch

direct

## Log

- 2026-08-04 Authored from the boardkit machinery audit (wiring items 1,
  2, 7).
