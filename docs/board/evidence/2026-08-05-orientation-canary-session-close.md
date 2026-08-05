# Orientation canary: 2026-08-05 maintainer session close

Route: cross-harness per the canary procedure - opencode, model
DeepSeek-V4-Flash-0731 (baseten), a family and harness other than the
board owner's (Claude, claude-code). Staged packet: the two views, the
Roles and Recovery sections, and the unconditional deferred.md note the
drain-3 fix prescribes (the view is absent; absence reads as no
deferred gates). Nonce readback demanded and returned (OKAPI-5518).
Caller deadline perl-alarm 300s. First dispatch returned empty (env -C
invocation) and is recorded as a failed delegation; the plain-cd retry
ran clean.

## Key (boardkit canary-key, computed pre-dispatch at 0e435e7)

- In review: none. In progress: none.
- Next pull: S1, top of the ready queue (ready: S1, S2, S3, S4, S8,
  S9, S10).
- Open deferred gates: none.
- Q4 static key: the session the user put in charge, one at a time;
  stops at every user gate, never crossing one the card log does not
  show approved.

## Canary answers (condensed to the graded claims)

1. "None. Both the In Review and In Progress sections of board.md are
   empty."
2. "S1 (Wave-close retro...) - the first ready card in INDEX.md's
   ready list."
3. "Deferred: none. deferred-note.md records that deferred.md does not
   exist, which reads as no deferred gates." (Answered outright - the
   abstention the drain-3 phrasing fix targeted did not recur.)
4. "Whichever session the user has put in charge... must stop for the
   user at every user gate... never cross a user gate the card log
   does not show as approved."

## Grade

Four of four against the key on the valid run. VERDICT: PASS. The
board with S5 and S11 closed this session reads cold across a harness
and model family other than the board owner's.
