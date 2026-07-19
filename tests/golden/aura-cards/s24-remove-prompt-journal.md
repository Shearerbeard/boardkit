---
id: S24
title: Remove the prompt-journal diagnostic
status: done
depends: [S2]
serialize-with: []
lineage: primary
executor: any
gates: "S -> A"
user-gates: []
commit-range: "3f75a68f..311b7598"
---

# S24: Remove the prompt-journal diagnostic

Mechanics: [PROCESS.md](../PROCESS.md). Required reading:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md).

User decision on the record (2026-07-12): the prompt journal is a
failed diagnostics experiment, verbose, and was never meant for OSS
consumers. Remove it rather than gate or document it; this is a
product-LOC reduction the target counts (unlike deleting the old
frame-validation tests, which only drains the informational test
bucket via S17).

## Scope

Epic primary worktree
(`/Users/mshearer/workspace/orchestration-simplification`). Remove the
`prompt_journal` module and every reference to it:

- `crates/aura/src/orchestration/prompt_journal.rs` (delete; 387
  lines, ~179 product before its bottom test module).
- `crates/aura/src/orchestration/mod.rs:57` (`mod prompt_journal;`).
- `crates/aura/src/orchestration/orchestrator.rs`: the `use` at 68,
  the `prompt_journal` struct field (390-391), the init block
  (472-505), and every `JournalPhase`/`PromptJournal` call site.
- `crates/aura/src/env_flags.rs`: drop the `AURA_PROMPT_JOURNAL` doc
  reference (and the flag if it has no other consumer).
- Doc-sync duty: the S2 harness records the worker-preamble capture
  inside `create_worker` as prompt-journal-gated (residual risk R3 in
  `context_fixture/DESIGN.md:136` and `MANIFEST.md:164`). Removing the
  journal removes that gate's only consumer; update both records so
  the residual note matches reality.

Shares `orchestrator.rs`/`mod.rs` with S3-S6 and S17; the board owner
sequences it worktree-serial with them (not encoded as serialize-with
to avoid a spurious symmetric edit across five cards).

## Deliverable

The `prompt_journal` module gone, the orchestrator free of its field
and call sites, `AURA_PROMPT_JOURNAL` retired, and the two S2 design
records updated so the R3 residual note reflects the removal.

## Acceptance

- `cargo build` and `cargo clippy -- -D warnings` are clean with no
  dead-code or unused-import warnings from the removal.
- The S2 golden-frame corpus still passes byte-identically
  (`cargo test --package aura --lib` under `INSTA_UPDATE=no`, zero
  pending snapshots): proof the request envelope is unchanged by the
  removal.
- `grep -rn 'prompt_journal\|PromptJournal\|AURA_PROMPT_JOURNAL'
  crates/aura/src` returns nothing.
- `DESIGN.md` and `MANIFEST.md` R3 residual notes updated; vale-clean.

## Gate checklist

- [x] Gate S: fmt, clippy -D warnings, the golden-frame lib tests
      byte-identical, the grep is empty, vale on the two updated docs.
- [x] Gate A: opencode rust-reviewer (GLM-5.2) reviewed the diff
      against this card's acceptance criteria. VERDICT: PASS with 3
      MINOR findings, all accepted and fixed in the same commit.
      WAIVER: PROCESS.md specifies a fresh-context Claude-family
      subagent with rust-review skill for the Gate A code leg. The
      board owner (GLM-5.2/opencode) has no Claude Code in session.
      The user directed use of the opencode rust-reviewer agent
      (GLM-5.2, same model family as the board owner) as the reviewer.
      This is an explicit per-wave waiver logged here per
      REVIEW-TOOLING.md. The friction point: the Claude Code
      rust-review requirement cannot be met from a non-Claude harness,
      and the standing rule's fallback (defer to user) was overridden
      by the user's direction to use the opencode agent.

## Branch

Local branch `card/S24` off the primary head; fast-forward promoted to
the primary (`mshearer/orchestration-simplification`) at `311b7598`;
card branch deleted after promotion. Final commit range:
`3f75a68f..311b7598`.

## Log

- 2026-07-12 Filed as backlog by the board owner from the user's
  ratification-session decision to remove the prompt journal. Depends
  on S2 so the byte-identity corpus guards the removal; blocked until
  S2 flips Done.
- 2026-07-16 Board owner (GLM-5.2/opencode) executed S24 on branch
  `card/S24` off primary head `3f75a68f`. Deleted `prompt_journal.rs`
  (387 lines), removed all references from `orchestrator.rs` (use
  import, struct field, init block, `journal_record` method, two call
  sites, comment), `mod.rs` (mod declaration), and `env_flags.rs` (doc
  reference). Fixed clippy: `worker_preamble` renamed to
  `_worker_preamble` (was only consumed by the removed `journal_record`
  call). Updated `context_fixture/DESIGN.md` R3 residual notes to
  record the journal module's removal by S24. MANIFEST.md had no
  direct prompt-journal reference to update (its R3 notes reference
  the comparison gate, not the journal). Net: 5 files changed, 9
  insertions, 445 deletions. Commit `2502ce5d`.
- 2026-07-16 Gate S passed: `cargo fmt --check` clean; `cargo clippy
  -- -D warnings` clean; `cargo test --package aura --lib` under
  `INSTA_UPDATE=no` — 841 passed, 0 failed, 0 pending snapshots
  (golden-frame corpus byte-identical); `grep -rn
  'prompt_journal\|PromptJournal\|AURA_PROMPT_JOURNAL' crates/aura/src`
  returns nothing; `vale DESIGN.md` clean.
- 2026-07-16 Gate A passed: opencode rust-reviewer (GLM-5.2, per user
  waiver logged above) reviewed the diff. VERDICT: PASS with 3 MINOR
  findings, all accepted and fixed in the amended commit:
  - F1 (MINOR, ACCEPTED): `current_iteration` AtomicUsize field was
    orphaned (sole reader was removed `journal_record`). Removed the
    field, its init, two store sites, the stale journal comment, and
    the now-unused `AtomicUsize` import. `Ordering` import also removed
    (sole remaining use at :3316 uses the full path).
  - F2 (MINOR, ACCEPTED): stale `AgentWithPreamble` doc comment
    referenced "journal recording"; updated to reference the R3
    golden-frame comparison gate.
  - F3 (MINOR, ACCEPTED): dangling `AURA_PROMPT_JOURNAL` env var in
    `compose/base.yml:74` (outside `crates/aura/src` scope). Removed.
  Re-ran Gate S after fixes: fmt, clippy, 841 lib tests, grep, vale all
  clean. Amended commit: `311b7598` (was `2502ce5d`). Net: 6 files
  changed, 11 insertions, 456 deletions. Reviewer: opencode
  rust-reviewer agent (GLM-5.2), fresh context, no implementation
  knowledge.
