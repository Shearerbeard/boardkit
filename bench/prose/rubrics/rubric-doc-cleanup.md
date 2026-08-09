# Rubric: doc cleanup rewrite

Grades a candidate model's rewrite of a defective document. Apply this
rubric with no context beyond this file and the grader packet.

## Inputs

The packet holds the original document, the candidate rewrite, and the
Vale report for the rewrite. If the packet marks protected terms,
treat that list as binding for dimension 1 and hard fail 3.

## How to score

Score the five dimensions 0-4 using the anchors below; odd scores sit
between their neighbors. Then check the hard-fail list. PASS requires
a total of 14 or more, no dimension under 2, and no hard fail.

## Dimensions

### 1. Claim fidelity

Cutting noise is the assignment; cutting content is failure. These
must survive the rewrite:

- commands with their exact flags, paths, and names
- numbers, units, and counts
- constraints and version pins the document itself imposes
- caveats, warnings, and limitations
- cross-references and links
- the author's own coinages and term choices

Anchors:

- 4: every item above survives intact; cuts touch only redundancy and
  register.
- 2: a secondary detail thinned; none that changes what a reader does.
- 0: facts a reader depends on are gone or altered.

### 2. Defect removal

Identify the original's dominant defects and confirm the rewrite
removed them:

- verbosity: padding is cut, not reshuffled
- duplication: each fact lands in one place; other mentions reference it
- ledger accretion: stacked status tables merge into one current view
- template residue: unfilled scaffold is deleted
- contradictions: announced counts match their lists; causal links hold

Anchors:

- 4: dominant defects gone and no new ones introduced.
- 2: main defects addressed with residue in secondary sections.
- 0: defects survive; or the rewrite trades them for new ones.

### 3. Structure and lede

The rewrite reads as one document written once. The claim the reader
came for opens the piece, sections follow a single order, and nothing
narrates the editing session. Prose describes the current state of
the thing rather than the change that produced it; "now", "no
longer", and "was added to replace" belong in changelogs.

Anchors:

- 4: lede first; the end-to-end read is coherent; no diff-anchored
  phrasing.
- 2: order improved but the opening still buries the main claim; or
  one section reads patched-in.
- 0: patchwork that requires knowing the old version to follow.

### 4. Register

Neutral, plain register is the target for technical reference prose.
Reward direct copulas and concrete specifics. Injected opinion, first
person, or humor in a reference doc scores lower here, never higher.

Anchors:

- 4: plain and direct; dry is fine.
- 2: register drift (tutorial tone, light marketing) without changed
  meaning.
- 0: promotional or chatty register; or dense tell clusters.

### 5. Concision for this artifact

A cleaned doc drops edit-history narration, duplicate statements,
restated headings, and review ledgers. It keeps exact commands,
configuration values, and every caveat. Dates and versions stay only
where the document is inherently versioned (changelog, migration
guide) or pins a premise.

Anchors:

- 4: shorter than the original with the keep list intact.
- 2: real fat cut but some remains; or a keep-list item lost its
  context.
- 0: length preserved by rewording; or concision achieved by deleting
  content (also a dimension 1 hit).

## Hard fails

Any of these forces FAIL regardless of scores:

1. The rewrite asserts a fact the original does not support.
2. A caveat, warning, or constraint a reader acts on is dropped.
3. An author coinage or packet-marked protected term is renamed or
   flattened.
4. Text inside code blocks, quoted output, or error messages is
   altered.
5. A count, value, or name silently changes between original and
   rewrite.

## False-positive guards

Do not penalize:

- neutral, dry register; that is correct for reference prose
- formal or precise vocabulary free of stock AI phrasing
- a single isolated tell in otherwise plain prose; penalize clusters
- unfamiliar coinages the original uses consistently
- short sentences used singly for emphasis

## Division of labor

This grader runs after Vale. Token-level tells, em-dash use, and
exactly-three enumerations are the linter's territory; Vale covers
this. Where the report flags a span, cite the finding instead of
re-arguing it. Spend judgment on what a regex cannot see (cluster
density, structure, fidelity).

## Grader output format

Return, in this order:

1. Numbered findings, one per line, each tagged with its dimension
   and quoting a short span or naming the section.
2. Scores, one line per dimension from "D1 claim fidelity: n/4"
   through "D5 concision: n/4", then "Total: n/20".
3. Hard-fail check: list any triggered conditions, or "none".
4. One verdict line with nothing after it: "Verdict: PASS" or
   "Verdict: FAIL".
