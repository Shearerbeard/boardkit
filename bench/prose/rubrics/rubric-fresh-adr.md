# Rubric: fresh decision record

Grades a candidate model's decision record (ADR) written from an
evidence packet. Apply this rubric with no context beyond this file
and the packet.

## Inputs

The packet holds the evidence the record was written from (notes,
issue links, spike results, constraints) plus the candidate ADR and
its Vale report. If the packet marks protected terms, that list binds
dimension 1 and hard fail 1.

## How to score

Score the five dimensions 0-4 using the anchors below; odd scores sit
between their neighbors. Then check the hard-fail list. PASS requires
a total of 14 or more, no dimension under 2, and no hard fail.

## Dimensions

### 1. Evidence fidelity (claim fidelity)

The record may compress the packet; it may not extend it. Check:

- every quantitative claim carries its source from the packet
- every pinned reference (branch, commit, PR, version) appears in the
  packet
- quotes are verbatim; packet coinages and project terms survive
  unchanged

Anchors:

- 4: all claims trace; references resolve within the packet.
- 2: one untraceable secondary claim, labeled as an assumption.
- 0: invented evidence; or numbers that contradict the packet.

### 2. Structure (MADR)

The record carries, in recognizable form:

1. a title stating the decision in plain language
2. status, date, and deciders
3. context naming the forces and who is blocked
4. decision drivers as testable criteria
5. two or more considered options that were live candidates
6. a decision outcome tied back to the drivers
7. consequences, positive and negative
8. links back to its sources (issue, spike, related records)

Scale: 4 = all eight present; 3 = one weak; 2 = one missing or two
weak; 1 = two missing; 0 = three or more missing.

### 3. Driver quality (RFC-2119)

Hard constraints use MUST or MUST NOT. Preferences use SHOULD, with
the condition that would flip them. A driver the reader cannot test
or disagree with is too vague and scores against this dimension. The
capitalized keywords are required vocabulary here, never a style
violation.

Anchors:

- 4: every driver testable; the MUST versus SHOULD split matches the
  packet's constraints.
- 2: drivers present but mixed with untestable wishes.
- 0: no drivers; or drivers that would fit any decision equally well.

### 4. Honest consequences

Negative consequences get the same care as benefits. Known gaps are
named with an owner (a follow-up record, an issue, a roadmap line).
Failure modes appear where the decision has them; think timeout,
denial, disconnect, the unhappy path.

Anchors:

- 4: downsides and failure modes concrete enough to disagree with.
- 2: downsides gestured at ("more complexity") without specifics.
- 0: only upside. A record with no downsides is under-reviewed.

### 5. Concision for this artifact

An ADR keeps what tickets drop: its date; the versions and pins its
premises rest on; quantitative limits. It drops implementation detail
that belongs in a design note or the code; context restated between
sections; sales language for the chosen option. Each rejected
option records the real reason it lost, in its own terms.

Anchors:

- 4: complete record that reads as one argument end to end.
- 2: sections repeat context; or the outcome restates a driver
  verbatim.
- 0: boilerplate register; or concision achieved by dropping required
  fields.

## Hard fails

Any of these forces FAIL regardless of scores:

1. Evidence the grader cannot find in the packet (a benchmark, quote,
   or reference), or a renamed protected term.
2. One live option padded with strawmen, or a single option total.
3. No negative consequences anywhere in the record.
4. No decision outcome, or no status and date. An ADR without its
   date fails here; the date requirement inverts the ticket rule on
   purpose.
5. A conflicting or superseded prior decision in the packet goes
   unmentioned.

## False-positive guards

Do not penalize:

- MUST, SHOULD, and MUST NOT in capitals; required RFC-2119
  vocabulary, never shouting
- neutral register; do not reward injected personality
- dates, versions, and commit pins; required here, never stale-prone
  clutter
- packet coinages and project terms; unfamiliar is not wrong
- a single isolated tell; penalize clusters

## Division of labor

This grader runs after Vale. Stock phrases, em-dash use, and
exactly-three enumerations are the linter's territory; Vale covers
this. Cite report findings instead of re-arguing them. Spend judgment
on evidence tracing and on the argument's coherence.

## Grader output format

Return, in this order:

1. Numbered findings, one per line, each tagged with its dimension
   and quoting a short span or naming the section.
2. Scores, one line per dimension from "D1 evidence fidelity: n/4"
   through "D5 concision: n/4", then "Total: n/20".
3. Hard-fail check: list any triggered conditions, or "none".
4. One verdict line with nothing after it: "Verdict: PASS" or
   "Verdict: FAIL".
