---
id: S35
title: Fix templates chained .replace() re-substitution (Gate F1)
status: backlog
depends: []
serialize-with: []
lineage: accepted-head
executor: any
gates: "S -> A"
user-gates: []
---

# S35: Fix templates chained .replace() re-substitution (Gate F1)

Fix-forward card from the MILESTONE Gate F review (F1) and the accept
investigation, which confirmed the bug is real but inert on benchmark
content (task text carries no `%%MARKER%%` tokens). Mechanics:
[PROCESS.md](../PROCESS.md). Required reading:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md).

## Scope

`crates/aura/src/orchestration/templates.rs`: the `TemplateVars::render`
impls render `%%VAR%%` placeholders with chained `.replace()` calls. A
value substituted for an earlier placeholder is then re-scanned by the
later `.replace()` calls, so content that literally contains a later
`%%MARKER%%` token is re-substituted. This is a latent injection /
behavior-drift bug: a user query or worker output containing a marker
token would be corrupted, unlike the baseline `format!` single-pass
render.

## Deliverable

A single-pass substitution in `render` (one scan that fills each
placeholder from the context without re-scanning already-substituted
content), preserving the existing `%%VAR%%` convention and output for
marker-free input.

## Acceptance

- A unit test where a variable value literally contains a later
  placeholder token (`query = "show %%WORKER_SECTION%%"`) renders that
  token verbatim, not re-substituted.
- `cargo test` passes; the golden frames are unchanged (marker-free
  input renders byte-identically to today).
- `cargo fmt` and `cargo clippy` clean.

## Gate checklist

- [ ] Gate S: fmt, clippy, lib tests, the new re-substitution test.
- [ ] Gate A: fresh cross-model review of the diff.

## Branch

Local branch `card/S35` off the accepted head `7a0f0651`; no pushes
before gates pass; commit range recorded here at Done.

## Log

- 2026-07-18 Filed on MILESTONE acceptance as the F1 fix-forward the
  accept investigation required. Real bug, inert on benchmark content;
  not accept-blocking, fix-forward.
