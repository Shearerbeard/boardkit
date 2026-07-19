# Gate F review: codex over Phases 0-2

- Date: 2026-07-18, overnight run requested by the user.
- Scope: all four commits and the working tree at `e9e6ba2`.
- Author models under review: claude-fable-5 (orchestration, design, fixes)
  with claude-sonnet workers (Phase 1 port, Phase 2 drafts).
- Reviewer: codex CLI 0.144.5, default model (GPT-5.x family),
  `--sandbox read-only`. Different family from every author, per the
  reviewer-differs-from-author invariant.
- Reviewer verdict as returned: `GATE F: FAIL, 0 blocker / 6 major / 2 minor`.
- Caveat from the reviewer: it could not run the test suite inside its
  read-only sandbox. The board owner ran the full suite after folding in
  the fixes: pytest, ruff, and vale all clean.

## Finding ledger

F1 (major) - `boardkit check` did not enforce the WIP limit or the
serialize-with mutual exclusion that PROCESS.md documents.
Disposition: ACCEPTED, fixed. `build_board` now errors when more than two
cards are `in-progress` (`WIP_LIMIT = 2`) and when two reciprocally
serialized cards are both `in-progress`. Tests:
`test_wip_limit_enforced`, `test_serialized_cards_may_not_both_be_in_progress`.

F2 (major) - a lineage card could enter `in-review` with no `commit-range`,
deferring the failure to review-packet time.
Disposition: ACCEPTED for the validation half, fixed. `in-review` plus a
lineage other than `none` without `commit-range` is now a check error
(`test_in_review_lineage_card_requires_commit_range`). REJECTED for the
"check review packet existence" half: packets are gitignored per-machine
working material, so their existence is not a property of the board and
cannot be validated across sessions.

F3 (major) - `boardkit init` never installed the gitignore contract for the
review-packet output dir, inviting adopters to commit local diffs and paths.
Disposition: ACCEPTED, fixed. `init` now appends the output dir to the
repo's `.gitignore`, creating it if needed and preserving existing content
(`test_init_installs_review_packet_gitignore`). The absolute repo path
inside `REVIEW.md` stays: the packet is now guaranteed-ignored local
material and the path is useful there.

F4 (major) - the golden test is self-referential: regenerating the committed
fixtures with a broken renderer would bake the bug into the expectation.
Disposition: ACCEPTED with a partial fix. A public repo cannot test against
the private source board directly, so full independence is not achievable.
Added: an explicit regeneration prohibition in `tests/test_golden.py`
(fixtures may only be refreshed by re-copying from the source repo) and a
renderer-independent tripwire, `test_golden_views_match_card_population`,
which counts card files straight from the filesystem against INDEX rows.

F5 (major) - the shipped card template still carried source-project
references: a plan link `init` never scaffolds and the old script names.
Disposition: ACCEPTED, fixed. `src/boardkit/data/_template.md` is
genericized. It now names boardkit commands throughout and replaces the
plan link with an instruction. Its frontmatter contract comment reflects
the config-driven id scheme, and notes the new validations inline.

F6 (major) - PROCESS.md said all frontmatter fields are required while also
saying `commit-range` is absent before `in-review`.
Disposition: ACCEPTED, fixed. The schema intro now reads "all required
except `commit-range`", matching the validator.

F7 (minor) - config path values were not type-checked; `cards_dir = 7`
raised a raw TypeError.
Disposition: ACCEPTED, fixed. `cards_dir`, `repo`, and `output_dir` must be
non-empty strings, enforced with config errors
(`test_non_string_path_values_are_config_errors`).

F8 (minor) - MODEL-CLASSES.md promised dated examples but carried no date.
Disposition: ACCEPTED, fixed. "Examples last updated: 2026-07-18" with an
instruction to bump it on every example edit.

## Reviewer PASS areas

The reviewer explicitly passed: removal of the hardcoded private repo
default in the review-packet port, snapshot secret hygiene (placeholder
keys only, publish-strip already tracked in EXTRACTION.md), banner
normalization in the golden test (no hidden differences beyond the banner),
and working-tree cleanliness.

## Post-fix state

All eight findings dispositioned; six fixed outright, one fixed in its
valid half with the invalid half rejected with reason, one mitigated to the
limit a public repo allows. Gate S re-ran clean after the fixes (pytest,
ruff, vale), and a fresh `init` smoke verified the new gitignore behavior. The Gate F verdict stands as FAIL-then-fixed; the fix
commit needs the user's Gate U review along with Phases 1-2.
