# Orientation canary - Gate B close (2026-08-09)

Transport record: the contract's canary route (opencode-reviewer,
deepseek-v4-flash pin) stalled twice at its deadline with zero bytes on
both streams; the REVIEW-TOOLING post-stall fallback (codex lane) stalled
identically, so both external CLI transports were unreachable this
sitting. The canary ran instead as a cold Claude-harness subagent on
claude-haiku-4-5 - a different model from the board owner's, same
harness. So cross-harness legibility was NOT exercised; the
transport outage is flagged for the next session and the model swap is
recorded here rather than silently absorbed.

Surface given: the staged copies of INDEX.md, board.md, deferred.md,
PROCESS.md, and the ten in-review card files. Nothing else.

## Verdict: PASS 4/4

1. In-review/in-progress: exact match with the key (ten in-review, none
   in-progress).
2. Next pull: S1 (wave-close retro), top of ready - match.
3. Deferred gates: Gate A on all ten cards, batch-review reason quoted -
   match.
4. Board owner: "the session the user put in charge", stopping at the
   user gates (Gate U named, Gate T named) - matches the static key from
   the Roles and Gates sections.

## Key (computed by boardkit canary-key before dispatch)

# Canary key

Computed by `boardkit canary-key` from card frontmatter. Grade the
orientation canary's answers against this key, never against the
canary's own confidence. The fourth question (who owns the board,
and where must it stop) has a static key: the Roles and Gates
sections of `PROCESS.md`.

## In Review

- [S13](s13-board-discovery.md) R5' .boardkit resolution with the CardStore seam (at Gate A)
- [S16](s16-gate-position-in-views.md) Render each card's current gate position in the generated views (at Gate A)
- [S18](s18-boards-registry.md) R4 boards registry - the manifest is the registry (at Gate A)
- [S19](s19-lanes-first-class.md) R1 lanes as first-class card data (at Gate A)
- [S20](s20-board-charters.md) R10 board charters with the bk dogfood charter (at Gate A)
- [S21](s21-cross-board-refs.md) R3 qualified cross-board references (at Gate A)
- [S22](s22-dag-queries.md) R9 goal-directed dag queries with Mermaid renders (at Gate A)
- [S23](s23-epic-grouping.md) R2 epic cards and epic membership (at Gate A)
- [S24](s24-doctor-host-hazards.md) R6/R7 doctor checks - host-repo hazards and harness parity (at Gate A)
- [S25](s25-title-hash-truncation.md) R8 fix - card titles truncated at an inline hash (at Gate A)

## In Progress

- none

## Next pull

- [S1](s1-wave-close-retro.md) Wave-close retro with snapshots and driver input (top of the ready queue)

Ready queue: S1, S2, S3, S4, S8, S9, S10, S12, S14, S15, S17, S26.

## Open deferred gates

- [S13](s13-board-discovery.md) Gate A: adversarial reviews batch at the Session B boundary so the reviewer sees the whole wave; packets present at the Gate B user gate
- [S16](s16-gate-position-in-views.md) Gate A: adversarial reviews batch at the Session B boundary; packets present at the Gate B user gate
- [S18](s18-boards-registry.md) Gate A: adversarial reviews batch at the Session B boundary; packets present at the Gate B user gate
- [S19](s19-lanes-first-class.md) Gate A: adversarial reviews batch at the Session B boundary; packets present at the Gate B user gate
- [S20](s20-board-charters.md) Gate A: adversarial reviews batch at the Session B boundary; packets present at the Gate B user gate
- [S21](s21-cross-board-refs.md) Gate A: adversarial reviews batch at the Session B boundary; packets present at the Gate B user gate
- [S22](s22-dag-queries.md) Gate A: adversarial reviews batch at the Session B boundary; packets present at the Gate B user gate
- [S23](s23-epic-grouping.md) Gate A: adversarial reviews batch at the Session B boundary; packets present at the Gate B user gate
- [S24](s24-doctor-host-hazards.md) Gate A: adversarial reviews batch at the Session B boundary; packets present at the Gate B user gate
- [S25](s25-title-hash-truncation.md) Gate A: adversarial reviews batch at the Session B boundary; packets present at the Gate B user gate

## Views

Current: INDEX.md, board.md, deferred.md, graph.md.

## Canary's verbatim answers

1. **In-review cards**: S13, S16, S18, S19, S20, S21, S22, S23, S24,
   S25. **In-progress cards**: None.
2. **Next pull**: S1 (Wave-close retro with snapshots and driver input) -
   ready column is non-empty, so it is the top ready card.
3. **Open deferred gates**: Gate A on cards S13, S16, S18, S19, S20,
   S21, S22, S23, S24, S25. All wait on the same thing: adversarial
   reviews batch at the Session B boundary so the reviewer sees the
   whole wave; packets present at the Gate B user gate.
4. **Board owner**: The session the user has put in charge of the board
   (no specific session named in the files). Must stop for the user at
   Gate U (user gate, to present diffs and findings) and Gate T (user
   testing, to let the user exercise the behavior by hand).
