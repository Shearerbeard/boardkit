---
id: S48
title: Document stores overlay and close-review in the living docs
status: ready
depends: [S33]
serialize-with: []
lineage: primary
executor: any
gates: "S -> U(acceptance)"
user-gates: [acceptance]
epic: S41
---

# S48: Document stores overlay and close-review in the living docs

Mechanics: [PROCESS.md](../PROCESS.md).

## Scope

`docs/DOCKING.md` and `docs/board/PROCESS.md` prose only; no code
changes.

## Deliverable

Close the two doc divergences S33 logged at Gate S and Gate D
confirmed as the only drifts:

- `docs/DOCKING.md` documents the `[stores]` overlay table (the
  `.boardkit/local.toml` row that binds a store name to a location,
  e.g. the `bk-sidecar` git locator).
- `docs/board/PROCESS.md` gate-close prose names `close-review` and
  `publish-pending` as the mechanics a gate close runs through.

## Acceptance

- A fresh agent reading DOCKING.md can configure a store overlay
  without reading the source.
- PROCESS.md's gate-close description matches what the CLI actually
  does on a close.
- `boardkit check`, `boardkit render --check`, and `boardkit doctor`
  stay green; vale clean on the touched files.

## Gate checklist

- [ ] Gate S: `boardkit check`, `boardkit render --check`,
  `boardkit doctor`; `vale` on the touched markdown.
- [ ] Gate U (acceptance): Mike reads the new prose; stop.

## Branch

direct

## Log

- 2026-08-25 Minted at S33's Gate U close: the two divergences S33
  logged (DOCKING.md lacks `[stores]` overlay prose; PROCESS.md
  gate-close prose does not name `close-review`/`publish-pending`)
  were confirmed by S33's Gate D audit as the only doc drifts, and
  Mike approved this card as part of S33's Gate U.
