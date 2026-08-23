---
id: S15
title: Restore the human review guide to generated packets
status: in-review
commit-range: "23dea92..d01c3a1"
depends: []
serialize-with: []
lineage: primary
executor: smart
gates: "S -> A -> U(code-review)"
user-gates: [code-review]
epic: S41
---

# S15: Restore the human review guide to generated packets

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Drain record:
[2026-08-05-feedback-drain-5.md](../../plans/2026-08-05-feedback-drain-5.md),
second entry.

## Scope

`src/boardkit/review_packet.py`, `src/boardkit/cli.py` (any new
packet flags), tests. Card frontmatter or card body conventions for
naming a typed-holes design record, if a pointer is needed.
`src/boardkit/data/templates/PROCESS.md` and `docs/board/PROCESS.md`
for the retention-contract paragraph.

## Deliverable

REVIEW.md leads with a ranked review guide instead of opening on
commit stats: churn-supersession flags are generated where mechanical
(a file rewritten by a later commit in the range is flagged so the
reader skips the superseded hunks), and the packet accepts an
author-supplied ordering for the judgment calls. The ranked order is
an entry point over an indexed packet, not the packet's one path: the
E1 user gate showed a single prescribed order does not fit every
reviewer. A card that names a typed-holes design record gets it linked
near the top of the packet, and its packet carries a type-relationship
section: which introduced types wrap, return, or consume which, as a
table or diagram derived from the design record.
The packet docs also state the ruled retention contract: packets are
regenerable working material, gitignored by init; cards and their logs
are the durable record; a repo that wants retention un-ignores the
output directory deliberately and owns the consequence.
Diff and file references in log-like packet content render as relative
markdown links so editors that follow links (the board owner reviews
in nvim/LazyVim) jump straight from a log line to the diff it names.

## Acceptance

- `uv run pytest -q` green; tests cover the guide section ordering,
  the supersession flag, and the relative-link rendering.
- A regenerated packet for a multi-commit range opens with the review
  guide, and every file reference in it resolves as a relative link
  from the packet's directory.
- A card carrying a typed-holes design record produces a packet that
  links the record above the commit listing and includes the
  type-relationship section.

## Gate checklist

- [x] Gate S: load skill `gate-probes`, then `uv run pytest -q`,
  `uv run ruff check`, `vale` on touched markdown.
- [ ] Gate A: adversarial review, focus: does the generated guide
  mislead (supersession flag hiding a hunk that still matters, rank
  order implying reviewed-first equals safe-to-skim-later)?
- [ ] Gate U (code-review): review packet to Mike, batched with the
  wave-2 Phase 2 window; stop.

## Branch

direct

## Log

- 2026-08-22 Fix round 2 landed by the same Claude executor: the
  binary flag now derives from the net pass alone (a transient binary
  reads as undone work, a binary-to-text file keeps its real net
  counts, and an entry whose understated raw count cannot account for
  its net one drops the raw figure rather than printing it); the
  rebase regex carries CommonMark link titles through byte-for-byte;
  and destinations percent-encode `%` and `#` in the path while a
  real fragment stays a fragment. Four new tests pin the reviewer's
  scenarios. Board owner re-ran the checks: `uv run pytest -q` (411
  passed), `uv run ruff check` (clean), `uv run ruff format --check`
  on touched Python (clean). Board owner also ruled on the executor's
  double-encoding flag: record link targets are literal relative
  paths, and percent-encoding round-trips them; URI-encoded author
  intent was never a supported contract.
- 2026-08-22 Gate A round 2 returned VERDICT: FAIL, in convergence:
  finding 1 verified RESOLVED with evidence; findings 2, 3, and 4
  re-raised as narrower residuals with three BLOCKING findings and no
  new scope. The residuals: the binary flag accumulates across all
  commits, so a transient binary (added then deleted) wrongly renders
  as surviving change and a binary-to-text file suppresses valid net
  counts; a title-carrying inline link does not match the rebase regex
  and stays record-relative; an angle-bracketed destination leaves `#`
  un-encoded, so a filename containing it resolves as path plus
  fragment. Reviewer: GPT 5.6-sol via the codex CLI; round spend
  100,439 tokens, cumulative 217,558. Reviewer unverified checks:
  pytest, ruff, boardkit check and doctor (sandbox denies uv cache and
  temp writes); the board owner's Gate S runs stand for them. Board
  owner accepted all three residuals; fix round 2 dispatched to the
  authoring executor. The round bound applies after this fix round: a
  written ruling precedes any further cycle.
- 2026-08-22 Commit-range extended to 23dea92..d01c3a1 to cover the
  fix commit per the fix-commit re-review duty; the packet regenerated
  over the full range and Gate A round 2 dispatched to the same
  reviewer lane with the convergence discipline in the brief.
- 2026-08-22 Fix round for the four round-1 findings landed, authored
  by the same Claude executor: the churn line reports instead of
  instructing when the card supplies a review order; binary numstat
  rows carry a flag instead of collapsing to zero, with the guide and
  the zero-total wording branching on it; lifted design-record links
  rebase from the record's directory to the packet's; and all link
  emission routes through one escaping path, which also surfaced and
  fixed git's trailing-tab guard corrupting references to filenames
  with spaces. Seven new tests, one per behavior. Board owner re-ran
  the checks: `uv run pytest -q` (407 passed), `uv run ruff check`
  (clean), `uv run ruff format --check` on touched Python (clean).
- 2026-08-22 Gate A round 1 returned VERDICT: FAIL with four BLOCKING
  findings, all in scope: the focus line ignores an author-supplied
  order and can contradict it; binary changes collapse to zero churn
  and a binary-only range renders as fully undone; a lifted
  design-record section keeps its record-relative links, which break
  from the packet directory; link labels and targets are emitted
  unescaped and legal git filenames can break them. Author of the
  diff: Claude (claude-opus executor under a claude-fable-5 board
  owner). Reviewer: GPT 5.6-sol via the codex CLI, read-only sandbox;
  round spend 117,119 tokens. Reviewer unverified checks: pytest,
  ruff, boardkit check and doctor (uv cache unreachable in its
  sandbox); the board owner's passing Gate S outputs stand for them.
  Board owner accepted all four findings; fix round dispatched to the
  authoring executor.
- 2026-08-22 Entered in-review: commit-range 23dea92..21b6c33 recorded
  and the review packet generated with the card's own new pipeline
  (first dogfood of the ranked guide on a live gate). Gate A dispatch
  to the code-review fallback lane follows; the packet presentation to
  Mike stays batched with the Phase 2 window.
- 2026-08-22 Gate S passed, run by the board owner after a two-round
  Claude-subagent execution (initial implementation, then an amendment
  round for the path:line anchor text and the card-body convention
  docs): `uv run pytest -q` (400 passed, up from 383), `uv run ruff
  check` (clean), `uv run ruff format --check` on touched Python
  (clean), `vale` on all five touched markdown files (clean),
  `boardkit check` (41 cards valid, views current), `boardkit render
  --check` (current), `boardkit doctor` (20 passed, 0 errors). Board
  owner ratified the executor's conventions: `## Design record` and
  `## Review order` as card-body sections (no frontmatter change, no
  CLI flag), the narrow supersession flag with its stated limit,
  inline-code rendering for deleted-file references, and the
  render-before-clean reorder with its regression test. Doc-sync: the
  diff updates both PROCESS copies (retention contract, card-body
  section note) and both card-template copies (the two optional
  sections); README, REVIEW-TOOLING, and MODEL-CLASSES checked and
  unaffected.
- 2026-08-22 Board owner pulled S15 for wave-2 Phase 2 and inserted the
  standing U(code-review) gate into the card's gates and checklist per
  the PROCESS code-card rule. The packet presentation batches with the
  Phase 2 user-gate window per the approved wave-2 plan.
- 2026-08-05 Minted by the fifth feedback drain from the Epoch E1
  packet regression finding.
- 2026-08-07 Scope extended by the sixth drain from the E1 user-gate
  feedback: type-relationship section for typed-holes cards, and the
  ranked order restated as an entry point rather than the one path
  ([2026-08-07-feedback-drain-6.md](../../plans/2026-08-07-feedback-drain-6.md)).
- 2026-08-09 Scope extended by the seventh drain: the packet docs carry
  the ruled ephemeral-retention contract (the D4 kit-contract half,
  interview decision 3 in
  [2026-08-09-feedback-drain-7.md](../../plans/2026-08-09-feedback-drain-7.md)).
- 2026-08-22 Joined epic S41 (co-worker consumption readiness) at
  the wave-2 Gate U (Phase 0). Grouping only; readiness unchanged.
