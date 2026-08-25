---
id: S33
title: Receipts and sidecar implementation per the ADR
status: in-review
commit-range: "a289224..34e9f4f"
depends: [S32]
serialize-with: []
lineage: primary
executor: smart
gates: "S -> A -> M -> D -> U(code-review)"
user-gates: [code-review]
epic: S41
---

# S33: Receipts and sidecar implementation per the ADR

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Minting record:
[2026-08-19-wave-2-plan.md](../../plans/2026-08-19-wave-2-plan.md)

## Scope

`src/boardkit/store.py` (ArtifactStore seam and posture backends),
gate-close logging, `boardkit.toml` here (`posture = sidecar`), tests.

## Deliverable

Gate closes write a compact receipt into the tracked repo and the
packet into the configured store, in the same commit as the log line.
This board flips to `posture = sidecar`.

## Acceptance

- A gate close on this board produces a tracked receipt and a sidecar
  packet without hand steps.
- Gate M ran from a clean clone: receipt digests validate against
  fetched packets, and a deliberately tampered packet fails.

## Design record

[Artifact store types](../design/s33-artifact-store-types.md) - the
typed-holes record for PacketRef, Published, StoreInfo, the receipt
schema, and the driver contracts.

## Review order

- `docs/board/design/s33-artifact-store-types.md`
- `src/boardkit/store.py`
- `src/boardkit/receipts.py`
- `src/boardkit/config.py`
- `src/boardkit/cli.py`
- `src/boardkit/doctor.py`
- `src/boardkit/review_packet.py`
- `boardkit.toml`
- `docs/board/receipts/_rulings/2026-08-16-r-wave.md`

## Gate checklist

- [x] Gate S: load skill `gate-probes`, then `uv run pytest -q`,
  `uv run ruff check`, `boardkit check`, `boardkit render --check`,
  `boardkit doctor`; `vale` on touched markdown.
- [ ] Gate A: opencode-lane review, fresh context.
- [ ] Gate M: the clean-clone digest validation and tamper test, plus
  the wave smoke test on one of this wave's own cards.
- [ ] Gate D: drift audit before the user gate.
- [ ] Gate U (code-review): Mike reads the receipt as an outside
  vetter would; stop.

## Branch

direct

## Log

- 2026-08-24 Gate S passed; the card enters in-review with commit-range
  a289224..34e9f4f and the packet generated. The executor (this
  harness's coder agent, two dispatches: the implementation, then the
  gate-close CLI wiring the board owner sent back as a scope gap)
  delivered per the accepted ADR. The board owner re-ran the checks
  itself: `uv run pytest -q` 512 passed (baseline 430), `uv run ruff
  check` clean, `boardkit check` and `render --check` current,
  `boardkit doctor` 22 passed 0 errors, vale clean on the touched
  markdown. Work commit 34e9f4f. Machine-local integration by the board
  owner: a bare sidecar at `~/dev/boardkit-sidecar.git` and the
  `[stores.bk-sidecar]` row in `.boardkit/local.toml`. Disclosed
  executor incident: an accidental `git stash`/pop mid-run, working
  tree verified identical after, suite green. Integration follow-ups
  logged, not done (outside the card's named scope): DOCKING.md's
  overlay prose does not yet mention `[stores]`, and PROCESS.md's
  gate-close prose does not yet name `close-review`/`publish-pending`.
  Gate A dispatches on the opencode lane per the session directive.
- 2026-08-24 Pulled by the board owner (a Kimi Code session) on S32's
  Gate U close; status in-progress. The spec is the accepted ADR
  (`docs/adr/0001-artifact-store.md`, accepted 2026-08-24 with OQ1-OQ4
  settled and both Gate A amendments applied). A session provider
  directive is on record with the board owner: authoring runs on this
  harness's own coder agents, gate reviews route to the opencode lane
  per the card checklist, with a second lane named for larger end-state
  gates. Executor dispatch follows; the executor makes no board writes
  and no git operations, per the roles rule.
- 2026-08-22 Minted at the wave-2 Gate U (Phase 0) per the plan's
  card map; Mike approved the plan and its dispositions that day.
