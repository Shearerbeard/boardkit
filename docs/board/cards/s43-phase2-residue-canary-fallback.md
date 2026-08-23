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
commit-range: "f769416..6bd4d25"
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
- [x] Gate A: adversarial review of the diff against the plan's
  decision-5 wording and the shipped resolver of `resolve-route`.
- [ ] Gate U (code-review): packet to Mike, batched with the Phase 2
  window; stop.

## Branch

direct

## Log

- 2026-08-22 Gate A passed. Round 3 verified the round-2 disposition
  RESOLVED with the section's temporal claims checked against the
  shipped review_packet.py behavior and returned an explicit
  zero-findings VERDICT: PASS. Cycle shape: round 1 FAIL (1 BLOCKING,
  the rest of the card verified), round 2 FAIL in convergence (the
  fix verified, one fix-introduced regression), round 3 PASS - closed
  at the two-fix-round bound with no ruling needed. Author of the
  reviewed range: Claude (claude-opus executor under a claude-fable-5
  board owner). Reviewer all rounds: GPT 5.6-sol via the codex CLI,
  read-only sandbox. Reviewer spend: 132,723 + 97,285 + 84,749 =
  314,757 tokens. Unverified in round 3: full pytest (sandbox temp
  denial); the board owner's own run stands (424 passed). Review
  record: prompts and outputs for all three rounds in the packet
  directory. The card now waits at U(code-review), batched with the
  Phase 2 window.
- 2026-08-22 Commit-range extended to f769416..6bd4d25 over the second
  fix commit, the packet regenerated, and Gate A round 3 dispatched.
  Two fix rounds are spent: a round 3 short of a clean pass requires a
  written board-owner ruling before the cycle continues.
- 2026-08-22 Fix round 2 landed by the same Claude executor: the
  section now says the regenerated full-range packet stays whole and
  defers to the retention contract by name (both packets regenerable
  working material, the card and its log the durable record), the
  overwrite hazard is stated against the current re-review's packet,
  and a new guard test asserts the deference positively and the
  retracted phrasing's absence. Board owner re-ran the checks: pytest
  424, ruff clean, vale clean, the copies' section byte-identical.
- 2026-08-22 Gate A round 2 returned VERDICT: FAIL, in convergence:
  the round-1 disposition verified RESOLVED (both copies lead with
  the duty, sections byte-identical, subordination pinned), with one
  fix-introduced regression - the reworded section calls the packet
  "the record", contradicting the PROCESS retention contract that
  packets are regenerable working material, and misstates which
  packet an unsuffixed run overwrites; the replacement test pins the
  wrong claim. Reviewer: GPT 5.6-sol via the codex CLI; round spend
  97,285 tokens, cumulative 230,008. Unverified: full pytest (sandbox
  limits; the focused file's 8 tests passed in-sandbox). Board owner
  accepted; fix round 2 dispatched - the bound, so a round 3 short of
  a clean pass requires a written ruling.
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
