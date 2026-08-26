# Orientation canary, feedback drain 8 (2026-08-23)

Route: `canary` resolved to opencode-reviewer (adapter opencode,
working-dir staging). Model: `baseten/deepseek-ai/DeepSeek-V4-Flash-0731`
(flash class, differs from the board owner's family). Surface staged:
`INDEX.md`, `board.md`, `PROCESS.md` (no deferred view exists).

## Key (computed by `boardkit canary-key` before dispatch)

- In review: S32 (ArtifactStore ADR, at Gate U).
- In progress: none.
- Next pull: S1 (top of the ready queue). Ready queue: S1, S2, S3,
  S4, S8, S9, S10, S12, S17, S26, S38, S39, S40, S45, S47.
- Open deferred gates: none.
- Q4 static key: PROCESS.md Roles and Gates sections.

## Canary answers (verbatim)

1. "In-review: S32 (ArtifactStore ADR). In-progress: none (column
   empty)."
2. "Ready is non-empty, so the next pull is the top ready card: S1
   (Wave-close retro with snapshots and driver input)."
3. "None visible in these three files. No `Gate <X> open: deferred
   (<reason>)` log lines appear in INDEX.md, board.md, or PROCESS.md,
   and no `deferred.md` view is present (its absence reads as 'no
   deferred gates')."
4. "The board owner is the session the user has put in charge of the
   board - currently this session. It must stop for the user at every
   Gate U (present diffs/findings/risks, no proceeding without
   explicit approval), every Gate T (user testing), and at the
   standing user gates: architecture/type-design decisions,
   acceptance, baseline, launch, and milestone decisions. Every code
   card also carries a U(code-review) stop where the review packet
   goes to the user. The board owner is the only session that talks
   to the user at a gate."

## Verdict

Graded against the key: 4/4. The board, including the three cards
drain 8 minted (S45, S46, S47, all visible in the ready queue the
canary read), is legible to a cold session. PASS; no board miss, no
model-weakness miss.
