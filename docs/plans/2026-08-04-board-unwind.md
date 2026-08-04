# Plan: unwind the competing boards (2026-08-04)

Status: authored 2026-08-04 from the board-inventory audit. The
deterministic pre-delete canary has already run and passed (stage 1
below records it); the satellite-card disposition fan-out ran as an
ultracode workflow the same session. Everything destructive waits at
its gate.

## Scope

- Core problem: seven card registries in the family, four contract
  states, three copies of the same board with thirteen actively
  contradictory card statuses. Any session opening the wrong copy is
  silently misled.
- Audience: the aura board family (terminalbench-aura survivor,
  aura-session-docs satellites), chore-lottery, and boardkit's own
  dogfood board.
- Success: one live board per workstream family, every survivor
  stamped and doctor-clean, every open satellite card absorbed or
  killed with a recorded reason, chore-lottery on contract v2.
- Non-goals: no card-content rewrites during the move; no change to
  the survivor board's own 25 open cards beyond what S77/S80 decide;
  no touching chore-lottery S19 (standing card, user direction).

## Fan-out and burn budget

Orchestration stays in the main session. Mechanical stages run as
workflow agents pinned to Sonnet; adversarial canaries route to
cross-family reviewers (opencode kimi lane, codex lane) through the
boardkit contract, which costs no Claude tokens and keeps
reviewer-differs-from-author. Fable authors nothing per-card.

## Canary battery

1. Pre-delete subset proof (deterministic, no model): the clone
   boards hold zero unique files, and on every differing file the
   survivor's copy has the newer git date. RAN 2026-08-04: both
   clones pass both directions.
2. Disposition adversarial verify (workflow): every satellite card's
   absorb-or-kill call is independently refuted-or-confirmed by a
   second agent with no shared context. Disagreements and "unclear"
   land at the stage 3 user gate, never auto-resolved.
3. Post-absorb readback: after each absorbed card lands on its target
   board, a fresh agent reads only the target board and answers "what
   is this card, what unblocks it" - graded against the source card.
4. Negative control: plant one deliberate status error in a scratch
   copy of the survivor registry and confirm `boardkit check` plus
   the orientation canary catch it. A canary battery that has never
   caught a planted fault is unproven.
5. Cross-family orientation canary (boardkit canary-key mechanism)
   on every surviving board at close, via the contract's canary
   route.

## Implementation Stages

#### Stage 1: freeze and prove (no model work)
- Goal: rollback anchors plus the lossless-deletion proof.
- Steps: `git tag board-unwind-2026-08-04` in terminalbench-aura,
  -s59, -s73; aura-session-docs gets a dated commit. Re-run the
  subset proof and file its output next to this plan.
- Gates: S
- [x] Gate S: subset proof both directions, both clones - PASSED
  2026-08-04 (zero unique files; survivor newer on all 29 differing
  files).
- Done when: tags exist and the proof output is committed.

#### Stage 2: delete the clone boards 🛑 USER GATE
- Goal: `-s59` and `-s73` lose their `docs/redesign/cards/` copies;
  the repos and code branches stay.
- Gates: S -> U
- [x] Gate S: stage 1 tags present; proof re-run green on the day of
  deletion (2026-08-04, both clones zero unique files).
- [x] Gate U: user approved 2026-08-04 ("fix cloned deletion"); deleted
  in commits 56156cc (-s59) and 3dfdd19 (-s73), rollback via the
  board-unwind-2026-08-04 tags.
- Done when: neither clone has a cards directory; a one-line note in
  each repo's README or commit message points at the survivor.

#### Stage 3: satellite dispositions 🛑 USER GATE
- Goal: the 13 open cards on webhook-surface and 271-hitl-park-reify
  each end as absorbed (moved to the board that owns the work) or
  killed (log line with reason), boards then archived.
- Target correction (from the disposition workflow, 2026-08-04): the
  absorb target is NOT terminalbench-aura - every verifier flagged the
  domain mismatch. Both satellites hold aura-orchestration-mode work
  (HITL webhook surface, park-reify), so the absorptions land on one
  consolidated aura-orchestration-mode board at contract v2, replacing
  the two satellites and their dead [review].repo worktree paths. That
  keeps the census at one board per workstream family: terminalbench,
  aura-orchestration-mode, chore-lottery, boardkit.
- Fan-out: the disposition workflow (dossier -> adversarial verify,
  Sonnet) drafts the table; canary 2 is built into it.
- Gates: S -> A -> U
- [x] Gate S: every card has a disposition row; no row unverified
  (26-agent workflow, 13/13 dispositioned, zero empty returns).
- [x] Gate A: satisfied in substance rather than as specified - the
  adversarial-verify lane inside the workflow overturned all three
  proposed kills before the table reached anyone, and the one kill
  that survived (W3) was ruled by the user directly, so the "which
  kill would you reverse" question had no remaining target. Recorded
  as a gate-shape deviation, not a silent skip.
- [x] Gate U: W3 kill ruled by the user 2026-08-04 (Gate T waived);
  transplant of all survivors approved and executed (wiki d3dfee8);
  P10/P13 deferred to the DAG re-cut session by user direction -
  board mechanics hold both unpullable meanwhile.
- Rulings so far (2026-08-04): W3 kill approved - Gate T waived by the
  user (work merged as PRs 489-491; chore-lottery is the better Gate T
  venue, per card S5); close GH issue 399 as part of the kill. P10 and
  P13 still await a ruling. GH check note: open issues 474 and 475 are
  live defects in P7/P11/P12 territory, so those absorptions carry the
  ticket links forward.
- Done when: both satellite boards are archived (directory renamed
  `_archived-<date>` or deleted per user call), absorbed cards live
  on their target boards, canary 3 readback passes per absorbed card.

#### Stage 4: survivor board adopts or declines boardkit (S77 -> S80)
- Goal: the migration the survivor board already carded for itself.
  Pull S77 (parity proof: boardkit engine against the live board,
  ready today), then S80 (adopt CLI + retire cards_index.py, or
  decline with reasons). S80 carries its own USER GATE in its gates
  string; this plan defers to it rather than duplicating it.
- Fan-out: S77's parity checks are mechanical and workflow-friendly
  (Sonnet agents compare generated views per card); S80 is a decision
  card and stays with the user.
- Gates: per the cards' own gate strings.
- [ ] S77 done with parity evidence.
- [ ] S80 decided at its own user gate.
- Done when: the survivor board is either on the boardkit CLI with a
  stamped PROCESS.md, or has a recorded decline and keeps
  cards_index.py deliberately.

#### Stage 5: chore-lottery v1 -> v2 re-sync
- Goal: `staging` on every route, `version = 2`, PROCESS re-synced,
  doctor clean. S19 untouched.
- Gates: S -> A
- [x] Gate S: doctor 17/17 clean at v2, check green over 21 cards,
  S19 untouched (2026-08-04, migration run by the user as a live
  smoke test; traceback presentation defect found and fixed in the
  kit, aae4de7).
- [x] Gate A: codex lane (opencode's k3 shares no family with the
  diff's author). Round 1 FAIL, 2 blocking + 2 minor - exactly the
  clobber question: three locally-authored sections lost, echo
  pre-vet retained. Fixed in e7f3219; round 2 PASS with all four
  findings verified resolved.
- Done when: doctor reports v2 with no findings.

#### Stage 6: close 🛑 USER GATE
- Goal: the family is one-board-per-workstream and provably oriented.
- Steps: canary 4 (negative control) then canary 5 (orientation
  canary per surviving board); wiki workstream question ("boardkit
  workstream merges into terminalbench or stays") answered by the
  user; wave-close record with per-stage costs.
- Gates: S -> U
- [ ] Gate S: canaries 4 and 5 green; negative control caught the
  planted fault.
- [ ] Gate U: present the end state - board census before/after, every
  kill with its reason, canary record - and the workstream-merge
  question.
- Done when: the user has the census and the canary record.

## Rollback

- Stage 2: `git checkout board-unwind-2026-08-04 -- docs/redesign/cards`
  in the affected clone.
- Stage 3: satellite boards are archived, not destroyed, until the
  close gate passes; absorbed cards carry a source line naming the
  original board.
- Stage 4: S80 declining is itself a valid outcome; nothing forces
  adoption.
- Stage 5: chore-lottery re-sync is one commit; revert restores v1.
