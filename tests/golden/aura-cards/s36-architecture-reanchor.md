---
id: S36
title: Re-anchor ARCHITECTURE.md to the accepted head 7a0f0651
status: ready
depends: []
serialize-with: []
lineage: none
executor: any
gates: "S -> A"
user-gates: []
---

# S36: Re-anchor ARCHITECTURE.md to the accepted head 7a0f0651

Discharges the ARCHITECTURE.md anchor divergence the MILESTONE Gate D
audit logged and deferred to acceptance. Now that 7a0f0651 is the
accepted head, its living-contract anchors must track it. Mechanics:
[PROCESS.md](../PROCESS.md), Document accuracy over time.

## Scope

`docs/redesign/ARCHITECTURE.md` (adapter repo): the `file.rs:line`
anchors and the anchor header. Anchors are currently pinned to
`3f75a68f` (S30, 2026-07-16), twelve commits behind the accepted head;
at least one is materially wrong (`build_continuation_wrapper` cited at
`orchestrator.rs:1346`, actually near `:1263`).

## Deliverable

An S30-style re-verification pass: every cited `file.rs:line` anchor
checked against the accepted head `7a0f0651` in the primary worktree and
corrected where it drifted, and the anchor header bumped from `3f75a68f`
to `7a0f0651`. The 2026-07-18 anchor-divergence note (added by the Gate
D audit) is removed once the anchors are current.

## Acceptance

- Every `file.rs:line` anchor in ARCHITECTURE.md resolves to the cited
  symbol at `7a0f0651` (spot-check the sampled anchors against the
  worktree).
- The anchor header states `7a0f0651`.
- `vale docs/redesign/ARCHITECTURE.md` is clean.

## Gate checklist

- [ ] Gate S: anchors re-verified against `7a0f0651`; vale clean.
- [ ] Gate A: fresh-agent spot-check of the sampled anchors and header.

## Branch

Adapter repo, direct; no aura code.

## Log

- 2026-07-18 Filed Ready on MILESTONE acceptance, discharging the Gate D
  anchor divergence deferred to acceptance. Dependency-free and
  immediately workable.
