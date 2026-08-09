# Defect brief: epoch-retro (fresh-write source)

Fixture: `bench/prose/fixtures/chore-lottery/2026-08-09-epoch-retro.md`
Source:
`chore-lottery@0b0330e:docs/board/retro/2026-08-04-epoch-friction-retro.md`
(894 words). Line numbers below refer to the source doc; the frozen
fixture body starts 7 lines later. This fixture is a fresh-write
source: the friction evidence is the candidate input and the proposals
are the reference answer. The task: from the evidence alone, write the
upstream ticket to the Epoch maintainer proposing the fixes. Grade it
with `rubric-ticket`; no rubric grades a retro, so a run must not ask
for one.

## Confirmed properties

1. Compact maintainer-facing findings as hypothesized: five friction
   entries E1-E5, each with concrete evidence and cost ("the
   coordinator's generic bounds became the single ugliest surface in
   the crate", 40-41; "two reviewers independently asked what the
   semantics were", 91-92), a kept-patterns section (10-29), a
   wave-cost paragraph (115-122), and a prioritized fix list
   (124-130). The audience is declared in the header: "this retro is
   written for the Epoch maintainer" (6-7).
2. Structural wrinkle that matters for staging: evidence and answer
   interleave. Each friction section ends with its proposal paragraph
   (R2 at 43-49, R1 at 64-69, R3 at 81-84, R4 at 94-97, R5 at
   109-113), and the E1/E2 headings carry "(your fix: ...)" spoilers
   (33, 51).
3. Minor residue: "## Human notes" closes with the unfilled stub
   "Left for the user." (132-134).

## Rejected or unconfirmed hypotheses

No defect hypotheses were assigned beyond the characterization, which
held. The interleaving in point 2 is a staging hazard, not a prose
defect.

## What a good fresh-write does

Given the evidence only, a candidate ticket:

1. Keeps the maintainer framing: proposals addressed to Epoch, each
   one the maintainer can act on alone, each anchored to the consumer
   evidence that motivates it.
2. Reproduces the substance of the five fixes: a documented
   clone-and-sharing contract for the in-memory store, generic stream
   ids, a lifetime-free repository trait, version-semantics doctests,
   and a consumer-shaped postgres smoke test.
3. Orders the fixes with a stated rationale comparable to the doc's
   (doc-first clone semantics first, generic ids as the highest
   consumer payoff, doctests as the cheapest close).
4. Preserves the keep-this list so the maintainer knows the
   Clone-with-shared-stream-state capability stays and only its
   documentation is owed.
5. States the cost at wave scale without spin: about a tenth of the
   coordinator's bulk was boundary machinery, two review rounds
   carried the workarounds, and nothing blocked the card.

## Reference answer and staging excisions

The reference answer is proposals R1-R5 plus the ordered "What to fix
first" list (124-130).

Because evidence and answer interleave, staging must edit inside
sections rather than dropping whole ones. A candidate must not see:

- The proposal paragraphs: R2 at lines 43-49, R1 at 64-69, R3 at
  81-84, R4 at 94-97, and R5 at 109-113.
- The "(your fix: generics)" and "(your fix: clone bounds)" heading
  spoilers (33, 51).
- The header sentence "proposals are marked R1..R5 and referenced from
  the S19 card" (7-8).
- The clause "the semantics need to be *documented* (R4), not
  changed" (29).
- The whole "## What to fix first" section (124-130).

What remains as candidate input: the header minus the R sentence, the
kept-patterns list minus the R4 clause, the evidence and cost prose of
E1-E5, and "Cost to the wave". A grader scoring an unexcised run must
treat points 2 and 3 above as potentially copied.
