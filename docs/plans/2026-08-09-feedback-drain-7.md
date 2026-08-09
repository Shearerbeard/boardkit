# Feedback drain 7 (2026-08-09)

Maintainer session drain, run as SESSION B of the aura board-consolidation
plan of record
(`aura-session-docs/reports/board-consolidation-plan-of-record-2026-08-09.md`,
Gate 0 granted, Gate S signed off). Three entries drained; the inbox
empties. Mike (kit author, decision owner) was interviewed in-session on
every point the plan of record marks as maintainer discretion; the answers
below are his dispositions, recorded here as the durable record. The seven
consolidation rulings themselves live in the plan of record and its
verbatim transcript; this drain does not restate them.

Interview decisions (Mike, in-session 2026-08-09):

1. bk/S17 is EXTENDED under R5', not superseded: the convention prose and
   canary probe stand; the "real board" option becomes
   `.boardkit/boards/<code>`; the agent-driver TODO demotion lands at
   Session C.
2. The un-scoped hole-inventory entry drains now as a card; building it is
   not Session B scope.
3. Review-packet retention: ephemeral is affirmed as kit contract. Packets
   are regenerable working material, gitignored by init; cards and their
   logs are the durable record; a repo that wants retention un-ignores
   deliberately and owns the consequence. This is the kit-contract half of
   the wiki's D4; the wiki's own keep-vs-track ruling stays with Mike at
   Gate A.
4. Inbox contract: FEEDBACK.md stays the canonical intake. A maintainer
   drain MAY also sweep claude-skills `feedback/` for entries naming
   boardkit that were never mirrored, and the drain record must name
   that source when it does. This legitimizes what drains 5 and 6
   did without abandoning the inbox. The FEEDBACK.md header now states
   this.
5. R4 registry shape: the `.boardkit/manifest.toml` IS the registry. Rows
   carry short-code, scheme-prefixed location, engine, id prefix, and
   scope; `boardkit boards` reads the resolved manifest plus `local.toml`;
   family completeness is a property of the family-home repo's manifest;
   for `dir:` boards the cached row fields are verified against the
   board's own config. Board-level config stays in `boardkit.toml` at the
   board root.
6. Elaborations accepted for this sitting's v1: gates-on-edges in the
   `dag` output; `check`-level charter validation (presence and route
   resolvability only); append-log as a CardStore seam method.
   `dag --to <epic>` rides the post-R2 epic pass.
7. R2 shape: an epic is itself a card (`kind: epic`), member cards carry
   `epic: <id>` validated against it.
8. bk/S16 builds this sitting as a ride-along (it shares the view-render
   code R1/R10 rewrite).

## Drained: board-family-registry-and-short-codes (2026-08-07)

Source: `aura-session-docs/reports/board-topology-consistency-2026-08-07.md`.
Three parts, disposed separately:

- Boards registry with enumeration (R4): accepted, carded S18, shaped by
  interview decision 5 (manifest-is-registry) and the RULE-3 store-seam
  constraints (scheme-prefixed refs, id-not-filename identity).
- `boardkit render` title truncation at an inline `#` (R8/D3): accepted,
  carded S25 as an isolated bugfix. Diagnosis at drain time: an unquoted
  `#` in YAML frontmatter starts a comment, so the title dies at parse
  time and every consumer of the frontmatter sees it truncated; the fix
  belongs at parse/validation, not in the renderer.
- Inbox-bypass observation: accepted as a contract fix, disposed
  in-sitting per interview decision 4; the FEEDBACK.md header change is
  this drain's diff, no card.

## Drained: hole-inventory-not-checked (2026-08-09, opencode/kimi-k3)

Source: claude-skills
`feedback/2026-08-09-opencode-hole-inventory-drift/process-feedback.md`,
routed here by the family-inbox rule in rust-holes' FEEDBACK.md. Accepted,
carded S26: a rust-holes HOLES ledger whose rows record each hole's site,
marker id, owning card, and fill bound, plus a hook-grade check that
fails on a `todo!()` without a registered marker or a ledger row whose
hole is gone. Not built this
sitting (interview decision 2); the card sits ready for a rust-holes
maintainer pull.

## Drained: boardkit-dotdir-store-seam-graph-charters (2026-08-09)

Source: claude-skills
`feedback/2026-08-09-claude-code-boardkit-dotdir-and-graph/process-feedback.md`
and the plan of record. Six parts, disposed separately:

- (a) R5' `.boardkit/` anatomy and resolution order: accepted, folded
  into S13, which already owns discovery and carries the drain-4 record.
  S13's deliverable is rewritten to the ruled shape (manifest, in-repo
  homes, overlay, common-dir fallback, legacy fallback).
- (b) Store-seam dividing line: accepted as a binding design constraint,
  folded into S13 (CardStore interface, markdown driver #1,
  id-not-filename identity, append-log seam method) and S18 (scheme-
  prefixed manifest locations). The permanent lines - one source of truth
  per board, views non-authoritative, gates/WIP/routing kit-side - are
  restated on both cards.
- (c) R9 graph queries and renders: accepted, carded S22, including the
  gates-on-edges elaboration (interview decision 6). Epic clustering is
  explicitly out of S22's scope: R9 is not recorded complete until a
  post-R2 pass adds it.
- (d) R10 board charters: accepted, carded S20, including check-level
  presence and route-resolvability validation (interview decision 6).
  bk authors its own charter on the same card as the dogfood.
- (e) One-board-per-family bright line: accepted, folded into S20's docs
  scope (PROCESS template guidance beside the charter section).
- (f) Maintained architecture flowchart: accepted, carded S27, backlog:
  it wants the post-wave architecture to draw, so it is deliberately not
  prioritized this sitting.

## Same-sitting mints from the standing requirements doc

R1, R3, R2, and R6/R7 come from
`aura-session-docs/reports/boardkit-requirements-from-aura-2026-08-07.md`
(which the plan of record extends rather than replaces), not from inbox
entries; they are carded here so Session B's build runs on cards:

- S19: R1 lanes as first-class card data.
- S21: R3 qualified cross-board references, resolved through the S18
  registry, informational only.
- S23: R2 epics, per interview decision 7.
- S24: R6/R7 doctor ride-alongs (host-repo hazards, harness-instruction
  parity).

Ride-along card edits recorded by this drain: S15 gains the
retention-contract docs duty (interview decision 3); S17 is re-scoped
under R5' (interview decision 1); S16 is unchanged but scheduled for this
sitting (interview decision 8).
