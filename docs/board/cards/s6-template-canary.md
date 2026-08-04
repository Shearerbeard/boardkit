---
id: S6
title: Template baseline digest, template-diff, and golden briefs
status: backlog
depends: []
serialize-with: [S1]
lineage: primary
executor: smart
gates: "S -> A"
user-gates: []
---

# S6: Template baseline digest, template-diff, and golden briefs

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Plan:
[2026-08-04-productionize-verification.md](../../plans/2026-08-04-productionize-verification.md),
stage 5.

## Scope

`src/boardkit/doctor.py`, `src/boardkit/contract.py`,
`src/boardkit/cli.py`, `tests/` including a new
`tests/golden/briefs/` tree.

## Deliverable

The consumer-side canary for template changes:

1. A kit baseline digest alongside `contract_digest`, so doctor can
   report body-level drift between a consumer's contract docs and the
   shipped templates - today it compares stamps only, and a reworded
   Gate A ships silently.
2. `boardkit template-diff`: show the drift the digest detects, per
   section.
3. Checked-in golden briefs over the golden fixture board
   (`tests/golden/briefs/`), regenerated and diffed by a test - a
   whole-frame snapshot of the template prose that briefs quote
   verbatim into every dispatch.

## Acceptance

- `uv run pytest -q` green; a deliberate one-word template edit in a
  scratch checkout trips both the digest and the golden-brief diff
  (negative control recorded in the card log).
- Doctor output distinguishes "consumer edited their copy" from "kit
  moved under the consumer".

## Gate checklist

- [ ] Gate S: `uv run pytest -q`, `uv run ruff check`.
- [ ] Gate A: adversarial review, focus: can a template change ship that
  neither the digest nor the golden briefs would surface?

## Branch

direct

## Log

- 2026-08-04 Authored from the snapshot-surfaces audit (gaps 1, 2, 4).
