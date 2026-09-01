---
id: S39
title: Machine-bootstrap recipe and account inventory
status: in-review
commit-range: c3ac009..379a130
depends: []
serialize-with: []
lineage: primary
executor: smart
gates: "S -> A -> U(code-review) -> D -> U"
user-gates: [review]
epic: S41
---

# S39: Machine-bootstrap recipe and account inventory

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Minting record:
[2026-08-22-spread-readiness-hypothesis.md](../../plans/2026-08-22-spread-readiness-hypothesis.md)

## Scope

`docs/board/REVIEW-TOOLING.md` template appendix,
`src/boardkit/data/templates/`, `src/boardkit/doctor.py` (pointer
only), README.

## Deliverable

What a second machine needs and where each piece comes from: the
dotfiles opencode group, the claude-skills install, codex and agy
config, provider accounts by kind (never model ids), and the kit's
own clone URL. Cards EXTRACTION.md's never-shipped Phase 4
sibling-install obligation. The planned notanton bootstrap is the
cold-test.

## Acceptance

- A fresh machine can reach a dispatch-ready state from the recipe
  plus its own credentials; the notanton cold-test passes or its
  failures become findings here.

## Gate checklist

- [x] Gate S: `boardkit check`, `boardkit render --check`,
  `boardkit doctor`, `vale` on touched markdown.
- [ ] Gate A: adversarial prose review per the roster.
- [ ] Gate U (code-review): packet to Mike; stop.
- [ ] Gate D: drift audit before the user gate.
- [ ] Gate U: Mike reviews the recipe; stop.

## Branch

direct

## Log

- 2026-08-31 Round-bound ruling after fix round 2 (R3 re-raised
  finding 2 once more; finding 3 accepted): CONTINUE, one more fix
  round. The disagreement is ownership, not substance - the appendix
  kept a checkout-count rule and one enumerated pre-vet item, and the
  reviewer correctly reads both as another owner's facts. Fix round 3
  deletes the checkout bullet outright (the README "Second machine"
  section already states clone-once) and reduces the verification
  bullet to a bare pointer. Trajectory 8 -> 2 -> 1 findings supports
  convergence over escalation; if round 4 re-raises without new
  evidence, escalate to Mike with the ledger rather than loop.
- 2026-08-31 Gate A round 2: codex, gpt-5.6-sol. VERDICT: FAIL, 2
  findings, both re-raises of round 1 items 2 and 3 (appendix still
  enumerated pre-vet items; still asserted a README-stated clone URL).
  No new scope. Both accepted and fixed in 379a130: appendix reduced
  to lane inventory plus bare pointers, no clone-URL assertion. This
  is fix round 2 of the round bound; round 3 verifies.
- 2026-08-31 Gate A round 1: codex lane, model gpt-5.6-sol (provider
  openai; the pi lane's intended model, reached through codex after pi
  failed pre-vet on a Bedrock inference-profile routing error - pi
  resolves gpt-5.6-sol to a raw on-demand ID). Reviewer differs from
  author (GLM). VERDICT: FAIL, 8 blocking findings, all accepted and
  fixed in dbc542e: check-vs-doctor probe wording, appendix
  deduplication plus per-harness config kinds, clone-url ownership
  claim, dispatch-shaped lane probe, gitleaks-allowlisted canary
  (AWS example keys pass - verified locally; ghp_-shaped canary
  verified to trip), doctor clean-rerun requirement, two-commit split
  with named paths, canary-key/deferred.md in the orientation probe.
  Round 2 dispatched over dbc542e.
- 2026-08-31 Inserted U(code-review) into the gate ladder: the card's
  commit range touches src/ (the REVIEW-TOOLING template copy), and an
  active code-touched card carries the packet gate per PROCESS.
- 2026-08-31 Gate S passed: 518 tests green, ruff clean, vale clean
  over the touched markdown, render and check green. Card entered
  in-review over c3ac009..a52f54a (README second-machine section,
  REVIEW-TOOLING bootstrap appendix in repo copy and template, notanton
  cold-test runbook). Gate A next: pi lane per Mike's routing.
- 2026-08-31 Pulled in-progress as the notanton cold-test vehicle.
  Mike scoped the session to boardkit install and verification on
  tang-nano-cores and snes-hello (hooks, remotes, and wiki docking
  landed there by other agents; verified read-only). Pack to author:
  recipe here, notanton runbook in docs/plans/.
- 2026-08-22 Minted at the wave-2 Gate U (Phase 0) from the approved
  spread-readiness action list.
