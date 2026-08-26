---
id: S45
title: rust-holes repo self-check with template provenance stamp
status: in-progress
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
