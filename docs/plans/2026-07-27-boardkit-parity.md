# Plan: boardkit parity with the terminalbench-aura process (Goal 1)

## Scope

- Core problem: boardkit's engine is already a validated superset of aura's
  `scripts/cards_index.py` (zero frontmatter drift, three extra checks, 37
  tests), but the *process* is not yet portable: no skills ship (Phase 3
  pending), the orientation-canary hard stop is missing at PROCESS level,
  the kit instructs a `Card: <ID>` commit-trailer convention it never
  establishes, and three aura rules added after the 2026-07-21 extraction
  freeze are unaccounted for in EXTRACTION.md.
- Audience: future board-owner sessions bootstrapping new repos with
  `boardkit init`; the aura board itself once it migrates (stage 5).
- Success: a fresh repo after `boardkit init` + skill install runs the same
  session lifecycle aura runs today (orient → pull → gates → hygiene →
  canary → commit), and aura's own board validates clean under `boardkit
  check` byte-identically.
- Non-goals: multi-source backends (Plan 3), the typed-holes playbook
  content (Plan 4), publishing (existing Phase 6 gates unchanged).

## Verification

- Smoke test: `boardkit init` in a scratch repo, author one card, walk it
  ready → in-progress → in-review (packet) → done, run `boardkit check` and
  the board-hygiene skill end to end (this is existing Phase 5, unchanged).
- Deterministic: `uv run pytest -q` (37+ tests, golden byte-identity),
  `boardkit check` on the aura board copy (stage 5), `bin/check-skills` in
  claude-skills for any skill this plan touches.

## Blast Radius

- Files: `EXTRACTION.md`; `src/boardkit/data/templates/PROCESS.md`;
  `src/boardkit/data/templates/REVIEW-TOOLING.md.template`;
  `src/boardkit/review_packet.py` (+ tests); new skills under the Phase 3
  plugin; aura's `docs/redesign/PROCESS.md` + `scripts/` only in stage 5.
- Existing building blocks: the audit-remediation wave pattern (three-worker
  audit + codex adversarial pass) is the proven mechanism for stage 1;
  aura's `.claude/skills/board-hygiene/SKILL.md` is the source for the
  generalized skill; `snapshots/opencode/agent/*.md` for agent defs.
- Coverage gaps: `cli.py` subcommand-level tests; no test binds PROCESS.md
  prose constants (WIP limit, statuses) to `board.py` constants (Plan 3.1).

## Implementation Stages

### Stage 1: extraction refresh (close the post-freeze drift)
- Goal: every aura process rule dated after 2026-07-21 has exactly one
  recorded state in boardkit (ported / deferred / dropped), restoring the
  one-rule-one-state invariant the Gate U approval certified.
- Changes: diff aura `PROCESS.md`, `board-hygiene/SKILL.md`,
  `REVIEW-TOOLING.md`, `scripts/*.py` git history 2026-07-21..HEAD; known
  items: detached-side-quest WIP exemption (2026-07-25), card-reference
  prose convention, per-repo review packets for multi-repo cards
  (2026-07-27, S73), fix-commit re-review duty wording, executor-fallback
  three-attempt threshold. Disposition each in `EXTRACTION.md`; port the
  general ones into the PROCESS template in the same commit.
- Evidence fold-in (2026-08-02): the chore-lottery bootstrap wave is the
  first live consumer exercise of `boardkit init` and the board lifecycle.
  Its kit-relevant findings are triaged in `FEEDBACK.md` (wave-close docs
  bus test, landed in the PROCESS template 2026-08-02; card read-back
  duty; per-gate restatement of deterministic checklist steps). The
  extraction refresh dispositions those inbox entries alongside the aura
  diff instead of treating aura as the only source.
- Gates: S → A
- [ ] Gate S: load skill `gate-probes`; `uv run pytest -q`; re-run the
      audit re-grep tripwire from the remediation wave; `vale` on touched
      markdown
- [ ] Gate A: fresh-context second-model review of the disposition table
      against the raw aura diff (reviewer ≠ author family)
- Done when: EXTRACTION.md has a dated "refresh 2026-07" section and no
  aura rule in the diff window is unaccounted.

### Stage 2: easy-lift template and packet fixes (both sides)
- Goal: close the concrete gaps that are one-file lifts.
- Changes (kit side):
  - Add a Commit standards section to the PROCESS template: conventional
    first line, **the `Card: <ID>` trailer convention** (fixing the live
    gap where `review_packet.py:164` instructs a grep the kit never
    establishes), no AI attribution / sign-off trailers.
  - Port the card-reference prose convention and the side-quest WIP
    exemption into the PROCESS template board-mechanics section.
  - `review_packet.py`: support per-repo packet dirs for multi-repo cards
    (`reviews/<id>-<suffix>` via a `--suffix` flag) + tests.
- Changes (aura side, backport): none required - aura already has all of
  these; aura is the source here.
- Gates: S → A
- [ ] Gate S: load skill `gate-probes`; `uv run pytest -q` (new
      review_packet suffix tests red first, then green); `vale`
- [ ] Gate A: agent review of the template diff against the aura originals
- Done when: kit templates state every rule its own code references, and
  the suffix flag has red→green test coverage.

### Stage 3: canary restoration 🛑 USER GATE
- Goal: the two-canary structure survives extraction. (a) The
  **orientation canary** hard stop becomes a PROCESS-level mandate, not
  just a skill step - per the standing EXTRACTION.md board-hygiene row
  obligation. (b) The program-specific OTEL **trace-receipt canary** stays
  dropped, but its *pattern* is generalized: an "evidence-receipt canary"
  rule in the REVIEW-TOOLING template - before any expensive run whose
  value depends on captured evidence, a per-repo canary command must prove
  end-to-end receipt (not endpoint reachability), or the card records an
  explicit user waiver.
- Changes: PROCESS template gains the orientation-canary mandate (cheap
  cross-family model, four questions, key computed from `boardkit check` +
  frontmatter, board-miss = hard stop, model-weakness miss = swap model);
  REVIEW-TOOLING template gains an optional `canary` fill-in slot (command
  + waiver rule). Optional automation (continue-automating directive):
  a `boardkit canary-key` subcommand that computes the grading key
  (in-review/in-progress lists, next eligible pull, open-deferred gates
  with unticked boxes) deterministically from frontmatter - the piece the
  aura skill computes by hand today, and the generated deferred-queue view
  aura's skill names as a tracked follow-up.
- Gates: S → A → U
- [ ] Gate S: load skill `gate-probes`; `uv run pytest -q` (canary-key
      golden test against the aura fixture board); `vale`
- [ ] Gate A: fresh agent answers the four canary questions using only the
      new template text + fixture board; grade against `canary-key` output
- [ ] Gate U: present the mandate wording and the canary-key output format
      - this changes the process contract every future repo inherits
- Done when: a cold model given only kit-template text can run the
  orientation canary, and the deferral-record gap flagged in the wiki
  workstream is closed.

### Stage 4: Phase 3 skills + opencode agent defs 🛑 USER GATE
- Goal: ship the skills plugin PLAN.md Phase 3 names: `board-hygiene`
  (generalized), `delegating-work`, `typed-holes` (thin - body lands via
  Plan 4 stage 2), plus genericized opencode agent defs from snapshots.
- Changes: new plugin in claude-skills (or boardkit-shipped plugin dir -
  decide at Gate U; claude-skills gives `bin/check-skills` enforcement and
  the existing install path). board-hygiene is rewritten against boardkit
  commands (`boardkit check/render/review-packet/canary-key`) and
  boardkit.toml paths - zero hardcoded aura paths. delegating-work
  supersedes the collaborating-with-* snapshots and encodes Plan 2's
  routing rules. Agent defs: rust/python write+reviewer with the S3
  lesson (reviewer bash allowlist must cover reading the packet; point
  reviewers at `full-range.diff`, never require git).
- Gates: S → A → U
- [ ] Gate S: load skill `gate-probes`; `bin/check-skills` +
      `bin/check-install` in claude-skills; `vale`
- [ ] Gate A: cross-family review of each SKILL.md against its aura
      source for silent drops (the stage-1 failure class)
- [ ] Gate U: present the plugin layout + skill bodies; the
      skills-vs-boardkit packaging decision is the user's
- Done when: `install-skills` deploys them, and a scratch-repo session can
  run board hygiene end to end with no aura references.

### Stage 5: parity proof on the live aura board 🛑 USER GATE
- Goal: aura's own board validates under boardkit with no regression;
  then (user decision) aura adopts the kit CLI and retires
  `scripts/cards_index.py`.
- Changes: a `boardkit.toml` for aura (`cards_dir: docs/redesign/cards`,
  `id_prefix: "S"`, `sentinel_ids: ["MILESTONE"]`, review repo/output per
  PROCESS.md). Run `boardkit check` read-only; triage the three
  net-new validations against live state (WIP limit with the side-quest
  exemption from stage 2, serialize mutex, in-review commit-range);
  byte-compare generated views modulo the banner line.
- Gates: S → A → M → U
- [ ] Gate S: load skill `gate-probes`; `boardkit check` on aura exits 0
      or every finding is triaged as a real board defect (fix the board,
      not the check)
- [ ] Gate A: agent diff of kit-rendered views vs script-rendered views
- [ ] Gate M: one full session-close hygiene pass on the aura board using
      only boardkit commands, orientation canary included
- [ ] Gate U: adoption decision - flip aura's PROCESS.md/skill references
      to boardkit and retire the script, or keep dual-running
- Done when: the user has accepted or deferred adoption with the evidence
  in hand; until then both validators run and must agree.

## Rollback

- Stages 1–4 are additive template/skill/docs changes in boardkit and
  claude-skills: revert the commits.
- Stage 5 leaves aura's script untouched until the Gate U decision; the
  dual-run period is the rollback path (delete aura's boardkit.toml).
