# Plan: opencode self-knowledge for review routing (Goal 2)

## Scope

- Core problem: a board-owner session running natively inside opencode
  shells out to `opencode run -m <model>` for adversarial review instead of
  dispatching its own configured subagents. Research showed this is not a
  model failure but a documentation contradiction: REVIEW-TOOLING.md's
  harness-bindings table prescribes the `rust-reviewer`/`python-reviewer`
  agents, while its transport block (correctly) notes `opencode run --agent`
  silently falls back for subagent-only agents, then prescribes the
  staged-directory `opencode run -m` recipe. A native session reads the
  second and recurses. Compounding facts: opencode currently loads no
  global instruction file (`~/.config/opencode/AGENTS.md` missing,
  `opencode.json` has no `instructions` key), and the
  `collaborating-with-opencode` skill is written only for external Claude
  sessions, with a stale model matrix, and lives unversioned in
  `~/.claude/skills/` (only backup: boardkit snapshots).
- Audience: any opencode primary agent (build/plan/general) acting as
  board owner; external Claude/codex sessions driving opencode.
- Success: a native opencode board owner (a) reads its own agent config
  before routing, (b) dispatches gate reviews via its in-session task tool
  to the pinned subagents, (c) never spawns `opencode run` from inside an
  opencode session, and (d) falls back to staging context into the cwd
  (the S46 remedy) when a subagent cannot reach files, never to CLI
  recursion.
- Non-goals: changing which models are pinned; MCP server behavior;
  the delegating-work skill rewrite (Plan 1 stage 4 consumes this plan's
  rules but ships separately).

## Verification

- Smoke test (Gate M): start a fresh native opencode session in a repo
  with a staged diff, ask it to run an adversarial review; confirm from the
  session transcript that it greps the agent pins, dispatches the correct
  reviewer subagent via task dispatch, and never execs `opencode run`.
- Deterministic: `tuckr` deploy check for the dotfiles group; `vale` on
  touched markdown; `bin/check-skills` if the skill moves into
  claude-skills.

## Blast Radius

- Files: new `~/.dotfiles/Configs/opencode/.config/opencode/AGENTS.md`
  (tracked, symlinks into place like the agent files); optionally
  `opencode.json` `instructions` key; aura
  `docs/redesign/REVIEW-TOOLING.md` (transport + bindings sections);
  `~/.claude/skills/collaborating-with-opencode/SKILL.md`; boardkit
  `src/boardkit/data/templates/REVIEW-TOOLING.md.template`.
- Existing building blocks: AGENTS.md step 5 pin-check rule in aura
  (already prescribes the grep, just not the dispatch preference); the
  skill's existing "config is the only source of truth" rule; PROCESS.md's
  "a review is never nested inside another delegation" invariant, which is
  the principled basis for the no-recursion rule.
- Test coverage gaps: none of this is machine-checkable today; the smoke
  test is the check.

## Implementation Stages

### Stage 1: global opencode rules file 🛑 USER GATE
- Goal: give every opencode session the routing rules regardless of repo.
- Changes: author `AGENTS.md` in the dotfiles opencode group with three
  rules. (1) Self-inventory first: before routing executor or reviewer
  work, read `~/.config/opencode/agent/*.md` pins and the `agent` block of
  `opencode.json`; agent names do not imply model families. (2) Dispatch
  preference: a native session uses its own task/subagent dispatch for the
  pinned reviewer agents; `opencode run` is for external harnesses only,
  and a session that is already opencode never invokes the opencode CLI
  (nested servers break cost capture and the review-nesting invariant).
  (3) Context fallback: when a subagent cannot read external paths, stage
  the packet into the working directory (`.review/` convention), do not
  fall back to CLI recursion. Wire deployment via the tuckr `opencode`
  group; decide at Gate U whether to also list the file in an
  `instructions` key for explicitness.
- Gates: S → A → U
- [ ] Gate S: load skill `gate-probes`; `vale` on the new file; confirm
      symlink lands via tuckr dry-run
- [ ] Gate A: second-model review of the rules text for conflicts with
      REVIEW-TOOLING.md and MODEL-CLASSES semantics
- [ ] Gate U: new always-injected instruction surface for every opencode
      session; wording and deploy mechanism are the user's call
- Done when: a fresh opencode session in any directory can state the three
  rules when asked how it would run a review.

### Stage 2: fix the REVIEW-TOOLING.md contradiction (aura side)
- Goal: the bindings table and the transport block agree.
- Changes: scope the CLI-first transport rule explicitly to external
  harnesses driving opencode; add a native-opencode board-owner paragraph:
  in-session subagent dispatch to the pinned reviewer, staged-context
  fallback, no CLI self-invocation; cross-reference the pin-check duty.
  Keep the staged-directory `opencode run -m` recipe, relabeled as the
  external-harness recipe. Mirror the same wording into boardkit's
  REVIEW-TOOLING template (both sides fixed in one stage).
- Gates: S → A
- [ ] Gate S: load skill `gate-probes`; `vale docs/redesign/REVIEW-TOOLING.md`
      from the aura adapter root; boardkit `uv run pytest -q`
- [ ] Gate A: cross-family prose review with the specific question "can a
      native session still find a reading that tells it to shell out?"
- Done when: no sentence in either file routes a native session to
  `opencode run`, and the aura Changelog records the review per its own
  standard.

### Stage 3: skill refresh and versioning
- Note (2026-08-02): partially covered already. claude-skills'
  `bin/install-skills` mechanism works and versions skills for the
  agent-skills harnesses (`bin/check-install` passes), so the "gains a
  home" half is solved infrastructure; what remains of this stage is the
  content refresh (drop the stale model matrix, add the native-session
  section) for whichever skill survives, since
  `collaborating-with-opencode` has since been retired in favor of an
  opencode-cli skill.
- Goal: `collaborating-with-opencode` stops lying and gains a home.
- Changes: correct the stale agent/model matrix (or better, delete the
  table and keep only the read-the-config rule, which cannot go stale);
  add a short "if you are the opencode session" section pointing at the
  stage-1 rules; move the skill into version control. Preferred home:
  claude-skills (new or existing plugin) so `bin/check-skills` and
  `install-skills` govern it; note it is slated to be superseded by
  boardkit's `delegating-work` skill (Plan 1 stage 4), so keep the diff
  minimal.
- Gates: S → A
- [ ] Gate S: load skill `gate-probes`; `bin/check-skills` after the move;
      `vale`
- [ ] Gate A: agent review comparing skill claims against live
      `opencode.json` and agent pins on the day of the change
- Done when: the skill contains no model claims that can drift, and the
  skill file is tracked in a repo.

### Stage 4: live verification 🛑 USER TEST
- Goal: prove the behavior change in a real native session.
- Changes: none (verification only).
- Gates: M → T
- [ ] Gate M: agent-driven smoke test per Verification above, transcript
      excerpts saved next to this plan
- [ ] Gate T: user runs one real Gate A review from a native opencode
      board-owner session on a live card
- [ ] Gate T handout: exact session-start command, reference prompt
      ("run Gate A on card X"), expected observations in order (pin grep
      appears; task dispatch to reviewer agent; verdict returned; no
      `opencode run` in the transcript), failure signatures (`opencode run`
      exec'd; silent agent fallback; empty return treated as pass), revert
      steps (delete the dotfiles AGENTS.md symlink target and redeploy)
- Done when: one real review completes through the new routing with the
  transcript as evidence.

## Rollback

- Stage 1: remove the AGENTS.md from the dotfiles group and redeploy tuckr;
  opencode returns to no-global-rules state.
- Stages 2 to 3 are doc/skill edits: revert commits.
