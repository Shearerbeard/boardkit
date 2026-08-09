# Prose defect taxonomy

Shared vocabulary for the prose lane. Defect briefs, specimen intake
notes, and the rubrics in this directory cite these names. A specimen
usually carries more than one defect; label the dominant ones rather
than every trace. Twelve defects in four families. The ai-tells Vale
styles detect the token-level subset deterministically; the rest need
a reader.

## Economy defects

**Verbosity.** More words than the content supports: restated points,
padded transitions, explanation of the obvious. Cue: an editor can cut
a third of the words without losing a fact.

**Over-prescription.** The text pins details its artifact type should
leave to another system: dependency versions and calendar dates in a
ticket body; file-by-file narration in a commit message; step-numbered
implementation plans in an issue. These specifics rot without the text
changing. Cue: a fact owned elsewhere (source control, a lockfile,
CI) rather than by the text. Scope note: this defect is
artifact-relative. An ADR must carry
its date and the versions its premises rest on; the same specifics
that are defects in a ticket are required content there.

**Em-dash pileup.** Em dashes as the default connective, several per
paragraph, standing in for commas and colons and parentheses. Cue: two
or more in one paragraph outside quoted text. Vale covers detection
where the EmDashUsage rule is on; repos that write asides with a
spaced hyphen suppress it by convention.

## Register defects

**AI tells.** Stock phrases, inflated vocabulary, and manufactured
rhythm overrepresented in model prose: contrastive formulas;
mic-drop fragments; exactly-three enumerations; puffed importance.
Cue: clusters. One tell in otherwise plain prose is weak evidence;
several families in one passage read as generated. Vale covers the
enumerated token set; this entry exists for the judged residue,
density and the shapes a regex cannot reach.

## Fidelity and logic defects

**Count contradiction.** An announced count disagrees with the list it
introduces: "three changes" followed by four bullets. Cue: count the
items behind every enumerated claim.

**Broken causality.** A causal connective joins claims where the
stated cause does not produce the effect. Cue: swap the connective for
"and"; if nothing is lost, the causality was decorative.

**Non-sequitur.** A sentence or section with no relation to its
neighbors, usually an artifact of patch-mode editing. Cue: the reader
cannot say what question the sentence answers in its position.

**Fact duplication.** The same fact stated in two places, in one file
or across files, so an edit reaches one copy and the copies drift.
Cue: grep the claim; two hits with different values is the proven
form. The fact lives in one place; every other location references
it.

## Structure defects

**Ledger accretion.** Status tables, review verdicts, or dated addenda
appended per session and never merged, until the document is a log of
its own edits. Cue: multiple tables or dated blocks answering the same
question; the reader must merge them mentally to learn the current
state.

**Template residue.** Scaffold left over from the template the
document was stamped from: unfilled placeholders; boilerplate sections
with no instance content; a heading restated as its own first
sentence. Cue: "TBD", angle-bracket slots, or a section that could
appear unchanged in any other repo.

**Diff-anchored writing.** Prose that narrates a change instead of
describing the thing as it now works, so it only parses against
knowledge of the previous version. Cue: "now", "no longer", or "was
added to replace" in a document that is not a changelog, release note,
or migration guide.

**Buried lede.** The claim the reader came for sits under wind-up,
history, or context. Cue: the sentence that answers the reader's
question is missing from the opening paragraph; a problem statement
opens with drama or background instead of the observation.
