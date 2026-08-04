---
id: S9
title: Session-model classification and example freshness
status: ready
depends: []
serialize-with: [S1]
lineage: primary
executor: any
gates: "S -> A"
user-gates: []
---

# S9: Session-model classification and example freshness

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Drain record:
[2026-08-04-feedback-drain-2.md](../../plans/2026-08-04-feedback-drain-2.md),
D2.

## Scope

`src/boardkit/data/templates/MODEL-CLASSES.md`,
`src/boardkit/data/templates/PROCESS.md` (inventory step),
`plugins/board/skills/delegating-work/SKILL.md`, tests where template
text is pinned, installed skill copies re-synced.

## Deliverable

The delegation-inventory step gains a classify-the-session-model line
beside the provider question. The session states which capability
class it occupies - resolved against the class definitions rather than
the example lists - and the call lands in the session log. The
worked examples refresh from their 2026-07-18 vintage, and the
template states the rule for a model the examples do not name -
classify by the capability description, never stall for a user ruling
mid-session unless the classification decides board ownership. The
rejected alternative (examples chasing live pins) is recorded in the
drain record and stays rejected.

## Acceptance

- `uv run pytest -q` green; `vale` clean over touched templates.
- All three inventory copies (skill, MODEL-CLASSES, PROCESS recovery
  step) carry the classification line without drifting from each
  other.
- The examples block carries a fresh date and the absent-model rule.

## Gate checklist

- [ ] Gate S: load skill `gate-probes`, then `uv run pytest -q`,
  `uv run ruff check`, `vale` on touched files.
- [ ] Gate A: adversarial review, focus: can the classification line
  be satisfied by copying a model id into a card or brief (it must
  not be)?

## Branch

direct

## Log

- 2026-08-04 Minted by the second feedback drain; filed by a Kimi-K3
  opencode board-owner session, which is itself the classification
  case the card fixes.
