---
id: S22
title: R9 goal-directed dag queries with Mermaid renders
status: in-review
depends: [S13, S19]
serialize-with: []
lineage: primary
commit-range: d059160..85ab722
executor: smart
gates: "S -> A -> U(code-review)"
user-gates: [code-review]
---

# S22: R9 goal-directed dag queries with Mermaid renders

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Drain record:
[2026-08-09-feedback-drain-7.md](../../plans/2026-08-09-feedback-drain-7.md)
(part (c) of the dotdir entry). The ruling is RULE-4 of the aura plan of
record; gates-on-edges is interview-accepted elaboration.

## Scope

A new `src/boardkit/dag.py`, `src/boardkit/cli.py` (the `dag`
command), `src/boardkit/board.py` (the standing `graph.md` view),
docs, tests.

## Deliverable

`boardkit dag --to <id>` answers over the CardStore with stdlib
traversal (`graphlib`). Its output has four parts: the goal's ancestor
closure, its unblocked frontier, a wave partition over the closure, and
which gates sit on which edges (an edge's gate annotation is the tail
card's remaining gate ladder, so a wave plan shows where reviews land,
not just order). File-backed,
in-process, no daemon, no external graph store; SQLite stays a
documented escape hatch only.

Render surfaces: a standing generated `graph.md` (Mermaid, status
colors, lane subgraph clusters from S19) written and drift-checked with
the other views, and `dag --to <id> --render` emitting a goal-scoped
Mermaid wave plan as the agent-to-user artifact.

INCOMPLETENESS RULE (from the plan of record): this card ships lane
clusters only, and R9 is not recorded complete until a post-R2 pass
adds epic clustering and `--to <epic>`. That pass extends this card's
log or a successor card; Gate B records R9 as shipped-incomplete
either way.

## Acceptance

- `uv run pytest -q` green; tests cover ancestor closure, frontier,
  wave partition on a fixture DAG, gate-on-edge annotation, and
  graph.md drift detection.
- `boardkit dag --to S20` on this board names S18 in the closure and
  partitions S13 ahead of it.
- `graph.md` regenerates with `render`, and `check` fails when it
  drifts.

## Gate checklist

- [x] Gate S: load skill `gate-probes`, then `uv run pytest -q`,
  `uv run ruff check`, `vale` on touched markdown.
- [ ] Gate A: adversarial review, focus: does the wave partition
  mislead (serialize-with pairs landing in one wave, done cards in the
  closure, gate annotations claiming a passed gate still blocks)?
- [ ] Gate U (code-review): present the review packet; stop.

## Branch

direct

## Log

- 2026-08-09 Minted by the seventh feedback drain from part (c) of the
  dotdir entry, gates-on-edges accepted at the interview, epic
  clustering explicitly deferred to the post-R2 pass.
- 2026-08-09 Pulled in-progress straight from backlog (S13/S19
  in-review, same-hand build order per drain 7); executor is the
  maintainer session.
- 2026-08-09 Built: `dag.py` (ancestor closure, unblocked frontier,
  longest-path wave partition over remaining work, gates-on-edges as
  the tail's unticked ladder letters via the new
  `board.remaining_gates`); `boardkit dag --to <id>` text output and
  `--render` Mermaid wave plan; standing `graph.md` view (status
  colors, lane subgraph clusters, depends arrows, dotted
  serialize-with links) rendered and drift-checked with the other
  views; `gate_tokens` moved to board.py so brief/doctor/dag share
  one parser. Gate S PASS: 322 pytest green (6 dag tests; golden
  fixture gains a frozen first-render graph.md with its provenance
  noted), ruff clean.
- 2026-08-09 Acceptance run: `dag --to S20` names S18 in the closure
  and partitions S13 ahead (waves S13 -> S18 -> S20, edges annotated
  A,U); graph.md drift fails check via the standard view machinery.
- 2026-08-09 R9 recorded SHIPPED-INCOMPLETE per the plan of record:
  lane clusters only; epic clustering and `--to <epic>` land at the
  post-R2 pass.
- 2026-08-09 In-review; commit-range d059160..85ab722.
- 2026-08-09 Gate A deferred, superseded 2026-08-16: adversarial reviews batch at the
  Session B boundary; packets present at the Gate B user gate.
- 2026-08-09 Post-R2 epic pass landed in S23's commit (epic clusters
  in graph.md, `dag --to <epic>` member-union closure). R9 is now
  COMPLETE; the shipped-incomplete marker above is closed.
- 2026-08-16 Gate A ran (resolving the deferral): reviewer gpt-5.6-sol
  via codex exec, author claude-fable-5 (whole wave); codex fallback
  after the opencode lane stalled its read probe. Verdict FAIL, three
  BLOCKING findings and one MINOR.
  1. BLOCKING waves considered dependency edges only, so a reciprocal
     serialize-with pair landed in one dispatchable wave against the
     board mutex. Confirmed. Fixed in 6af06a7: the partition splits
     mutex pairs, deferring the later-sorted member and dragging any
     same-wave dependent down with it. The unblocked frontier stays
     dependency-only by its documented meaning; the wave plan is where
     dispatchability is claimed, and it now tells the truth.
  2. BLOCKING gate state collapsed by letter, so a passed U(mockup)
     still annotated edges as an open U beside U(launch). Confirmed
     (the S16 review hit the absorption half of the same defect). Fixed
     in 6af06a7: qualified occurrences track independently; views,
     canary key, and edge annotations share the computation.
  3. BLOCKING the graph drift test never perturbed graph.md. Confirmed.
     Fixed in 6af06a7: the test writes the views, tampers graph.md, and
     asserts the drift check names it.
  4. MINOR the deliverable names stdlib graphlib and the traversal was
     custom. Fixed in 6af06a7 rather than amended: the wave partition
     now runs on graphlib.TopologicalSorter batches; the closure stays
     a plain reachability walk, which graphlib does not provide.
  Reviewer-reported UNVERIFIED (sandbox): the acceptance suite, lint,
  board checks, Mermaid render - run board-owner-side: 355 pytest
  green and ruff clean; boardkit check OK. Fix commit 6af06a7 (shared
  with S23/S24, per-card trailers) sits apart from the reviewed range,
  so commit-range stays d059160..85ab722 and the fix-commit re-review
  runs over 6af06a7^..6af06a7 via the packet override; Gate A's box
  stays unticked until that re-review passes.
- 2026-08-16 Gate A review cycle closed by ruling; full round ledger in
  [2026-08-16-gate-a-review-cycle.md](../evidence/2026-08-16-gate-a-review-cycle.md).
  Rounds 2 to 5 re-reviewed the fix commits. Round 5 confirms every
  recorded fix and every round-4 residue resolved; from round 3 on, the
  findings were confined to `_is_shim` in the S24 fix code, one narrower
  evasion per round, and that hardening is carded as S29 rather than
  patched a sixth time. Every finding against this card's own reviewed
  diff is resolved. The reviewer never issued an explicit sign-off, so
  the box stays unticked, because a failed return is never a pass. The
  2026-08-09 batch deferral is superseded - the batch ran, on the codex
  fallback after the opencode lane failed its read probe four times.
- 2026-08-16 Gate A open: deferred (review cycle closed by ruling after five
  rounds with every card-diff finding resolved and no explicit reviewer
  sign-off; the pass decision is the user's at U code-review, on the ledger
  in docs/board/evidence/2026-08-16-gate-a-review-cycle.md)
