---
id: S21
title: R3 qualified cross-board references
status: done
depends: [S18]
serialize-with: []
lineage: primary
commit-range: 62e5ea1..d059160
executor: smart
gates: "S -> A -> U(code-review)"
user-gates: [code-review]
---

# S21: R3 qualified cross-board references

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Drain record:
[2026-08-09-feedback-drain-7.md](../../plans/2026-08-09-feedback-drain-7.md)
(same-sitting mints); requirement R3 in the aura requirements doc,
evidence: coordination prose already names three boards in one clause
with no qualifiers, and `depends` resolves same-board only.

## Scope

`src/boardkit/board.py` (the `refs:` field and its validation),
`src/boardkit/data/templates/PROCESS.md`, `docs/board/PROCESS.md`, and
`_template.md` (schema prose), tests.

## Deliverable

A qualified reference syntax `<code>/<id>` (as in `tb/S91`), valid in
card prose and in a new optional `refs:` frontmatter list. Resolution
goes through the S18 registry: the short-code must be a registry row,
and the id must match that row's declared prefix scheme. Refs are
informational for DAG purposes - the local scheduler never blocks on
another board's state - so `check` validates form and short-code
existence, warns when the target board is unreachable on this machine,
and never reads the other board's card status. Bare ids stay valid
inside a single board.

## Acceptance

- `uv run pytest -q` green; tests cover ref parsing, unknown
  short-code errors, prefix-mismatch errors, the unreachable-board
  warning, and that a ref never affects ready/blocked computation.
- A fixture card with `refs: [tb/S91]` passes `check` against a
  manifest that rows `tb`, and fails against one that does not.
- The schema prose in the shipped template and this board's PROCESS
  copy agree.

## Gate checklist

- [x] Gate S: load skill `gate-probes`, then `uv run pytest -q`,
  `uv run ruff check`, `vale` on touched markdown.
- [x] Gate A: adversarial review, focus: can an informational ref leak
  into scheduling, and does the prefix check hold for sentinel ids?
- [x] Gate U (code-review): present the review packet; stop.

## Branch

direct

## Log

- 2026-08-09 Minted by the seventh feedback drain from standing
  requirement R3, per the Session B build order.
- 2026-08-09 Pulled in-progress straight from backlog (S18 in-review,
  same-hand build order per drain 7); executor is the maintainer
  session.
- 2026-08-09 Built: `refs:` optional frontmatter list with `<code>/<id>`
  shape validated at parse; registry resolution in `check` via
  `card_ref_findings` - unknown short-code is an error, a
  prefix-scheme mismatch or an unreachable board is a warning (sentinel
  ids of another board are not knowable from its row); refs never feed
  readiness; schema prose in both PROCESS and both _template copies.
  Gate S PASS: 316 pytest green (5 ref tests), ruff clean, vale clean.
- 2026-08-09 In-review; commit-range 62e5ea1..d059160.
- 2026-08-09 Gate A deferred, superseded 2026-08-16: adversarial reviews batch at the
  Session B boundary; packets present at the Gate B user gate.
- 2026-08-16 Gate A ran (resolving the deferral): reviewer gpt-5.6-sol
  via codex exec, author claude-fable-5 (whole wave); codex fallback
  after the opencode lane stalled its read probe. Verdict FAIL, two
  findings. The reviewer confirmed no scheduling leak: readiness
  consumes only depends.
  1. BLOCKING every non-prefix id downgraded to a warning, against the
     acceptance's prefix-mismatch errors. Confirmed, with the build
     log's stated premise (sentinels not knowable from the row) holding
     only for unresolvable boards. Fixed in 99cfd4a: a resolvable
     board's own config names its sentinels, so a sentinel passes clean
     and anything else errors; the warning stays where the board is
     unreachable or its config unreadable.
  2. BLOCKING cards carrying refs validated as a silent pass when no
     registry was reachable. Confirmed against the deliverable
     (resolution goes through the registry). Fixed in 99cfd4a: that
     state is now an error naming the carded files.
  Reviewer-reported UNVERIFIED (sandbox): pytest, ruff, check, doctor -
  run board-owner-side instead: 348 pytest green and ruff clean;
  boardkit check OK. Fix
  commit 99cfd4a (shared with S19/S20, per-card trailers) sits apart
  from the reviewed range, so commit-range stays 62e5ea1..d059160 and
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
