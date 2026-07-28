# Plan: typed-holes + layered red-green as a repeatable practice (Goal 4)

## Scope

- Core problem: the Rust practice that produced the good autonomous
  results lives only as terminalbench-aura project prose (PROCESS.md Type
  discipline, TYPE_PLAN.md skeleton conventions, retro-2026-07-02, the S2
  golden-frame harness card) plus two evidence-backed instances tracked in
  the wiki `typed-holes` workstream. Nothing in claude-skills encodes it:
  no skill mentions typed holes, and no skill prescribes any test
  practice at all. The user's judgment that this is "more than a skills
  install" is right: the practice includes code-level templates, harness
  patterns, and private aura-derived exemplars that do not fit a public
  SKILL.md.
- Audience: future Rust work in any aura-family repo; delegated executors
  (including non-Claude models that receive the rules quoted in dispatch
  briefs, per REVIEW-TOOLING's card-implementer standards).
- Success: a new Rust repo can adopt the practice from the private repo +
  optional skills, with the same shape aura used: skeleton commit that
  compiles, design panel, pre-failing golden frames, tracked hole closure.
- Non-goals: rewriting rust-design/rust-quality wholesale; forcing a
  third instance (wiki P2 stays opportunistic); publishing the private
  repo.

## The practice, named (so the repo has a spec to carry)

Two layers of machine-tracked holes, filled over time:

1. **Layer 1, compiler-tracked (typed holes).** Full type surface first:
   real signatures, derives, From/Into, real leaf types, `todo!()` only at
   real-behavior bodies. Must pass `cargo check` + `cargo clippy` before
   any body lands, as its own commit (auditable git object). Each
   `todo!()` fn carries `#[expect(unused_variables, reason = ...)]` so the
   lint firing stops when the body lands and the marker forces its own
   removal. Every public type maps to one business rule with the invalid
   state it forbids named (TYPE_PLAN.md or co-located DESIGN.md). Between
   skeleton and first body: a two-reviewer design panel (adversarial
   invalid-states pass + second-model logic pass), numbered per-finding
   ledger with dispositions.
2. **Layer 2, test-runner-tracked (red-green golden frames).** Expect-style
   golden tests of whole rendered frames/envelopes, written pre-failing
   from the spec before implementation: the spec-side complement of the
   skeleton. The compiler tracks behavior holes; the failing golden tests
   track rendering/semantics holes. A committed coverage manifest names
   what the frames do NOT cover; byte-identity assertion mode exists for
   refactor cards (proven by a no-op refactor). Known limits stay recorded
   as correctives: compile surface misses partly-private gaps and runtime
   semantic mismatches (wiki workstream P3's full-surface oracle is the
   open answer).

## Verification

- Smoke test: in a scratch crate, follow the repo's PLAYBOOK end to end
  (skeleton → panel → pre-failing frame → fill one hole to green) using
  only the repo + skills, no aura files.
- Deterministic: `cargo check`, `cargo clippy`, `cargo +nightly fmt
  --check`, the pre-failing test flipping red→green; claude-skills
  `bin/check-skills` for stage 2.

## Blast Radius

- Files: new private repo `~/dev/rust-holes` (name at Gate U);
  claude-skills `plugins/rust/skills/` (new `typed-holes` skill +
  a rust-design paragraph); boardkit PROCESS template type-discipline stub
  (already points at an unshipped `typed-holes` skill, so no change needed
  beyond the skill existing); wiki `typed-holes` workstream update via
  handoff.
- Existing building blocks: aura PROCESS.md:516-554 (Type discipline),
  TYPE_PLAN.md:18-45 (skeleton conventions incl. the `#[expect]` marker),
  retro-2026-07-02 (the layered complement statement), S2 card + its
  DESIGN.md exemplar, evidence retros; wiki workstream P0 text is written
  and ready to land verbatim.
- Coverage gaps: no third instance yet (P2); no deterministic full-surface
  oracle (P3). Both are recorded in the wiki workstream and do not block this plan.

## Implementation Stages

### Stage 1: scaffold the private repo
- Goal: one durable home for the full playbook and its templates.
- Changes: `~/dev/rust-holes` (private) with: `PLAYBOOK.md` (the two-layer
  practice above, written repo-neutral); `templates/` (DESIGN.md
  type-inventory template, skeleton-conventions doc, dispatch-brief block
  quoting the rules for executors without skills, design-panel prompt
  pair); `examples/` (aura-derived exemplars: the CLI approval ADT shape,
  the S2 frame-harness structure, sanitized of benchmark specifics);
  `EXTRACTION.md` ledger mapping every rule to its aura source line, same
  discipline boardkit used. Record the known-limits correctives verbatim.
- Gates: S → A
- [ ] Gate S: load skill `gate-probes`; `vale` on all markdown; extraction
      re-grep tripwire (every aura type-discipline rule has a row)
- [ ] Gate A: cross-family review against the aura sources for silent
      drops and for private material that must not leak into templates
- Done when: the smoke test's PLAYBOOK walk is possible without opening
  any aura file.

### Stage 2: skills in claude-skills 🛑 USER GATE
- Goal: the public, composable slice of the practice.
- Changes:
  - New `typed-holes` skill in the rust plugin: the two-layer workflow,
    skeleton-commit rule, `#[expect]` marker convention, design-panel
    procedure, golden-frame red-green ordering, byte-identity refactor
    mode. References `rust-design` and `gate-probes` by bare name; states
    the fallback when rust-holes templates are absent (the skill is
    self-sufficient for the workflow, the repo adds templates/exemplars).
  - rust-design gets the P0 paragraph from the wiki workstream verbatim
    ("compile and lint the type surface before any implementation;
    `serde(untagged)` over enums with overlapping field shapes is a class
    of bug that only shows up at the typing stage") plus the P1
    `#![allow(dead_code)]`/`#[expect]` convention. This closes wiki P0/P1.
  - Description authoring per repo conventions (no trigger-magic wording,
    front-loaded user phrases, ≤1024 chars).
- Gates: S → A → U
- [ ] Gate S: load skill `gate-probes`; `bin/check-skills`;
      `bin/check-install`; `vale`
- [ ] Gate A: fresh agent given only the skill body executes the scratch
      smoke test's first two steps (skeleton + panel prompts) correctly
- [ ] Gate U: public skill surface + the rust-design edit; also confirm
      the composition line (skill standalone vs repo-augmented) reads as
      intended
- Done when: `install-skills` deploys, wiki P0/P1 close via handoff, and
  the skill triggers on the phrases the description names.

### Stage 3: boardkit + delegation integration
- Goal: the practice is reachable from the board process without coupling.
- Changes: verify the boardkit PROCESS template type-discipline stub names
  the now-real `typed-holes` skill and degrades gracefully without it;
  add the dispatch-brief quote-block (from rust-holes templates) to the
  delegating-work skill (Plan 1 stage 4) so non-skill executors get the
  rules inline; boardkit EXTRACTION.md rows for type discipline flip from
  deferred to ported-via-skill.
- Gates: S → A
- [ ] Gate S: load skill `gate-probes`; boardkit `uv run pytest -q`;
      `vale`
- [ ] Gate A: agent review that boardkit still runs rust-free (the
      standalone guarantee)
- Done when: a boardkit-initialized Rust repo's cold agent finds its way
  from PROCESS.md to the skill to the repo in one read chain.

### Stage 4: third-instance validation (opportunistic)
- Goal: close wiki P2 when the next real Rust feature arrives; never force it.
- Changes: none up front; when a qualifying feature appears in any
  aura-family repo, run the full practice from the new repo + skills and
  record the retro as a corrective or confirmation in the wiki
  workstream.
- Gates: M
- [ ] Gate M: the feature's own gates plus a retro judged against the
      PLAYBOOK; findings recorded as correctives, never silently absorbed
- Done when: one third instance is recorded, or the workstream documents
  why none arose this cycle.

## Rollback

- Stages 1 and 3: new repo and additive doc edits; delete/revert.
- Stage 2: `install-skills` prune removes the skill; revert the
  rust-design paragraph commit.
