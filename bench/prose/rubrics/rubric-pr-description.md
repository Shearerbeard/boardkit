# Rubric: PR description

Grades a candidate-written pull-request description. Two readers: a
reviewer deciding how to read the diff, and a future engineer arriving
from git blame. The diff shows what files changed; the description
exists for what the diff cannot say. Apply this rubric with no context
beyond this file and the grader packet.

## Inputs

The packet holds the diff evidence (the diff itself or a faithful
summary of it), any linked-issue context, the candidate description,
and its Vale report. If the packet marks protected terms, that list
binds dimension 2 and hard fail 1.

## How to score

Score the five dimensions 0-4 using the anchors below; odd scores sit
between their neighbors. Then check the hard-fail list. PASS requires
a total of 14 or more, no dimension under 2, and no hard fail.

## Dimensions

### 1. What and why

The opening lines state the behavior-level change and the reason for
it. The why names the problem or motivation from the packet rather
than restating the title.

Anchors:

- 4: a reviewer knows what changed and why before scrolling.
- 2: the what is clear; the why is thin or implied.
- 0: neither is present; or a restated commit subject padded into a
  paragraph.

### 2. Fidelity to the diff (claim fidelity)

Every described change appears in the diff evidence, and every
behavioral or breaking change in the evidence appears in the
description. Performance and correctness claims match what the packet
supports; an unquantified "faster" with no baseline scores against
this dimension. Project terms and packet coinages survive unchanged.

Anchors:

- 4: description and diff match in both directions.
- 2: a secondary change goes undescribed; nothing user-facing.
- 0: describes work the diff lacks; or omits a breaking change.

### 3. Review guidance

The description points the reviewer at risk: which part is subtle;
what was verified and how; what is intentionally out of scope.
Verification reads as fact ("ran the migration against a staging
snapshot"), never as a test-count tally.

Anchors:

- 4: a reviewer can order their attention from the description alone.
- 2: generic guidance ("please review carefully"); or verification
  implied but unstated.
- 0: no guidance and no verification note.

### 4. Concision for this artifact

A PR description drops file-by-file listing (the diff shows it);
session narration ("first I tried..."); test-count claims; marketing
adjectives. It keeps breaking changes with their migration steps; the
issue link; verification notes; anything else the diff cannot show.

Anchors:

- 4: everything present earns its line; nothing restates the diff.
- 2: some diff restatement or narration around an otherwise sound
  body.
- 0: the body is a file list or a session log.

### 5. Register

Plain and factual. The description is a work record read under time
pressure, and neutral prose is correct for it. Marketing register and
tell clusters score against this dimension.

Anchors:

- 4: dry, direct, skimmable.
- 2: mild drift (enthusiasm, tutorial tone) without changed meaning.
- 0: ad copy; or a body that reads generated.

## Hard fails

Any of these forces FAIL regardless of scores:

1. The description claims a change the diff evidence does not
   contain, or renames a protected term.
2. A breaking change present in the evidence goes unmentioned.
3. An attribution or AI-signature trailer appears in the body.
4. The body's main structure is a file-by-file walkthrough.

## False-positive guards

Do not penalize:

- dry, neutral prose; that is the target register, and injected
  personality earns nothing
- short bodies; a small diff deserves a small description
- project terms and coinages from the packet; unfamiliar is not wrong
- a single isolated tell; note it without cutting a score

## Division of labor

This grader runs after Vale. The ai-tells-commits rules police
commit-message text deterministically (file listing, test counts,
buzzwords); Vale covers this for commits, and this rubric applies the
same standard to the PR body, which Vale does not see in that mode.
Cite report findings instead of re-arguing them. Spend judgment on
diff fidelity and review guidance.

## Grader output format

Return, in this order:

1. Numbered findings, one per line, each tagged with its dimension
   and quoting a short span or naming the section.
2. Scores, one line per dimension from "D1 what and why: n/4" through
   "D5 register: n/4", then "Total: n/20".
3. Hard-fail check: list any triggered conditions, or "none".
4. One verdict line with nothing after it: "Verdict: PASS" or
   "Verdict: FAIL".
