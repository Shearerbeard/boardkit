# Prompt patterns

Proven scaffolds for each OpenCode agent. Always pass `providerID` and
`modelID` explicitly.

## rust-write - implementation

Use when delegating Rust code creation or refactoring. The agent
automatically loads `rust-design`, `rust-quality`, and `rust-modules`.

```
Implement: <what to build>
Project: <absolute path>
Files to touch: <list>
Constraints:
- Follow existing module conventions (no mod.rs, re-export facade).
- Newtypes for stringly-typed parameters with validation in ::new().
- thiserror for library errors, anyhow for application errors.
- Design types before logic. Sketch signatures first.
Out of scope: <anti-goals>
After implementation: run `cargo check` and `cargo clippy -- -D warnings`.
```

Example:
```
opencode_run(
  prompt="""Implement: ModelId newtype with validation
Project: /Users/mshearer/dev/opencode-usage
Files to touch: src/types.rs
Constraints:
- Private inner String field, pub fn new() -> Result<Self, Error>
- Validate: non-empty, ASCII alphanumeric + hyphens + dots + slashes
- Implement Display, AsRef<str>, TryFrom<String>
- #[must_use] on the constructor
Out of scope: serialization, database mapping
After implementation: run cargo check and cargo clippy -- -D warnings.""",
  providerID="opencode-go", modelID="kimi-k2.6",
  agent="rust-write"
)
```

## rust-reviewer - code review

Use for reviewing diffs, PRs, or specific files. Read-only. The agent
runs cargo check/clippy/fmt, then applies rust-review and gate-probes.

```
Review: <what to review - diff, branch, or specific files>
Focus on, in order:
1. Correctness (logic bugs, edge cases, type safety)
2. Ownership (unnecessary clones, borrow issues, lifetime problems)
3. Error handling (proper ? chaining, no unwrap in library code)
4. Style (only if it hurts readability)
Output: numbered list, severity P0/P1/P2/P3, with file:line.
Skip nits.
```

Example:
```
opencode_fire(
  prompt="""Review: all changes on the current branch vs main
Focus on:
1. Correctness (logic bugs, edge cases, type safety)
2. Ownership (unnecessary clones, borrow issues)
3. Error handling (proper ? chaining, no unwrap)
Output: numbered list, P0-P3 severity, file:line references.""",
  providerID="opencode-go", modelID="minimax-m2.7",
  agent="rust-reviewer"
)
```

## plan - multi-step breakdown

Use before non-trivial implementation. No edit tools available.

```
Goal: <one-sentence goal>
Project: <absolute path>
Key files: <list of relevant files>
Known constraints: <test suite, public API, backwards compat>
Plan format: numbered steps, each independent, each <= 30 min.
Out of scope: <anti-goals>
```

## explore - codebase search

Use for finding files, symbols, or text patterns.

```
opencode_ask(
  prompt="Find all uses of the Tier enum across the codebase. List each
file and line number.",
  providerID="opencode-go", modelID="minimax-m2.7",
  agent="explore"
)
```

Specify thoroughness in the prompt: "quick" for targeted lookup,
"medium" for moderate exploration, "very thorough" for comprehensive
search across multiple locations and naming conventions.

## build - general coding

The default agent. Use for non-Rust tasks or mixed work.

```
opencode_ask(
  prompt="<task description>",
  providerID="opencode-go", modelID="kimi-k2.6",
  agent="build"
)
```

## Anti-patterns

- **Don't concatenate unrelated tasks** into one prompt. One goal per
  session.
- **Don't skip the constraints block** - without it the agent may
  introduce unwanted patterns (mod.rs, speculative fallbacks, etc.).
- **Don't ask rust-reviewer to fix things** - it's read-only by design.
  Use rust-write for fixes.
- **Don't omit the project path** when targeting a specific repo.