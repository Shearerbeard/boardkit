# Topology hardening: delegation contract, doctor, resolve-route, dispatch-brief

Status: approved 2026-08-03 (user gate in the consuming program's plan
interview). This is the binding design for the engine wave; the consuming
board tracks execution. The source review is the codex gpt-5.6-sol second
opinion on the skill topology (8 BLOCKING + 1 MINOR, archived in the
consumer's review directory), and the design was authored by a Claude
Opus design agent against the tree at `456a434`, adopted with no
structural edits.

The findings this wave implements here: F1 (installation-state matrix
incomplete, fail-open), F2 (no compatibility contract across skills,
repo docs, and config), F3 (routing needs four prose hops; make it
mechanically resolvable), F5 (dispatch briefs are quoted policy text
that goes stale), F9 (templates ship placeholders that look complete).
Findings 4, 6, 7 land in the skills marketplace repo; finding 8 lands in
the board-bound skill bodies.

Field evidence from FEEDBACK.md, drained by this wave (dispositions at
the end): the silent wrong-path `BOARDKIT_HOME` bootstrap, hardcoded
model ids where dispatch-time resolution was wanted, an agy shell-proxy
misrouting incident that left 12 stray worktrees, and card edits that
silently failed to persist.

## Decisions

1. **Bindings live in `boardkit.toml`** as strict new top-level sections,
   not a separate file (a separate file adds a hop, discovery logic, and
   its own missing-file quadrant). Shape:

   ```toml
   [contract]
   version = 1

   [routes.<slug>]
   adapter = "..."      # the harness this transport reaches
   skill = "..."        # child skill to load; "" means none
   pin_source = "docs/board/REVIEW-TOOLING.md#harness-bindings"
   preflight = ["..."]  # printed by boardkit, NEVER executed by it

   [roles.<name>]
   routes = ["primary-route", "fallback-route"]  # ordered
   ```

   `pin_source` is a pointer to where live pins are read at dispatch
   time, never a pin. Required roles: `executor`, `code-review`,
   `prose-review`, `frontier-review`, `drift-audit`, `canary`. Strict in
   both directions (unknown and missing keys both raise); a missing
   `[contract]` gets a migration-shaped error naming `boardkit doctor`.
   Recorded v1 skew guard: an old kit reading a new config fails loudly
   on the unknown sections, which is the detectability F2 asks for.

2. **Three commands, three modules, one resolver.** `boardkit doctor
   [--json]` (whole-repo cold-start diagnostic, `doctor.py`),
   `boardkit resolve-route <role> [--json]` (hot-path single-role
   resolution, in `contract.py`), `boardkit dispatch-brief <card-id>`
   (deterministic generator, `brief.py`). `dispatch-brief` calls the
   same `contract.resolve_role` as `resolve-route`. Layering, acyclic:
   `contract.py` (no boardkit imports) <- `config.py` <- `board.py` <-
   `doctor.py`/`brief.py` <- `cli.py`. `contract.py` also owns the
   strict-key helper, the placeholder vocabulary, and the kit paths
   (`DATA_DIR`, `TEMPLATES_DIR`, `BOARD_DOCS`, `CONTRACT_DOCS`) moved
   out of `cli.py`.

3. **Versioning is one integer plus a digest.** `CONTRACT_VERSION = 1`,
   `SUPPORTED_CONTRACT_VERSIONS = frozenset({1})`; every shipped
   contract doc carries `<!-- boardkit-contract: v1 -->` (the
   pre-commit sample uses a `#` comment; the card template is
   deliberately unstamped so consumers never copy a stamp into cards);
   board-bound skills declare `metadata: {boardkit-contract: 1}`;
   doctor compares all four. `contract_digest(config)`: sha256 over the
   version, the consumer's three contract docs, and the canonically
   serialized contract tables, truncated to 12 hex, repo-relative so a
   clone digests identically. No compatible-range negotiation at 0.0.1
   with one consumer; when v2 arrives, equality widens to membership in
   the supported set.

4. **Placeholder detection is section-identity, not a markdown scan.**
   A general angle-bracket scan false-positives on legitimate template
   text (`Gate <X> open: deferred (<reason>)`, `timeout <seconds>`).
   Instead: the required fill-in sections of the consumer's
   REVIEW-TOOLING.md ("Tools, in order of preference", "Harness
   bindings") are unfilled when byte-identical to the shipped template
   (the view-drift compare inverted); the angle-bracket scan runs only
   over TOML route values and inside those two sections, where the
   template's own placeholders are the only angle brackets.

5. **`check` and `doctor` split.** `check` stays the board-validity and
   hook contract; installation readiness is doctor's. A fresh
   `boardkit init` repo passes `check` and fails `doctor` on unfilled
   roles - by design, so init can stamp placeholders without lying.
   Doctor never raises (config load failures become findings so the
   quadrant is nameable), exits 1 on any error and 0 on warnings alone,
   emits stable check ids, and reports skipped checks (silence must not
   read as success). Errors: `config.present`, `config.loads`,
   `docs.present`, `contract.version-known`, `contract.docs-stamped`,
   `contract.skills-declared`, `review-tooling.filled`,
   `review-tooling.placeholders`, `roles.filled`, `routes.pin-source`,
   `board.parses`, `views.current`. Warnings: `env.boardkit-home`
   (names both the env value and the install root), `config.repo-root`
   (walk-up grabbed a parent repo's config), `skills.installed`
   (installed vs available, lists searched paths), `worktrees.stray`
   (`.agy-mcp/worktrees/job-*`), `entry.agents-stamp`.

6. **Doctor cannot detect boardkit's own absence.** That quadrant is
   the board-hygiene skill's fail-closed first step ("run
   `boardkit doctor`; if the command is not found, stop and tell the
   user; never proceed on the docs alone"). Doctor also never executes
   `preflight` strings - a diagnostic that shells out to repo config is
   a code-execution surface; it prints them and the caller runs them.

7. **`dispatch-brief` is deterministic and timestamp-free.** Header
   (card id and path, contract version, digest, source paths), the card
   file verbatim, reference links as repo-relative paths, resolved
   routes (Gate A prints both `code-review` and `prose-review` with the
   routing rule quoted from the consumer's MODEL-CLASSES.md - cards
   carry no artifact-kind field, an honest limit), contract clauses
   quoted from the consumer's PROCESS.md (dispatch-brief paragraph,
   decision-authority paragraph, the bullet for each gate the card
   declares - extracted, never restated in code; a missing anchor is a
   `BriefError`), provenance footer (regenerate rather than edit; a
   brief whose digest differs from doctor's is stale).

8. **Plugin scaffold ships manifests only.** `.claude-plugin/
   marketplace.json` (name `boardkit` - it must differ from the
   personal marketplace name or the per-source install manifests
   cross-prune) and `plugins/board/.claude-plugin/plugin.json`. No
   placeholder skill bodies: a skill that says nothing is worse than an
   absent one, because absence is detectable. Recorded state until the
   bodies land: `install-skills <boardkit>` exits 1 on the empty
   plugin; `check-skills`/`check-install` pass on zero skills; a test
   pins the empty state and the bodies card deletes it.

9. **Schema-copy collapse first.** The config schema exists in six-plus
   places (config.py constants, the init template literal in cli.py,
   the conftest template, and inline literals across five test
   modules). Stage 1 collapses the test-side copies into one conftest
   helper and adds binding tests (init template parses, declares every
   required role, matches the conftest schema). Also in stage 1: the
   cli.py dispatch dict is replaced with argparse
   `set_defaults(handler=...)`, and `--version` lands with a test
   binding `__version__` to pyproject.

10. **Template edits carry the four inbox fixes with binding tests.**
    Card read-back duty (PROCESS Session close); briefs name the role
    and pin source, never a model id (PROCESS Roles + MODEL-CLASSES
    pre-vet); the `BOARDKIT_HOME` export on its own line with the
    same-line-prefix failure named (AGENTS template bootstrap); the
    metered-reviewer reservation, retry cap, and stray-worktree
    accounting (REVIEW-TOOLING template Transport rule).

## Stages

Each stage leaves `uv run pytest -q` and `ruff check` green.

1. **Contract schema + plumbing.** New `src/boardkit/contract.py`
   (constants, `Route`/`ContractConfig` frozen dataclasses,
   `require_keys`, `placeholders`, `parse_contract`); config.py gains
   the three sections and the migration-shaped error; cli.py init
   template gains the contract block (placeholders valid, so `check`
   stays green); conftest collapse; handler refactor; `--version`.
   New tests: `test_contract.py` (strictness matrix: unknown/missing
   sections, keys, roles, routes, slug rule, ordered routes),
   `test_schema_copies.py` (both templates parse, declare every role,
   match each other), `test_cli.py` (every subcommand binds a handler;
   version flag; bare invocation pinned).

2. **Stamps + inbox template fixes.** `read_stamp` in contract.py;
   stamps across PROCESS/MODEL-CLASSES/REVIEW-TOOLING templates, the
   three shims, pre-commit.sample; the four decision-10 prose edits.
   New tests: `test_contract_stamp.py` (every contract doc stamped at
   the current version; card template unstamped), extended
   `test_process_template.py` (read-back duty, no-model-ids rule), new
   `test_agents_template.py` (export requirement bound to the doctor
   constant), new `test_review_tooling_template.py` (reservation +
   stray-worktree duty bound to the doctor pattern).

3. **`boardkit doctor`.** `_view_drift` promotes to
   `board.view_drift`; `doctor.py` with `Finding`/`Skip`/
   `DoctorReport`, `run_doctor` (never raises), text and JSON
   renderers, pure helpers (`unfilled_sections`,
   `section_placeholders`, `unfilled_routes`, `missing_pin_sources`,
   `stray_job_worktrees` over captured porcelain text,
   `boardkit_home_finding`). Tests: the quadrant matrix (empty dir;
   docs without config; config that fails to load is a finding not an
   exception; pre-contract config reports the migration; fresh init
   fails on unfilled roles; fully filled passes), pure-helper units
   including the false-positive guard, stamp mismatch, drifted views
   via the golden fixture, exit semantics, stable JSON ids, skips
   reported.

4. **`resolve-route`.** `Resolution` dataclass, `resolve_role` (fails
   closed on unknown role, placeholder first route, missing pin_source;
   validates only the asked-for role - laziness proven by test), text
   output byte-pinned, `skill: none (this transport loads no child
   skill)` for empty skill, JSON shape pinned.

5. **`dispatch-brief`.** `brief.py` (section/anchor extraction bound to
   the shipped PROCESS.md by test, `gate_tokens`, `build_brief` on
   `build_board` - never a second card parser), `contract_digest`.
   Tests: byte-stable whole-output pin, card verbatim, reference links,
   gate-scoped clause quoting, both Gate A roles, digest
   stability/sensitivity/location-independence, fail-loud on missing
   anchors and unknown cards, no timestamp.

6. **Init polish, manifests, docs, drain.** Init prints the NEXT line
   (fill routes and the fill-in sections, then run doctor) and the
   stamped version; the two manifests land with
   `test_plugin_manifest.py` (valid JSON, name differs from the
   personal marketplace, declared sources exist, no skills yet);
   README gains a Diagnostics and routing section (three commands, the
   contract version, the check-vs-doctor split); EXTRACTION.md gains
   the plugin-dir and contract rows; PLAN.md notes the scaffold;
   FEEDBACK.md drains the four entries per the inbox convention, with
   the dispositions below as their durable record.

## Inbox dispositions (drained by stage 6)

- **card-edit-readback** (chore-lottery): accepted; the read-back duty
  lands in the PROCESS template Session close with a binding test.
- **no-hardcoded-model-ids** (terminalbench-aura): accepted; the
  role-and-pin-source rule lands in PROCESS Roles and the
  MODEL-CLASSES pre-vet, and the `[routes].pin_source` mechanism is
  the structural fix.
- **boardkit-home-export** (terminalbench-aura): accepted; the AGENTS
  template bootstrap gains the export-on-its-own-line requirement with
  the failure named, and doctor's `env.boardkit-home` warning names
  both paths at runtime.
- **agy-shell-proxy-routing** (chore-lottery): accepted; the
  REVIEW-TOOLING template Transport rule gains the metered-reviewer
  reservation, the retry cap, and session-close worktree accounting,
  and doctor's `worktrees.stray` warning surfaces the leftovers.

The other three entries (docs-bustest-wave-close,
lint-suppression-disposition, per-gate-skill-loads) stay in the inbox
for the maintainer session.

## Recorded skews and limits

- Old kit + new config fails loudly on unknown sections; that is the
  v1 skew guard, on purpose.
- `install-skills` exited 1 against this repo until the board-bound
  skill bodies landed (pinned by a test while true); resolved
  2026-08-03 when `board-hygiene` and `delegating-work` shipped and
  the pin test was deleted.
- Gate A code-vs-prose selection stays board-owner judgment; briefs
  print both routes.
- Whether a route is actually reachable stays the pre-vet checklist's
  job; preflight is printed, never run.
- The typed-Card seam and `review_packet.py`'s duplicated parser are
  out of scope (separately gated plan).

### Recorded limits (2026-08-03, post-build)

Found while building, kept rather than fixed. Each one is a deliberate
stopping point with its trigger for revisiting recorded.

- A gate qualifier in a card's `gates` string is parsed and then
  ignored. `gate_tokens` reduces `U(code-review)` to `U`, and `GATE_ROLES`
  binds routes for `A`, `F`, and `D` only, so `S`, `M`, and `U` pull no
  route into a brief. So a qualifier that names a role looks like it
  selects one and does not. Revisit if board owners start relying on the
  parenthetical to mean something.
- The digest covers contract content, not config layout. Reordering
  `[routes.*]` blocks in `boardkit.toml` leaves the digest unchanged,
  because `canonical_contract` sorts table keys; reordering the route
  names inside one role's `routes` list does change it: that sequence is
  the fallback order, which is contract. The asymmetry is intended and
  worth knowing before reading a digest diff.
- `dispatch-brief` prints an unresolvable reviewer route in place, as
  `UNRESOLVED`, rather than refusing to generate. The executor still
  needs dispatching, and a broken reviewer binding is exactly what the
  board owner should see printed. `doctor`'s `roles.filled` is the check
  that fails on it; the brief is not a second gate.

All six engine stages are complete: contract schema and plumbing;
stamps and the inbox template fixes; `boardkit doctor`; `resolve-route`;
`dispatch-brief`; and this stage, init polish, manifests, docs, and the
inbox drain.
