---
id: S46
title: rust-holes CONSUMING.md onboarding doc
status: in-review
commit-range: 49b5501..f0d843d
depends: [S4]
serialize-with: []
lineage: none
executor: any
gates: "S -> A -> U(acceptance)"
user-gates: [acceptance]
epic: S41
---

# S46: rust-holes `CONSUMING.md` onboarding doc

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Drain record:
[2026-08-23-feedback-drain-8.md](../../plans/2026-08-23-feedback-drain-8.md).
External repo: `~/dev/rust-holes` (private; never publish). Plan:
`rust-holes docs/plans/2026-08-23-second-dev-readiness.md`. Depends
on S4 so the doctrine pointer it writes is the settled one; the
docking dependency was deliberately dropped at the drain (record,
item 3), and S36 owns the one-line resolution update when it lands.

## Scope

The rust-holes repo (external): new `CONSUMING.md`, one pointer line
added to `README.md`. No doctrine changes. One lean page, not a book.

## Deliverable

The document a second developer reads first: access (private GitHub
repo, collaborator grant, branch `master`, the never-publish boundary
stated for a consumer); environment prerequisites (Rust 1.81+,
nightly fmt or the stable fallback, `insta`, the `bin/check`
interpreter, two model families for the design panel); the standalone
path first (no boardkit, no skills: read order, `bin/check`, the
dispatch-brief quote blocks, friction in your own log); the family
path second (`BOARDKIT_HOME`, the FEEDBACK inbox, the commit standard
with no AI trailers); what is discoverable from where, including that
the public skill deliberately does not name this repo; the consumer
re-diff recipe against the provenance stamp; and every remaining
ask-Mike step listed explicitly (today that includes the S39/S40
gaps).

## Acceptance

- `docs-bustest` scorecard recorded, and its behavioral test passes:
  a cold human and a cold agent can each state, from this file alone,
  how to get access, what to read in what order, how to verify the
  repo, and where friction goes.
- Every remaining ask-Mike step is named in the file as exactly that.

## Gate checklist

- [x] Gate S: rust-holes `bin/check` green (S45); vale on touched
  markdown; `docs-bustest` run recorded.
- [x] Gate A: second-model review, focus: what would a cold reader
  still have to ask Mike, and is anything restated from a file that
  owns it?
- [ ] Gate U (acceptance): Mike reads it as the second developer
  would; stop.

## Branch

direct; external commits recorded in the Log as they land.

## Log

- 2026-08-23 Minted by feedback drain 8 from the rust-holes
  second-dev audit (adopted RH3 draft, adversarially reviewed there;
  S26/S36 depends dropped at the drain, see record item 3).
- 2026-08-26 S4 done, so the dependency is satisfied; pulled to
  in-progress under the cleanup execution plan. Executor lane:
  opencode on bedrock, write-only dispatch from the rust-holes
  worktree; reviewer lane: codex; Gate U is Mike's read.
- 2026-08-26 Executor (bedrock lane, write-only) landed a 51-line
  page and the README row. Board-owner repairs before Gate S: wrapped
  to 72 columns; removed a closing line that was instruction residue
  from the brief; added the clone command under Access (the audit's
  finding 2 named the clone path as appearing in no doc); reworded
  the fmt prerequisite to the post-S4 form; added the PLAYBOOK map
  pointer and "no board of its own" to the discoverability list.
  `bin/check` green (README row present), vale clean, no model ids
  or machine paths. Commit `b2f57aa` on rust-holes master; packet
  generated. The bus test and Gate A follow.
- 2026-08-26 Gate S passed. Bus test scored 18/24 (survivable), no
  P1; scorecard filed at
  [2026-08-26-s46-bus-test.md](../evidence/2026-08-26-s46-bus-test.md).
  Its four P2 items are outside this card's scope as minted and go to
  Gate U as findings rather than silent scope growth: no repo-level
  agent entry file, the fmt-gate residual from S4, the seeded harness
  not checked in, no README pointer to docs/plans. Gate A dispatched
  to the codex lane.
- 2026-08-26 Gate A round 1 (codex lane): FAIL, 3 BLOCKING + 1 MINOR,
  all ACCEPTED and repaired in `264bbe1` by the board owner: (1) the
  read order was circular (page deferred to the README table whose
  first row is the page); the page now owns the consumer read order
  and README stays the per-file table. (2) the commit standard was
  partially restated; now points at the boardkit checkout's
  PROCESS.md commit standards, keeping only the harness-trailer
  warning. (3) the publication boundary was stated more broadly than
  EXTRACTION owns it; now "never published" plus a pointer to
  EXTRACTION's Standing obligations. (4) the skill's public home was
  unnamed; now names the `Shearerbeard/claude-skills` marketplace.
  Range spans S45's `32d7eac`, which touches only `bin/check`; round
  2's prompt names it out of scope. Round 2 dispatched.
- 2026-08-26 Gate A round 2 (codex lane): FAIL, 1 BLOCKING (the
  round-1 commit-standard fix was incomplete: a trailer clause still
  restated PROCESS.md) + 1 MINOR (the read-order fix claimed README
  describes every file; it catalogs templates and examples). Both
  ACCEPTED and repaired in `f0d843d`. Second fix round; a round-3 FAIL
  takes the board-owner ruling. Round 3 dispatched.
- 2026-08-26 Gate A round 3 (codex lane): PASS, zero findings, both
  round-2 fixes verified, on `f0d843d`. Board owner re-checked:
  `bin/check` green with the README row present, page at 80 lines,
  no model ids or machine paths. Holding at in-review for Gate U:
  Mike reads the page as the second developer would. Items carried
  to that stop rather than absorbed: the four bus-test P2s, and two
  minor observations from the intent validation (template headers
  still call `../PLAYBOOK.md` the rules home after S4 made it a map;
  second-model-family access is a prerequisite but not an Ask Mike
  line).
