# Usage reference

Full MCP tool reference, async patterns, and session lifecycle for
OpenCode collaboration.

## Tool reference by tier

### Tier 1 - Essential

**opencode_ask** - One-shot. Creates a session, sends prompt, returns
response. Simplest entry point.
```
opencode_ask(prompt, providerID, modelID, [agent], [directory], [title])
```

**opencode_reply** - Continue a conversation in an existing session.
```
opencode_reply(sessionId, prompt, [providerID], [modelID], [agent])
```

**opencode_context** - Read-only project info (path, git, config, agents).
```
opencode_context([directory])
```

**opencode_setup** - Health check + provider discovery. Call first if
unsure about available providers.
```
opencode_setup([directory])
```

### Tier 2 - Async tasks

**opencode_run** - Send task, block until done. Best for tasks under 10
min. Combines session create + send + poll.
```
opencode_run(prompt, [providerID], [modelID], [agent], [directory],
             [maxDurationSeconds], [sessionId], [title])
```

**opencode_fire** - Fire-and-forget. Returns immediately with sessionId.
Use `opencode_check` to monitor.
```
opencode_fire(prompt, [providerID], [modelID], [agent], [directory],
              [sessionId], [title])
```

**opencode_check** - Cheap progress report: status, todos, file counts.
Much lighter than `opencode_conversation`.
```
opencode_check(sessionId, [detailed], [directory])
```

**opencode_wait** - Block until session finishes. Use after
`opencode_message_send_async`. Has timeout.
```
opencode_wait(sessionId, [timeoutSeconds], [pollIntervalMs], [directory])
```

### Tier 3 - Monitoring and review

**opencode_review_changes** - All file diffs from a session.
```
opencode_review_changes(sessionId, [messageID], [directory])
```

**opencode_conversation** - Full message history.
```
opencode_conversation(sessionId, [limit], [directory])
```

**opencode_session_todo** - Agent's internal task list.
```
opencode_session_todo(id, [directory])
```

### Tier 4 - Session management

**opencode_session_list** - List all sessions.
**opencode_session_get** - Get session details by ID.
**opencode_session_abort** - Stop a running session.
**opencode_session_delete** - Delete a session and its data.
**opencode_session_fork** - Fork at a specific message.
**opencode_sessions_overview** - Quick titles + status for all sessions.

### Tier 5 - Permissions

**opencode_permission_list** - See pending permission requests.
**opencode_session_permission** - Approve/deny a permission request.
```
opencode_session_permission(id, permissionID, reply="once"|"always"|"reject")
```

### Tier 6 - Provider management

**opencode_provider_list** - All providers with connection status.
**opencode_provider_models** - Models for a specific provider.
**opencode_provider_test** - Quick-test a provider (creates temp session).

## Async workflow patterns

### Pattern 1: Fire and check (non-blocking)

Best for long tasks where you want to continue working.

```
# Fire the task
r = opencode_fire(prompt="...", agent="rust-reviewer", ...)
sid = r.sessionId

# Do other work...

# Check progress when convenient
opencode_check(sessionId=sid)

# When done, review results
opencode_review_changes(sessionId=sid)
opencode_conversation(sessionId=sid, limit=5)
```

### Pattern 2: Run and wait (blocking)

Best for sequential workflows where you need the result.

```
r = opencode_run(prompt="...", agent="rust-write", ...,
                 maxDurationSeconds=300)
# r contains the full response
```

### Pattern 3: Multi-turn conversation

Best for iterative refinement.

```
r1 = opencode_ask(prompt="Analyze src/types.rs", ...)
# Review r1...
r2 = opencode_reply(sessionId=r1.sessionId,
                     prompt="Now add Display impl for ModelId")
```

### Pattern 4: Parallel agents

Fire multiple independent tasks, check all.

```
r1 = opencode_fire(prompt="Review src/types.rs", agent="rust-reviewer")
r2 = opencode_fire(prompt="Review src/client.rs", agent="rust-reviewer")
# Later:
opencode_check(sessionId=r1.sessionId)
opencode_check(sessionId=r2.sessionId)
```

## Session lifecycle

```
created → running → completed
                  → failed
                  → aborted (via opencode_session_abort)
```

Sessions persist across OpenCode restarts. Use
`opencode_session_delete` to clean up old sessions.

## Configuration

OpenCode config lives at `~/.config/opencode/opencode.json` (symlinked
from dotfiles). Key fields:

- `model` - default model (`opencode-go/kimi-k2.6`)
- `small_model` - fast model for lightweight tasks (`opencode-go/deepseek-v4-flash`)
- `default_agent` - agent used when none specified (`plan`)
- `agent` - per-agent model and permission overrides
- `provider` - custom provider/model definitions
- `mcp` - MCP server configs (includes agy bridge)
- `lsp` - language server configs (vale for markdown)

## Error handling

- If `opencode_setup` shows a provider as not ready, its API key is
  missing or invalid.
- Empty responses usually mean `providerID`/`modelID` were omitted.
- Permission blocks show up in `opencode_permission_list`. Approve
  or reject to unblock the session.
- Use `opencode_session_abort` to kill a stuck session.