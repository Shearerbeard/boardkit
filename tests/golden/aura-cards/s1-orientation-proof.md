---
id: S1
title: Fresh-agent orientation proof
status: done
depends: [S0]
serialize-with: []
lineage: none
executor: any
gates: "S -> A"
user-gates: []
---

# S1: Fresh-agent orientation proof

Plan section: Stage 1 in
[2026-07-11-orchestration-redesign.md](../plans/2026-07-11-orchestration-redesign.md).
Mechanics: [PROCESS.md](../PROCESS.md). Required reading:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md).

## Scope

Adapter repo, evidence only, no code: the orientation-test protocol
card plus its sealed answer key, and a dated results evidence file
with per-model transcripts under a named directory.

## Deliverable

Proof of success criterion 4: `protocol-orientation-test.md` giving
the exact prompt text, model identifiers, isolation conditions, and
the one-attempt rule with a single named exception class for infra
failure; a SEALED answer key (the expected ready-work DAG, committed
before any trial); a dated results file with the graded matrix and
per-model transcripts saved under a named directory.

## Acceptance

- Protocol and answer key are committed before the first graded
  trial; the rubric has binary pass/fail criteria.
- At least 2 smart-class models and 1 lesser-class model pass against
  the sealed key; the graded matrix is in the results file.
- Failures spawn registry-fix follow-up cards rather than being waved
  through.
- Per-model transcripts are on disk under the named directory.

## Gate checklist

- [ ] Gate S: protocol and answer key vale-clean and committed BEFORE
      the first trial; rubric has binary pass/fail criteria.
- [ ] Gate A: one dry run with a single model before the full matrix;
      the rubric may be amended only before the graded trials start.

## Branch

Adapter repo, direct.

## Log

- 2026-07-11 Filed by S0 from the approved plan.
- 2026-07-12 In Progress, pulled in the four-card bolus (WIP-2
  deviation authorized; see S2 log). Fairness fixes landed first per
  user decision (adapter commit `1b1663c`): the BOARD.md freeze pointer
  (an unmet S0 acceptance item) and the README contents/read-order
  routing to `cards/INDEX.md`, so trials measure the registry rather
  than known-broken pointers. Trials run against a read-only adapter
  worktree pinned at the sealed-key commit sha so live board motion
  cannot skew grading. Grading hazards to encode in the rubric:
  MILESTONE counts as a DAG node, serialize-with is non-blocking for
  readiness, smart/lesser class model identifiers named explicitly.
- 2026-07-12 Protocol and sealed key written and committed before any
  trial. Logged divergence from the card deliverable: the protocol
  lives at `evidence/2026-07-12-s1-protocol-orientation-test.md`, not
  `cards/protocol-orientation-test.md`, because the registry generator
  rejects non-card filenames in `cards/` (its filename rule); the
  protocol records this in its location note. The sealed key is
  `evidence/2026-07-12-s1-sealed-answer-key.md`, pinned at `1b1663c`
  and re-verified by the board owner against the frontmatter at that
  sha before sealing (exact match: ready set, 20-line edge list,
  MILESTONE node).
- 2026-07-12 In Review. Round 1 complete: dry run (codex) matched the
  key on every check, rubric frozen unamended; graded matrix ran
  codex gpt-5.6-sol PASS, fireworks minimax-m3 PASS (lesser class),
  claude-opus-4-8 FAIL on the format check only (one framing sentence
  before READY; content byte-equivalent to the key; dispositioned as
  a model/harness limitation per the protocol, not a registry
  defect). Acceptance (2 smart + 1 lesser passes) is NOT met by round
  1 as graded; every model derived the exactly correct DAG, so the
  discoverability claim held for all entrants. Results:
  `evidence/2026-07-12-s1-orientation-results.md`; transcripts under
  `evidence/2026-07-12-s1-orientation-trials/`. One infra retry
  during the dry run (codex stdin hang; logged). Board owner
  re-graded all three answers directly. Whether to accept the round
  as delivered proof or commission a resealed round 2 with hardened
  answer extraction is a USER decision at morning ratification.
- 2026-07-12 Done. User accepted round 1 as delivered proof at
  morning ratification. Rationale on the record: all three models,
  including the lesser class, derived the exactly correct 20-card DAG
  from the registry docs alone, so success criterion 4
  (discoverability) held for every entrant; the opus-4-8 miss was a
  format-only failure (one framing sentence before READY, content
  byte-equivalent to the key) dispositioned as a subagent-harness
  artifact, not a registry defect. No round 2 commissioned; no
  registry-fix follow-up cards needed.
