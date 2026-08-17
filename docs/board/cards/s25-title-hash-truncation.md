---
id: S25
title: R8 fix - card titles truncated at an inline hash
status: in-review
depends: []
serialize-with: []
lineage: primary
commit-range: 028ce5d..a95fcab
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

- [x] Gate S: load skill `gate-probes`, then `uv run pytest -q`,
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
- 2026-08-09 Pulled in-progress; executor is the maintainer session.
- 2026-08-09 Built: `parse_card` compares the raw frontmatter title
  line against the YAML-parsed value and refuses with a
  quote-the-title message when an unquoted '#' comment ate part of it;
  quoted titles with '#' pass and render in full. Both _template
  frontmatter contracts gain the quoting line. Diagnosis confirmed:
  parse-time YAML comment semantics, so every frontmatter consumer saw
  the truncation - the fix is upstream of all of them. Gate S PASS:
  337 pytest green (regression test with the verbatim W4 shape), ruff
  clean, vale clean.
- 2026-08-09 In-review; commit-range 028ce5d..a95fcab.
- 2026-08-09 Gate A deferred, superseded 2026-08-16: adversarial reviews batch at the
  Session B boundary; packets present at the Gate B user gate.
- 2026-08-16 Gate A ran (resolving the deferral): reviewer gpt-5.6-sol
  via codex exec, author claude-fable-5 (whole wave); the pinned
  opencode lane stalled its read probe on two models and the declared
  codex fallback took the dispatch. Verdict FAIL, two findings, both
  confirmed by reproduction before fixing.
  1. BLOCKING board.py title guard falsely refused an anchored quoted
     title (raw line starts with '&', read as unquoted). Fixed in
     fa9db37: the guard now fires on the truncation signature (parsed
     value a prefix of the raw line, remainder at '#') instead of the
     first-char-quote heuristic.
  2. BLOCKING TITLE_LINE_RE only matched an unindented exact 'title:'
     key, so YAML-tolerated spellings (space before colon, indented
     frontmatter) truncated silently past the guard. Fixed in fa9db37:
     the matcher tolerates what YAML tolerates; regression tests cover
     both spellings plus the anchor pass-through.
  Reviewer-reported UNVERIFIED (sandbox): pytest, ruff - run
  board-owner-side instead: 338 pytest green, ruff clean. Fix commit
  fa9db37 sits apart from the card's reviewed range with foreign
  commits between, so commit-range stays 028ce5d..a95fcab and the
  fix-commit re-review runs over fa9db37^..fa9db37 via the packet
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
