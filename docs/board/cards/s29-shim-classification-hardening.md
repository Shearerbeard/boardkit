---
id: S29
title: Decide how strictly doctor should classify an entry-file shim
status: backlog
depends: []
serialize-with: []
lineage: primary
executor: smart
gates: "S -> A -> U(code-review)"
user-gates: [code-review]
---

# S29: Decide how strictly doctor should classify an entry-file shim

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Minted 2026-08-16 as the carded
residue of the Gate A review cycle over the R-wave; the cycle's round
ledger and the ruling that closed it are in
[2026-08-16-gate-a-review-cycle.md](../evidence/2026-08-16-gate-a-review-cycle.md).

## Scope

`src/boardkit/doctor.py` (`_is_shim` and the `entry.parity` remedy text),
`tests/test_doctor_host.py`, and whichever of `PROCESS.md` or the entry-file
templates ends up stating the shim convention. No change to what
`entry.parity` costs a board: it is a warning, never an error.

## Deliverable

A decided answer to what a shim is, rather than another heuristic patch.
`_is_shim` today accepts a file whose every substantive sentence names
AGENTS.md, after comment spans are stripped and bare file-name headings
dropped. Four adversarial rounds each found one narrower evasion of the
previous shape, which is the signature of a heuristic standing in for a
convention.

The two candidate shapes, to be chosen rather than blended:

- **Convention, checked exactly.** The kit states the shim's text and
  doctor checks for it, so anything else is flagged and the guessing
  stops. Cheap and total; costs consumers the freedom to word their own.
- **Signal, with its limits stated.** Keep a heuristic, document what it cannot
  catch, and stop treating each new evasion as a defect. Costs nothing to
  consumers; the check then advertises less than a reader assumes.

Whichever wins, the residual risk is a MISSED warning about a divergent
shim, never a false failure of a legitimate board.

## Acceptance

- `uv run pytest -q` green; the chosen shape's rule is stated in one place
  and tested against the evasions the cycle already found: a directive
  glued to a pointer sentence, a directive wearing heading syntax, prose
  after a mid-line comment close, and a sentence that names AGENTS.md
  while contradicting it.
- The shipped entry-file templates and this repo's own shims pass.
- Whichever shape is chosen, the limit it accepts is written down where a
  consumer reads it, not only in a docstring.

## Gate checklist

- [ ] Gate S: `uv run pytest -q`, `uv run ruff check`, `boardkit check`,
  `vale` on touched markdown.
- [ ] Gate A: adversarial review, focus: does the chosen shape stop the
  evasion treadmill, or does it just move the next evasion one step out?

## Branch

direct

## Log

- 2026-08-16 Minted by the board owner as the carded residue of the R-wave
  Gate A review cycle. Rounds 3 to 5 each returned exactly one new
  `_is_shim` evasion, each narrower than the last; the ruling that closed
  the cycle carded the hardening rather than iterating a sixth time. The
  concrete evasions found so far are listed in the acceptance criteria
  above and are already covered by regression tests, so this card is a
  design decision, not a bug queue.
