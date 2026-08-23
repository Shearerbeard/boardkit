# Agent instructions

<!-- boardkit-contract: v2 -->

This file is the canonical agent entry point for this repo, for every
harness. OpenCode reads it natively. Claude Code and Gemini sessions reach
it through a one-line shim (`CLAUDE.md`, `GEMINI.md`) that says to read this
file first.

## Read order for a fresh agent

1. `README.md`, for what this repo is and how to set it up.
2. `docs/board/PROCESS.md`, for how the card board works: schema, gates,
   roles, recovery. If this file is missing, the board was scaffolded
   incompletely; stop and tell the user instead of improvising process.
3. `docs/board/MODEL-CLASSES.md`, for which class of model may own which
   card, and the invariants that govern review.
4. `boardkit.toml` at the repo root, for where the cards directory lives.
5. Run `boardkit check`. boardkit is a Python CLI that is not published to
   a package index; it runs from a local checkout. Set `BOARDKIT_HOME` to
   that checkout's path (the default assumes it sits next to this repo) and
   run:

   ```sh
   export BOARDKIT_HOME=/path/to/boardkit
   uv run --project "${BOARDKIT_HOME:-../boardkit}" boardkit check
   ```

   `BOARDKIT_HOME` must be exported on its own line, before the `uv run`
   line. A same-line prefix - `BOARDKIT_HOME=/path/to/boardkit uv run
   --project "${BOARDKIT_HOME:-../boardkit}" ...` - expands
   `${BOARDKIT_HOME:-../boardkit}` while building the command, before the
   assignment lands, so the run silently targets the default path instead
   of the one you named. It then either fails on a directory that is not
   there or, worse, succeeds against the wrong checkout.

   It validates the card registry and confirms the
   generated views (`INDEX.md`, `board.md`, `graph.md`) are current. A clean run means
   the board state you are about to read is trustworthy; a failing run
   means fix the drift before acting on anything the views say.
6. Read the registry's `INDEX.md`, then the eligible `ready` card you are
   asked to act on. When resuming a dead or interrupted session, follow the
   Recovery protocol at the end of `PROCESS.md` instead of trusting the
   last chat transcript.

Read `docs/board/REVIEW-TOOLING.md` before running any review or delegation
tool; it pins the actual tools this repo uses and overrides generic
delegation guidance a skill might otherwise load.

## Board owner rule

The session the user puts in charge of the board is the board owner. It
runs the board end to end. Card promotion, dispatch of executors and
reviewers, gate execution, and the board's git operations are all its
responsibility. It stops for the user only at Gate U and at any standing
user gate. There
is no role question to ask; a session asked to "run the board" is the
board owner starting now, per `PROCESS.md`.

## Hygiene rule

Update a card's status and log entry in the same turn as the change they
record. Never leave a status change to be logged later. Before ending a
session that touched the board, run `boardkit check`; a session should not
close with the board in a drifted state.

## Entry files and their shims

A shim's text is a convention, not a matter of taste. It is the line
`boardkit init` scaffolds:

```
Read `AGENTS.md` first; it is the stable agent handoff for this repo.
```

A title that is only the file's own name (`# CLAUDE.md`) may stand above
it. HTML comments may sit anywhere around it, and the contract stamp is
one. Nothing else belongs in the file: put a rule in a shim and two
harnesses read different instructions out of the same checkout.

`boardkit doctor` compares each shim against that text exactly, dropping
only comment spans, that title, and whitespace differences. Reword a shim
and the `entry.parity` check warns, even when the rewording says the same
thing: doctor cannot tell a faithful rewrite from a second instruction set,
so it stops guessing and names anything that is not the stated text. The
finding is a warning, never an error, so a repo that wants its own wording
keeps it and carries the warning.
