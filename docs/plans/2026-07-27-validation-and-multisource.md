# Plan: validation completeness and multi-source direction (Goal 3)

## Scope

- Core problem: two questions. (a) Is all the validation scripting the
  process depends on present and automated? Mostly: `boardkit check` is a
  strict superset of aura's script and has 37 tests, but enforcement is
  invocation-by-rule (no hooks), the deferred-gate queue is grepped by
  hand, and the PROCESS prose restates validator constants with nothing
  binding them. (b) Could boardkit drive or be driven by Linear instead of
  filesystem cards, and would a Linear-to-markdown sync be needed to keep
  the current steering and accuracy?
- Audience: board owners relying on `--check` as the only machine gate;
  the user deciding whether Linear enters the picture.
- Success: the remaining validation gaps have machine checks; a typed seam
  exists so a second card source is an additive change; a recorded
  decision on the Linear question.
- Non-goals: building a full Linear backend this cycle; GitHub-issues
  support (same seam, later); changing the card schema.

## Position on multi-source (the answer to the question)

Markdown-on-disk stays the canonical store. If Linear is adopted, it
enters as a synced mirror rather than a native backend. Reasons, from
the research:

- Every accuracy mechanism the process has is file-and-git shaped: the
  same-turn log rule, `commit-range` frontmatter, `Card: <ID>` trailers,
  gitignored review packets, view-drift byte-comparison, the orientation
  canary's grading key, and the recovery protocol's "the registry is the
  state" rule. A remote API as source of truth breaks the atomicity of
  "card update commits with the code change" that the steering depends on.
- Agents steer the board by editing files in the same turn as the work;
  Linear writes would be uncheckable side effects outside `--check`.
- So yes: if Linear is wanted for human visibility, a one-way
  Linear-pull sync (`boardkit sync linear`) materializing/refreshing
  markdown cards, with frontmatter carrying the Linear issue id, preserves
  the current guarantees. Writeback (status pushes to Linear) is a later,
  optional stage and always derivative of frontmatter.

## Verification

- Smoke test: `boardkit check` still byte-identical on the golden board
  after the seam refactor (pure refactor, zero behavior change).
- Deterministic: `uv run pytest -q`; new prose-constants binding test;
  golden tests unchanged without regeneration (regeneration prohibition
  holds).

## Blast Radius

- Files: `src/boardkit/board.py` (Card type, CardSource seam),
  `src/boardkit/config.py` (source discriminator design only),
  `src/boardkit/cli.py` (deferred view), `src/boardkit/review_packet.py`
  (reuse `parse_card`, killing the duplicated frontmatter parser, a
  standing defect), tests; aura side only if stage 1 backports.
- Existing building blocks: `BoardResult(cards, views)` is already the
  seam; everything downstream of `cards` is pure. `GENERATED` constant
  gates view names.
- Coverage gaps: `cli.py` subcommands, `find_config` walk, `_fail`
  formatting (add while touching).

## Implementation Stages

### Stage 1: close the validation gaps (easy lifts, both sides)
- Goal: what is rule-enforced today becomes machine-enforced where cheap.
- Changes:
  - Deferred-queue view: `boardkit render` emits a deferred-gates section
    (cards with `open: deferred` log lines and unticked boxes), replacing
    aura's hand grep; `check` includes it in drift comparison. This also
    feeds Plan 1's `canary-key`.
  - Prose-constants binding test: a test asserting the PROCESS template
    states the same WIP limit, statuses, and lineage vocabulary as
    `board.py` constants (regex over the template; fails when one moves).
  - Optional commit hook: `boardkit init` offers a pre-commit snippet
    running `boardkit check` (opt-in file, not installed silently).
  - Aura side: adopt the same pre-commit snippet for
    `cards_index.py --check` now (independent of the stage-5 migration in
    the parity plan).
- Gates: S → A
- [ ] Gate S: load skill `gate-probes`; `uv run pytest -q` with new tests
      red first then green; golden fixtures untouched
- [ ] Gate A: agent review focused on drift-check semantics (new view must
      not break existing boards mid-flight; absent section tolerated for
      boards rendered before the change)
- Done when: deferral state is a generated view, the prose/constants pair
  cannot silently diverge, and both repos can gate commits mechanically.

### Stage 2: typed card and source seam 🛑 USER GATE
- Goal: card acquisition is behind an interface; behavior byte-identical.
- Changes: replace the `_file`/`_body`-smuggling dict with a real Card
  type; extract the glob-and-parse loop into a `CardSource` (protocol with
  one filesystem implementation); move link-checking behind the source
  (it is filesystem-specific); consolidate `review_packet.py` onto
  `board.parse_card`; design (not implement) the config discriminator
  (`[board] source = "markdown"` default, per-source key sets, keeping
  unknown-key strictness per source).
- Gates: S → A → U
- [ ] Gate S: load skill `gate-probes`; `uv run pytest -q`; golden views
      byte-identical (the refactor's whole acceptance)
- [ ] Gate A: second-model review of the Card type and protocol surface
      (public interface change)
- [ ] Gate U: present the Card type, the CardSource protocol, and the
      config discriminator sketch before any second source exists
- Done when: `build_board` never touches the filesystem directly and all
  tests pass unmodified.

### Stage 3: Linear decision and spike 🛑 USER GATE
- Goal: decide, then prove, the mirror-sync shape.
- Changes: Gate U first (direction decision using the Position section
  above; options: no Linear / pull-mirror / bidirectional). If approved:
  spike `boardkit sync linear` pulling one Linear project into markdown
  cards (issue id in frontmatter, body sections mapped, statuses mapped to
  the five-status vocabulary), then `boardkit check` validates the result
  like any board. Writeback explicitly out of scope for the spike.
- Gates: U → S → A → M
- [ ] Gate U: direction decision before any code
- [ ] Gate S: load skill `gate-probes`; `uv run pytest -q` with sync-unit
      tests over recorded API fixtures (no live calls in tests)
- [ ] Gate A: agent review of the field mapping (lossy mappings named
      explicitly, never silent)
- [ ] Gate M: one real pull against a scratch Linear project; run the full
      lifecycle on a synced card; report divergences
- Done when: the decision is recorded here with its date, and (if built)
  a synced board passes `check` and one card completes the lifecycle.

## Rollback

- Stage 1: revert; views regenerate from frontmatter.
- Stage 2: revert the refactor commit; golden tests prove equivalence in
  both directions.
- Stage 3: the sync is additive; delete synced cards and the config
  section.
