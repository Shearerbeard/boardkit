# Feedback drain 6 (2026-08-07)

Maintainer session drain of three entries inboxed after the fifth
drain, all filed by claude-code sessions: two from the epoch-board E1
review and its tracking canary, one from an aura-orchestration-mode
session reading agent-driver-rs. All three are accepted; one amends an
existing card (S15) and two become cards S16 and S17.

## Drained: review-packet-type-relationships (accepted, folded into S15)

Source: epoch-board `docs/board/cards/e1-foundation-type-surface.md`,
the 2026-08-06 user-gate log entry. The user approved E1 off the
hand-written guide but flagged two packet gaps: the single ranked
reading order was not the format they would have chosen, and a
type-surface card's packet showed no view of how the introduced types
relate (wraps, returns, consumes).

Disposition: S15 already owns packet restoration and has not started,
so this rides that card rather than minting a new one. S15's
deliverable gains a type-relationship section for cards with a
typed-holes design record, and the guide requirement is restated so
the ranked order is an entry point over an indexed packet rather than
the packet's one path.

## Drained: index-shows-gate-ladder-not-position (accepted, carded S16)

Source: epoch-board `docs/board/retro/2026-08-06-e9-tracking-canary.md`.
The generated views render each card's gate ladder verbatim but never
its current position, so a cold reader cannot tell which gate an
in-review card is parked at; a canary guessed Gate A where Gate U was
the answer, and the data to answer correctly (`- [x]` checklist state)
already lives in the card. Card S16: render gate position in the
generated views.

## Drained: satellite-repo-todo-looks-canonical (accepted, carded S17)

Source: claude-skills
`feedback/2026-08-07-claude-code-agent-driver-unboarded-todo/process-feedback.md`.
A repo-level TODO.md self-declared "the canonical active roadmap"
inside a boarded workstream, so a session derived a DAG from it that
inverted priorities; the driving goal had no entry on any surface.
Card S17: a satellite-repo convention (a real board, or a demoted
TODO.md that names the driving goal and marks itself an enhancement
backlog) plus a canary probe for canonical-roadmap claims outside the
board.
