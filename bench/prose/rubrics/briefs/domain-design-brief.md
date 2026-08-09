# Defect brief: domain-design (cleanup fixture)

Fixture: `bench/prose/fixtures/chore-lottery/2026-08-09-domain-design.md`
Source: `chore-lottery@0b0330e:crates/domain/DESIGN.md` (2,796 words).
Line numbers below refer to the source doc; the frozen fixture body
starts 7 lines later.

## Confirmed defects

1. Type table as the front door. CONFIRMED, count corrected: 43 data
   rows, not 46 (lines 12-54, machine-counted twice). After a
   five-line preamble the reader hits the full inventory wall before
   any narrative of what the crate models or how its aggregates
   relate. The table also understates its own bulk: row 54 packs 14
   error types into a single row ("`TextError`/`ChoreError`/
   `KidError`/`PhotoError`/..."), so the 43 rows cover roughly 56
   types.

2. Nested remediation-round sections. CONFIRMED, with a shape nuance:
   the rounds are nested bullets, not headed sections. "Fill-phase
   repairs (S5)" (line 90) holds a "Gate A remediation round" bullet
   (120) whose sub-bullets include "Second remediation round, after
   the re-review returned FAIL" (141-154) and "Third remediation
   round" (155-161). Three rounds of review fallout nest three list
   levels deep, and the second-round bullet is one semicolon-chained
   sentence spanning 14 source lines and eight distinct repairs.

3. Cross-file and row-id accretion (found during the full read).
   Residual risks cite "panel finding 7" (235) and "panel finding 8"
   (239-240) by number. The S7 additions section cites "panel finding
   11" (179) and "repair finding 15" (181) whose ledgers live in a
   different crate's doc, per lines 166-167: "Ruled on by the S7
   design panel (ledger in `crates/lottery/DESIGN.md`)." Decoding this
   file requires the other crate's findings tables.

## Rejected or unconfirmed hypotheses

The 46-row figure is wrong; the table has 43 rows. The substance of
the front-door hypothesis stands. Nothing else was rejected.

## What a good cleanup does

1. The doc opens with a narrative front door: what the crate models,
   the aggregate split (chore FSM, kid mirror, lottery, AI audit,
   Vikunja sync types), and how to read the inventory, before any
   table.
2. The inventory is grouped or split so each cluster scans on its own
   (states, commands and events, constrained scalars, errors), and the
   14-type error row becomes rows or prose a reader can search.
3. Remediation history flattens to provenance: repairs read as current
   facts in the sections they touched, one history note names the
   rounds and where their ledgers live, and no third-level round
   bullets remain.
4. Row-number pointers into another file's ledger are replaced with
   self-contained statements or stable links.
5. Nothing normative is dropped: every business rule and
   forbidden-state pair in the current rows survives, restated or
   regrouped, and the residual-risks section keeps its content.
