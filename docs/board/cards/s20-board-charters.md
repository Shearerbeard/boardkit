---
id: S20
title: R10 board charters with the bk dogfood charter
status: done
depends: [S18]
serialize-with: []
lineage: primary
commit-range: bb2d0f8..62e5ea1
executor: smart
gates: "S -> A -> U(code-review)"
user-gates: [code-review]
---

# S20: R10 board charters with the bk dogfood charter

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Drain record:
[2026-08-09-feedback-drain-7.md](../../plans/2026-08-09-feedback-drain-7.md)
(part (d) of the dotdir entry, plus part (e) folded here). The ruling is
RULE-6 of the aura plan of record.

## Scope

`src/boardkit/config.py` (`[charter]` block), `src/boardkit/board.py`
(view header), `src/boardkit/brief.py` (brief injection),
`src/boardkit/data/templates/PROCESS.md` and `docs/board/PROCESS.md`
(charter prose and the one-board-per-family guidance), this repo's
`boardkit.toml` (the bk charter, the dogfood), tests.

## Deliverable

A `[charter]` block in the board-root `boardkit.toml` with `owns`,
`not`, and `route`: `owns` is the one-liner mirrored into the S18
registry row, `not` names what the board refuses, `route` maps refused
work to board short-codes resolvable via the registry. The admission
test is one question: where does the diff land. Charters render at the
top of both generated views and are injected into every dispatch brief.
Enforcement is prose-level in v1; `boardkit check` validates presence
of the three keys and that every `route` target resolves to a registry
short-code, nothing more.

Docs guidance ships beside it (folded part (e)): one board per family;
epics and lanes group initiatives; a new board is justified only by a
different source-of-truth repo or lifecycle owner, because cross-board
refs are informational and splitting coupled initiatives removes their
edges from the schedulable DAG.

bk authors its own charter on this card as the dogfood: owns the kit
family (boardkit, rust-holes, the bench), not consumer-repo process
fixes, routes aura-family work to the wiki board.

## Acceptance

- `uv run pytest -q` green; tests cover charter parsing, the
  route-resolvability check, view-header rendering, and brief
  injection.
- Both generated views of this board open with the bk charter, and
  `boardkit dispatch-brief S19` carries it.
- The shipped PROCESS template and this board's copy state the charter
  schema and the one-board-per-family guidance in the same sections and
  agree.

## Gate checklist

- [x] Gate S: load skill `gate-probes`, then `uv run pytest -q`,
  `uv run ruff check`, `vale` on touched markdown.
- [x] Gate A: adversarial review, focus: can a charter mislead a
  dispatch (route target that resolves but is wrong, owns line drifting
  from the registry mirror)?
- [x] Gate U (code-review): present the review packet; stop.

## Branch

direct

## Log

- 2026-08-09 Minted by the seventh feedback drain from part (d) of the
  dotdir entry, with part (e) folded in and check-level validation
  accepted at the interview.
- 2026-08-09 Pulled in-progress straight from backlog: S18 is in-review
  in the same sitting (same-hand build order per drain 7). Executor is
  the maintainer session.
- 2026-08-09 Built: optional `[charter]` block (owns/not/route) parsed
  strictly; rendered atop INDEX and as a %% comment in board.md so the
  kanban plugin ignores it; injected into every dispatch brief; owns
  mirrored byte-for-byte against the registry row scope (check fails on
  drift); route targets validated against registry short-codes when a
  manifest is reachable, silent when none is (v1 prose-level rule);
  check WARNs on a missing charter. bk dogfood charter authored in
  boardkit.toml with an external aura row added to the manifest so the
  route resolves. One-board-per-family guidance (folded part e) shipped
  in both PROCESS copies. Gate S PASS: 311 pytest green (4 charter
  tests), ruff clean, vale clean incl. the strict template tier.
- 2026-08-09 Acceptance run: generated views open with the bk charter;
  `boardkit dispatch-brief S19` carries the Board charter section; both
  PROCESS copies agree.
- 2026-08-09 Work commit is shared with S19 (both trailers).
- 2026-08-09 In-review; commit-range bb2d0f8..62e5ea1.
- 2026-08-09 Gate A deferred, superseded 2026-08-16: adversarial reviews batch at the
  Session B boundary; packets present at the Gate B user gate.
- 2026-08-16 Gate A ran (resolving the deferral): reviewer gpt-5.6-sol
  via codex exec, author claude-fable-5 (whole wave); codex fallback
  after the opencode lane stalled its read probe. Verdict FAIL, three
  findings.
  1. BLOCKING mirror validation skipped a chartered row whose scope was
     absent, so deleting the mirror passed check. Confirmed. Fixed in
     99cfd4a: absence is drift; the error names the owns line the row
     must mirror.
  2. BLOCKING _parse_charter defaulted a missing route key to empty, so
     a two-key charter loaded clean against the three-key schema.
     Confirmed. Fixed in 99cfd4a: a missing route table is refused; an
     empty [charter.route] stays a legal explicit statement.
  3. BLOCKING the acceptance names brief-injection test coverage and no
     test called build_brief for the charter. Confirmed. Fixed in
     99cfd4a: the brief test asserts owns, not-here, and route lines in
     the generated brief.
  Reviewer-reported UNVERIFIED (sandbox): pytest, ruff, check, doctor -
  run board-owner-side instead: 348 pytest green and ruff clean;
  boardkit check OK. Fix
  commit 99cfd4a (shared with S19/S21, per-card trailers) sits apart
  from the reviewed range, so commit-range stays bb2d0f8..62e5ea1 and
  the fix-commit re-review runs over 99cfd4a^..99cfd4a via the packet
  override; Gate A's box stays unticked until that re-review passes.
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
