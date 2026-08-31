# Extraction map

This file traces every boardkit artifact to its source and records its
disposition. It is the working contract for the extraction; it gets pruned to
a short provenance note before publish.

Source repositories (on the author's machine):

| Source | Path | What it holds |
|---|---|---|
| terminalbench-aura | `~/dev/terminalbench-aura` | The live board program - process docs, the card registry with its board scripts, and the board-hygiene skill |
| claude-skills | `~/dev/claude-skills` (github.com/Shearerbeard/claude-skills) | Language/docs/workflow skill plugins, marketplace install tooling |
| dotfiles | `~/.dotfiles` (github.com/Shearerbeard/dotfiles) | OpenCode config and agent definitions (version-controlled) |
| user skills | `~/.claude/skills/` | collaborating-with-opencode, collaborating-with-antigravity (NOT version-controlled anywhere; snapshotted here) |

Dispositions: **port** (copy + parameterize), **author** (net-new, informed by
source), **template** (generic fill-in shipped by init), **sibling** (installed
from claude-skills, referenced only), **snapshot** (raw capture kept as source
material, stripped before publish).

## Board engine (Phase 1)

| Kit artifact | Source | Disposition | Notes |
|---|---|---|---|
| `boardkit check` / `render` | `scripts/cards_index.py` (terminalbench-aura) | port | Parameterize cards dir (`docs/redesign/cards`), card-id scheme (`S\d+\|MILESTONE`), allowed statuses. Golden test: byte-identical output vs. a Phase 1 snapshot of the source board (cards S0-S37). |
| `boardkit review-packet` | `scripts/card_review_packet.py` | port | Remove hardcoded `DEFAULT_REPO` absolute path; repo path comes from `boardkit.toml`. Output dir stays gitignored working material. |
| `boardkit init` | none (pattern: claude-skills `bin/install-skills`) | author | Scaffolds cards dir, template, `boardkit.toml`, AGENTS.md/CLAUDE.md shims; grows sibling-install and agent-def placement in Phase 4. |
| `boardkit.toml` schema | none | author | cards dir, id prefix + sentinel, review repo path, statuses. |
| Card template + frontmatter contract | `docs/redesign/cards/_template.md` | port | Schema is already generic: id, title, status, depends, serialize-with, lineage, executor, gates, user-gates, commit-range. |
| NOT extracted: `scripts/loc_measure.py` | - | dropped | Aura-crate-specific LOC bucketing; not board machinery. |
| Delegation contract + `boardkit doctor` / `resolve-route` / `dispatch-brief` | none (source: the 2026-08-03 topology review findings F1, F2, F3, F5, F9) | author | Net-new capability, no counterpart in the source repo. `[contract]`/`[routes]`/`[roles]` in `boardkit.toml` make routing mechanically resolvable instead of four prose hops; `doctor` covers the installation-state matrix `check` was never meant to; `dispatch-brief` generates the brief PROCESS.md describes, quoting its clauses instead of restating them. Design: `docs/plans/2026-08-03-topology-hardening.md`. |

## Process documents (Phase 2)

| Kit artifact | Source | Disposition | Notes |
|---|---|---|---|
| `PROCESS.md` (kit) | `docs/redesign/PROCESS.md` - card schema, board mechanics, roles, gates sections | port | Strip the Aura program narrative (its program summary, repo map, branch topology, and commit standards) plus the Rust type-discipline specifics, which move to the typed-holes skill. Keep: WIP limit, log-in-same-turn, done-only-verified, roles (board owner / planner / executor / reviewer), gate ladder S/A/M/D/F/U, deferral logging, fix-commit re-review duty, executor-fallback rule. |
| `MODEL-CLASSES.md` | `PROCESS.md` roles section + `REVIEW-TOOLING.md` harness bindings, pre-vet, attended/unattended policy | author | Genericize to model *classes* (frontier orchestrator / smart writer-reviewer / small explorer) with current pins (GLM-5.2, Kimi K2.7, MiniMax M3, GPT-5.x, Claude) as worked examples. Carries: smart/any executor classes, reviewer-differs-from-author invariant, reviewer pre-vet checklist, empty-return-is-failed-delegation, attended/unattended guidance. |
| `REVIEW-TOOLING.md` template | `docs/redesign/REVIEW-TOOLING.md` | template | The per-project override doc: fill-in harness-bindings table, tool bindings, budget etiquette. Kit ships the shape; each project pins its own tools. |
| AGENTS.md / CLAUDE.md shims | terminalbench-aura root `AGENTS.md` + `CLAUDE.md` | template | Entry-point pattern: AGENTS.md canonical, CLAUDE.md/GEMINI.md one-line shims. Board-owner role rule and read order included. |
| Case-insensitivity trap note | PROCESS.md / AGENTS.md | dropped | `board.md` vs `BOARD.md` collision was an artifact of aura's frozen root archive; boardkit repos have no colliding file by construction, so no note ships. |

## Skills plugin (Phase 3)

| Kit artifact | Source | Disposition | Notes |
|---|---|---|---|
| `typed-holes` skill | `PROCESS.md` "Type discipline" + `TYPE_PLAN.md` conventions + retro-2026-07-02 ("golden frames") | author | Net-new skill; exists nowhere as a skill today. DMMF types first; compile-clean `todo!()` skeleton as its own commit; every public type maps to a business rule + forbidden invalid state; adversarial design panel between skeleton and fill; then small-model fill. "Ollama holes" is the informal name for this practice. |
| `board-hygiene` skill | `.claude/skills/board-hygiene/SKILL.md` (terminalbench-aura) | port | Generic steps kept (frontmatter-is-truth, log-in-same-turn, view regen, orientation canary); repo-specific steps (repo-map sync) become config-driven hooks. The Phase-3 port needs the skill steps plus the source PROCESS.md-level cold-start orientation-canary mandate ("a miss is a hard stop", source PROCESS.md ~230-238). (Landed: the kit PROCESS.md now carries the mandate in its orientation-canary section, hard-stop framing included.) |
| `delegating-work` skill | snapshots/user-skills/* + `REVIEW-TOOLING.md` transport guidance | author | CLI-first rewrite: `opencode run` / `codex exec` over MCP. Sources: REVIEW-TOOLING.md transport rule (MCP `opencode_fire`/`opencode_run` observed hanging, stale embedded build returning empty text) and the author's direct report that Claude Code struggles juggling OpenCode over MCP. Supersedes collaborating-with-opencode and collaborating-with-antigravity for board work. |
| Plugin marketplace layout + frontmatter validator | claude-skills `.claude-plugin/`, `bin/_check-frontmatter.py`, `bin/install-skills`, `bin/check-install` | port | Same mechanism: Claude Code marketplace + flat copy to `~/.agents/skills/` for OpenCode, manifest-based pruning, temp-`$HOME` install test. |
| Plugin marketplace scaffold (`.claude-plugin/marketplace.json`, `plugins/board/`) | none (shape follows claude-skills) | author | Landed 2026-08-03, manifests only: a marketplace named `boardkit` declaring one `board` plugin, and that plugin's manifest. The name must differ from the personal marketplace's `my-skills` or the per-source install manifests cross-prune. Shipped manifests-first on purpose - a skill that says nothing is worse than an absent one, because absence is detectable - with a test pinning the empty state until the bodies landed. The `board-hygiene` and `delegating-work` bodies landed later on 2026-08-03 and that test is gone. |

## Harness adapters (Phases 3-4)

| Kit artifact | Source | Disposition | Notes |
|---|---|---|---|
| `harness/opencode/agent/*.md` | `snapshots/opencode/agent/` (from `~/.dotfiles`) | port | rust-write (kimi-k2p7-code), rust-reviewer (glm-5p2, locked down so it cannot edit and its bash is restricted), and the python pair. Genericize model pins to documented defaults; keep permission profiles (the S3 lesson: a reviewer's bash allowlist must let it read the diff packet). |
| `harness/opencode/opencode.json` fragment | `snapshots/opencode/opencode.json` | port | Agent model pins + skill-permission blocks for build/plan/explore/general. Ship as a documented fragment to merge, not a whole-file overwrite. |
| Sibling install of language skills | claude-skills repo | sibling | `boardkit init` detects rust-*/python-*/docs-* skills and points at claude-skills `bin/install-skills` if missing. Never vendored. |
| Codex board owner | `REVIEW-TOOLING.md` harness bindings row | deferred | Named deferral: codex worked as a board owner (attended) but is out of v1 scope. The harness-bindings template keeps a codex row so adopters can wire it. |
| Pi harness | claude-skills README mentions | deferred | Mentioned in the claude-skills README but not planned for boardkit. |

## Snapshots (Phase 0 captures; stripped 2026-08-31, see the publish-gate rulings)

| Path | Origin | Why captured |
|---|---|---|
| `snapshots/opencode/agent/*.md` | `~/.config/opencode/agent/` -> `~/.dotfiles` | Working copies for Phase 3 genericization (also safe in dotfiles). |
| `snapshots/opencode/opencode.json` | same | Agent/skill-permission blocks. Checked: no real secrets (placeholder apiKey values only). |
| `snapshots/user-skills/collaborating-with-*` | `~/.claude/skills/` | Previously unversioned anywhere; git history is now their only backup. Source material for the `delegating-work` rewrite. |

## Dropped (program-specific)

| Dropped rule | Source | Why dropped |
|---|---|---|
| OTEL trace-receipt canary + benchmark-provenance user gates | `docs/redesign/PROCESS.md` ~421-428 | Specific to the aura benchmark program. |
| Gate M comparison-validity / provenance-delta table | `docs/redesign/PROCESS.md` ~398-411 | Specific to the aura benchmark program. |
| Single-variable benchmark loop rules | root `AGENTS.md`, "Benchmark Loop Rules" | Specific to the aura benchmark program. |
| Wiki-handoff writing bound to Claude Code | `docs/redesign/PROCESS.md` ~208-213, 441-443 | Specific to the aura benchmark program. |
| Vale-on-every-touched-markdown hygiene step | `.claude/skills/board-hygiene/SKILL.md:36` | Repo-specific tooling: the linter choice is repo-specific, and the REVIEW-TOOLING template is where a repo pins its linter. |
| Bounded-router ossification-risk rule | `docs/redesign/PROCESS.md` ~552-572 | Specific to the aura benchmark program. |
| Worktree inventory and accepted-head vs primary-head pin discipline | `docs/redesign/PROCESS.md` repo map and branch topology, post-freeze commits `ac8c931`, `18413dd`, `ceed389`, `4d5f7a7`, `c6a0806`, `832cd17` | Live program state, not a rule; the repo map and topology diagram were already stripped in Phase 2. |
| Writer/reviewer model pins in the harness-bindings prose | `docs/redesign/REVIEW-TOOLING.md` ~105-115, ~240-253, post-freeze commit `9705c5e` | Pins are a per-repo fill-in by design; the durable lesson lives in `MODEL-CLASSES.md` pre-vet. |

## Refresh 2026-07-28 (post-freeze drift)

The Phase 2 extraction froze against terminalbench-aura at `52784c1`
(2026-07-21). This section dispositions every process rule the source added
after that point, so the one-rule-one-state invariant holds again. Diff
window: `git diff 52784c1^..HEAD -- docs/redesign/PROCESS.md
docs/redesign/REVIEW-TOOLING.md .claude/skills/board-hygiene/SKILL.md
scripts/cards_index.py scripts/card_review_packet.py`. Line numbers below are
in the source repo at `832cd17` unless the target column says otherwise.

| Rule | Source | Disposition | Notes |
|---|---|---|---|
| Detached-side-quest WIP exemption | `docs/redesign/PROCESS.md:160-165`, `c2e189c` (2026-07-25) | port | A flow the user declares a detached side quest does not count against the WIP limit. It must not interrupt the mainline. It shares only test resources with the mainline, coordinated at its launch gates. The exemption is recorded on the flow's own cards. Target: PROCESS template, "Board mechanics", folded into the WIP-limit bullet. Genericize away the aura instance data (the S54-S60 flow, and notanton/Phoenix/Docker as the shared resources). (Landed in the working tree, 2026-07-28, as the optional `side-quest` frontmatter key the WIP check honors.) |
| Card-reference prose convention | `docs/redesign/PROCESS.md:170-175`, `be54d3b` (2026-07-26) | port | A card ID in prose (card logs, evidence files, process docs) carries a short human-readable qualifier; a bare ID is acceptable only in frontmatter `depends` lists and in inline code. Target: PROCESS template, "Board mechanics", new bullet after the accuracy-over-verbosity bullet. Rewrite the worked examples against the template's own id scheme, not `S53`/`S56`. (Landed in the working tree, 2026-07-28.) |
| Per-repo review packets for multi-repo cards | `docs/redesign/PROCESS.md:185-194`, `650caf3` (2026-07-27, user directive on S73) | port | A card whose work spans more than one repo gets one packet per repo, each output directory named for the repo it covers (`reviews/<id>-<suffix>`), so an external-repo diff never sits in a directory that reads as primary-repo content. Targets: PROCESS template, "Card schema", the `in-review` status bullet (currently lines 56-63) and the code-review packet paragraph under "Gates" (currently line 218). The kit must also grow the `--suffix` flag this naming implies; aura states the convention but its script has no flag for it, so the packet dirs are hand-made there. (Landed in the working tree, 2026-07-28, as `--suffix` plus the `--commit-range` override a second repo's shas need.) |
| Review packet cleans only its own outputs | `scripts/card_review_packet.py:199-209`, `4ef3f50` (2026-07-22) | port | Regenerating a packet used to `rmtree` the output directory, destroying the gate ledgers and reviewer transcripts kept alongside the generated diffs. The fix deletes only the generated files (`NN-*.diff`, `full-range.diff`, `REVIEW.md`) and keeps the directory. Not a template change: `src/boardkit/review_packet.py:176-178` still carries the pre-fix `shutil.rmtree`, so the kit has the same defect. (Landed in the working tree, 2026-07-28: `clean_generated` replaced the `shutil.rmtree` and deletes only this module's own outputs.) |
| Control checkout stays on the base branch | `docs/redesign/PROCESS.md:56`, `425a9ec` (2026-07-27) | port | The checkout that holds the board never parks on a `card/*` branch; a card that touches code takes its own worktree. A held card branch strands the board state a fresh session reads. The generalizable rule ships; the aura branch and path names do not. Target: PROCESS template, "Board mechanics", new bullet. (Landed in the working tree, 2026-07-28.) |
| Repo map lists every live worktree | `0151d20`, `ecf0918` (2026-07-26) | deferred | Two hygiene passes found worktrees missing from the map, which is a recurring hygiene defect, not a one-off. The generic form is a hygiene step that reconciles `git worktree list` against whatever worktree map the repo keeps. Deferred to the Phase 3 `board-hygiene` skill; no repo map ships in the kit templates (the Phase 2 row already strips the aura one), so this has no template home today. |
| Card worktrees cut off the accepted head; primary-head advances | `ac8c931`, `18413dd`, `ceed389`, `4d5f7a7`, `c6a0806`, `832cd17` | dropped | Live worktree inventory and benchmark-baseline pin discipline (which head is the accepted control versus the primary). Program-specific; the repo map and branch topology were already stripped at extraction. Also carried in the "Dropped (program-specific)" ledger. |
| Writer/reviewer model pin swap | `docs/redesign/REVIEW-TOOLING.md:105-115` and `:240-253`, `9705c5e` (2026-07-27) | dropped | The pins moved (`rust-write` to fireworks glm-5p2, `rust-reviewer` and `python-reviewer` to baseten Kimi-K2.7-Code, `python-write` to baseten GLM-5.2-Fast). Pins are exactly what the REVIEW-TOOLING template leaves as a per-repo fill-in, so a pin swap is never kit drift. The durable lesson under it, that agent names do not imply model families and the agent-definition file is the authority, is already carried by `MODEL-CLASSES.md` in the pre-vet "Model identity" bullet. |

Checked and unchanged in the window, so the Phase 2 dispositions still hold:
the fix-commit re-review duty (`docs/redesign/PROCESS.md:375-385`, last
touched `9afcedf`, 2026-07-17) and the executor-fallback three-attempt
threshold (`:303-310`, last touched `5e55745`, 2026-07-14). Both predate the
freeze and are already in the PROCESS template at lines 167-172 and 130-131.
`.claude/skills/board-hygiene/SKILL.md` and `scripts/cards_index.py` have no
commits in the window at all.

## Publish gate obligations (Phase 6)

- `snapshots/`: ruled STRIP 2026-08-31 and removed from the tree; git
  history keeps the only copy.
- `tests/golden/aura-cards/` and the `/Users/mshearer` paths in fixtures
  and one evidence doc: ruled KEEP 2026-08-31 - the cards are live test
  fixtures, their provenance (`mezmo/aura`) is a public repo, and the
  paths expose no credential. The sweep for account identifiers and cost
  figures outside clearly-marked examples still stands.
- README must pass a docs bus test cold: a fresh human or agent reaches a
  working board from the README alone. The bus test runs as a standing gate on
  every doc-producing phase, not only at publish.
