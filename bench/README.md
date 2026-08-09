# Bench lanes

A lane is the durable material for vetting one class of artifact against
a quality bar: specimens of the failure, exemplars of the target, frozen
inputs, and the hidden material that grades candidates. `bench/prose/`
is the first lane. Future lanes (commit messages, agent configs, code
review) copy this contract, not the prose lane's content.

Lanes hold material only. Run tooling, candidate rosters, and prompt
contracts belong to the run that uses them; scorecards and run logs
land in `docs/board/evidence/`, named `<date>-<lane>-<what>.md`. The
split keeps lane material reusable across runs that ask different
questions of different candidates.

## Directory contract

```
bench/<lane>/
  corpus-inbox/   defective specimens, verbatim, append-only intake
  goldens/        exemplars of the target quality, verbatim
  fixtures/       frozen repo-internal inputs, verbatim
  rubrics/        grading material: rubrics, keys, taxonomy, defect briefs
  MANIFEST.md     index of every file: role, provenance, baseline, hash
```

## Entry format

One file per sample, named `YYYY-MM-DD-short-slug.md`, body verbatim
under a provenance header. Never edit or trim a body; the bench needs
the raw artifact. Two normalizations are allowed at capture time and
no others: CRLF line endings become LF, and trailing whitespace at
end of body may drop.

```markdown
---
source: <repo, URL, or "session draft">
date: 2026-08-09
artifact: commit-message | ticket | pr-description | doc-draft | doc-excerpt | other
license: <required for third-party material; omit for own or org material>
note: <optional one-liner on why the sample is here>
---

<the prose, untouched>
```

Org-sourced and third-party material gets flagged in the MANIFEST for a
keep-or-purge ruling at the consuming card's user gate.

## Freezing

A run freezes its inputs by listing each file in MANIFEST.md with a
`shasum -a 256` content hash. Files stay where they are; the hash is
the freeze. A hash mismatch at run time means the input changed under
the run, and the run stops there.

## Hidden material

`rubrics/` never enters a candidate prompt path. Candidate packets are
staged outside this repo and assembled only from corpus, goldens, and
fixtures. Graders receive rubrics through their own staging, after the
candidates have produced output. Grader models never appear on the
candidate roster.

Defect briefs (per-fixture analysis of what is wrong and what a good
fix does) are answer-key material and live in `rubrics/`, not next to
their fixtures; a packet assembled from `fixtures/` must not be able to
pick them up by accident.

Two staging rules close the remaining leak paths. First, candidates
receive specimen BODIES only: staging strips the frontmatter header,
since its note field is written for maintainers and graders and can
spoil the defects under test. Second, fixtures sometimes embed their
own reference answer, such as a decision section or a proposal list.
The fixture's brief lists the exact excisions; the consuming run
applies that list to the staged copy while the frozen fixture stays
untouched. A fixture whose brief lists no excisions stages whole.

## Lint tiers

Verbatim dirs (corpus-inbox, goldens, fixtures) are vale-exempt in the
repo `.vale.ini`; linting a specimen corrupts it. Authored files
(rubrics, defect briefs, MANIFEST, this README) pass the ai-tells gate
like any other doc.

## What a new lane copies

Copy the directory contract, the entry format, the freeze rule, the
hidden-material rule, the lint tiers, and the evidence naming. Do not
copy another lane's taxonomy, artifact list, or roster; those are lane
content and live in that lane's rubrics and MANIFEST.

## Divergences from the S10 draft

The S10 card (`docs/board/cards/s10-prose-reviewer-bench.md`) and the
corpus-inbox README sketched this first. This contract departs where
the draft baked prose-lane and reviewer-bench specifics into the
structure:

- Role-agnostic material. S10 benches reviewer models; the first
  consumer of this contract benches writer models. The same specimens
  and goldens grade both, so rosters and prompt contracts moved out of
  the lane and into the run.
- Tooling deferred. S10 places a grading script and roster config
  inside `bench/prose/`. No shared tooling exists until a second lane
  proves a shared shape; until then each run scripts itself and files
  the results as evidence.
- Goldens and fixtures added. Grading writers needs exemplars of the
  target and controlled dirty inputs alongside the defect corpus.
- Hash freeze instead of file moves. The inbox keeps its name and its
  feeders (the prose-corpus capture skill); freezing is a MANIFEST
  property, not a relocation.
- License field added to the entry header, since goldens include
  third-party excerpts.
