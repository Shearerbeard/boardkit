# 2026-08-09 prose packet vertical QC (k3)

End-state review of the phase-1 prose lane packet (38 manifest rows:
corpus, goldens, fixtures, rubrics) against `bench/README.md`.
Reviewer: `kimi-for-coding/k3` via `opencode run`, nonce readback both
rounds, caller-owned deadlines. Author models: claude-fable-5
(orchestrator plus four research subagents). Prompts staged under
`.review/2026-08-09-prose-packet/` (gitignored); raw transcripts in
session scratch.

## Round 1: FAIL, five findings

1. BLOCKING. The epoch-retro fresh-write task asked for a retro and no
   rubric grades one; rubric-fresh-adr would hard-fail a correct
   retro. Fixed: the brief re-scopes the task to an upstream ticket to
   the Epoch maintainer, graded by rubric-ticket.
2. BLOCKING. Fixtures embedding their own reference answers (spike
   TL;DR and Decision sections, retro fix spoilers) leaked under
   verbatim staging; the contract barred only `rubrics/` from candidate
   packets. Fixed: `bench/README.md` hidden-material section adds two
   staging rules, bodies-only staging (frontmatter stripped) and
   brief-listed excisions applied to staged copies.
3. MINOR. Seat-count mismatch between the review prompt (6 candidates)
   and the pre-vet evidence. Disposition, no packet change: the roster
   is 5 candidates plus the Opus control, 6 seats; the error was in
   the review prompt.
4. MINOR. Keep-or-purge flag covered only org-sourced rows. Fixed: the
   MANIFEST flag paragraph now also covers every third-party row with
   a license header.
5. MINOR. Corpus frontmatter notes named the defects under test and
   would coach a candidate. Fixed by the bodies-only staging rule.

## Round 2: PASS, empty ledger

k3 verified every fix by direct reads, re-hashed all 38 manifest rows
with zero mismatches, and confirmed the evidence file is internally
consistent with the 5-plus-control roster.

Carried note for the eval design (not a defect): rubric-ticket D3
prefers one problem per ticket, and the epoch-retro task proposes five
fixes on one problem surface (Epoch's consumer-boundary contract), so
a compliant candidate caps at the mild-prescription anchor there.
Graders should read D3 for that task with the brief's framing in mind.
