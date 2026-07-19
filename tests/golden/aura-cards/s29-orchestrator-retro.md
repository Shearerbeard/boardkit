---
id: S29
title: Grade the next orchestrator wave against a sealed rubric
status: done
depends: []
serialize-with: []
lineage: none
executor: smart
gates: "S -> A"
user-gates: []
---

# S29: Grade the next orchestrator wave against a sealed rubric

Mechanics: [PROCESS.md](../PROCESS.md). Required reading:
[REVIEW-TOOLING.md](../REVIEW-TOOLING.md). Filed 2026-07-12, before
the first wave run by a non-Fable orchestrator (GLM 5.2 or GPT-5.x
class), so the rubric below is sealed ahead of the run it grades.
The goal is to decide, from artifacts, whether the cheaper
orchestrator can keep owning waves and what to fix before the one
after.

## Scope

Runs in a strong-class session after the next orchestration wave
session ends, regardless of how many cards it completed (partial
completion is itself a datum). Evidence only; no code. Inputs are
the durable artifacts the wave leaves behind: card frontmatter and
logs, the git history with `Card:` trailers in both repos, review
packets regenerated from `commit-range`, gate outputs pasted on
cards, the wiki handoff events, and the orchestrator's own session
transcripts (opencode sessions are retrievable by id or title;
codex keeps local session logs).

## Deliverable

A dated evidence file in `docs/redesign/evidence/` grading the wave
against the sealed rubric, one row per dimension with the artifact
cited, plus a short list of concrete changes for the next wave
(prompt, docs, card shape, or model choice).

Sealed rubric; every row graded from artifacts, not recollection:

1. Board integrity: `cards_index.py --check` clean at every board
   commit; every status change has a same-turn dated log line; no
   unlogged work found in either repo.
2. Gate fidelity: every ticked gate box has verifiable output
   recorded; the board owner re-ran at least one acceptance check
   directly before any Done; no Done rests on a subagent claim
   alone.
3. Scope discipline: each card's packet diff stays inside its Scope
   file list; worktree-serial cards did not interleave commits.
4. Envelope identity: golden tests green under `INSTA_UPDATE=no` at
   every card boundary; every snapshot re-pin is intentional, in the
   same commit as its behavior change, and ledgered on the card.
5. Type discipline: any card introducing types followed
   skeleton -> panel -> repair -> implement with numbered
   dispositions on the design record.
6. Delegation quality: dispatch briefs carried the scope rule,
   evidence paths, and report format; either-or decisions stayed
   with the board owner.
7. Review-packet duty: `commit-range` set and a packet generated for
   every card that reached In Review.
8. Escalation behavior: stopped at every user gate; blocked work
   parked as in-progress with a named blocker rather than pushed
   through. A crossed user gate fails the wave outright.
9. Cost and wall clock: tokens and duration per card from the
   session records, compared against this session and the 2026-07-12
   bolus as baselines.
10. Finding pressure: blocking findings per card from Gate A and the
    codex reviews, and repair rounds needed, compared to the S2
    bolus (one DMMF blocker plus ten codex logic issues).

## Acceptance

- The evidence file grades all ten dimensions with an artifact cite
  each and is vale-clean.
- The comparison baselines (this session, the S1/S2/S8/S16 bolus)
  are cited by commit or card log, not memory.
- The file ends with go/no-go advice for the following wave and
  names the single highest-leverage fix.

## Gate checklist

- [x] Gate S: vale on the evidence file; every rubric row carries an
      artifact cite.
- [x] Gate A: fresh-agent spot-check of three rubric rows against
      the primary artifacts.

## Branch

Adapter repo, direct; commit recorded here at Done.

## Log

- 2026-07-12 Filed as backlog by the board owner, sealed before the
  first non-Fable wave. The wave kickoff prompt should tell the
  orchestrator to record its model string and session ids in its
  wiki handoff so this retro can pull transcripts.
- 2026-07-13 Pulled by the board owner (Fable 5 session) after the
  GLM 5.2 wave ended at 20:55. Six context-isolated verification
  agents re-ran every deterministic wave claim; all reproduced. The
  wave handoffs omitted session ids (the kickoff never carried the
  instruction above), so the cost dimension was recovered by SQL
  from the opencode session store.
- 2026-07-13 In Review, same session. Evidence file
  [2026-07-13-s29-glm-wave-retro.md](../evidence/2026-07-13-s29-glm-wave-retro.md)
  grades all ten dimensions with artifact cites; verdict GO with
  named conditions. Gate S: vale clean (0 errors) after two rewrites.
  Gate A: fresh-agent spot-check of rows 2, 7, and 9 - all three
  verified exactly; one out-of-row defect found (dimension 5 claimed
  18 DEFAULT consts, code has 16), repaired, and the count re-verified
  directly by the board owner (grep count 16). Held at In Review for
  user ratification alongside the next-wave gated plan; the evidence
  commit lands with that ratification.
- 2026-07-13 Done. User ratified the retro and its GO verdict in
  session. Verification record: Gate S run by the board owner (vale,
  0 findings after two rewrites); Gate A by a fresh agent (rows 2, 7,
  9 verified against primary artifacts; its one refutation repaired
  and re-counted directly by the board owner). The evidence file and
  this flip land in one adapter commit carrying a `Card: S29`
  trailer. The next-wave execution plan is parked at
  [2026-07-13-phase-b-bolus-plan.md](../plans/2026-07-13-phase-b-bolus-plan.md)
  pending the user's usage-limit refresh; retro changes 1-6 fold into
  that wave's kickoff rather than landing now.
