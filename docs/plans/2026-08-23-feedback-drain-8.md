# Feedback drain 8 (2026-08-23)

Maintainer-directed partial drain. Mike directed the sitting with one
framing that governs every disposition below: this is cleanup and
minor tweaks for a system the program has very little issue with, not
a readiness program. One entry drains
(`rust-holes-second-dev-audit-cards`); the three earlier entries
(`opencode-exit0-truncation-not-in-stall-protocol`,
`serialize-with-misses-in-review-fix-rounds`,
`dispatch-briefs-may-over-instruct`) stay queued for the next sitting,
which owes them.

Source material: the rust-holes audit and staged plan at
`rust-holes docs/plans/2026-08-23-second-dev-readiness.md` (revision
2, both adversarial reviews dispositioned in its ledger) and the local
record at claude-skills
`feedback/2026-08-23-claude-code-rust-holes-second-dev-audit/`.

Dispositions:

1. **RH1 ADOPTED as S45** (`s45-rust-holes-self-check.md`, ready). A
   `bin/check` self-check in rust-holes plus the template
   provenance-stamp line, and the fix for the stale README read-order
   table the audit found. Smallest card, first pull.
2. **RH4 ADOPTED as S47** (`s47-rust-holes-brief-class-tags.md`,
   ready, serialize-with S4 since both touch
   `templates/dispatch-brief.md`). Model-class tags on the two brief
   blocks; classes only, never model ids. Closes the two 2026-08-05
   executor-cost-plan checkboxes or routes the prose half to the
   Delegating section's post-S4 owner.
3. **RH3 ADOPTED as S46** (`s46-rust-holes-consuming-doc.md`,
   backlog, depends S4, epic S41). One lean page: access,
   prerequisites, standalone path first, family path second, the
   re-diff recipe, the explicit ask-Mike list. Sequencing amendment
   under the cleanup framing: the draft's S26/S36 dependencies are
   dropped. The review finding that argued for them (K3) assumed the
   discovery section must document the docked end state; the
   maintainer framing prefers the doc now, documenting current state,
   with the one-line resolution update owned by S36 when docking
   lands. Recorded here so the reversal is a decision, not drift.
4. **RH2 REJECTED.** The smoke crate with cold-run canary and Gate T
   handout is over-scoped for current pain: the practice already has
   a live external consumer (chore-lottery, the standing Gate T
   venue and first external boardkit + rust-holes consumer), which is
   stronger evidence than a synthetic exercise. Re-propose when a
   real second-developer onboarding is scheduled. The draft's
   exercise-branch mechanism (cut the exercise from the recorded
   skeleton sha so HEAD stays green) is worth keeping and is recorded
   here for that future card.
5. **Retro vet, narrow slice.** The claude-skills 2026-07-28 retro's
   §6a sentence is vetted for use at S4 time: it names no repo, path,
   or private identifier, and it states the same authority direction
   S4 encodes. The full retro stays unvetted; only §6a is cleared.
   The sentence lands in the public SKILL.md during the S4 phase with
   the diff user-gated, since S4's own scope is rust-holes-only.
6. **Phasing** (the maintained sequence for the adopted work):
   Phase 1 is S45 then S47, mechanical, no user gates. Phase 2 is S4
   as written plus the vetted §6a sentence, one user gate on the
   public diff. Phase 3 is S46, one user gate on the read. S26 and
   S36 stay on the board at their own pace; neither blocks a second
   developer under the cleanup framing, and S36 still owes the
   interim-pointer retirement.

The FEEDBACK.md entry for this drain is deleted with this record as
its durable replacement, per the inbox contract. Close evidence: the
orientation canary ran post-mint and graded 4/4 against the computed
key
([2026-08-23-drain8-canary.md](../board/evidence/2026-08-23-drain8-canary.md)).
