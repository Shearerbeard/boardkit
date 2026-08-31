---
id: S49
title: Pre-publication docs pass - feedback intake to issues, bus test, publish-gate rulings
status: done
commit-range: db5da56..08f93e7
depends: []
serialize-with: []
lineage: none
executor: any
gates: "S -> A"
user-gates: []
epic: S41
---

# S49: Pre-publication docs pass - feedback intake to issues, bus test, publish-gate rulings

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Minted retroactively on
2026-08-31 to bring the board in line with work already landed and
pushed that day; the card records the gates as they actually ran.

## Scope

The kit's own repo, ahead of making it public: retire the tracked
FEEDBACK.md inbox for GitHub issues, close the documentation bus test,
and discharge the Phase 6 publish-gate obligations by user ruling. Out
of scope: the rust-holes publicity annotations (f2fa84f, board
bookkeeping inside the range window) and the remaining S41 members.

## Deliverable

- FEEDBACK.md untracked and gitignored (local archive kept); PROCESS.md,
  its scaffold template, and the prose corpus-inbox README route
  friction to https://github.com/Shearerbeard/boardkit/issues. The
  board-hygiene plugin skill's stale inbox line follows in 837097a.
- README gains a Development section and real bootstrap steps;
  PROCESS, MODEL-CLASSES, and REVIEW-TOOLING (plus their templates)
  lose the contradictions codex round 1 named: graph.md missing from
  the view inventory, the schema's required-fields claim, the stall
  wrapper's missing recipe and unrecorded deadline, and the Gate A
  model-versus-family drift.
- `snapshots/` stripped; EXTRACTION.md and PLAN.md record the dated
  publish-gate rulings (snapshots STRIP; aura-cards and machine paths
  KEEP, with reasons).
- ruff joins the dev dependency group; the vale setup documents the
  `.vale/styles` prestep; PLAN.md staleness and the drain-7 intake
  claim corrected.
- External half: the process-feedback skill rewrite lives in
  claude-skills `c79fe3a` (files feedback as a GitHub issue), recorded
  here the way S45 records rust-holes shas.

## Gate checklist

- [x] Gate S: `uv run pytest -q` 518 passed, `uv run ruff check` clean,
  vale clean on every touched doc, `boardkit check` OK, doctor 22
  passed with 0 errors. Re-run in full at mint.
- [x] Gate A: codex CLI adversarial review of the docs surface, three
  rounds (FAIL 8 blocking / 4 minor; FAIL 2 not-fixed plus 1 new
  minor; one residual fixed as prescribed). The reviewer's family
  differs from the authoring session's harness. Verdicts and
  per-finding dispositions are summarized in the log below.

## Branch

direct

## Log

- 2026-08-31 Minted retroactively at the user's direction ("make sure
  we're using the boardkit machinery for our own board properly to
  track the work"), after the work landed as `90df4ca` and `08f93e7`
  and the user confirmed push-readiness. User rulings during
  execution: FEEDBACK.md dropped with history kept and a local
  archive; future feedback to GitHub issues; snapshots STRIP;
  aura-cards KEEP.
- 2026-08-31 Gate S PASS as ticked; every fix round re-ran the full
  deterministic set before the next review round went out.
- 2026-08-31 Gate A PASS as ticked: round 1's 12 findings all
  dispositioned; round 2 verified 9 fixed and returned 2 not-fixed
  plus 1 new minor, all fixed; round 3 verified every prior item and
  returned one residual (the literal plugin-install command), fixed
  as prescribed in the final tree. The user's convergence rule for
  the cycle: three rounds maximum, convergence equals pushability.
- 2026-08-31 The commit-range covers `db5da56..08f93e7`. Two later
  commits belong to this card's close rather than its reviewed diff:
  `837097a` (the board-hygiene skill's stale inbox line, the same
  intake move) and this mint commit.
- 2026-08-31 Orientation canary PASS 4/4 at session close
  (deepseek-v4-flash via the opencode lane, graded against
  `boardkit canary-key`). Evidence:
  [2026-08-31-s49-close-canary.md](../evidence/2026-08-31-s49-close-canary.md).
