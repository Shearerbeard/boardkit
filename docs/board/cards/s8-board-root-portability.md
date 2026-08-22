---
id: S8
title: Board-root portability and checkout-independent references
status: ready
depends: []
serialize-with: []
lineage: primary
executor: smart
gates: "S -> A"
user-gates: []
epic: S41
---

# S8: Board-root portability and checkout-independent references

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Drain record:
[2026-08-04-feedback-drain-2.md](../../plans/2026-08-04-feedback-drain-2.md),
D1.

## Scope

`README.md`, `src/boardkit/data/templates/` (where board placement is
described), `src/boardkit/review_packet.py`, `src/boardkit/doctor.py`,
tests.

## Deliverable

The machine-dir board-root pattern (`~/workspace/boards/<name>` shape,
proven by the aura family) documented as a first-class option beside
in-repo boards, with the trade-off stated: colocated boards inherit the
governed repo's branch topology, and the S59 split plus thirteen
contradictory clone statuses are the recorded cost. Review-packet
references become checkout-independent or fail detectably: a packet
path that does not resolve from the reading checkout is reported, never
silently dangled. The `reviews/` gitignore stance is decided and
recorded, not defaulted.

## Acceptance

- `uv run pytest -q` green; a test proves a dangling packet reference
  is detected and named.
- The shipped docs describe both board placements with the trade-off.
- Doctor or check reports (not fixes) a packet path that cannot
  resolve from the current checkout.

## Gate checklist

- [ ] Gate S: load skill `gate-probes`, then `uv run pytest -q`,
  `uv run ruff check`, `vale` on touched markdown.
- [ ] Gate A: adversarial review, focus: does any new path handling
  break the repo-relative digest guarantee (`contract_digest` hashes
  repo-relative paths on purpose)?

## Branch

direct

## Log

- 2026-08-04 Minted by the second feedback drain; claims verified
  against the same-day board unwind evidence.
- 2026-08-22 Joined epic S41 (co-worker consumption readiness) at
  the wave-2 Gate U (Phase 0). Grouping only; readiness unchanged.
