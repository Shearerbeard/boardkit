# Orientation canary: S10-authoring session close (2026-08-04)

Route: `canary` resolved to opencode-reviewer per the contract; model
pin read at dispatch time from the opencode config explore agent
(a DeepSeek flash-class model on baseten). Working-dir staging, nonce
readback demanded and returned (TEAL-4471). Caller deadline via perl
alarm, 300s; the run returned well inside it.

## Key (boardkit canary-key, computed pre-dispatch)

- In review: none. In progress: none.
- Next pull: S1 (top of the ready queue; ready holds S1, S2, S3, S4,
  S5, S8, S9, S10).
- Open deferred gates: none.
- Q4 static key: one board-owner session at a time; stops at Gate U
  and the standing user gates PROCESS.md names.

## Canary answers (verbatim, condensed to the graded claims)

1. "No cards are in-review and no cards are in-progress right now."
2. "The next pull is S1 (Wave-close retro with snapshots and driver
   input) - the top card in the non-empty ready column."
3. "No gates are open and deferred."
4. "The board owner is the session the user put in charge of the
   board (exactly one at a time); it must stop for the user at every
   Gate U and at standing user gates."

## Grade

Four of four against the key, first attempt. VERDICT: PASS. The board
added this session (S10 plus the corpus inbox) reads cold across a
harness and model family other than the board owner's.
