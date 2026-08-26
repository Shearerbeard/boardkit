---
id: S45
title: rust-holes repo self-check with template provenance stamp
status: in-review
commit-range: a2b3f2e..32d7eac
depends: []
serialize-with: []
lineage: none
executor: any
gates: "S -> A"
user-gates: []
---

# S45: rust-holes repo self-check with template provenance stamp

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Drain record:
[2026-08-23-feedback-drain-8.md](../../plans/2026-08-23-feedback-drain-8.md).
External repo: `~/dev/rust-holes` (private; never publish). Plan:
`rust-holes docs/plans/2026-08-23-second-dev-readiness.md`.

## Scope

The rust-holes repo (external): a new `bin/check` (stdlib-only, no
project scaffolding), one provenance-stamp instruction line added to
each template header, and fixes for what the check's first run finds.
No doctrine changes. This board carries the card and the logged sha
range.

## Deliverable

The repo can fail loudly on its own drift. `bin/check` verifies:
every relative path referenced in the markdown resolves; every file
under `templates/` still opens with its template header and the new
stamp instruction ("record `copied from rust-holes@<sha>` when you
copy this file", the consumer-side half of drift detection); the
`README.md` read-order table names every file under `templates/` and
`examples/`; the never-publish header is intact. Known first catch:
the read-order table omits `templates/MANIFEST.md` and
`templates/golden-frame-harness.md`, both added in `410fa0c`.

## Acceptance

- `bin/check` exits 0 on the repaired repo.
- Each defect class, seeded deliberately (dangling link, half-filled
  template, missing read-order row, stripped Private header,
  stripped stamp line), exits nonzero with a message naming the file
  and the rule; the runs are recorded in the Log.

## Gate checklist

- [x] Gate S: the acceptance runs above; vale on touched markdown.
- [ ] Gate A: second-model review, focus: which drift class does the
  check miss, and does any check assert something the docs do not
  promise?

## Branch

direct; external commits recorded in the Log as they land.

## Log

- 2026-08-23 Minted by feedback drain 8 from the rust-holes
  second-dev audit (adopted RH1 draft, adversarially reviewed there).
- 2026-08-25 Pulled to in-progress under the cleanup execution plan
  (rust-holes `docs/plans/2026-08-25-cleanup-execution.md`). Executor
  lane: opencode on bedrock, dispatched from a rust-holes worktree
  because opencode refuses the primary checkout path; reviewer lane:
  codex. Brief generated at digest 5b86d0ba5e6e.
- 2026-08-25 Executor attempt 1 (bedrock lane, whole card, 900s
  deadline) stalled: zero bytes of output, no files written, killed
  at the deadline. Attempt 2 dispatched as a smaller unit (the
  `bin/check` script alone, 600s). Per the stall protocol, a second
  stall switches the lane rather than retrying.
- 2026-08-25 Executor attempt 2 (bedrock lane, `bin/check` alone,
  600s) stalled the same way and was stopped at 8 minutes: zero
  output, no files. Diagnosis: the harness's build agent has no bash
  permission configured, so a headless run blocks on the first shell
  step (`mkdir bin`, `chmod`, running the check), while the pre-vet
  tasks, which only read and wrote files, succeeded. Attempt 3 is
  write-only with `bin/` pre-created and shell steps moved to Gate S.
  A third stall switches the executor lane to the board's configured
  route.
- 2026-08-26 Executor attempt 3 (bedrock lane, write-only, `bin/`
  pre-created) succeeded; a second write-only dispatch landed the
  template headers and README rows. Board-owner repairs before Gate
  S, recorded as deviations from the executor's output: the
  `template-header` rule rewritten to check for a `Template.` opening
  paragraph (the card's "delete this line" phrase was never uniform
  across the six templates, so the rule as specified asserted
  something the docs did not promise); stamp rule scoped to the
  opening section instead of a 12-line window; stamp sentences moved
  into the opening paragraph in two files and all six reflowed to 72
  columns.
- 2026-08-26 Gate S passed: `bin/check` exits 0 on the repo; seeded
  defects (dangling link, stripped `Template.` opener, missing
  read-order row, stripped Private header, stripped stamp line) each
  fail on their intended rule, harness at rust-holes
  `scratch/seed-defects.sh`; vale clean on touched markdown. Commit
  `605056b` on rust-holes master; commit-range set; packet generated;
  Gate A dispatched to the codex lane.
- 2026-08-26 Gate A round 1 (codex lane): FAIL, 5 BLOCKING + 1 MINOR.
  Dispositions, all ACCEPTED and repaired in `4511add` by the board
  owner (reviewer differs from both authors): (1) links rule skipped
  same-directory targets, fragments, angle-wrapped forms; now every
  target resolves against the referencing file. (2) read-order rule
  matched substrings; now parses the table's first column. (3) the
  `Template.` marker was promised by no doc; README "Using it" now
  states the header convention, and the rule checks the paragraph
  after the title structurally. (4) stamp rule accepted a partial
  token anywhere before the first H2; now requires the full
  instruction in the opening paragraph. (5) `**Private.**` accepted
  on any line; now must open the README. (6) ruff findings, trailing
  whitespace, missing final newline: cleaned, `ruff check` and
  `ruff format --check` green. Seeded harness grew from 5 to 10
  cases, one per evasion the reviewer named; all fail on their
  intended rule. Round 2 dispatched to the same lane.
- 2026-08-26 Gate A round 2 (codex lane): FAIL, 4 BLOCKING; the six
  round-1 dispositions verified fixed. Classification under the
  re-review rule: two incomplete round-1 fixes (angle-wrapped link
  with a title still evaded the links rule; read-order rows were
  accepted from any README table) and two regressions the round-1
  fix introduced (a heading with no blank line after it merged into
  the first paragraph; template discovery lost recursion). All four
  ACCEPTED and repaired in `ff130a8` by the board owner; the harness
  gained one seed per finding (14 cases, all failing on their
  intended rule). Second fix round; a round-3 FAIL triggers the
  board-owner ruling. Range spans S47's and S4's commits, which touch
  no `bin/check` line; round 3's prompt names them out of scope.
- 2026-08-26 Gate A round 3 (codex lane): FAIL, 2 BLOCKING, both
  in-cycle: the read-order fix was incomplete (a second table under
  the same section counted) and the heading split was a regression
  (`#tag` at a line start read as a heading). Board-owner ruling
  after two fix rounds: CONTINUE. Reason: rounds have converged 6, 4,
  2 with no new scope, every finding stayed in cycle, and both
  repairs are two lines with a seed each. Repaired in `49b5501`;
  harness now 15 failing seeds plus one must-still-pass case. Round
  4 dispatched; a round-4 FAIL escalates to Mike rather than a fifth
  round.
- 2026-08-26 Gate A round 4 (codex lane): FAIL, 1 BLOCKING, a
  regression of the round-3 heading fix: a tab-separated or bare ATX
  heading merged into the opening paragraph. Both round-3 fixes were
  verified. Repaired in `32d7eac` with the reviewer's own regex and two
  harness seeds (18 failing seeds plus one must-pass case, all
  green). Per the round-3 ruling, this FAIL escalates instead of
  opening round 5: Gate A open, escalated to Mike. The board owner's
  position for that stop: the four rounds converged 6, 4, 2, 1, every
  finding stayed in the markdown-parsing family and in cycle, and
  this last fix is one regex verified by the seeds; the recommendation
  is to accept the board owner's verification and close, with round 5
  available if Mike prefers the reviewer's word.
