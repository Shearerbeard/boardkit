---
id: S15
title: Restore the human review guide to generated packets
status: ready
depends: []
serialize-with: []
lineage: primary
executor: smart
gates: "S -> A"
user-gates: []
---

# S15: Restore the human review guide to generated packets

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Drain record:
[2026-08-05-feedback-drain-5.md](../../plans/2026-08-05-feedback-drain-5.md),
second entry.

## Scope

`src/boardkit/review_packet.py`, `src/boardkit/cli.py` (any new
packet flags), tests. Card frontmatter or card body conventions for
naming a typed-holes design record, if a pointer is needed.

## Deliverable

REVIEW.md leads with a ranked review guide instead of opening on
commit stats: churn-supersession flags are generated where mechanical
(a file rewritten by a later commit in the range is flagged so the
reader skips the superseded hunks), and the packet accepts an
author-supplied ordering for the judgment calls. A card that names a
typed-holes design record gets it linked near the top of the packet.
Diff and file references in log-like packet content render as relative
markdown links so editors that follow links (the board owner reviews
in nvim/LazyVim) jump straight from a log line to the diff it names.

## Acceptance

- `uv run pytest -q` green; tests cover the guide section ordering,
  the supersession flag, and the relative-link rendering.
- A regenerated packet for a multi-commit range opens with the review
  guide, and every file reference in it resolves as a relative link
  from the packet's directory.
- A card carrying a typed-holes design record produces a packet that
  links the record above the commit listing.

## Gate checklist

- [ ] Gate S: load skill `gate-probes`, then `uv run pytest -q`,
  `uv run ruff check`, `vale` on touched markdown.
- [ ] Gate A: adversarial review, focus: does the generated guide
  mislead (supersession flag hiding a hunk that still matters, rank
  order implying reviewed-first equals safe-to-skim-later)?

## Branch

direct

## Log

- 2026-08-05 Minted by the fifth feedback drain from the Epoch E1
  packet regression finding.
