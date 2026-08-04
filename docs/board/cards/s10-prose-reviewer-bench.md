---
id: S10
title: Prose-reviewer bench over snapshotted external prose
status: ready
depends: []
serialize-with: []
lineage: primary
executor: any
gates: "S -> A -> M -> U"
user-gates: [blind-ranking]
---

# S10: Prose-reviewer bench over snapshotted external prose

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Prior art: the 2026-08-04
ad-hoc prose canary (single-passage, five planted defects) that this
card turns into a repeatable measurement. Grounding for the failure
mode: `~/dev/claude-skills/feedback/2026-07-17-claude-code-voice-persona-hierarchy/`
and the humanizer skill's Voice Calibration section - the target prose
discipline already exists; this bench measures which models can enforce
it.

## Scope

New bench tree in this repo (`bench/prose/`: fixtures, defect
taxonomy, candidate roster config, grading script), a pytest module
for the grader's deterministic parts, and evidence files under
`docs/board/evidence/` per bench run. External reads only:
claude-skills voice materials, the git-commit and prose-lint skill
rules, and exemplar tickets from the org tracker harvested via `gh`.
No template or skill text changes ride on this card.

## Problem

External prose written on the user's behalf - commit messages and
GitHub tickets above all - drifts verbose and overly prescriptive:
stale-prone specifics, dependency versions and dates in ticket bodies,
file-by-file narration in commits, AI tells throughout. The one ticket
that escaped this (mezmo/aura #383) took hand-tuning against an
exemplar (#310) and a voice profile. Reviewer-model selection for the
prose lane currently rests on one canary run and gut feeling; the gut
feelings deserve a scoreboard.

## Deliverable

A two-lane bench, run against a roster of candidate models, producing
one scorecard per candidate.

Lane 1, planted defects (ground truth held out): ten or more short
passages seeded from a written defect taxonomy - verbosity,
over-prescription (stale-prone specifics, versions and dates where the
artifact rules forbid them, commit-body file narration), AI tells,
count contradiction, broken causality, non-sequitur, em-dash pileup -
plus at least two clean control passages seeded with nothing. Score
recall and false-positive rate per defect class against the key. The
clean controls exist because recall alone rewards a linter that flags
everything.

Lane 2, frozen real prose (no key): five or more snapshotted samples
of verbose external prose, commit messages and ticket drafts mixed,
provenance recorded per sample. Each candidate lints and rewrites
under the same contract. Three scores per candidate:

- Vale ai-tells findings per thousand words, before the rewrite and
  after it, alongside the compression ratio.
- Claim fidelity. An independent grader model diffs the factual claims
  of original against rewrite, so a candidate cannot win by gutting
  meaning.
- The user's blinded pairwise ranking, rewrites anonymized and
  position-swapped.

Harness rules:

- One prompt contract for every candidate: numbered findings, a
  mandated rewrite, an explicit verdict line.
- Staged packet with nonce readback, so an empty return records as a
  failed run rather than a zero.
- Two runs minimum per candidate per passage, measuring verdict
  stability.
- A cost and latency column in every scorecard.
- Grader models never appear on the candidate roster.

The initial roster is kept in the bench config rather than this card
so it can churn without card edits. It holds the incumbent prose
reviewer as baseline, the v4-class deepseek entry and its elder
3.1-class sibling (reachability check first), the fast GLM pin, the
5.5 and 5.6 OpenAI generations, and gemini-3.1-pro gated on funding
its gateway. The agy bridge stays off the transport list until its
empty-return defect is fixed.

## Acceptance

- Taxonomy documented; lane-1 corpus of ten-plus passages including
  the clean controls, answer key stored outside any prompt path.
- Lane-2 corpus of five-plus frozen samples with provenance lines;
  org-sourced samples flagged for the Gate U review since this repo
  may not keep them long-term.
- Grading script covers the deterministic scoring; `uv run pytest -q`
  green including the grader's own tests.
- One full bench run covering the baseline plus at least two
  candidates, scorecards filed as evidence.
- Gate U blind ranking recorded; the resulting prose-lane pin
  recommendation lands in REVIEW-TOOLING with the scorecard cited.

## Gate checklist

- [ ] Gate S: load skill `gate-probes`, then `uv run pytest -q`,
  `uv run ruff check`, `vale` on touched markdown.
- [ ] Gate A: adversarial review, focus: can a candidate top the
  scorecard while degrading meaning or over-deleting, and would the
  claim-fidelity check catch it?
- [ ] Gate M: agent runs the full bench once end to end and reports
  per-candidate scorecards plus any failed delegations.
- [ ] Gate U: user performs the blinded pairwise ranking and rules on
  the pin recommendation. 🛑 USER GATE

## Branch

direct

## Log

- 2026-08-04 Authored from the prose-canary follow-up; corpus focus
  set by the user to external prose (commits, tickets) and the
  claude-skills voice work named as grounding.
- 2026-08-04 Corpus inbox opened at `bench/prose/corpus-inbox/` so the
  user can drop samples before the card is pulled; harvest-at-pull
  from gh and git history covers the rest of lane 2.
- 2026-08-04 Capture automated: claude-skills ships `prose-corpus`
  (workflow plugin 1.2.0, claude-skills 27a50c7), which snapshots
  pre-rewrite drafts into the inbox and sunsets at this card's close.
