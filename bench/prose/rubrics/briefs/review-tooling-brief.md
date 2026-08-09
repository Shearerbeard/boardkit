# Defect brief: review-tooling (cleanup fixture)

Fixture: `bench/prose/fixtures/chore-lottery/2026-08-09-review-tooling.md`
Source: `chore-lottery@0b0330e:docs/board/REVIEW-TOOLING.md` (2,131 words).
Line numbers below refer to the source doc; the frozen fixture body
starts 7 lines later.

## Confirmed defects

1. Template residue shipped in a live doc. CONFIRMED. Lines 129-132
   carry a fill-time instruction addressed to whoever fills the
   template: "If this repo has no such transport installed, delete the
   preceding sentence when filling this file in, so a filled-in copy
   never advertises a path nothing here can take." Line 173 orders
   "Record the deadline this repo uses per tool alongside the
   invocations above," and the recording never happened: only the codex
   route names a deadline (`timeout 900`, line 92); tools 1 and 3 have
   none. Lines 199-214 keep the template's own imperative ("Fill this
   in when this repo has runs...") plus two commented-out placeholder
   table rows still carrying `<command>` markers. The canary section at
   least resolves its state explicitly (line 209: "This repo has no
   such runs today"), so grade the placeholder rows as residue and the
   deferral itself as defensible.

2. Internal fact duplication. CONFIRMED (found while checking the
   cross-file claim; machine-counted after unwrapping line breaks).
   "Agent names do not imply model families" appears twice (lines 58-59
   and 144-145). "Never a deterministic shell proxy" appears twice
   (109 and 148-149). The agy budget gate is stated twice (98-99 and
   218-219). The stage-into-`.review/` recipe appears three times
   (81-85, 89-90, 140-142).

3. Cross-file duplication of the reviewer-differs-from-author rule.
   CONFIRMED, with drift. Full statements: REVIEW-TOOLING.md lines
   14-26 ("The standing rule"), MODEL-CLASSES.md lines 83-88 (the
   named invariant), PROCESS.md lines 149-153 (the Reviewer role
   bullet) and again lines 202-211 (the Gate A bullet), so PROCESS.md
   alone states it in full twice, with name-only echoes at lines 166,
   181, 280, and 469. The copies disagree on strength:
   REVIEW-TOOLING demands a reviewer from a different model FAMILY,
   while MODEL-CLASSES and PROCESS demand only a different MODEL, and
   no doc reconciles the two. MODEL-CLASSES lines 89-96 even states
   the repo's own single-statement principle for the adversarial
   procedure ("stated once, in REVIEW-TOOLING.md... this file does not
   restate it"), which the invariant's four full copies violate.

4. Aphorism density. CONFIRMED. Sample closers: "the invariant
   decides, convenience does not" (22-23); "An empty or verdict-less
   return is a failed review, never a clean pass" (33-35); "A
   transport that completes the work inside the tool call leaves the
   caller nothing to hold" (123-124); "Falling back to a CLI
   self-invocation is not the remedy" (143); "Past three, the approach
   changes rather than the attempt count" (155-156); "Endpoint
   reachability is not receipt" (204); "Escalate reviewer class on
   failure, not by default" (221-222). Nine or more maxim-shaped
   sentences in 2,131 words; most paragraphs end on one.

5. Zero unordered bullets. CONFIRMED: `grep -cE '^\s*[-*] '` returns
   0. List-shaped rule content runs as comma-spliced paragraph prose:
   the hard routing exclusions (109-112), the three exits from the
   dispatch cap (156-157), and the stall signatures (170-173).

## Rejected or unconfirmed hypotheses

None. All three assigned hypotheses held under a full read; the only
softening is the canary section's explicit deferral noted in defect 1.

## What a good cleanup does

1. No fill-time instruction survives: the "delete the preceding
   sentence when filling this file in" sentence is gone, and every
   record-this-here imperative is either satisfied with the actual
   value (a deadline per tool) or removed. Check by grepping for
   "filling this file in" and by reading each tool's entry.
2. Each fact is stated once. The agy budget gate, the shell-proxy
   exclusion, the pins-at-dispatch warning, and the `.review/` staging
   recipe each appear in one place, with later mentions pointing back.
   Check by phrase search.
3. The standing rule names its canonical home. The cleanup either
   defers to MODEL-CLASSES.md for the invariant or declares this doc
   the owner, and it reconciles the family-versus-model discrepancy
   explicitly instead of keeping both strengths.
4. List-shaped content renders as lists. Routing exclusions, stall
   signatures, and the dispatch-cap exits become bullets or table rows
   a reader can scan.
5. Aphorisms are cut or demoted to at most one closing line per
   section; the rule content they carried survives as plain statements.
6. No operational content is lost: the harness-bindings table, tool
   order, transport rule, stall protocol, pre-vet probe, budget
   etiquette, and the cost-record recipe keep their commands, paths,
   and numbers.
