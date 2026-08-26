---
id: S45
title: rust-holes repo self-check with template provenance stamp
status: in-review
commit-range: a2b3f2e..605056b
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

- [ ] Gate S: the acceptance runs above; vale on touched markdown.
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
