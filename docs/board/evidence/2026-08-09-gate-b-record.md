# Gate B record - Session B of the board-consolidation plan (2026-08-09)

Plan of record:
`aura-session-docs/reports/board-consolidation-plan-of-record-2026-08-09.md`.
Drain record: [2026-08-09-feedback-drain-7.md](../../plans/2026-08-09-feedback-drain-7.md)
(carries the eight in-session interview decisions). This file is the
record Gate B requires: exactly which R-items shipped, because Session
C's steps have per-item dependencies.

## R-items shipped, with their commits

| Item | Card | Work commit | State |
|---|---|---|---|
| R5' `.boardkit` resolution + common-dir fallback + CardStore seam | S13 | deb9c2b | shipped |
| R4 registry (manifest-is-registry) + `boardkit boards` | S18 | bb2d0f8 | shipped |
| R1 lanes (vocabulary, per-lane WIP, exempt lanes, view grouping) | S19 | 62e5ea1 | shipped |
| R10 charters (views, briefs, owns-mirror, route validation; bk dogfood) | S20 | 62e5ea1 | shipped |
| R3 qualified cross-board refs (informational, registry-resolved) | S21 | d059160 | shipped |
| R9 dag queries + `graph.md` (gates-on-edges included) | S22 | 85ab722 + 22bd55c | shipped COMPLETE |
| R2 epic cards + membership + rollup | S23 | 22bd55c | shipped |
| R6/R7 doctor (host hazards; harness parity) | S24 | 028ce5d | shipped |
| R8 title-hash truncation refusal | S25 | a95fcab | shipped |
| S16 gate position in views (ride-along, interview decision 8) | S16 | 5211b1b | shipped |

R9 completeness: the plan of record required R9 to stay recorded
incomplete until a post-R2 pass added epic clustering. R2 (S23) landed in
this sitting and its commit carries that pass (epic subgraphs in
`graph.md`, `dag --to <epic>` member-union closure), so R9 closes
COMPLETE at Gate B, not shipped-incomplete.

Not shipped, by design: S26 (rust-holes HOLES ledger, drained and carded,
out of Session B scope), S27 (architecture flowchart, backlog until the
post-wave architecture settles), S15's retention-contract docs fold (rides
S15's own pull). CardStore `put` is deferred on S13's log (no caller, no
format-preserving serialization).

## Gate B exit criteria

1. `boardkit boards` answers from the registry: run in this repo it
   enumerates bk (default, reachable) and aura (external, overlay-pending)
   from `.boardkit/manifest.toml` alone; `--json` carries stable fields.
2. bk dogfood check passes: `boardkit check` exits 0 with the charter
   rendered atop the views, the registry row verified against this
   board's config, and the charter route target resolving to the aura
   row. `boardkit doctor`: 19 passed, 0 errors (one warning:
   host.tree-state, this session's own close-out diff).
3. Cross-board resolution test, defined and green:
   `tests/test_resolution.py::test_cross_board_resolution_lands_each_code_on_its_own_config`
   (one manifest, two boards; each short-code resolves to its own
   `boardkit.toml`; the default lands on the manifest's named board).

## Gate state on the cards

All ten cards sit at `status: in-review` with commit ranges set and
review packets generated (`docs/board/reviews/S13 ... S25`). Gate S
passed and is logged per card. Gate A is OPEN-DEFERRED on every card,
logged with the batch reason; the deferred view lists all ten. The
U(code-review) standing gate is where Mike receives the packets; no card
reaches `done` until its Gate A runs (reviewer-differs-from-author
holds: the whole wave was authored by the maintainer session's model, so
the batch reviews route to the opencode/codex lanes) and Mike's
code-review gate passes.

## What this unblocks (Session C dependency map)

- C1 (aura manifests + overlays, worktree fallback verification): needs
  R5' - UNBLOCKED.
- C2 (remove the nine aura-family symlinks): needs R5' after C1 -
  UNBLOCKED.
- C3 (agent-driver repo-local board + charters, aura charter in the
  wiki): needs R5' AND R10 - UNBLOCKED.
- Deferred aura-board initiative structuring: needs R1/R2 - UNBLOCKED
  (its own session after Gate B, per the plan of record).

## Canary

Orientation canary record: see the closing handoff and
[2026-08-09-gate-b-canary.md](2026-08-09-gate-b-canary.md) (key, verbatim
answers, graded verdict).
