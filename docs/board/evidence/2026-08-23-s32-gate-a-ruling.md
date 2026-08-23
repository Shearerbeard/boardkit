# S32 Gate A ruling at the convergence bound (2026-08-23)

Written board-owner ruling required by the S14 convergence rule: two
fix rounds are spent on the S32 cycle and round 3 was not a clean
pass. Template: the 2026-08-16 ruling. Options weighed: continue,
card, or escalate.

## Cycle state

The object is the ADR `docs/adr/0001-artifact-store.md`, 985 lines at
650b844. Round 1 raised ten BLOCKING findings and every one was
accepted. Round 2 verified seven of the fixes and re-raised three
residuals. Round 3 found none of the three residual fixes complete,
and named a narrower contradiction in each area:

1. §4's receipt lifecycle mandates per-round packet hashing and a
   `published` flip, while the ruling receipt is cycle-spanning with
   no packets and no `published` key; no kind-specific scoping
   reconciles them.
2. §2 calls the 12-hex locator prefix the `dir:` anchor that detects
   change, §5 reduces the prefix to an identifier and assigns
   verification to the full 64-character root, and the collision rule
   treats a matching prefix as a harmless republish though distinct
   roots can share a prefix.
3. The priced `check` kind omits `round` (required by the filename
   grammar) and `author_models` (required by driver 9), so the OQ4
   literal branch is still not encodable as written.

Reviewer all rounds: GPT 5.6-sol via the codex CLI, read-only
sandbox. Round spends: 132,320 + 132,178 + 127,759 = 392,257 tokens.

## Diagnosis

Every round's findings, including these, are internal-consistency
defects between sections, never fidelity failures against the ruled
inputs. The fix rounds grew the document from 620 to 985 lines, and
each addition created new surface that contradicted existing surface.
The remedy is a constrained shrink, not another expansion.

## Ruling: continue, once, under constraint

One further fix round runs, restricted to the three findings, with
the fix shape fixed by this ruling rather than left to the author:

1. **Scope the lifecycle by kind.** §4 opens by stating it governs
   `kind: review` receipts. One added paragraph covers the other two
   kinds: a ruling or decision receipt is written once, at the event
   it records, in the same commit as the card-log line; it has no
   publish phase and no `published` flip, and its digest rows attest
   tracked documents. No other lifecycle machinery is added.
2. **One meaning for the prefix.** The prefix identifies; the full
   manifest root verifies, everywhere. §2's note drops the
   change-detection claim. §5's collision rule compares the full root
   read from the existing target's own manifest file: equal roots
   are an idempotent republish, different roots are a refusal. The
   prefix is never an equality operand.
3. **Complete the priced schema.** The `check` kind gains `round` and
   `author_models`, keeping `ran_by` as the runner. Nothing else in
   the OQ4 branch changes.

The round's constraints. Edits land only at the three sites, plus any
cross-reference a site edit forces. Where a contradiction can close
by qualifying or deleting an overclaiming sentence, that beats adding
new text. The round adds no new sections, no schema fields beyond the
two named, and no new claims about existing code.

## Exit condition

A clean round 4 PASS closes Gate A. Anything short of clean ends the
cycle here: the surviving findings present at Gate U as flagged
amendments under the ADR's own `proposed` status, for Mike to settle
where the open questions already sit. No further fix rounds either
way.

## Grounds

Against carding: shipping reviewer-verified contradictions to the
user gate would hand the board owner's consistency work to Mike.
Against escalating: the defects are mechanical, their fixes can be
written down, and this ruling writes them down; escalation is for a
disagreement of substance. And the round runs once because three
rounds of adjacent contradictions is the treadmill signature S29
documented - the S14 rule exists to stop it, and a constrained shape
with a hard exit is the stop.
