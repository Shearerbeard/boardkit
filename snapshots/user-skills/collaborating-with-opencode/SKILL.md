---
name: collaborating-with-opencode
description: Delegate Rust code writing, review, and exploration to OpenCode's autonomous agents (kimi-k2p7-code, glm-5p2, qwen3.7-max). Use for low-level Rust work, code review with dedicated agents, or long autonomous coding tasks. Prefer agy/Gemini for architectural, spec, product, and marketing review.
---

# Collaborating with OpenCode

OpenCode is an autonomous AI coding agent exposed via MCP tools. It runs
its own sessions with provider/model selection, permission management,
and file mutation capabilities.

## When to use

- **Rust code writing** - delegate implementation to the `rust-write`
  agent (kimi-k2p7-code), which loads `rust-design`, `rust-quality`, and
  `rust-modules` skills automatically.
- **Rust code review** - delegate review to the `rust-reviewer` agent
  (glm-5p2), which runs cargo check/clippy/fmt, then applies
  `rust-review`, `gate-probes`, and `prose-lint` probes. Read-only.
- **Long autonomous tasks** - fire off a coding task and monitor
  progress without blocking the main conversation.
- **Codebase exploration** - use the `explore` agent (minimax-m2.7)
  for fast file/symbol/text search across a project.
- **Planning** - use the `plan` agent (qwen3.7-max) for multi-step
  decomposition before implementation.

## When NOT to use (use agy/Antigravity instead)

- Architectural review or second opinion
- Spec, product, or marketing review
- Design discussion at the system level
- Any task where you want Gemini Pro's perspective

See `references/delegation-guide.md` for the full decision matrix.

## Quick start

### One-shot question
```
opencode_ask(prompt="Explain the error handling in src/error.rs",
             providerID="opencode-go", modelID="kimi-k2.6")
```

### Rust review (fire-and-forget)
```
opencode_fire(prompt="Review the diff on the current branch for correctness bugs",
              providerID="opencode-go", modelID="minimax-m2.7",
              agent="rust-reviewer")
# Check progress:
opencode_check(sessionId=<id>)
```

### Rust implementation (synchronous)
```
opencode_run(prompt="Implement the Provider newtype with validation",
             providerID="opencode-go", modelID="kimi-k2.6",
             agent="rust-write")
```

## Agent / model matrix

| Agent | Model | Mode | Use for |
|-------|-------|------|---------|
| `rust-write` | `fireworks-ai/.../kimi-k2p7-code` | subagent, writes | Rust implementation, refactoring |
| `rust-reviewer` | `fireworks-ai/.../glm-5p2` | subagent, read-only | Rust code review, cargo checks |
| `python-write` | `fireworks-ai/.../kimi-k2p7-code` | subagent, writes | Python implementation |
| `python-reviewer` | `fireworks-ai/.../glm-5p2` | subagent, read-only | Python code review |
| `plan` | `opencode-go/qwen3.7-max` | primary | Multi-step planning, breakdown |
| `build` | `opencode-go/kimi-k2.6` | primary | General coding (default) |
| `explore` | `opencode-go/minimax-m2.7` | subagent | Fast codebase search |
| `general` | `opencode-go/kimi-k2.6` | subagent | Multi-step research tasks |

Model pins drift and agent names do not imply model families: before
any review gate depends on an agent's model family, read
`~/.config/opencode/agent/*.md` - the config is the only source of
truth; this table is illustrative (custom-agent rows verified
2026-07-16). When a repo carries its own delegation doc (for
terminalbench-aura, `docs/redesign/REVIEW-TOOLING.md`), that doc
overrides this skill's routing and invocation defaults - including
its codex-first adversarial-review rule, its agy user-approval gate,
and its CLI-first transport rule (`opencode run -m <provider>/<model>`
for native sessions; MCP `session_create` + `message_send_async` +
`check` as the fallback, not `opencode_fire`/`opencode_run`).

## Tool tiers (prefer higher tiers)

### Tier 1 - one-shot (simplest)
- `opencode_ask` - create session + get response in one call
- `opencode_reply` - continue an existing session

### Tier 2 - async tasks (for complex work)
- `opencode_run` - send task, wait for completion (up to 10 min)
- `opencode_fire` - fire-and-forget, check with `opencode_check`
- `opencode_check` - cheap progress: status, todos, file counts

### Tier 3 - monitoring
- `opencode_review_changes` - see all file diffs from a session
- `opencode_conversation` - full message history
- `opencode_session_todo` - agent's internal task list

## Provider discovery

Always discover providers before sending prompts - do not hardcode:
```
opencode_setup()  # health check, list ready providers
opencode_provider_models(providerId="opencode-go")  # see available models
```

The user's preferred providers are `opencode-go` (Go subscription, 14
models) and `opencode` (Zen pay-as-you-go, 44 models). Both carry
`kimi-k2.6`.

Fireworks model strings: pass the plain
`accounts/fireworks/models/<name>` id, like
`accounts/fireworks/models/glm-5p2`. Never pass an
`accounts/fireworks/routers/*` id - routers are hardware-accelerated
variants that bill extra (user rule, 2026-07-12).

Reliability note (2026-07-12): `opencode_fire` and `opencode_run`
have hung at the MCP client while the server kept working. When they
misbehave, fall back to `opencode_session_create` +
`opencode_message_send_async` + polling with `opencode_check`.

## Multi-turn sessions

Capture the `sessionId` from the first response and pass it to
`opencode_reply` for follow-ups:
```
r1 = opencode_ask(prompt="Analyze the type model in src/types.rs", ...)
# r1 includes sessionId
opencode_reply(sessionId=r1.sessionId, prompt="Now propose improvements")
```

## Permission handling

OpenCode has its own permission system. When a session blocks on a
permission request:
```
opencode_permission_list()  # see pending requests
opencode_session_permission(id=<session>, permissionID=<perm>,
                            reply="once"|"always"|"reject")
```

The `rust-reviewer` agent is locked down: edit denied, bash limited to
cargo commands, skills limited to rust-*/gate-probes/prose-lint.

The `rust-write` agent allows edits but limits bash to cargo/rustc.

## Project targeting

Every OpenCode tool accepts an optional `directory` parameter to target
a specific project. Omit it to use OpenCode's current working directory.
```
opencode_ask(prompt="...", directory="/path/to/project")
```

## Detailed references

- `references/delegation-guide.md` - when to use OpenCode vs agy vs
  direct work.
- `references/prompt-patterns.md` - proven prompt scaffolds for each
  agent type.
- `references/usage.md` - full MCP tool reference, async patterns,
  session lifecycle.
