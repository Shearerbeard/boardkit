---
id: S23
title: R2 epic cards and epic membership
status: done
depends: []
serialize-with: []
lineage: primary
commit-range: 85ab722..22bd55c
executor: smart
gates: "S -> A -> U(code-review)"
user-gates: [code-review]
---

# S23: R2 epic cards and epic membership

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Drain record:
[2026-08-09-feedback-drain-7.md](../../plans/2026-08-09-feedback-drain-7.md)
(same-sitting mints, interview decision 7); requirement R2 in the aura
requirements doc, evidence: the aura-agent-driver epic spans three
surfaces while existing on none, and the 2026-08-04 hitl/webhook
consolidation discovered late that two boards were one initiative.

## Scope

`src/boardkit/board.py` (the `kind:` and `epic:` keys, validation,
rollup rendering), `src/boardkit/data/templates/PROCESS.md`,
`docs/board/PROCESS.md`, `_template.md` (schema prose), tests.

## Deliverable

An epic is itself a card: optional `kind:` frontmatter, `card` when
absent, `epic` for epic cards. Member cards carry an optional
`epic: <id>` validated against an existing same-board epic card. An
epic card holds the initiative's goal prose and may carry gates like
any card; per the plan of record, the aura A5 epic card gains its
`epic:`-related keys only after this ships. Views gain a per-epic
rollup: which cards serve which initiative, answered mechanically.
Build order per the plan of record: this card lands last in the
Session B wave, and its landing unblocks the R9 epic-cluster pass on
S22.

## Acceptance

- `uv run pytest -q` green; tests cover kind validation, epic refs to
  missing or non-epic cards failing, and the rollup rendering.
- A fixture board with one epic and two member cards renders a rollup
  naming both members; a member naming a plain card as its epic fails
  `check`.
- The schema prose in the shipped template and this board's PROCESS
  copy agree.

## Gate checklist

- [x] Gate S: load skill `gate-probes`, then `uv run pytest -q`,
  `uv run ruff check`, `vale` on touched markdown.
- [x] Gate A: adversarial review, focus: epic cycles (an epic member of
  itself or of another epic), status semantics of an epic card with
  open members.
- [x] Gate U (code-review): present the review packet; stop.

## Branch

direct

## Log

- 2026-08-09 Minted by the seventh feedback drain from standing
  requirement R2, epic-card shape chosen at the interview.
- 2026-08-09 Pulled in-progress; executor is the maintainer session.
- 2026-08-09 Built: `kind: epic` cards and validated `epic:` membership
  (target must exist and be an epic; an epic may not be a member, so
  nesting and cycles are unrepresentable); per-epic rollup section in
  INDEX with member roster and done count; schema prose in both
  PROCESS and both _template copies. The same commit carries the
  post-R2 R9 pass: epic subgraph clusters in graph.md (epic wins over
  lane for members - Mermaid subgraphs cannot overlap and the epic is
  what a wayfinding reader traces) and `dag --to <epic>` closing over
  the members' union. Gate S PASS: 329 pytest green (7 epic tests),
  ruff clean, vale clean.
- 2026-08-09 In-review; commit-range 85ab722..22bd55c.
- 2026-08-09 Gate A deferred, superseded 2026-08-16: adversarial reviews batch at the
  Session B boundary; packets present at the Gate B user gate.
- 2026-08-16 Gate A ran (resolving the deferral): reviewer gpt-5.6-sol
  via codex exec, author claude-fable-5 (whole wave); codex fallback
  after the opencode lane stalled its read probe. Verdict FAIL, two
  findings.
  1. BLOCKING `kind: [epic]` - valid YAML - raised a TypeError from
     hashing a list instead of a structured BoardError. Confirmed.
     Fixed in 6af06a7: non-string kinds join the must-be-one-of
     refusal, with the regression test the reviewer noted missing.
  2. BLOCKING an epic could sit done with open members, while the dag
     closure rule says finishing an epic means finishing its members -
     the initiative rendered complete and incomplete at once.
     Confirmed. Fixed in 6af06a7 by enforcement: check refuses a done
     epic with open members, naming them.
  Reviewer-reported UNVERIFIED (sandbox): pytest and the board
  commands - run board-owner-side: 355 pytest green and ruff clean;
  boardkit check OK. Fix commit 6af06a7 (shared with S22/S24, per-card
  trailers) sits apart from the reviewed range, so commit-range stays
  85ab722..22bd55c and the fix-commit re-review runs over
  6af06a7^..6af06a7 via the packet override; Gate A's box stays
  unticked until that re-review passes.
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
- 2026-08-22 Gate A PASS: Mike accepted the R-wave on the 2026-08-16
  ruling record at the wave-2 Gate U (runbook and packet-companion
  artifacts), per ruling point 5. The box ticks on that acceptance,
  resolving the 2026-08-16 deferral. Board-side re-check at close:
  pytest green, ruff clean, boardkit check clean.
- 2026-08-22 Gate U(code-review) passed: Mike approved the batched
  R-wave packets at the wave-2 Gate U with the packet companion; his
  design-read stands as the substance per wave-2 decision 1.
- 2026-08-22 Done: every gate passed. Verified by Mike's Gate U
  approval and the board owner's re-run of the deterministic checks
  at close.
