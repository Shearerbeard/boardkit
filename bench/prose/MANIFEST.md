# Prose lane manifest

Index of every specimen and authored file in this lane. Frozen
2026-08-09 for the writer mini-eval; a consuming run re-verifies
hashes before staging and stops on any mismatch (freeze rule:
`bench/README.md`).

Baseline validity rule: a vale count is valid only when vale's stderr
was empty on that run. Two silent-failure modes produced fake zeros
during intake (unquoted YAML colons breaking the frontmatter parser,
and an unwritable stderr redirect); every count below is from a
stderr-verified run. Specimens are counted under the GLOBAL config
(`~/.vale.ini`), since the repo config exempts specimen dirs on
purpose. Authored files are counted under the repo config and must be
zero.

Reading the golden baselines: aura and chore-lottery goldens score at
or near zero since they already pass this toolchain's style gates.
The OSS doc goldens are a different case. Upstream em dashes and
human prose rhythms trip the ai-tells heuristics (tailwind 13,
herdr 12); those files exemplify OSS documentation tone rather than
the local style rules, so their counts are recorded for honesty, not
as defects. Rubric false-positive guards cover the distinction.

Org-sourced rows (every `aura-` entry) and third-party rows (every
row with a license in its entry header: the OSS docs excerpts and the
`oss-` pr-issue goldens) are flagged keep-or-purge: the user rules at
a gate whether mezmo-internal and quoted third-party text stays in
this repo long term. Ruled KEEP at the 2026-08-09 phase-1 packet
gate.

Not indexed: `corpus-inbox/README.md` and this file (lane
infrastructure, not material); `bench/README.md` (the contract sits
above the lane).

| File | Role | Provenance | Vale baseline | Words | sha256/16 |
|------|------|------------|---------------|-------|-----------|
| corpus-inbox/2026-08-09-aura-474-redis-approval-no-durable-record.md | corpus | https://github.com/mezmo/aura/issues/474 | 2 (global) | 230 | 819bfeb908932297 |
| corpus-inbox/2026-08-09-aura-475-cross-instance-cancel-no-terminal-frame.md | corpus | https://github.com/mezmo/aura/issues/475 | 1 (global) | 248 | 93bef7aa7fe9dfd5 |
| goldens/pr-issue/2026-08-09-aura-310-blessed-mcp-install-helper.md | golden | https://github.com/mezmo/aura/issues/310 | 1 (global) | 256 | d2896dc8e8a4b2f4 |
| goldens/pr-issue/2026-08-09-aura-383-a2a-visibility-first-party-cli.md | golden | https://github.com/mezmo/aura/issues/383 | 0 (global) | 426 | ef5260a877c8c312 |
| goldens/pr-issue/2026-08-09-aura-423-docs-site-buildout.md | golden | https://github.com/mezmo/aura/issues/423 | 0 (global) | 95 | 1da95e1ae9f9fe43 |
| goldens/pr-issue/2026-08-09-aura-424-31-days-of-aura.md | golden | https://github.com/mezmo/aura/issues/424 | 0 (global) | 124 | db90b44740b9edd1 |
| goldens/pr-issue/2026-08-09-aura-429-ruleprod-demo-environment.md | golden | https://github.com/mezmo/aura/issues/429 | 0 (global) | 148 | 746d55d1dfec0df4 |
| goldens/pr-issue/2026-08-09-aura-430-pagerduty-demo-path.md | golden | https://github.com/mezmo/aura/issues/430 | 0 (global) | 107 | 6f9da3142576e83c |
| goldens/pr-issue/2026-08-09-oss-ghostty-pr-remove-blake3-digests.md | golden | https://github.com/ghostty-org/ghostty/pull/13680 | 2 (global) | 184 | e110beaa658e40d2 |
| goldens/pr-issue/2026-08-09-oss-tokio-issue-msrv-windows.md | golden | https://github.com/tokio-rs/tokio/issues/8299 | 6 (global) | 254 | 6c00ce0f880089f1 |
| goldens/pr-issue/2026-08-09-oss-tokio-issue-zero-length-pending.md | golden | https://github.com/tokio-rs/tokio/issues/8321 | 1 (global) | 366 | e9a360f50053f02f |
| goldens/pr-issue/2026-08-09-oss-tokio-pr-delayqueue-clear-wake.md | golden | https://github.com/tokio-rs/tokio/pull/8320 | 1 (global) | 150 | 1ac6d97d03ab30de |
| goldens/pr-issue/2026-08-09-oss-tokio-pr-zero-length-mem-stream.md | golden | https://github.com/tokio-rs/tokio/pull/8323 | 1 (global) | 166 | 2ef3a813dfd74e52 |
| goldens/pr-issue/2026-08-09-oss-zed-pr-hover-reconcile.md | golden | https://github.com/zed-industries/zed/pull/62335 | 0 (global) | 215 | e7285ebfc5573419 |
| goldens/pr-issue/2026-08-09-oss-zed-pr-run-until-readiness.md | golden | https://github.com/zed-industries/zed/pull/62220 | 0 (global) | 200 | 1af7371726a5c645 |
| goldens/oss-docs/2026-08-09-herdr-readme.md | golden | https://github.com/herdrdev/herdr/blob/master/README.md | 12 (global) | 381 | 89d66e8434e4599e |
| goldens/oss-docs/2026-08-09-kubernetes-pods-concept.md | golden | https://kubernetes.io/docs/concepts/workloads/pods/ | 1 (global) | 406 | e84f3651a204581e |
| goldens/oss-docs/2026-08-09-rust-book-what-is-ownership.md | golden | https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html | 0 (global) | 1071 | 2aec24bb290ed341 |
| goldens/oss-docs/2026-08-09-stripe-webhooks-intro.md | golden | https://docs.stripe.com/webhooks | 3 (global) | 564 | 480d9272bc740627 |
| goldens/oss-docs/2026-08-09-tailwind-styling-with-utilities.md | golden | https://tailwindcss.com/docs/styling-with-utility-classes | 13 (global) | 587 | edfe90898b20c450 |
| goldens/chore-lottery/2026-08-09-readme.md | golden | chore-lottery@0b0330e87bf8aca2e059c633665d17603a6be13a:README.md | 0 (global) | 334 | 7b8fc8d2e7ae6ec6 |
| goldens/chore-lottery/2026-08-09-sync-architecture.md | golden | chore-lottery@0b0330e87bf8aca2e059c633665d17603a6be13a:docs/design/sync-architecture.md | 0 (global) | 680 | 5d4597e32f1e1672 |
| fixtures/chore-lottery/2026-08-09-domain-design.md | fixture | chore-lottery@0b0330e87bf8aca2e059c633665d17603a6be13a:crates/domain/DESIGN.md | 0 (global) | 2813 | ce86752ced7117b5 |
| fixtures/chore-lottery/2026-08-09-epoch-retro.md | fixture | chore-lottery@0b0330e87bf8aca2e059c633665d17603a6be13a:docs/board/retro/2026-08-04-epoch-friction-retro.md | 0 (global) | 910 | 6c9ffd69bf4bc0f6 |
| fixtures/chore-lottery/2026-08-09-lottery-design.md | fixture | chore-lottery@0b0330e87bf8aca2e059c633665d17603a6be13a:crates/lottery/DESIGN.md | 0 (global) | 2925 | 2327c9635770d3d4 |
| fixtures/chore-lottery/2026-08-09-review-tooling.md | fixture | chore-lottery@0b0330e87bf8aca2e059c633665d17603a6be13a:docs/board/REVIEW-TOOLING.md | 0 (global) | 2147 | 76ea097db7994c2d |
| fixtures/chore-lottery/2026-08-09-s2-webhook-spike.md | fixture | chore-lottery@0b0330e87bf8aca2e059c633665d17603a6be13a:docs/spikes/s2-vikunja-webhooks.md | 0 (global) | 2116 | 3844b172b0bf566d |
| rubrics/rubric-doc-cleanup.md | rubric | authored | 0 (repo) | 787 | 59f427e07d880b87 |
| rubrics/rubric-fresh-adr.md | rubric | authored | 0 (repo) | 801 | 89bf799e2463b123 |
| rubrics/rubric-pr-description.md | rubric | authored | 0 (repo) | 747 | 4d854660b26db53e |
| rubrics/rubric-ticket.md | rubric | authored | 0 (repo) | 755 | 94795fe8a6756617 |
| rubrics/taxonomy.md | rubric | authored | 0 (repo) | 613 | 1d8be68f3a87781b |
| rubrics/voice-profile-draft.md | rubric | authored | 0 (repo) | 550 | c7583475d1a7d2a8 |
| rubrics/briefs/domain-design-brief.md | rubric | authored | 0 (repo) | 417 | cf3638f7d277a056 |
| rubrics/briefs/epoch-retro-brief.md | rubric | authored | 0 (repo) | 549 | eec00f4e2c157dc8 |
| rubrics/briefs/lottery-design-brief.md | rubric | authored | 0 (repo) | 481 | 938f15af717ad529 |
| rubrics/briefs/review-tooling-brief.md | rubric | authored | 0 (repo) | 708 | 6566dfa4b43c5477 |
| rubrics/briefs/s2-webhook-spike-brief.md | rubric | authored | 0 (repo) | 523 | f318f92d3b18803b |
