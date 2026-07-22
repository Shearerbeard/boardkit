# boardkit build plan

The phased extraction plan, recorded here so any fresh session (or fresh model)
can resume it without chat history. Update the status column in the same turn a
phase changes state. `EXTRACTION.md` holds the per-artifact source map.

## Current state (update every session)

Last updated: 2026-07-21, after the audit-remediation wave.

**An audit-remediation wave has landed on top of the Gate F fixes** (commits
c83076a..dec0775). A three-worker audit against the source repo found six
process rules the extraction silently dropped, plus an untested module. The
wave restores the rules to the kit templates (standing U(code-review) gate,
wave-close cost duty, living-contract anchor/doc-sync duties, external-repo
sha duties, recovery-state-in-files, standalone prose review ledger), records
every deliberate drop in EXTRACTION.md's new "Dropped (program-specific)"
table, notes the orientation-canary hard-stop mandate on the board-hygiene
row for Phase 3, and adds direct tests for `review_packet.py` (suite 22 ->
37). Each stage passed Gate A; a codex (GPT-5.6-sol) wave review FAILed with
6 findings, all fixed in dec0775 and re-reviewed to PASS. The open Gate U
below now covers these commits too.

**Gate F has run.** At the user's request, a codex CLI review (GPT-5.x
family, different from every author model) went over Phases 0-2
adversarially. Verdict as returned: FAIL, 0 blocker / 6 major / 2 minor.
All eight findings are dispositioned and the accepted ones fixed; the full
ledger with per-finding dispositions is `reviews/2026-07-18-codex-gate-f.md`
(start there in the AM). Post-fix Gate S: pytest, ruff, and vale all clean.

**Gate U approved, 2026-07-21.** The user approved Phases 1 and 2 together,
covering the Gate F fix commit and the audit-remediation wave
(c83076a..64305fe). Phase 3 may start. What the user reviewed:

1. The CLI/config public interface: `boardkit check | render | review-packet |
   init` and the `boardkit.toml` schema (commit 31893d5). Fidelity is proven
   by the golden test in `tests/test_golden.py` (byte-identical views vs. a
   Phase 1 snapshot of the source board, cards S0-S37, banner lines excepted,
   not the live board).
2. The process docs placed by `init` (commit cec6a0f):
   `src/boardkit/data/templates/PROCESS.md` and `MODEL-CLASSES.md` are the two
   that need the user's judgment: did the generic/specific
   split keep the rules they actually run by? Supporting files:
   `REVIEW-TOOLING.md.template`, `AGENTS.md.template`, and the CLAUDE/GEMINI
   shims.
3. Known judgment calls made without the user (flag these): the smart-class
   attended policy was restored to require BOTH attendance and a
   planner-vetted wave; the case-insensitivity trap note was dropped as
   avoided-by-construction (EXTRACTION.md records the disposition change);
   `init` ships the docs now (pulled forward from Phase 4) because the
   cold-agent read order otherwise pointed at files that did not exist.

Gate S and Gate A both passed for Phases 1 and 2; the Gate A findings and
their fixes are recorded in the two commit messages. A fresh session resuming
this work: read this file, then EXTRACTION.md and the Gate F ledger in
`reviews/`, run `uv run pytest -q` to confirm green, and start on Phase 3.
The board-hygiene row in EXTRACTION.md carries the Phase 3 obligation to
restore the PROCESS-level orientation-canary hard stop along with the skill.

Standing rules for every phase:

- A docs bus test is a standing Gate S check on every doc-producing phase, not
  only at publish. The end state must be flawless from the README alone, for
  fresh human eyes and for a fresh agent.
- Gate A reviewers are fresh-context agents that never share a model with the
  author of the work they review.
- Mechanical work is delegated to worker models; orchestration, design
  decisions, gate dispatch, and final verification stay with the board-owner
  session.

## Locked decisions

- Name: boardkit. License: MIT. Audience: public/open source.
- Distribution: git repo + `boardkit init`; scripts delivered as a
  uv-installable CLI, never copied per-repo.
- Harnesses: Claude Code and OpenCode first-class; codex is a named deferral.
- Language skills (rust-*, python-*, docs-*) install as a sibling from
  claude-skills; never vendored.
- Delegation layer: authored fresh, CLI-first (`opencode run` / `codex exec`);
  supersedes the snapshotted collaborating-with-* skills for board work.

## Phases

| Phase | Deliverable | Gates | Status |
|---|---|---|---|
| 0 | Scaffold, EXTRACTION.md, snapshots of unversioned flow assets | S, A | done (commit 89a07ae) |
| 1 | `boardkit` CLI: check/render/review-packet/init, boardkit.toml, golden test vs a Phase 1 snapshot of the aura board | S, A | done |
| 2 | Process docs: PROCESS.md, MODEL-CLASSES.md, REVIEW-TOOLING template, AGENTS/CLAUDE shims | S, A, **U** | done (Gate U approved 2026-07-21) |
| 3 | Skills plugin: typed-holes (new), board-hygiene (generalized), delegating-work (CLI-first rewrite); opencode agent defs | S, A | pending |
| 4 | `boardkit init` full bootstrap: plugin install, claude-skills sibling detect, agent-def placement; temp-HOME install test | S, A, M | pending |
| 5 | Dogfood: one card through the full lifecycle in a scratch repo, Claude Code leg + attended OpenCode leg | S, A, M, **T** | pending |
| 6 | Public polish (README bus test plus the personal-data sweep and humanizer pass), then publish | S, A, **U** | pending |

U = user review gate (stop and present). T = user testing gate with a full
handout (setup commands, expected observations in order, failure signatures,
revert steps).

Phase 2's user gate reviews Phases 1 and 2 together: the CLI/config interface
plus the process docs, the generic/specific split only the author can judge.

## North star: the agent-driver conversion run

A standing, user-triggered verification step. Do not run it automatically as
part of this plan; it is token-expensive. Offer it explicitly once the
cheaper hurdles (Phases 1-5) have passed and the kit is optimized.

The run starts by snapshotting the real agent-driver-rs repo and using
boardkit to create a new board there from its final ADRs, converted into
cards. Review the resulting cards and their delegation plan, then execute a
few stages to check adherence to PROCESS.md and MODEL-CLASSES.md. This is both the acceptance test closest to
real adoption and the tuning loop for the kit's docs: every point where the
converting agent stumbles is a bus-test failure to fix.

Treat this as the north star for all phase-level decisions: anything that would
make the agent-driver conversion run harder is the wrong choice.

## Publish-gate obligations

Tracked in `EXTRACTION.md` ("Publish gate obligations"): strip `snapshots/`,
genericize or remove `tests/golden/aura-cards/` fixture content, sweep for
machine paths and account identifiers, README bus test cold-pass.
