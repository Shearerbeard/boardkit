---
id: S33
title: Receipts and sidecar implementation per the ADR
status: in-review
commit-range: "a289224..16644f7"
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
- [x] Gate A: opencode-lane review, fresh context.
- [x] Gate M: the clean-clone digest validation and tamper test, plus
  the wave smoke test on one of this wave's own cards.
- [x] Gate D: drift audit before the user gate.
- [ ] Gate U (code-review): Mike reads the receipt as an outside
  vetter would; stop.

## Branch

direct

## Log

- 2026-08-24 Gate D passed: a fresh-context auditor (this harness's
  read-only explorer; this harness offers no cheaper in-harness class,
  so the lower-cost rule is met by context isolation rather than a
  smaller model) audited the card log against git, the implementation
  against the ADR's settled decisions, the living documents, the ADR
  premise table, and the R-wave receipt against its evidence file
  (round and findings counts, card list, `gate_ticked: false`, and the
  digest all match). The auditor re-ran the suite itself: 518 passed,
  ruff clean, check and doctor green. DRIFT AUDIT: 2 FINDINGS, both
  being the divergences already logged at Gate S (DOCKING.md does not
  document the `[stores]` overlay table; PROCESS.md gate-close prose
  does not name `close-review`/`publish-pending`); the auditor
  confirmed they are the only doc drifts. Both stand as logged
  divergences and are Gate U material for a documentation card. The
  ADR premise rows S33 made false are past-tense state under the
  table's 57b6390 stamp; no bump owed. The card waits at Gate U.
- 2026-08-24 Gate M passed, run by the board owner end to end. From a
  clean clone at /tmp/s33-clean-clone: `verify-receipt` passes 5/5 on
  A-r1, 5/5 on A-r2, and 4/4 on the R-wave ruling receipt (schema,
  manifest root, reviewer-distinctness, commit-range resolution,
  card-log agreement). From a fresh clone of the sidecar: every digest
  row in both receipts recomputes from the packet bytes at the locator
  sha, and the manifest root matches the receipt (`211cabe0...` for
  A-r2). Tamper test: one appended byte in the fetched full-range.diff
  changes the digest away from the receipt's value - detected, as
  required. The wave smoke test is this card itself: two real Gate A
  rounds closed through `close-review` with publication to the
  bk-sidecar and no hand steps, which is also acceptance criterion 1.
- 2026-08-24 Gate A passed: round 2 returned VERDICT: PASS, findings: 0,
  both round-1 dispositions verified RESOLVED with file:line evidence
  (the `author_models: []` rendering, the loud ruling/decision list
  checks, the writer round-trip test, the five ruling/decision verify
  tests), no regressions, no scope expansion. Cycle shape: round 1 FAIL
  (2 findings), fix 16644f7, round 2 PASS. Reviewer both rounds:
  GLM-5.2-Fast via the opencode lane; author: kimi-k3 coder agents in
  this harness. The close ran through the card's own tooling - the
  acceptance exercised on itself: `close-review` wrote A-r1 (FAIL,
  packet suffix r1) and A-r2 (PASS, primary packet) and published both
  to the bk-sidecar at the locators the receipts record, each receipt
  and its log line landing as one local unit. Two first-use frictions,
  logged for process feedback rather than fixed here: `close-review`
  appends its log lines at the END of the Log section (the house
  convention is newest-first), and the reviewer transcripts were copied
  into the packet directories only after publication, so they are not
  in the attested byte set - future closes should drop the transcript
  into the packet dir before running `close-review`.
- 2026-08-24 Gate A round 1 returned VERDICT: FAIL, findings: 2 (1
  BLOCKING, 1 MINOR). BLOCKING: `render_review` emitted a bare
  `author_models` key for the empty case, which parses back as None and
  aborts `close_review_round` on exactly the DEFERRED
  unestablished-authorship receipt the ADR requires - the board owner
  reproduced the YAML None parse before accepting. MINOR: no test
  exercised `verify_receipt` on ruling or decision receipts. Reviewer:
  GLM-5.2-Fast via the opencode lane (baseten provider), pre-vetted
  (echo plus staged read probe); author: this harness's coder agent, so
  the invariant holds. Dispositions: both accepted; fix round 1 landed
  as 16644f7 (empty `author_models` renders as `[]`, loud failures for
  illegitimately empty ruling/decision list fields, writer round-trip
  and ruling/decision verify tests; pytest 518 passed, ruff clean,
  re-run by the board owner). Unverified by the reviewer (no repo in
  the sandbox): pytest, ruff, `boardkit check` - the board owner's runs
  stand. Reviewer spend not captured from the plain-text opencode run;
  recovery owed at wave close. Commit-range extended to
  a289224..16644f7, packet regenerated, round 2 dispatched with the
  convergence discipline.
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
- 2026-08-24 Gate A round 1: FAIL, 2 finding(s). Reviewer glm-5.2-fast via opencode-reviewer; authors kimi-k3. Receipt: [A-r1](../receipts/S33/A-r1.md).
- 2026-08-24 Gate A round 2: PASS, 0 finding(s). Reviewer glm-5.2-fast via opencode-reviewer; authors kimi-k3. Receipt: [A-r2](../receipts/S33/A-r2.md).
