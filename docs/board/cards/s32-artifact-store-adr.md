---
id: S32
title: ArtifactStore ADR - receipts, postures, sidecar mechanics
status: in-review
commit-range: "3435716..bb671ca"
depends: [S28]
serialize-with: []
lineage: primary
executor: smart
gates: "S -> A -> D -> U"
user-gates: [adr-approval]
epic: S41
---

# S32: ArtifactStore ADR - receipts, postures, sidecar mechanics

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Minting record:
[2026-08-19-wave-2-plan.md](../../plans/2026-08-19-wave-2-plan.md)

## Scope

A new ADR under `docs/`; no storage code.

## Deliverable

Wave-2 decision 2 as a reviewed ADR before any storage code exists:
the ArtifactStore interface beside CardStore, the per-board posture
key (`ephemeral`, `in-repo`, `sidecar`), the receipt format (verdict,
numbered findings ledger, author and reviewer models, content
digests), sidecar mechanics and failure modes, and the outside-vetter
validation path. Ruled inputs: R-wave backfill is start-fresh plus one
receipt for the 2026-08-16 ruling (Mike, 2026-08-22 Gate U); the
per-harness machine-local pointer pattern is weighed here beside S12.

## Acceptance

- ADR accepted with its adversarial-review ledger appended; S33 cites
  it.

## Gate checklist

- [x] Gate S: `adr-review` structure checks, then `uv run pytest -q`,
  `uv run ruff check`, `boardkit check`, `boardkit render --check`,
  `boardkit doctor`, `vale` on the ADR prose.
- [ ] Gate A: adversarial prose review per the roster, ledger appended
  to the ADR.
- [ ] Gate D: drift audit before the user gate.
- [ ] Gate U: Mike approves the ADR; S33 does not start without it.

## Branch

direct

## Log

- 2026-08-23 Gate A round 2 returned VERDICT: FAIL, in convergence:
  seven of ten round-1 dispositions verified RESOLVED with file:line
  evidence (stamp, manifest, vetter wording, author_models, suffix,
  lifecycle, overlay schema); three re-raised as narrower residuals
  with no new scope. The residuals: the worked ruling receipt is
  internally contradictory (claims an empty digest table beside a
  one-row table, packets: [] carries no published field though the
  text calls published essential, and the example names a singular
  reviewer_model against the prose's no-single-reviewer rule); the
  dir: locator derives from card, gate, and round while the text
  calls publication content-addressed solely by the manifest root,
  which the locator does not contain; and OQ4's literal per-gate
  branch stays unencodable, since the decision kind is defined for
  user gates while D, M, and S receipts fit no kind without the
  format change the text says is not needed. Reviewer: GPT 5.6-sol
  via the codex CLI; round spend 132,178 tokens, cumulative 264,498.
  Unverified: pytest and the uv wrappers (sandbox limits); in-sandbox
  boardkit check, render --check, doctor, ruff, and vale all passed.
  Board owner accepted all three; fix round 2 dispatched - the bound,
  so a round 3 short of a clean pass requires a written ruling.
- 2026-08-23 Commit-range extended to 3435716..bb671ca over the fix
  commit and the packet regenerated over the full range; Gate A
  round 2 dispatched with the convergence discipline. The fix round
  survived a session-limit interruption mid-edit: the executor's
  saved progress resumed cleanly after the reset, with the
  interruption and resume both on this ledger.
- 2026-08-23 Fix round landed by the same Claude executor as bb671ca,
  all ten dispositions implemented: stamp corrected to the sha
  actually verified with all 30 anchors re-checked there (one
  re-anchored); the manifest restated as transcription checking with
  tamper-evidence assigned to git history; the vetter path reworded
  to assertion; a ruling kind whose worked R-wave receipt encodes ten
  cards and five rounds; author_models as a list with set-membership
  checking; the suffix in filename grammar and schema with packets as
  a list; a new lifecycle section (hash, write, log in one commit,
  publish outside it, the published flip as the one permitted
  mutation); the [stores.<name>] overlay schema stated against the
  strict parser; dir: backend semantics with the weaker guarantee in
  the posture table and failure rows; and OQ4 reframed as an explicit
  flagged departure from decision 2's literal per-gate wording. Board
  owner re-ran the checks: pytest 430, ruff clean, boardkit check
  green, vale clean. Correction, executor-caught: the Gate S entry
  below says nothing tracked in-repo names docs/adr/ - too broad, as
  this card's own log names it; the true gap is that no living
  contract document (AGENTS.md, PROCESS.md, README.md) states the ADR
  home, and the ADR's premise row now says exactly that.
- 2026-08-23 Gate A round 1 returned VERDICT: FAIL with ten BLOCKING
  findings, all accepted by the board owner: the verification stamp
  names 23dea92 while the anchors match the working HEAD (the
  premises were checked live; the stamp is wrong, the checks were
  not); the manifest root overclaims tamper-evidence, since it binds
  only the digest table and an editor can recompute it; the
  tracked-only vetter path says "establishes" where the design
  supports attestation; the ruling receipt cannot encode ten cards
  and five rounds in a singular schema; author_model is singular
  against multi-author ranges; PacketRef carries a suffix the
  receipt filename and schema drop; the receipt lifecycle (write
  timing, ordering against publish and log, the
  unpublished-to-published transition) is unspecified; the machine
  overlay's strict parser accepts no store keys, so the sidecar
  location has no schema to live in; the dir: transport gets none of
  the semantics the git transport gets; and OQ4 narrows decision 2's
  "per gate" without naming the departure while requiring a reviewer
  model Gate U cannot supply. Reviewer: GPT 5.6-sol via the codex
  CLI; round spend 132,320 tokens. Unverified: the uv-backed
  commands (sandbox limits); the board owner's runs stand. Board
  owner dispositions for the fix round: the stamp corrects to the
  sha actually verified with anchors re-checked there; the manifest
  restates as transcription integrity, tamper-evidence assigned to
  git history, commit signing kept as the named upgrade; ruling
  receipts take a cards list; author_models becomes a list; the
  suffix joins the filename and schema; a lifecycle section lands;
  the overlay gains a stated [stores.<name>] schema extension; dir:
  gets its semantics with the weaker guarantee stated; and receipts
  split kind review|ruling|decision with reviewer_model required
  only where a reviewer exists, the per-gate narrowing named as an
  explicit departure for Gate U to approve. Fix round dispatched to
  the authoring executor.
- 2026-08-23 Entered in-review: commit-range 3435716..ce38986 recorded
  and the review packet generated. Gate A prose review dispatches to
  the codex lane under the leaner round prompt.
- 2026-08-23 Gate S passed, run by the board owner after a
  single-round Claude executor draft and a full board-owner read of
  the ADR: structure complete against the adr-review probes (status,
  context, drivers, options with rejection reasons, outcome,
  consequences, links), `uv run pytest -q` (430 passed), ruff clean,
  `boardkit check`, `render --check`, and `doctor` green, `vale` on
  the ADR clean (the executor rewrote its ten first-pass errors
  rather than suppressing them). The ADR's 18-row premise table
  checks every existing-behavior claim against code anchors at
  23dea92, and two verified findings reshaped the design: REVIEW.md
  embeds this machine's absolute checkout path (named gap owned by
  S33, flagged to S12), and nothing tracked in-repo names docs/adr/
  as the ADR home (the pull ruling's cited routing line lives in the
  external gate-probes skill; ruling stands, gap recorded). Four open
  questions carry recommendations for Gate U: posture-key placement,
  failed-publish semantics, sidecar transport, and which gates get
  receipts.
- 2026-08-23 Board owner pulled S32 for wave-2 Phase 4 on S28's close
  (the dependency's user gate passed the same day). Board owner
  ruling at pull: the ADR home is `docs/adr/`, numbered from 0001,
  since the gate-probes routing already names that path and future
  ADRs join it. Gate A runs on the codex lane (GPT 5.6-sol) per this
  session's provider authorization; the metered lane is not proposed.
  The executor dispatch continues the leaner point-at-the-card brief
  under the dispatch-verbosity watch.
- 2026-08-22 Minted at the wave-2 Gate U (Phase 0) per the plan's
  card map; Mike approved the plan and its dispositions that day.
