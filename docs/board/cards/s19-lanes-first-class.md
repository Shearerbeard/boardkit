---
id: S19
title: R1 lanes as first-class card data
status: done
depends: []
serialize-with: []
lineage: primary
commit-range: bb2d0f8..62e5ea1
executor: smart
gates: "S -> A -> U(code-review)"
user-gates: [code-review]
---

# S19: R1 lanes as first-class card data

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Drain record:
[2026-08-09-feedback-drain-7.md](../../plans/2026-08-09-feedback-drain-7.md)
(same-sitting mints); requirement R1 in the aura requirements doc,
evidence: three of four cold readers misplaced tb/S88's lane, and the
spike lane's WIP exemption went stale in prose.

## Scope

`src/boardkit/config.py` (`[board]` lane vocabulary and per-lane WIP),
`src/boardkit/board.py` (validation and view grouping),
`src/boardkit/data/templates/PROCESS.md` and `docs/board/PROCESS.md`
(schema prose), `_template.md` frontmatter contract, tests.

## Deliverable

A `lane:` frontmatter key validated against a board-declared vocabulary
(`lanes` under `[board]` in `boardkit.toml`). A board with no declared
lanes accepts no `lane:` keys, so the feature is opt-in and existing
boards stay valid. Per-lane WIP limits and exemptions live in config
rather than prose: an optional per-lane table names a lane's own WIP
limit or marks it exempt, replacing what the boolean `side-quest` flag
cannot scope (that flag stays for user-declared side quests). Generated
views group by lane: `INDEX.md` gains a Lane column and `board.md`
carries the lane on each card line, so a cold reader places a card
without opening it.

## Acceptance

- `uv run pytest -q` green; tests cover vocabulary validation, the
  undeclared-lane error, per-lane WIP counting alongside the global
  limit, and lane rendering in both views.
- On a fixture board with two lanes and a per-lane limit of one, two
  in-progress cards in the same lane fail `boardkit check` while two in
  different lanes pass.
- The shipped PROCESS template and this board's copy state the lane
  schema in the same section and agree.

## Gate checklist

- [x] Gate S: load skill `gate-probes`, then `uv run pytest -q`,
  `uv run ruff check`, `vale` on touched markdown.
- [x] Gate A: adversarial review, focus: does per-lane WIP interact
  wrongly with `side-quest` exemptions or the global limit (double
  counting, exemption laundering)?
- [x] Gate U (code-review): present the review packet; stop.

## Branch

direct

## Log

- 2026-08-09 Minted by the seventh feedback drain from standing
  requirement R1, per the Session B build order.
- 2026-08-09 Pulled in-progress; executor is the maintainer session.
- 2026-08-09 Built: `[[board.lanes]]` vocabulary (name, optional wip,
  optional exempt) parsed strictly; `lane:` key validated against it;
  per-lane WIP cap counts every in-progress card in the lane while
  `exempt` lanes drop out of the global count only; INDEX gains an
  opt-in Lane column and board.md a per-card lane note; schema prose in
  both PROCESS copies and both _template copies. Gate S PASS: 311
  pytest green (5 lane tests in test_lanes_charter.py), ruff clean,
  vale clean on both PROCESS copies. This board declares no lanes yet -
  a fixture board exercises the feature; bk stays single-lane until it
  carries a second family of work.
- 2026-08-09 Work commit is shared with S20 (both trailers): the two
  cards land in one diff over config.py and PROCESS.md.
- 2026-08-09 In-review; commit-range bb2d0f8..62e5ea1. (Transition
  first missed and caught by the board's own WIP limit when S21 tried
  to start - the limit fired exactly as designed.)
- 2026-08-09 Gate A deferred, superseded 2026-08-16: adversarial reviews batch at the
  Session B boundary; packets present at the Gate B user gate.
- 2026-08-16 Gate A ran (resolving the deferral): reviewer gpt-5.6-sol
  via codex exec, author claude-fable-5 (whole wave); codex fallback
  after the opencode lane stalled its read probe. Verdict FAIL, one
  finding. The reviewer's focused WIP probing found no double counting
  and no exemption laundering.
  1. BLOCKING the acceptance names vocabulary-validation tests, but
     none of the lane declaration branches (missing name, duplicate,
     bad wip, bad exempt, unknown key) was tested. Confirmed. Fixed in
     99cfd4a: a parametrized refusal test drives every branch.
  Reviewer-reported UNVERIFIED (sandbox): pytest, ruff, check, doctor -
  run board-owner-side instead: 348 pytest green and ruff clean;
  boardkit check OK. Fix
  commit 99cfd4a (shared with S20/S21, per-card trailers) sits apart
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
