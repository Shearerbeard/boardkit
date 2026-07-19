# Delegation guide: OpenCode vs agy vs direct work

## Decision matrix

| Task type | Delegate to | Why |
|-----------|-------------|-----|
| Rust implementation | OpenCode `rust-write` (kimi-k2.6) | ADT-first design, type-driven Rust, loads rust-design/quality/modules skills |
| Rust code review | OpenCode `rust-reviewer` (minimax-m2.7) | Read-only, runs cargo checks, applies rust-review + gate-probes |
| Codebase exploration | OpenCode `explore` (minimax-m2.7) | Fast file/symbol/text search |
| Multi-step planning | OpenCode `plan` (qwen3.7-max) | Structured breakdown, no edit tools |
| Architecture review | agy (gemini-pro) | System-level thinking, different perspective |
| Spec / product review | agy (gemini-pro) | Product-oriented lens |
| Marketing copy review | agy (gemini-pro) | Voice, tone, positioning |
| Second opinion on design | agy (gemini-pro) | Independent model, different training data |
| Trivial one-shot question | Direct work | Round-trip overhead not worth it |
| Single-file edit | Direct work | Faster to do inline |
| Git operations | Direct work | Neither agent should touch git |

## When to go async

Use `opencode_fire` + `opencode_check` (not `opencode_run`) when:
- The task will take more than 2-3 minutes
- You have other work to do while waiting
- The task is exploratory and you don't need the result immediately

Use `opencode_run` when:
- You need the result before continuing
- The task is under 10 minutes
- You're in a sequential workflow

Use `opencode_ask` when:
- It's a simple question or small task
- You want the answer inline, right now

## Combining agents across a workflow

A typical Rust implementation flow:

1. **Plan** - `opencode_ask` with `agent="plan"` to break down the work
2. **Implement** - `opencode_run` with `agent="rust-write"` per step
3. **Review** - `opencode_fire` with `agent="rust-reviewer"` on the result
4. **Architecture check** - `agy` in `review` mode for system-level concerns

## Anti-patterns

- **Don't delegate trivial edits** - the session setup overhead costs
  more than doing it directly.
- **Don't skip provider discovery** - always pass `providerID` and
  `modelID` explicitly. Omitting them can produce empty responses.
- **Don't use OpenCode for architectural opinions** - that's agy's
  strength (Gemini Pro, different training data, different perspective).
- **Don't use agy for low-level Rust** - kimi-k2.6 with the dedicated
  rust-write agent and loaded skills is purpose-built for this.
- **Don't fire multiple sessions for the same task** - check if an
  existing session is still running first.