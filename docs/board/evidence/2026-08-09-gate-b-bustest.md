# Bus Test: boardkit (Session B wave close, 2026-08-09)

Scope: the docs surface this wave changed (README, both PROCESS copies,
both _template copies, AGENTS.md and its shipped template, the board
skills) plus the standing entry docs. Method: docs-bustest skill.

Score: 19/24 (survivable)

## P1 (blocking) - fixed in this wave

- README.md: status line claimed "Nothing here is usable yet" while the
  kit runs daily boards; rewritten to "unpublished; runs from a local
  checkout". Fixed.
- AGENTS.md + AGENTS.md.template: enumerated the generated views as
  INDEX.md and board.md, omitting graph.md, so a cold agent would not
  know the new view is generated and trustworthy. Fixed in both copies.

## P2 (friction) - fixed in this wave

- README.md: no quick start; the uv/BOARDKIT_HOME bootstrap lived only
  in AGENTS.md. Added, with the same-line-prefix warning stated once
  and referenced.
- README.md: `boardkit dag` and `graph.md` were undocumented. Added to
  the resolution-and-registry section.

## P3 (polish) - logged, not fixed

- No architecture diagram; S27 (maintained flowchart) is the carded fix
  and deliberately waits for this wave's architecture to settle.
- No CHANGELOG; git history plus drain records serve today.
- No CI; the pre-commit hook and local pytest are the gate. A public
  release would need both P3s revisited.

## Agent discoverability

- AGENTS.md: exists, canonical, contract-stamped; CLAUDE.md/GEMINI.md
  are one-line shims (doctor's new entry.parity check now enforces
  this shape for consumers).
- Handoff docs: session handoffs live in the aura wiki, linked from
  drain and gate records; current.
- Competing roadmaps: no - the board is the one roadmap (INDEX.md
  generated; PLAN.md/EXTRACTION.md are provenance, not roadmaps).
- Duplication: none found; the bootstrap is stated in README and
  AGENTS.md by design (both audiences need it at first contact), all
  other facts single-homed.

## Missing docs (Diataxis)

- Tutorial: missing (P3; quick start now covers first contact).
- How-to: partial - PROCESS.md is the operating manual.
- Reference: config surface documented across README + PROCESS +
  template comments; no single reference page (P3).
- Explanation: EXTRACTION.md, drain records, and the aura plan of
  record carry the why.
