---
id: S3
title: claude-skills defect sweep from the topology audit
status: ready
depends: []
serialize-with: []
lineage: none
executor: any
gates: "S -> A"
user-gates: []
---

# S3: claude-skills defect sweep from the topology audit

Mechanics: [PROCESS.md](../PROCESS.md). Required reading before pulling:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Plan:
[2026-08-04-productionize-verification.md](../../plans/2026-08-04-productionize-verification.md),
stage 3. External repo: `~/dev/claude-skills`.

## Scope

In `~/dev/claude-skills` only: the three transport skills
(`opencode-cli`, `codex-cli`, `collaborating-with-antigravity`),
`process-feedback`, plugin `bin/` directories, and `bin/check-skills`
if path rules move.

## Deliverable

- Both-absent degrade path stated in `opencode-cli` and
  `collaborating-with-antigravity`, matching the one `codex-cli`
  already carries.
- The fireworks router-id grammar line generalized to a
  provider-neutral cost warning; the glm/kimi trigger roster in the
  `opencode-cli` description softened to role vocabulary.
- `agy_bridge.py` moved from `skills/*/scripts/` to
  `plugins/workflow/bin/` with call sites updated;
  `collaborating-with-antigravity` gains the `compatibility:`
  frontmatter every other skill carries.
- The review-nesting invariant generalized: codex and agy sessions get
  the same never-self-shell rule opencode has.
- `process-feedback` stops advertising a rust-holes inbox format that
  does not exist; it names the redirect-to-boardkit contract instead.

## Acceptance

- `bin/check-skills` passes in that repo; `vale` clean on touched
  skills.
- Each bullet above verifiable by reading the named file.

## Gate checklist

- [ ] Gate S: `bin/check-skills`, `vale` on touched files.
- [ ] Gate A: adversarial review with the question: does any transport
  skill still leave a non-boardkit consumer at a dangling pointer?

## Branch

direct; external commits recorded in the Log as they land.

## Log

- 2026-08-04 Authored from the claude-skills tier audit (findings 1-10).
