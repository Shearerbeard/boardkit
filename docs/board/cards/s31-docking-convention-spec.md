---
id: S31
title: Versioned docking-convention spec with the three consumer postures
status: in-review
depends: []
serialize-with: []
lineage: primary
executor: smart
gates: "S -> A -> D -> U(code-review)"
user-gates: [code-review]
commit-range: "406309d..a65962e"
epic: S41
---

# S31: Versioned docking-convention spec with the three consumer postures

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Minting record:
[2026-08-19-wave-2-plan.md](../../plans/2026-08-19-wave-2-plan.md)

## Scope

A new versioned spec under `docs/`, the R5' docs it consolidates, and
`src/boardkit/data/templates/` where placement guidance ships; tests
only where template text is pinned.

## Deliverable

The `.boardkit/` docking convention as a versioned document: the
resolution order (flag, env, walk-up, common-dir fallback, legacy),
the three consumer postures (committed, gitignored, invisible via
`.git/info/exclude`) with the scale-up note that a second adopter
promotes invisible to a tracked line as a deliberate step, and the
common-dir fallback semantics. rust-holes adopts it as the second
consumer (S36); library extraction becomes a card only if the second
copy diverges.

## Acceptance

- The spec states all five resolution steps and all three postures
  with their promotion rule.
- `vale` clean; the spec carries a version and a contract stamp.
- S36 can execute from the spec alone.

## Gate checklist

- [x] Gate S: load skill `gate-probes`, then `uv run pytest -q`,
  `uv run ruff check`, `boardkit check`, `boardkit render --check`,
  `boardkit doctor`; `vale` on touched markdown.
- [ ] Gate A: adversarial review of the spec against the shipped
  resolver's actual behavior.
- [ ] Gate D: drift audit before the user gate.
- [ ] Gate U (code-review): packet to Mike; stop.

## Branch

direct

## Log

- 2026-08-22 Commit-range extended to 406309d..a65962e over the second
  fix commit, the packet regenerated, and Gate A round 3 dispatched.
  Two fix rounds are spent: a round 3 short of a clean pass requires a
  written board-owner ruling before the cycle continues.
- 2026-08-22 Fix round 2 landed by the same Claude executor:
  requirement 11 narrows to source reporting and a new requirement 12
  carries the bypass contract (outranks every step including the
  selector flag, no registry provenance, registry search from the
  board root, reports itself as the source, not-applicable escape
  mirroring the legacy step), each clause checked against cli.py
  before writing; and both skills' operational notes name doctor's two
  identifying lines for what each shows - the header line identifies
  the board, the resolved-via line names the step - quoting the line
  prefixes verbatim so the claim is checkable by running the command.
  Plugin bumped to 0.2.4. The regression's root cause is on the
  ledger: the round-1 note was written from the spec's prose instead
  of from doctor's actual output. Board owner made one direct edit,
  logged here: the preamble's scope sentence now names cli.py beside
  config.py, since requirement 12 describes CLI-layer behavior.
  Board owner re-ran the checks: pytest 417, ruff clean, vale clean.
- 2026-08-22 Gate A round 2 returned VERDICT: FAIL, in convergence:
  findings 1, 2, 4, and 5 verified RESOLVED with evidence; finding 3
  re-raised as a narrower residual (requirement 11 covers only source
  reporting, so the bypass's stated semantics - wins over every step,
  no registry provenance, registry re-search from the board root -
  are prose without a conformance requirement, and a second tool
  could rank its bypass lower and still conform); plus one
  fix-introduced regression - the skills' replacement note claims
  resolved-via confirms the board that answered, but that line names
  the source step while the board's identity is doctor's separate
  config-path header line, so the note as written could let a
  dispatch proceed unconfirmed. Reviewer: GPT 5.6-sol via the codex
  CLI; round spend 127,649 tokens, cumulative 258,908. Reviewer
  unverified: the uv-wrapped commands (sandbox cache denial);
  in-sandbox doctor, check, and render --check passed. Board owner
  accepted both; fix round 2 dispatched - the bound, so a round 3
  short of a clean pass requires a written ruling.
- 2026-08-22 Commit-range extended to 406309d..8d0801e over the fix
  commit, the packet regenerated, and Gate A round 2 dispatched with
  the convergence discipline.
- 2026-08-22 Fix round landed by the same Claude executor: the
  resolved-via vocabulary closes at six values including the bypass's
  own `--config`; the no-stale-pointer claim scopes to the two
  computed steps with the overlay named as the deliberate pointer-file
  exception; the conformance checklist grows to thirteen named
  requirements covering the selector grammar, the flag/variable
  asymmetry, default selection, the store-ref grammar, and the loud
  failures, each re-verified against config.py; the git invariant
  restates as never-consult-tracking-state at all three sites; and
  both skills drop the step enumeration for the operational note plus
  the spec pointer, with the plugin bumped to 0.2.3. Board owner
  re-ran the checks: pytest 417, ruff clean, vale clean on all six
  touched markdown files. Noted for the batch gate: the closed
  six-value resolved-via vocabulary is the one spec claim a future CLI
  flag could falsify silently; a pinned test is the candidate fix.
- 2026-08-22 Gate A round 1 returned VERDICT: FAIL with four BLOCKING
  and one MINOR finding, all in the reviewed diff: the resolved-via
  source list omits the `--config` value the CLI emits; the opening
  no-stale-pointer claim is contradicted by the local.toml overlay the
  spec itself calls a moved-overlay hazard; the eight-point
  conformance checklist omits selector grammar, default selection,
  store-ref schemes, and empty-variable semantics, so two conformant
  implementations could diverge and S36 could not execute from the
  checklist alone; the filesystem-only wording contradicts the git
  common-dir subprocess call, where the real invariant is
  never-consult-tracking-state; and the two board skills still
  enumerate the five steps beside the spec pointer, which the board
  owner had ratified and now reverses on the reviewer's
  one-fact-one-place argument. Author of the diff: Claude
  (claude-opus executor under a claude-fable-5 board owner). Reviewer:
  GPT 5.6-sol via the codex CLI; round spend 131,259 tokens. Reviewer
  unverified: pytest and the uv-wrapped commands (sandbox limits);
  in-sandbox doctor, check, and render --check all passed. Board owner
  accepted all five; fix round dispatched to the authoring executor.
- 2026-08-22 Entered in-review: commit-range 406309d..1ee9c7f recorded
  (the split with S29's concurrent doc-pair edits kept each card's
  commit to its own sections) and the review packet generated. Gate A
  dispatch to the codex lane follows; Gate D and the packet
  presentation batch with the Phase 2 window.
- 2026-08-22 Gate S passed, run by the board owner over the combined
  Phase 2 tree: `uv run pytest -q` (416 passed), `uv run ruff check`
  (clean), `vale` on all six touched markdown files (clean),
  `boardkit check`, `boardkit render --check`, and `boardkit doctor`
  all green, the AGENTS.md doc pair byte-identical, and the spec read
  in full by the board owner. The spec follows the shipped resolver
  where prose disagreed with code; the executor's eight divergence
  notes are stated inside the spec itself (the `--config` bypass, the
  flag/variable asymmetry, the manifest-not-directory walk-up rule,
  init scaffolding nothing under `.boardkit/`, the shorter
  registry-lookup path, the common-dir acceptance conditions, and the
  two doctor misfires recorded under Known limits). Board owner
  ratifications: `docs/DOCKING.md` as the spec's home (the
  consumer-scaffolded contract set is a fixed tuple in `contract.py`,
  so `docs/board/` would be a code change and posture shift);
  version-in-heading plus a `docking-spec: v1` stamp with an
  unversioned filename; and the two board-skill pointer clauses as the
  one-fact-one-place duty. Whether the spec joins `CONTRACT_DOCS` is
  deferred to the batch user gate. The doctor misfires on in-repo
  board homes are carded as S42 rather than fixed in-cycle.
- 2026-08-22 Board owner pulled S31 for wave-2 Phase 2 (the last
  Phase 2 card) and dispatched a Claude executor. WIP holds at two
  with S30 parked at Gate D; S15 and S29 sit in-review at the batched
  window.
- 2026-08-22 Minted at the wave-2 Gate U (Phase 0) per the plan's
  card map; Mike approved the plan and its dispositions that day.
