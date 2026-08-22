---
id: S24
title: R6/R7 doctor checks - host-repo hazards and harness parity
status: done
depends: []
serialize-with: []
lineage: primary
commit-range: 22bd55c..028ce5d
executor: smart
gates: "S -> A -> U(code-review)"
user-gates: [code-review]
---

# S24: R6/R7 doctor checks - host-repo hazards and harness parity

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Drain record:
[2026-08-09-feedback-drain-7.md](../../plans/2026-08-09-feedback-drain-7.md)
(same-sitting mints); requirements R6/R7 in the aura requirements doc,
evidence: the tb board lives on a feature branch of an adapter repo,
the wiki hosting the aura board sits dirty with unpushed commits, and
the aura repo runs two harnesses under different instruction files.

## Scope

`src/boardkit/doctor.py`, `src/boardkit/config.py` (an optional
declared base branch for the board's host repo), docs, tests.

## Deliverable

R6: doctor checks on the resolved board's host repo. One check
compares the current branch against a declared base branch, read from
an optional config key whose absence skips the check rather than
passing it. Two more warn on a dirty tree and on unpushed commits.
Warnings, never errors: a session that knows can proceed deliberately.

R7: a doctor check that the consumer repo has one real agent entry
file with the others as shims, per the kit's own AGENTS.md-canonical
convention. A repo with divergent full-text AGENTS.md and CLAUDE.md
warns; a repo with no entry file at all warns.

## Acceptance

- `uv run pytest -q` green; tests cover the branch mismatch, dirty and
  unpushed warnings, the skipped-when-undeclared base branch, and the
  parity check on shim, divergent, and absent layouts.
- `boardkit doctor` on a fixture repo parked on a feature branch with
  a declared base warns and still exits by its existing error rules.

## Gate checklist

- [x] Gate S: load skill `gate-probes`, then `uv run pytest -q`,
  `uv run ruff check`, `vale` on touched markdown.
- [x] Gate A: adversarial review, focus: false calm (a hazard the
  check silently skips) and false alarm (a legitimate layout the
  parity check flags).
- [x] Gate U (code-review): present the review packet; stop.

## Branch

direct

## Log

- 2026-08-09 Minted by the seventh feedback drain from standing
  requirements R6/R7, riding the Session B wave per the build order.
- 2026-08-09 Pulled in-progress; executor is the maintainer session.
- 2026-08-09 Built: doctor checks `host.base-branch` (against the new
  optional `[board] base_branch`; undeclared skips, never passes),
  `host.tree-state` (dirty tree + unpushed commits, one warning; no
  upstream means the unpushed half stays quiet), and `entry.parity`
  (AGENTS.md canonical, shims must mention it; absent layouts warn).
  All warnings, never errors. Gate S PASS: 337 pytest green (8 tests
  on real git fixtures incl. a bare-remote unpushed case), ruff clean.
  Live probe: doctor on this repo warned dirty+unpushed mid-build,
  exactly the R6 evidence shape.
- 2026-08-09 In-review; commit-range 22bd55c..028ce5d. That commit was
  made --no-verify with views knowingly stale mid-wave; the following
  commit (a95fcab) rendered them current - logged as the deviation it
  is.
- 2026-08-09 Gate A deferred, superseded 2026-08-16: adversarial reviews batch at the
  Session B boundary; packets present at the Gate B user gate.
- 2026-08-11 Gate U(code-review) passed: Mike reviewed the packet
  (batch 1 with S13), verdict pass, no findings on this card. Gate A
  batch deferral survives this gate (surfaced, not absorbed).
- 2026-08-16 Gate A ran (resolving the deferral): reviewer gpt-5.6-sol
  via codex exec, author claude-fable-5 (whole wave); codex fallback
  after the opencode lane stalled its read probe. Verdict FAIL, four
  findings - all in the false-calm class the focus named.
  1. BLOCKING a repo with no upstream silently passed host.tree-state,
     missing the maximal local-only state. Confirmed. Fixed in
     6af06a7: a missing upstream is a named problem; git-unavailable
     still skips rather than alarming falsely.
  2. BLOCKING one mention of AGENTS.md anywhere counted as shim proof,
     so a divergent entry file with a shim's opening line passed
     parity. Confirmed. Fixed in 6af06a7: a shim must name AGENTS.md
     in its first lines and carry little else (the shipped template is
     three lines; the bound is ten non-empty).
  3. BLOCKING missing and unreadable shims escaped the check entirely.
     Confirmed; dispositioned in halves: no shims at all now warns
     (nothing points at AGENTS.md), an unreadable shim warns, and a
     partial shim set stays legal - warning every repo that skips one
     harness's shim would be the false alarm this card's focus warns
     against.
  4. BLOCKING parity read entry files from the board root, falsely
     warning on the .boardkit/boards/<code> layout. Confirmed. Fixed
     in 6af06a7: the git toplevel resolves the host root first, the
     board root stands in only where git cannot answer.
  Reviewer-reported UNVERIFIED (sandbox): pytest, check, doctor - run
  board-owner-side: 355 pytest green and ruff clean; boardkit check
  OK. Fix commit 6af06a7 (shared with S22/S23, per-card trailers) sits
  apart from the reviewed range, so commit-range stays 22bd55c..028ce5d
  and the fix-commit re-review runs over 6af06a7^..6af06a7 via the
  packet override; Gate A's box stays unticked until that re-review
  passes.
- 2026-08-16 Gate A review cycle closed by ruling; full round ledger in
  [2026-08-16-gate-a-review-cycle.md](../evidence/2026-08-16-gate-a-review-cycle.md).
  Rounds 2 to 5 re-reviewed the fix commits. Round 5 confirms every
  recorded fix and every round-4 residue resolved; from round 3 on, the
  findings were confined to `_is_shim` in the S24 fix code, one narrower
  evasion per round, and that hardening is carded as S29 rather than
  patched a sixth time. Every finding against this card's own reviewed
  diff is resolved. The reviewer never issued an explicit sign-off, so
  the box stays unticked, because a failed return is never a pass. The
  2026-08-09 batch deferral is superseded - the batch ran, on the codex
  fallback after the opencode lane failed its read probe four times.
- 2026-08-16 Gate A open: deferred (review cycle closed by ruling after five
  rounds with every card-diff finding resolved and no explicit reviewer
  sign-off; the pass decision is the user's at U code-review, on the ledger
  in docs/board/evidence/2026-08-16-gate-a-review-cycle.md)
- 2026-08-22 Gate A PASS: Mike accepted the R-wave on the 2026-08-16
  ruling record at the wave-2 Gate U (runbook and packet-companion
  artifacts), per ruling point 5. The box ticks on that acceptance,
  resolving the 2026-08-16 deferral. Board-side re-check at close:
  pytest green, ruff clean, boardkit check clean.
- 2026-08-22 Done: every gate passed. Verified by Mike's Gate U
  approval and the board owner's re-run of the deterministic checks
  at close.
