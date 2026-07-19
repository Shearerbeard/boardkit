# boardkit build plan

The phased extraction plan, recorded here so any fresh session (or fresh model)
can resume it without chat history. Update the status column in the same turn a
phase changes state. `EXTRACTION.md` holds the per-artifact source map.

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
| 1 | `boardkit` CLI: check/render/review-packet/init, boardkit.toml, golden test vs the real aura board | S, A | done |
| 2 | Process docs: PROCESS.md, MODEL-CLASSES.md, REVIEW-TOOLING template, AGENTS/CLAUDE shims | S, A, **U** | awaiting Gate U |
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
