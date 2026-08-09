# Defect brief: lottery-design (cleanup fixture)

Fixture: `bench/prose/fixtures/chore-lottery/2026-08-09-lottery-design.md`
Source: `chore-lottery@0b0330e:crates/lottery/DESIGN.md` (2,908 words).
Line numbers below refer to the source doc; the frozen fixture body
starts 7 lines later.

## Confirmed defects

1. Ledger accretion. CONFIRMED. Four review ledgers stack in sequence:
   design-panel findings 1-14 (lines 117-132), the repair re-review
   rows 15-17 (139-143), the adversarial pass F1-F5 (150-156), and
   Gate A rows A1-A2 (187-190). Current design facts live inside
   dispositions: the chore-first ordering, the orphan-recovery shape,
   and the service split are each stated most fully as the resolution
   column of a finding row. The same facts then repeat in prose:
   chore-first appears in the ordering section (40-42), in decision 1
   (89-93), and in finding 5's disposition (123); the
   no-second-service-object argument appears at 22-23, at 70-74, and
   in F1's disposition (152).

2. Cross-referencing by row number. CONFIRMED. Line 135-136: "rows
   1-9, 11, 13, 14 verified IMPLEMENTED; rows 10 and 12 NOT
   IMPLEMENTED." Finding 16 (142) reads "Row 12's race coverage
   existed as a ledger sentence." Line 92-93: "the repair also retired
   seat 2's finding 4." Prose sections lean on row ids: "repair-review
   finding 17" (62), "panel finding 7" (94-95), "panel finding 8"
   (102), "Gate A finding 1" (54). The type inventory embeds ledger
   ids inside its rule columns ("(F1)" at 22, "(F2)" at 24), and the
   test contract keys tests to rows ("Finding 5 repair", "F2", "F3",
   164-179). A reader must replay four review rounds to decode the
   present-tense design.

3. SUPERSEDED rows. CONFIRMED in substance, count corrected to one.
   Row 14 (132) is the only literal SUPERSEDED disposition:
   "SUPERSEDED: chore-first ordering removed every freeing path that
   needed a re-derived actor (finding 5's repair)." Two more
   overturned-claim notes sit in prose: "the skeleton's single-writer
   envelope claim was overturned" (46-47) and "The skeleton's
   kid-first ordering and its parent-re-deriving reconcile were
   overturned" (90-91).

## Rejected or unconfirmed hypotheses

None rejected. The SUPERSEDED hypothesis implied several rows; the doc
holds one labeled row plus two overturned claims in prose.

## What a good cleanup does

1. The current design reads without the review history: ordering,
   recovery shapes, service structure, and seam decisions appear once
   as present-tense fact, and no row id is needed to parse any of them.
2. Review history compresses to provenance: one section records that
   four rounds ran, their verdicts, and where the full ledgers live
   (git history or a reviews file); superseded and overturned rows
   drop out of the main body.
3. The test contract survives keyed to behaviors: each test names the
   invariant it pins (same-kid concurrent draws yield one `Drawn`;
   returning an InReview card is `NotInProgress`) instead of a finding
   number.
4. Type-inventory rules stand alone, with no "(F1)"-style pointers in
   the business-rule or forbidden-state columns.
5. No invariant is lost: chore-first draw and kid-first return, orphan
   recovery through a repeated parent return, the `DrawSelection`
   digest binding, the typed `LostRace` on both appends, and every
   residual-risk entry all remain stated.
