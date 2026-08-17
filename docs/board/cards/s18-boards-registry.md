---
id: S18
title: R4 boards registry - the manifest is the registry
status: in-review
depends: [S13]
serialize-with: []
lineage: primary
commit-range: deb9c2b..bb2d0f8
executor: smart
gates: "S -> A -> U(code-review)"
user-gates: [code-review]
---

# S18: R4 boards registry - the manifest is the registry

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Drain record:
[2026-08-09-feedback-drain-7.md](../../plans/2026-08-09-feedback-drain-7.md)
(first drained entry, plus interview decision 5).

## Scope

`src/boardkit/config.py` (manifest row schema), `src/boardkit/cli.py`
(the `boards` command), `src/boardkit/doctor.py` (row-vs-board
verification), this repo's own `.boardkit/manifest.toml` (the bk
dogfood rows), docs, tests.

## Deliverable

The `.boardkit/manifest.toml` from S13 grows into the family registry.
Each `[boards.<code>]` row carries `location` (scheme-prefixed),
`engine`, `id_prefix`, and `scope` (one line; the charter `owns` mirror
once S20 lands). Optional `status` marks a row `transitioning` or
`archived`, with `active` the default; externality is the `location`
scheme plus the overlay, per the R4 scheme-prefixed ruling, not a
status. (Amended at Gate A: the minted line listed `external` in the
status vocabulary.) Engine heterogeneity is data: pre-boardkit,
hand-maintained, and TODO-file surfaces are first-class rows, so the
registry can describe a family before it is uniform.

`boardkit boards` enumerates from the resolved manifest plus
`local.toml`: one row per board with short-code, home, engine, prefix,
scope, and whether the home currently resolves on this machine.
Uniqueness: short-codes are unique by TOML table semantics; a new row
claiming an id prefix another row already holds fails validation unless
the collision is marked known on the row, because the aura family's
existing S-prefix collisions must remain describable while new ones are
refused. For `dir:` rows, cached fields are verified against the
board's own `boardkit.toml`; a mismatch fails `boardkit check`. A
second hand-maintained family copy is forbidden: prose indexes generate
from these rows.

## Acceptance

- `uv run pytest -q` green; tests cover row parsing, the known-collision
  refusal for new prefix claims, `dir:` row verification, and an
  external row with and without an overlay path.
- `boardkit boards` run in this repo answers from
  `.boardkit/manifest.toml` and lists the bk board without reading any
  hand-written index.
- A cross-board resolution test exists: from a fixture repo whose
  manifest names two boards, resolving each short-code lands on the
  right `boardkit.toml`.

## Gate checklist

- [x] Gate S: load skill `gate-probes`, then `uv run pytest -q`,
  `uv run ruff check`, `vale` on touched markdown.
- [ ] Gate A: adversarial review, focus: can the registry lie (cached
  row drifting from the board config, an overlay masking the committed
  location, collision marks papering over a real new collision)?
- [ ] Gate U (code-review): present the review packet; stop.

## Branch

direct

## Log

- 2026-08-09 Minted by the seventh feedback drain from the 2026-08-07
  registry entry, shaped by the manifest-is-registry interview decision
  and the RULE-3 store-seam constraints.
- 2026-08-09 Pulled in-progress straight from backlog: S13 is in-review
  in the same sitting and the dependency is on S13's diff, not its done
  state (same-hand build order per drain 7). Executor is the maintainer
  session.
- 2026-08-09 Built: registry fields on manifest rows (optional per the
  RULE-2 minimal shape; `dir:` boards self-describe and cached fields
  verify against them), `registry_rows` validation with the marked-
  collision rule, `boardkit boards` (+ `--json`), row drift wired into
  `check` via `board_row_errors`, the bk dogfood manifest, README
  section. Maintainer adjustment vs the card text: row verification
  landed in `boards` + `check`, not doctor - check is where drift
  fails; doctor stays installation-level. Gate S PASS: 302 pytest
  green (10 registry tests + the named Gate B cross-board resolution
  test), ruff clean, vale clean on README.
- 2026-08-09 Acceptance run: `boardkit boards` in this repo answers
  from `.boardkit/manifest.toml` (bk row, default-marked, reachable);
  `--json` emits stable fields; cross-board test
  `test_cross_board_resolution_lands_each_code_on_its_own_config`
  passes.
- 2026-08-09 In-review; commit-range deb9c2b..bb2d0f8.
- 2026-08-09 Gate A deferred, superseded 2026-08-16: adversarial reviews batch at the
  Session B boundary; packets present at the Gate B user gate.
- 2026-08-16 Gate A ran (resolving the deferral): reviewer gpt-5.6-sol
  via codex exec, author claude-fable-5 (whole wave); codex fallback
  after the opencode lane stalled its read probe. Verdict FAIL, four
  findings.
  1. BLOCKING a cached id_prefix was accepted exactly when the board's
     config was missing or unparseable - the cache won when it could
     not be checked. Confirmed. Fixed in fe308d0: unverifiable caches
     report; a readable config that merely omits the key stays clean.
  2. BLOCKING a new row can self-mark prefix_collision_ok and join an
     existing collision group. Rejected as designed, with the reason
     recorded: the registry holds no history, so old and new claims
     are indistinguishable in data; the mark is a deliberate reviewed
     manifest edit. The stronger shape (marks naming the codes they
     collide with, forcing edits to every existing row) is noted for
     drain 8. Surfaced at the next user gate.
  3. BLOCKING collision errors carried no [boards.<code>] marker, so
     board_row_errors' filter dropped them all and check never saw a
     collision involving its own board. Confirmed. Fixed in fe308d0:
     per-row emission with markers; regression test drives check-level
     visibility.
  4. BLOCKING ROW_STATUSES omits the 'external' status the deliverable
     listed. Dispositioned by amending the deliverable line: the R4
     ruling made externality a location scheme resolved through the
     overlay, and the implementation followed the ruling; a status
     duplicating the scheme would give one fact two homes. Amendment
     noted inline on the card.
  Reviewer-reported UNVERIFIED (sandbox): pytest, check, doctor - run
  board-owner-side: 343 pytest green, ruff clean, check OK. Fix commit
  fe308d0 sits apart from the reviewed range with foreign commits
  between, so commit-range stays deb9c2b..bb2d0f8 and the fix-commit
  re-review runs over fe308d0^..fe308d0 via the packet override; Gate
  A's box stays unticked until that re-review passes.
- 2026-08-16 Gate A review cycle closed by ruling; full round ledger in
  [2026-08-16-gate-a-review-cycle.md](../evidence/2026-08-16-gate-a-review-cycle.md).
  Rounds 2 to 5 re-reviewed the fix commits. Round 5 confirms every
  recorded fix and every round-4 residue resolved; from round 3 on, the
  findings were confined to `_is_shim` in the S24 fix code, one narrower
  evasion per round, and that hardening is carded as S29 rather than
  patched a sixth time. Every finding against this card's own reviewed
  diff is resolved. The reviewer never issued an explicit sign-off, so
  the box stays unticked, because a failed return is never a pass. The
  2026-08-09 batch deferral is superseded - the batch ran, on the codex
  fallback after the opencode lane failed its read probe four times.
- 2026-08-16 Gate A open: deferred (review cycle closed by ruling after five
  rounds with every card-diff finding resolved and no explicit reviewer
  sign-off; the pass decision is the user's at U code-review, on the ledger
  in docs/board/evidence/2026-08-16-gate-a-review-cycle.md)
