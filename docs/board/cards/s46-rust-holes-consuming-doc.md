---
id: S46
title: rust-holes CONSUMING.md onboarding doc
status: in-progress
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

- [ ] Gate S: rust-holes `bin/check` green (S45); vale on touched
  markdown; `docs-bustest` run recorded.
- [ ] Gate A: second-model review, focus: what would a cold reader
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
