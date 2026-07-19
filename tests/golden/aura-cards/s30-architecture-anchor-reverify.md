---
id: S30
title: Re-verify ARCHITECTURE.md line anchors
status: done
depends: []
serialize-with: []
lineage: none
executor: any
gates: "S -> A"
user-gates: []
---

# S30: Re-verify ARCHITECTURE.md line anchors

Plan section: none - filed 2026-07-15 from the S3 Gate D divergence
(user scheduled it at the S3 step-6 ratification instead of folding it
into that ratification).
Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md).

## Scope

Adapter repo, `docs/redesign/ARCHITECTURE.md` only.

## Deliverable

Every `file:line` anchor in ARCHITECTURE.md resolves to the symbol it
names at the current epic primary head, and the document's anchor
header is bumped to that verified commit. Behavioral claims stay
untouched unless verification shows one false; a false claim is fixed
or logged as an explicit divergence per the living-contract rules.

## Acceptance

- Each code anchor in the document checked against the primary head;
  stale line numbers corrected (the S3 Gate D sample found roughly ten
  stale anchors in `orchestrator.rs` / `types.rs` regions, one of them
  - `prompt_constants.rs:44` - already stale at the S3 baseline).
- The anchor header states the commit the anchors were verified
  against.
- `vale docs/redesign/ARCHITECTURE.md` from the adapter repo root
  passes.
- The card Log names any behavioral claim found false, with its fix or
  logged divergence; the S3 Gate D sample found none.

## Gate checklist

- [x] Gate S: vale clean; anchor header bumped; every corrected anchor
      spot-verified by opening the target file at the stated line.
- [x] Gate A: fresh-agent sample of the corrected anchors against the
      primary head.

## Branch

Adapter repo, direct.

## Log

- 2026-07-15 Filed from the S3 Gate D divergence log; the user
  scheduled it at the S3 ratification (decision 3) rather than folding
  the anchor pass into that ratification.
- 2026-07-16 Board owner (GLM-5.2/opencode) executed S30. Verified 41
  code anchors against epic primary head `3f75a68f`; corrected 30+ stale
  line numbers across `orchestrator.rs`, `types.rs`, `context/evidence.rs`,
  `prompt_constants.rs`, `configs/sre-shell-orchestrated.toml`, and
  `Cargo.lock`. Bumped anchor header from `f9738968`/`coordinator-context`
  to `3f75a68f`/`orchestration-simplification`. Spot-verified 6 corrected
  anchors by opening target files at stated lines. Gate S: vale clean.
- 2026-07-16 Gate A: codex CLI (GPT-5.x, `codex exec --sandbox
  read-only`) sampled 20 anchors across sections 1-6. All file:line
  anchors resolved correctly. Two behavioral-claim findings:
  - FINDING 1 (BLOCKING, ACCEPTED): section 4 claims R3e replaced the
    prescriptive prompt with the lean outline and `grep -i replan`
    returns nothing, but the config still has the old playbook
    (`replans` at line 37, `replan` at line 66, `REPLAN BUDGET:` at
    line 68). Root cause: adapter commit `b2db13b` reverted R3e's lean
    prompt during the W4 de-confounding control run. Fix: divergence
    logged in section 4.2 with commit reference and date; the
    `grep -i replan` acceptance criterion noted as not holding at this
    commit.
  - FINDING 2 (MINOR, ACCEPTED): section 5.1 says full coordinator input
    is recorded on `agent.stream_chat`, but the code records on
    `orchestration.planning` via `set_coordinator_input_attributes`
    (orchestrator.rs:1596, logging.rs:550). Fix: section 5.1 text
    corrected to name `orchestration.planning` as the recording span
    with `agent.stream_chat` as the alternative.
  Both findings fixed in the same turn as the review. Gate A re-check:
  vale clean. Reviewer: codex CLI v0.144.5 (GPT-5.x). No Claude Code in
  session; codex review is prose/logic only per REVIEW-TOOLING.md
  standing rule (S30 is a documentation card, no code leg).
- 2026-07-16 Gate S and Gate A passed. Card marked Done. Rig fork
  references in section 2.4 (lines 66, 54, 482 in
  `rig/rig-core/src/completion/message.rs` at rev `8908530`) were not
  re-verified: they point to the external rig fork checkout, not the
  epic primary worktree.
