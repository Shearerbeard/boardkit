---
id: S25
title: R8 fix - card titles truncated at an inline hash
status: ready
depends: []
serialize-with: []
lineage: primary
executor: any
gates: "S -> A -> U(code-review)"
user-gates: [code-review]
---

# S25: R8 fix - card titles truncated at an inline hash

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Drain record:
[2026-08-09-feedback-drain-7.md](../../plans/2026-08-09-feedback-drain-7.md)
(first drained entry, second part). Evidence: W4 on the consolidated
aura board renders as "Record the"; the `#398` fragment eats the rest
on every render.

## Scope

`src/boardkit/board.py` (frontmatter parsing and validation),
`_template.md` and the shipped template (authoring guidance), tests.

## Deliverable

Drain-time diagnosis: an unquoted `#` after whitespace in YAML starts a
comment, so the truncation happens at parse time and every consumer of
the frontmatter (views, canary key, dispatch briefs) sees the truncated
title. The fix is loud validation, not renderer patching: `parse_card`
compares the YAML-parsed title against the raw frontmatter line and
fails with a quote-the-title message when a comment ate part of it.
The template's frontmatter contract gains one line saying titles
containing `#` must be quoted.

## Acceptance

- `uv run pytest -q` green; a regression test with an unquoted
  `title: Record the #398 follow-up` fails `check` with the
  quote-the-title message, and the quoted form passes and renders in
  full.

## Gate checklist

- [ ] Gate S: load skill `gate-probes`, then `uv run pytest -q`,
  `uv run ruff check`, `vale` on touched markdown.
- [ ] Gate A: adversarial review, focus: other YAML-eats-content
  shapes the same check should catch or explicitly leave (anchors,
  colons in titles) without over-blocking legitimate frontmatter.
- [ ] Gate U (code-review): present the review packet; stop.

## Branch

direct

## Log

- 2026-08-09 Minted by the seventh feedback drain from the 2026-08-07
  registry entry's render-truncation finding (D3/R8), isolated bugfix
  per the build order.
