# Plan: implement the 2026-08-03 feedback-drain dispositions

Status: authored 2026-08-03 against `2fd52c6`, executed unattended in the
same session on the user's explicit directive ("start unattended"), which
is the approval for the mid-flow user gates this plan would otherwise
stop at. The final wave close still presents everything: diffs,
review verdicts, and any open findings.

## Scope

- Core problem: six accepted dispositions (D1-D6) in
  `2026-08-03-feedback-drain.md` are triaged but not implemented; the
  template contract still carries the gaps consumer sessions hit.
- Audience: consumer repos that sync the shipped templates, and board
  owners who read `resolve-route` / `dispatch-brief` output.
- Success: all six dispositions land, the full test suite passes, the
  shipped templates pass the kit's own prose gate, and every wave carries
  an adversarial review verdict from a model that did not author it.
- Non-goals: no consumer-repo edits (chore-lottery and terminalbench-aura
  re-sync on their own schedule); no new routing features beyond the
  `staging` field; no changes to the deferral-clearing semantics
  themselves (the tick still clears; D2's rejected alternative stays
  rejected).

## Verification

- Smoke test: `uv run pytest -q` green at every stage boundary (baseline
  green at `2fd52c6`); `vale` clean over
  `src/boardkit/data/templates/`; a scratch consumer fixture run of
  `boardkit resolve-route code-review` and `boardkit dispatch-brief`
  showing the staging contract in both outputs; a fixture card exercising
  the D2 phantom-deferral warning and the phase-scoped non-warning.
- Deterministic checks: `uv run pytest -q`, `uv run ruff check`, `vale
  --output line` on every markdown file each stage touches.

## Blast Radius

- Files to change: `src/boardkit/data/templates/PROCESS.md` (D3, D4, D5,
  D6), `src/boardkit/data/templates/MODEL-CLASSES.md` and
  `REVIEW-TOOLING.md.template` (D1 pre-vet and stall protocol),
  `src/boardkit/contract.py` (D1 schema), `src/boardkit/board.py` (D2
  warning), `src/boardkit/doctor.py` and `src/boardkit/brief.py` (D1
  rendering), plus `tests/` counterparts and a repo `.vale.ini` (D6).
- Existing building blocks: `deferred_gates()` already parses the
  deferral log lines and tick state D2's warning needs; `contract.py`
  already owns strict-key validation and rendering for routes, so D1 is
  one more key through an existing pipeline, not a new mechanism.
- Test coverage gaps: no test runs prose lint over the shipped templates
  (D6 adds one); no test covers a deferral-then-pass-then-unticked
  sequence (D2 adds one); golden briefs and contract fixtures will
  need regeneration when the schema and template text move.

## Delegation inventory (taken at planning time)

Author of every stage: claude-fable-5 (this session). Reviewers, all
confirmed reachable during planning:

- `fireworks-ai/accounts/fireworks/models/kimi-k3` via `opencode run`
  (listed by `opencode models`; provider constrained to fireworks-ai on
  the user's directive - the `kimi-for-coding/k3` pin in the live agent
  config is NOT the lane for this plan). Adversarial code+prose reviewer.
- `gpt-5.6-sol` via `codex exec` (pinned in `~/.codex/config.toml`,
  codex-cli 0.146.0). Adversarial reviewer; cwd at this repo, repo-native
  paths, caller-owned `timeout`.
- `fireworks-ai/accounts/fireworks/models/deepseek-v4-pro` via
  `opencode run`, prose-only lane for humanization review of reworded
  template spans.

Every reviewer model differs from the author model, so the
reviewer-differs-from-author invariant holds on every lane. Each wave is
reviewed as one digest: a single packet goes to both adversarial
reviewers, never per-file reviews.

## Implementation Stages

#### Stage 1: template wave (D3 + D4 + D5 + D6)
- Goal: the PROCESS template states the unrunnable-check rule in its
  Gate A bullet, the suppression-reason sentence on its prose-lint
  bullet, and the restate-per-gate note in its Gates section; the two
  `VerbTricolon` spans are reworded; the kit gains a prose gate over
  `src/boardkit/data/templates/` (repo `.vale.ini` plus a pytest that
  runs vale and fails loud, skipping only when the binary is absent and
  saying so).
- Changes: `PROCESS.md` template, `.vale.ini`, `tests/test_templates_prose.py`,
  test updates where template text is pinned.
- Gates: S → A
- [ ] Gate S: load skill `gate-probes`, then `uv run pytest -q`,
  `uv run ruff check`, `vale` over the templates and this plan.
- [ ] Gate A: one digest packet (diff + this plan + the drain record) to
  BOTH kimi-k3 (opencode, fireworks-ai) and gpt-5.6-sol (codex);
  deepseek-v4-pro (opencode, fireworks-ai) reviews the reworded prose
  spans only. Findings numbered, each with a resolution; empty or
  verdict-free returns are failures, never passes.
- Done when: both adversarial verdicts are recorded, findings resolved
  or logged, tests and lint green, stage committed.

#### Stage 2: deferral-clearing wave (D2)
- Goal: the PROCESS Deferrals section states the record/clear cycle, and
  `boardkit check` warns on a deferral log line followed by a pass log
  line for the same gate with its box still unticked - without firing on
  phase-scoped interim passes that never had a deferral.
- Changes: `board.py`, `PROCESS.md` template Deferrals section,
  `tests/test_deferred.py` (phantom-deferral fixture and the
  interim-pass non-warning fixture).
- Gates: S → A
- [ ] Gate S: load skill `gate-probes`, then `uv run pytest -q`,
  `uv run ruff check`, `vale` on touched markdown; run the new fixtures.
- [ ] Gate A: one digest packet to both kimi-k3 and gpt-5.6-sol, same
  rules as stage 1.
- Done when: warning fires on the phantom case, stays quiet on the
  interim-pass case, verdicts recorded, stage committed.

#### Stage 3: transport-contract wave (D1)
- Goal: `[routes.<slug>]` carries a required `staging` key
  (`working-dir` or `repo-native`), the contract version bumps to 2 with
  a migration-shaped error for v1 configs, `resolve-route` and
  `dispatch-brief` print the staging contract with the route, the
  pre-vet text in MODEL-CLASSES/REVIEW-TOOLING becomes a
  contract-shaped read probe, and the stall protocol gains the liveness
  convention (heartbeat or CPU check under the caller-owned deadline,
  bounded retry-then-switch).
- Changes: `contract.py`, `doctor.py`, `brief.py`, both template docs,
  shipped `boardkit.toml` template/fixtures, tests and goldens.
- Gates: S → A
- [ ] Gate S: load skill `gate-probes`, then `uv run pytest -q`,
  `uv run ruff check`, `vale`; scratch-fixture smoke of `resolve-route`
  and `dispatch-brief` showing the staging line; doctor error message
  check against a v1 config.
- [ ] Gate A: one digest packet to both kimi-k3 and gpt-5.6-sol, same
  rules as stage 1. This is the schema change, so the packet flags the
  version bump and migration error as the highest-risk surface.
- Done when: schema strict both ways, migration error names the fix,
  both outputs carry staging, verdicts recorded, stage committed.

#### Stage 4: wave close 🛑 USER GATE
- Goal: present the whole body of work.
- Gates: S → U
- [ ] Gate S: full suite, full lint, re-read of every touched file.
- [ ] Gate U: present per-stage diffs, all review verdicts with their
  resolutions, the highest-risk change (the contract version bump), and
  anything deferred. This is where the unattended run ends; nothing
  merges past it without the user.
- Done when: the user has the summary and the verdict record.

## Rollback

Each stage is its own commit; a failed stage reverts with `git revert
<sha>` and later stages do not start. Stage 3's version bump is the only
change with consumer-visible failure modes, and reverting its commit
restores the v1 contract exactly.
