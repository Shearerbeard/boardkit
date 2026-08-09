# Rubric: issue ticket body

Grades a candidate-written issue or ticket body. The house standard
for tickets is a short problem statement plus the data that makes the
problem diagnosable. The reader is a maintainer deciding what to do
next. Apply this rubric with no context beyond this file and the
grader packet.

## Inputs

The packet holds the evidence behind the ticket (bug notes, logs, a
request thread), the candidate body, and its Vale report. If the
packet marks protected terms, that list binds dimension 2 and hard
fail 2.

## How to score

Score the five dimensions 0-4 using the anchors below; odd scores sit
between their neighbors. Then check the hard-fail list. PASS requires
a total of 14 or more, no dimension under 2, and no hard fail.

## Dimensions

### 1. Problem statement

The body opens with the observation. It states what happens, against
what expectation, and who or what is blocked. Factual lead; context
follows the observation instead of preceding it.

Anchors:

- 4: observed versus expected within the first two sentences; a
  stranger could triage it.
- 2: the problem is findable but arrives after background.
- 0: no statement of what breaks; or symptom and cause conflated.

### 2. Data (claim fidelity)

The body carries the evidence a fixer needs, taken from the packet
without invention:

- the failing behavior verbatim (error text, a log line)
- the environment fact that triggers it, when the failure is version-
  or platform-bound
- links to the artifacts that hold the rest
- numbers and quotes that match the packet; reporter coinages kept

Anchors:

- 4: enough to reproduce or scope without asking; all of it
  traceable.
- 2: evidence summarized where verbatim was available; still
  accurate.
- 0: repro data missing; or data that contradicts the packet.

### 3. Scope discipline

One problem per ticket. Acceptance criteria describe the observable
end state, and the body leaves the implementation open: no file paths
to edit; no step-numbered plan; no chosen dependency. Those choices
belong to whoever picks the ticket up.

Anchors:

- 4: one ask and an observable end state, with the route left open.
- 2: mild prescription (an approach suggested and labeled as a
  suggestion).
- 0: an implementation plan wearing a ticket's clothes.

### 4. Concision (stale-proofing)

A ticket drops dependency version pins and calendar dates used as
prescription; source control owns history and lockfiles own versions.
It also drops restated code the linked commit shows, plus narration
of the reporter's debugging session. It keeps exact error text and
links. Separate the two version uses: "reproduces on 3.12 but not on
3.11" is evidence and stays; "bump to 3.12.4 by March" is
prescription and goes.

Anchors:

- 4: nothing in the body will rot if the fix takes a quarter.
- 2: one stale-prone specific that another system owns.
- 0: pinned plans and dates through the body.

### 5. Register

Plain, factual, neutral. A ticket is reference prose for a future
reader; personality belongs elsewhere. Urgency inflation and tell
clusters score against this dimension.

Anchors:

- 4: dry, direct, skimmable.
- 2: mild register drift (tutorial or chat tone).
- 0: marketing register; or a body that reads generated.

## Hard fails

Any of these forces FAIL regardless of scores:

1. No observed-versus-expected problem statement anywhere.
2. Fabricated evidence: an error, number, or behavior the packet does
   not contain, or a renamed protected term.
3. The body mandates implementation with stale-prone pins (calendar
   dates or dependency versions as plan).
4. Three or more distinct AI-tell families outside quoted material.

## False-positive guards

Do not penalize:

- dry, neutral prose; that is the target register, and added
  personality earns nothing
- version facts used as evidence; only prescriptive pins score
  against
- reporter coinages and project terms; unfamiliar is not wrong
- a single isolated tell; note it without cutting a score

## Division of labor

This grader runs after Vale. Stock hedges, urgency phrases, and
exactly-three enumerations are the linter's territory; Vale covers
this. Cite report findings instead of re-arguing them. Spend judgment
on scope, evidence fidelity, and stale-proofing.

## Grader output format

Return, in this order:

1. Numbered findings, one per line, each tagged with its dimension
   and quoting a short span or naming the section.
2. Scores, one line per dimension from "D1 problem statement: n/4"
   through "D5 register: n/4", then "Total: n/20".
3. Hard-fail check: list any triggered conditions, or "none".
4. One verdict line with nothing after it: "Verdict: PASS" or
   "Verdict: FAIL".
