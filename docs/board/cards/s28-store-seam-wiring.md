---
id: S28
title: Wire the CLI core through the CardStore seam
status: done
commit-range: "9b1c158..decedc3"
depends: []
serialize-with: []
lineage: primary
executor: smart
gates: "S -> A -> D -> U(code-review)"
user-gates: [code-review]
---

# S28: Wire the CLI core through the CardStore seam

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Minted from S13's Gate A
finding 4 (2026-08-16): the seam landed as an interface with driver-level
tests, but no production module imports it - `build_board` still walks
markdown directly, the protocol lacks the board-metadata surface the S13
deliverable names, and `put` stayed deferred (no caller, no
format-preserving serialization; S13 log, 2026-08-09).

## Scope

`src/boardkit/store.py` (board metadata on the protocol; `put` if and
only if a caller lands with it), `src/boardkit/board.py` and
`src/boardkit/cli.py` (route card traversal through a store constructed
from the resolved config), tests. No behavior change to views, check
output, or the resolution order.

## Deliverable

The CLI core reads cards through a CardStore constructed at resolution
time, with the markdown-dir layout as driver #1 behind the seam rather
than beside it. Board metadata (the config surface a second driver would
need) is defined on the protocol. `put` lands only with its first real
caller; if it stays deferred, this card's log says so and why.

## Acceptance

- `uv run pytest -q` green; a test constructs the store from a resolved
  config and `build_board` (or its successor path) consumes it.
- `grep -rn "from boardkit.store" src/` shows at least one production
  import; the golden views stay byte-identical.
- `uv run ruff check` clean.

## Gate checklist

- [x] Gate S: load skill `gate-probes`, then `uv run pytest -q`,
  `uv run ruff check`, `boardkit check`, `boardkit render --check`,
  `boardkit doctor`; golden-view comparison.
- [x] Gate A: adversarial review, focus: does the seam actually
  invert the dependency (could a second driver be written without
  touching board.py), or does every caller still reach the markdown
  traversal directly?
- [x] Gate D: drift audit of the living documents that describe the
  store seam before the user gate.
- [x] Gate U (code-review): packet to Mike; stop.

## Branch

direct

## Log

- 2026-08-23 Gate U (code-review) passed: Mike reviewed the Phase 3
  packet and accepted the card with a plain pass; the four
  board-owner rulings stand as logged. Card done.
- 2026-08-23 Gate D passed: a fresh small-class Claude auditor with
  no implementation context swept DOCKING.md, REVIEW-TOOLING.md,
  PROCESS.md, AGENTS.md, and README.md against the seam change and
  returned DRIFT AUDIT: CLEAN with zero findings. Evidence:
  [2026-08-23-s28-gate-d.md](../evidence/2026-08-23-s28-gate-d.md).
  The card now waits at its U(code-review) gate.
- 2026-08-23 Gate A passed. Round 2 verified the disposition RESOLVED
  with file:line evidence (the store passed at cli.py:486-495,
  id-only resolution through store.load_cards, the substitute-store
  pin, and an in-memory handoff probe the reviewer ran itself) and
  returned an explicit zero-findings VERDICT: PASS. Cycle shape:
  round 1 FAIL (1 BLOCKING), round 2 PASS - closed inside the
  two-fix-round bound. Author of the reviewed range: Claude
  (claude-opus executor under a claude-fable-5 board owner). Reviewer
  both rounds: GPT 5.6-sol via the codex CLI, read-only sandbox,
  under the leaner round prompts of the dispatch-verbosity watch.
  Reviewer spend: 97,427 + 92,424 = 189,851 tokens. Unverified in
  round 2: pytest, ruff, boardkit check and doctor (sandbox limits);
  the board owner's runs stand (430 passed). Review record: prompts
  and outputs for both rounds in the packet directory. Gate D follows
  before the user gate.
- 2026-08-23 Commit-range extended to 9b1c158..decedc3 over the fix
  commit and the packet regenerated over the full range; Gate A
  round 2 dispatched with the convergence discipline.
- 2026-08-23 Fix round landed by the same Claude executor as decedc3:
  the packet's card lookup resolves through the CLI-resolved store by
  declared id (`resolve_card` over `store.load_cards`), deleting the
  last cards-directory glob outside the store and the packet's own
  frontmatter parser; `cmd_review_packet` now resolves the board
  context and passes its store; a substitute-store test pins the path
  (a card served by the store while a different card sits on disk).
  Board owner re-ran the checks: pytest 430, ruff clean, check,
  render --check, and doctor green, golden views byte-identical.
  Board owner rulings on the executor's notes: the two reworded
  packet error messages stand (the filename stopped voting on
  identity; the card's no-behavior-change list - views, check output,
  resolution order - is untouched), and schema errors stay non-fatal
  in `resolve_card` (a malformed sibling card must not block every
  packet on the board; the strict path remains `get_card`). The
  rendered-output path arithmetic the executor reported (packet and
  brief display links built from `_file`) is a real residual for a
  follow-up, not a lookup bypassing the seam.
- 2026-08-23 Gate A round 1 returned VERDICT: FAIL with one BLOCKING
  finding, verified by the board owner at both cited sites:
  `cmd_review_packet` resolves a bare config and `build_review_packet`
  calls `load_card` on the cards directory, so the review-packet path
  bypasses the seam a second driver would need - and the phase's
  done-when names review-packet running through the seam.
  review_packet.py joins the card's scope as a logged extension on
  that ground. Reviewer: GPT 5.6-sol via the codex CLI, read-only
  sandbox; round spend 97,427 tokens under the leaner round prompt.
  Unverified: pytest, the boardkit commands, and golden-view execution
  (sandbox limits); the board owner's Gate S runs stand. Board owner
  accepted the finding; fix round dispatched to the authoring
  executor.
- 2026-08-23 Entered in-review: commit-range 9b1c158..79c2d71 recorded
  and the review packet generated. Gate A dispatch to the codex lane
  follows, with the leaner round prompt under the dispatch-verbosity
  watch; Gate D and the user gate follow the cycle per the phase
  ladder.
- 2026-08-23 Gate S passed, run by the board owner after a
  single-round Claude executor implementation under the leaner
  dispatch brief: `uv run pytest -q` (429 passed, up from 424),
  `uv run ruff check` (clean), `boardkit check` (44 cards valid),
  `boardkit render --check` (views current), `boardkit doctor` (20
  passed; warnings only the standing next-id note and the then-dirty
  tree), and the golden-view comparison byte-identical (all three
  views hashed before and after; render --check re-proves the bytes).
  Board owner rulings on the executor's open questions: `put` stays
  deferred - the wiring that landed is the read half, so it produced
  no writer, and the 2026-08-09 reason (no format-preserving
  serialization) is unchanged; `transition` and `append_log` remain
  caller-less with it. The `store=None` default on `build_board`
  stands - it delegates to `open_store`, the declared single
  choice-point, and removing it would push mechanical wiring into
  doctor.py and brief.py outside the card's scope for no inversion
  gain; Gate A is invited to probe it. Noted, not fixed: `parse_card`
  and `card_file_pattern` still live in board.py though only the
  driver calls them - a clean follow-up if a reviewer or a later card
  wants the purist split.
- 2026-08-23 Board owner pulled S28 for wave-2 Phase 3 and aligned the
  card with the plan's phase ladder: Gate D and the standing
  U(code-review) gate joined the checklist, and Gate S extended to the
  plan's probe list with the golden-view comparison. Gate A runs on
  the codex lane (GPT 5.6-sol) per this session's provider
  authorization; the plan's opencode naming predates it. The executor
  dispatch uses the leaner point-at-the-card brief under the
  dispatch-verbosity watch (FEEDBACK.md).
- 2026-08-16 Minted by the board owner from S13 Gate A finding 4
  (reviewer gpt-5.6-sol via codex): seam unused by production code,
  board metadata absent from the protocol. The put-deferral half of the
  finding was rejected as already ruled - the S13 log records the
  deferral and its reason; this card carries the wiring and the
  metadata surface.
