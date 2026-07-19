# Extraction map

This file traces every boardkit artifact to its source and records its
disposition. It is the working contract for the extraction; it gets pruned to
a short provenance note before publish.

Source repositories (private, on the author's machine):

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
| `boardkit check` / `render` | `scripts/cards_index.py` (terminalbench-aura) | port | Parameterize cards dir (`docs/redesign/cards`), card-id scheme (`S\d+\|MILESTONE`), allowed statuses. Golden test: byte-identical output vs. a snapshot of the live board. |
| `boardkit review-packet` | `scripts/card_review_packet.py` | port | Remove hardcoded `DEFAULT_REPO` absolute path; repo path comes from `boardkit.toml`. Output dir stays gitignored working material. |
| `boardkit init` | none (pattern: claude-skills `bin/install-skills`) | author | Scaffolds cards dir, template, `boardkit.toml`, AGENTS.md/CLAUDE.md shims; grows sibling-install and agent-def placement in Phase 4. |
| `boardkit.toml` schema | none | author | cards dir, id prefix + sentinel, review repo path, statuses. |
| Card template + frontmatter contract | `docs/redesign/cards/_template.md` | port | Schema is already generic: id, title, status, depends, serialize-with, lineage, executor, gates, user-gates, commit-range. |
| NOT extracted: `scripts/loc_measure.py` | - | dropped | Aura-crate-specific LOC bucketing; not board machinery. |

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
| `board-hygiene` skill | `.claude/skills/board-hygiene/SKILL.md` (terminalbench-aura) | port | Generic steps kept (frontmatter-is-truth, log-in-same-turn, view regen, orientation canary); repo-specific steps (repo-map sync) become config-driven hooks. |
| `delegating-work` skill | snapshots/user-skills/* + `REVIEW-TOOLING.md` transport guidance | author | CLI-first rewrite: `opencode run` / `codex exec` over MCP. Sources: REVIEW-TOOLING.md transport rule (MCP `opencode_fire`/`opencode_run` observed hanging, stale embedded build returning empty text) and the author's direct report that Claude Code struggles juggling OpenCode over MCP. Supersedes collaborating-with-opencode and collaborating-with-antigravity for board work. |
| Plugin marketplace layout + frontmatter validator | claude-skills `.claude-plugin/`, `bin/_check-frontmatter.py`, `bin/install-skills`, `bin/check-install` | port | Same mechanism: Claude Code marketplace + flat copy to `~/.agents/skills/` for OpenCode, manifest-based pruning, temp-`$HOME` install test. |

## Harness adapters (Phases 3-4)

| Kit artifact | Source | Disposition | Notes |
|---|---|---|---|
| `harness/opencode/agent/*.md` | `snapshots/opencode/agent/` (from `~/.dotfiles`) | port | rust-write (kimi-k2p7-code), rust-reviewer (glm-5p2, locked down so it cannot edit and its bash is restricted), and the python pair. Genericize model pins to documented defaults; keep permission profiles (the S3 lesson: a reviewer's bash allowlist must let it read the diff packet). |
| `harness/opencode/opencode.json` fragment | `snapshots/opencode/opencode.json` | port | Agent model pins + skill-permission blocks for build/plan/explore/general. Ship as a documented fragment to merge, not a whole-file overwrite. |
| Sibling install of language skills | claude-skills repo | sibling | `boardkit init` detects rust-*/python-*/docs-* skills and points at claude-skills `bin/install-skills` if missing. Never vendored. |
| Codex board owner | `REVIEW-TOOLING.md` harness bindings row | deferred | Named deferral: codex worked as a board owner (attended) but is out of v1 scope. The harness-bindings template keeps a codex row so adopters can wire it. |
| Pi harness | claude-skills README mentions | deferred | Mentioned in the claude-skills README but not planned for boardkit. |

## Snapshots (Phase 0 captures, strip before publish)

| Path | Origin | Why captured |
|---|---|---|
| `snapshots/opencode/agent/*.md` | `~/.config/opencode/agent/` -> `~/.dotfiles` | Working copies for Phase 3 genericization (also safe in dotfiles). |
| `snapshots/opencode/opencode.json` | same | Agent/skill-permission blocks. Checked: no real secrets (placeholder apiKey values only). |
| `snapshots/user-skills/collaborating-with-*` | `~/.claude/skills/` | Previously unversioned anywhere; this is now their only backup. Source material for the `delegating-work` rewrite. |

## Publish gate obligations (Phase 6)

- Remove or genericize `snapshots/` entirely.
- Grep-sweep for `/Users/mshearer`, account identifiers, cost figures outside
  clearly-marked examples.
- README must pass a docs bus test cold: a fresh human or agent reaches a
  working board from the README alone. The bus test runs as a standing gate on
  every doc-producing phase, not only at publish.
