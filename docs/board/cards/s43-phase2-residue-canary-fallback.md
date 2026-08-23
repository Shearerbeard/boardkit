---
id: S43
title: Land the phase 2 residue - canary fallback, degraded close, review notes
status: in-review
depends: []
serialize-with: []
lineage: primary
executor: smart
gates: "S -> A -> U(code-review)"
user-gates: [code-review]
commit-range: "f769416..4a946a6"
---

# S43: Land the phase 2 residue - canary fallback, degraded close, review notes

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Minting record: the wave-2
plan's Phase 2 change list
([2026-08-19-wave-2-plan.md](../../plans/2026-08-19-wave-2-plan.md)),
whose decision-5 and documentation items were phase deliverables
attached to no card; this card closes the gap so Phase 2's done-when is
met before its user gate presents.

## Scope

`boardkit.toml` (this board's live `[roles.canary]`), the init
scaffold's boardkit.toml source in `src/boardkit/`, `docs/board/PROCESS.md`
and `src/boardkit/data/templates/PROCESS.md` (the orientation-canary
section), `plugins/board/skills/board-hygiene/SKILL.md` (plus the
plugin manifest bump), `docs/board/REVIEW-TOOLING.md`, the
dispatch-brief data in `src/boardkit/`, tests where template or brief
text is pinned.

## Deliverable

The wave-2 plan's unassigned Phase 2 items, verbatim from its approved
decisions:

- Decision 5 in full: `roles.canary` gains `codex-reviewer` as its
  fallback (the board's only cross-provider escape) in this board's
  live `boardkit.toml` AND the init scaffold; the degraded-close
  definition lands in the live PROCESS orientation-canary section, the
  template copy, and the `board-hygiene` skill: canary-key generated
  and stored, deferral logged with outage evidence, canary owed at
  next session start.
- REVIEW-TOOLING documents the `--suffix` fix-packet pattern and the
  read-the-reviewer's-own-final-message rule.
- The dispatch-brief data gains the parallel-fill interference note.

## Acceptance

- `uv run pytest -q` green; `boardkit resolve-route canary` resolves a
  fallback on this board.
- Both PROCESS copies state the degraded close in the canary section
  and agree; the hygiene skill answers the outage case in writing.
- `vale` clean on every touched markdown file.

## Gate checklist

- [x] Gate S: load skill `gate-probes`, then `uv run pytest -q`,
  `uv run ruff check`, `boardkit check`, `boardkit render --check`,
  `boardkit doctor`; `vale` on touched markdown.
- [ ] Gate A: adversarial review of the diff against the plan's
  decision-5 wording and the shipped resolver of `resolve-route`.
- [ ] Gate U (code-review): packet to Mike, batched with the Phase 2
  window; stop.

## Branch

direct

## Log

- 2026-08-22 Commit-range extended to f769416..4a946a6 over the fix
  commit, the packet regenerated, and Gate A round 2 dispatched with
  the convergence discipline.
- 2026-08-22 Fix round landed by the same Claude executor: the
  fix-round packet section in both REVIEW-TOOLING copies now leads
  with the PROCESS fix-commit re-review duty (range extended, primary
  packet regenerated over the full range) and frames the --suffix
  packet as strictly supplementary, never the packet a gate is graded
  on, closing with this session's own worked shape. The pinned test
  now asserts the subordination rather than the objected-to wording.
  Board owner re-ran the checks: pytest 423, ruff clean, vale clean,
  the two copies' section byte-identical.
- 2026-08-22 Gate A round 1 returned VERDICT: FAIL with one BLOCKING
  finding: the new fix-round packet section in REVIEW-TOOLING (live
  and template) reads as an alternative to the PROCESS fix-commit
  re-review duty rather than a supplement to it, so following it
  literally could leave fix commits outside the durable reviewed
  range. Everything else verified: canary fallback resolution,
  degraded-close wording across all three homes, byte-identical
  PROCESS copies, brief extraction, scaffold parsing. Reviewer: GPT
  5.6-sol via the codex CLI; round spend 132,723 tokens. Unverified:
  full pytest (sandbox temp denial; 24 affected non-temporary tests
  passed in-sandbox); the board owner's run stands (422 passed). Board
  owner accepted the finding; fix round dispatched.
- 2026-08-22 Entered in-review: commit-range f769416..1d72d44 recorded
  and the review packet generated. Gate A dispatch to the codex lane
  follows; the packet presentation batches with the Phase 2 window.
- 2026-08-22 Gate S passed, run by the board owner after a two-round
  Claude-subagent execution (implementation, then an amendment adding
  the two review practices to the shipped REVIEW-TOOLING template -
  a board-owner scope extension logged here): `uv run pytest -q` (422
  passed, up from 417), ruff and format clean, vale clean on all five
  touched markdown files, the PROCESS pair byte-identical, `boardkit
  resolve-route canary` resolving codex-reviewer as fallback, check,
  render --check, and doctor green. Board owner rulings: the scaffold
  ships the fallback shape as a second placeholder route with a
  documented single-transport deletion escape, since a generic
  scaffold cannot name a real transport and parse_contract rejects
  undeclared routes - the scaffolded-not-lying consequence (a fresh
  init needs two transports or one deletion before doctor is clean)
  is accepted and surfaces in doctor's own message. The parallel-fill
  note rides the DISPATCH_BRIEF_ANCHOR paragraph so briefs quote it
  without a new required anchor for consumers, verified in a
  generated brief. Discovered, not fixed: the --suffix CLI help and
  two PROCESS passages still describe only the multi-repo use of the
  flag; queued for the next drain.
- 2026-08-22 Minted and pulled by the board owner on finding Phase 2's
  done-when unmet: the plan's decision-5 and documentation items were
  phase deliverables attached to no card, discovered while preparing
  the batched user gate. The content is pre-approved plan text; this
  card exists so it lands through the standard pipeline rather than as
  gateless board-owner edits.
