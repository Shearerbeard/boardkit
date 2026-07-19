---
id: S18
title: Rolling ADR batches
status: done
depends: [S3]
serialize-with: []
lineage: none
executor: smart
gates: "S -> A"
user-gates: []
---

# S18: Rolling ADR batches

Plan section: Stage 4 in
[2026-07-11-orchestration-redesign.md](../plans/2026-07-11-orchestration-redesign.md).
Mechanics: [PROCESS.md](../PROCESS.md). Required reading:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md).

## Scope

Documentation only: a rolling card with two due points. Batch 1 is
due after S3 lands (the frontmatter `depends` tracks batch 1); batch
2 is due after the S10 baseline gate, a second dependency the
frontmatter does not carry.

## Deliverable

ADRs recording the epic's structural decisions, written with the
`adr-review` skill from `~/dev/claude-skills`. Batch 1:
context-fixture schema, bounding unification, and the
branch/lineage/commit policy; batch 1 also decides the ADR home
(default: aura repo `docs/adr/` for code decisions, this directory
for program decisions). Batch 2: thread-shape and
contract-reconciliation outcomes, plus the S12/S13 decisions when
delivered.

## Acceptance

- Batch 1 ADRs land after S3; batch 2 ADRs land after the S10
  baseline gate.
- Every ADR passes the adr-review checklist and vale.
- MANDATORY each S18 session: run the `skill-retro` feedback skill
  and file notes on the adr-review skill itself.

## Gate checklist

- [x] Gate S: vale on every ADR; adr-review checklist applied.
- [x] Gate A: fresh-agent review of each batch.

## Branch

No code lands from this card; ADRs go direct into the home batch 1
decides (default: aura repo `docs/adr/` for code decisions, this
directory for program decisions).

## Log

- 2026-07-11 Filed by S0 from the approved plan.
- 2026-07-17 Promoted to Ready by the board owner (GLM 5.2 opencode).
  Dependency S3 done. Batch 1 ADRs are due; batch 2 waits on the S10
  baseline gate.
- 2026-07-17 In Progress (batch 1). Board owner (Fable, Claude Code,
  attended) dispatching a Claude Opus subagent as executor for the
  three batch-1 ADRs; drafts land in the session scratchpad and the
  board owner places them in the decided homes at gate time (ADR-home
  decision: aura repo `docs/adr/` for code decisions, this directory
  for program decisions, per the card default). Gate A reviewer will
  be a fresh-context Fable subagent with `adr-review` (models
  differ). The mandatory `skill-retro` on adr-review runs at session
  close.
- 2026-07-17 Batch 1 drafted (Claude Opus executor): three MADR
  records matching the house `docs/adr/` convention (date-prefix
  filename, no sequential number) - context-fixture schema (S2),
  unified-bounding module (S3), and the card-branch/lineage/commit
  policy. ADR-home decision confirmed and recorded inside the policy
  ADR and this card: aura repo `docs/adr/` for code decisions,
  adapter `docs/redesign/` for program decisions.
- 2026-07-17 Gate S PASSED. `vale` clean on all three ADRs (and the
  drafts-dir INDEX preamble). adr-review checklist applied by the
  drafting agent.
- 2026-07-17 Gate A PASSED. Reviewer: fresh-context Fable subagent
  (`adr-review`). Author: Claude Opus. Families differ. Verdict PASS,
  5 MINOR, 0 BLOCKING - all accuracy/freshness, all fixed by the
  board owner before placement: (1) the 28-site count cited the
  bounding DESIGN.md but belongs to the S3 card log; (2) "all 28
  rewired" overstated the two deliberately-uncolocated token sites;
  (3) the 16 `#[allow(dead_code)]` figure was present-tense but is
  8 at head, now anchored to the S3 landing commit with the
  downward trajectory noted; (4) the dependency-kind list called
  `worktree-serial` a frontmatter field, but the field is
  `serialize-with`; (5) the policy ADR's single Date fronted a
  6-day-later ADR-home rider, now dual-dated. Re-valed clean after
  the fixes.
- 2026-07-17 Done (batch 1). Homes and shas: context-fixture schema
  `docs/adr/2026-07-12-context-fixture-schema.md` and
  unified-bounding module `docs/adr/2026-07-15-unified-bounding-module.md`
  committed on the aura primary `mshearer/orchestration-simplification`
  at `7a0f0651`; card-branch/lineage/commit policy
  `docs/redesign/2026-07-11-card-branch-lineage-commit-policy.md`
  committed in the adapter repo (sha in this repo's log). This card
  closes on batch 1 (its tracked dependency was S3 only). Batch 2
  (thread-shape, contract-reconciliation, S12/S13) is deferred to a
  new card filed when the S10 baseline gate opens, so the obligation
  survives this card's close rather than holding it open across the
  whole S9/S10 arc. `skill-retro` on `adr-review` filed at session
  close.
