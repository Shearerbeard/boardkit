# Spread-readiness canary evidence (2026-08-22)

Evidence record for the canary and sweep runs behind
`docs/plans/2026-08-22-spread-readiness-hypothesis.md`, filed per the
PROCESS.md rule that a canary without a recorded key, answers, and
grade has not run for audit purposes. Coordinator: a Claude-family
board session; every probe below ran with fresh context on a
different model, graded by the coordinator against the key.

## Computed key

`boardkit canary-key` output at run time (board state: 29 cards,
views current, check OK):

```text
In Review: S13, S16, S18, S19, S20, S21, S22, S23, S24, S25 (all at
Gate A).
In Progress: none.
Next pull: S1 (top of the ready queue). Ready queue: S1, S2, S3, S4,
S8, S9, S10, S12, S14, S15, S17, S26.
Open deferred gates: Gate A on each of the ten in-review cards -
review cycle closed by ruling after five rounds with every card-diff
finding resolved and no explicit reviewer sign-off; the pass decision
is the user's at U(code-review), on the ledger in
docs/board/evidence/2026-08-16-gate-a-review-cycle.md.
Question 4 key (static): PROCESS.md Roles and Gates sections.
```

## Probe 1: orientation-plus-setup canary, opencode flash lane

Model: the opencode explore lane's flash-class pin (DeepSeek flash
over baseten), fresh session via `opencode run`, repo files only,
600s deadline, exit 0. Verbatim final answers:

```text
1. In-review and in-progress
- In-progress: none (the In Progress column is empty).
- In-review (10): S13, S16, S18, S19, S20, S21, S22, S23, S24, S25 -
  all executor: smart (S25 any), all at S -> A -> U(code-review) @ A.

2. Next pull
S1 (Wave-close retro with snapshots and driver input) - the top
ready card. Ready column (12): S1, S2, S3, S4, S8, S9, S10, S12,
S14, S15, S17, S26. No promotion gap: every backlog card with all
deps done is already ready (S6 and S27 have no deps but sit in
backlog; S7 depends on S2 which is not done). The 2026-08-16
evidence record confirms S1 as the next pull.

3. Open and deferred gates
Ten open-deferred Gate A entries, all on the in-review cards (S13,
S16, S18, S19, S20, S21, S22, S23, S24, S25). Each waits on the same
thing: the adversarial review cycle was closed by board-owner ruling
after five rounds with every card-diff finding resolved but no
explicit reviewer sign-off; the pass decision is the user's at each
card's U(code-review) gate, per the ledger in
docs/board/evidence/2026-08-16-gate-a-review-cycle.md. The user may
tick Gate A on that record, ask for a sixth round, or send S29 back
into the wave. (The 2026-08-19 addendum notes the earlier deferred
canary was resolved.)

4. Board owner
None active right now - this is a cold start. Per PROCESS.md Roles,
the session the user tells to run the board is the board owner from
that moment. It must stop for the user at: every Gate U (user gate),
every U(code-review) gate (all ten in-review cards owe one),
standing user gates (architecture/type-design decisions, acceptance
decisions, baseline, launch, milestone), any Gate F frontier review
(user pre-approves or skips), and any budget-gated spend
(agy/Antigravity language review). Recovery rule: never cross a user
gate the card log does not show as approved.

5. SETUP
Validate command (from AGENTS.md / README, BOARDKIT_HOME on its own
line before uv run):
export BOARDKIT_HOME=/Users/mshearer/dev/boardkit
uv run --project "${BOARDKIT_HOME:-../boardkit}" boardkit check
External dependencies the docs name: uv (installed:
/opt/homebrew/bin/uv); boardkit local checkout - this repo is the
kit checkout (it holds bench/, PLAN.md, FEEDBACK.md), so
BOARDKIT_HOME points at itself; the ../boardkit default resolves
here; claude-skills repo (/Users/mshearer/dev/claude-skills) for the
rust-*/python-*/docs-* language skills; config outside the repo
(REVIEW-TOOLING pin sources): ~/.config/opencode/opencode.json and
~/.config/opencode/agent/*.md (opencode lane), ~/.codex/config.toml
(codex lane), ~/.config/agy-mcp/config.toml (agy lane); CLI tools on
PATH: opencode, codex, agy; boardkit doctor diagnoses the whole
install; board resolution: .boardkit/manifest.toml (present).

6. GAPS
- docs/board/REVIEW-TOOLING.md references a graph.md view and the
  AGENTS.md read order names it - it exists in the cards dir (I did
  not open it; the canary brief only needs INDEX/board/deferred).
- The canary question 4 (board owner) has no file answer - it's
  static from the Roles section, and on cold start there is no owner
  yet; that's expected, not a gap.
- Minor ambiguity: BOARDKIT_HOME default ../boardkit resolving to
  the repo itself (a self-hosted kit) is not spelled out in the
  docs, but the checkout is present so the command works.
- Otherwise none: every referenced file (evidence ledger,
  deferred.md, all 29 cards) exists.

CANARY COMPLETE
```

Grade: 4/4 against the key. Question 1 exact match. Question 2 exact
match, with a correct no-promotion-gap analysis. Question 3 exact
match including the wait-reason. Question 4 matches the static key.
The setup reconstruction matched the dependency list the coordinator
verified independently; the one ambiguity it raised (the
`BOARDKIT_HOME` self-hosting default) is real and is carried into
the hypothesis document.

## Probe 2: cold onboarding simulation, Claude small class

Model: a Claude small-class model (haiku tier), fresh context, no
memory, repo files plus documented read-only commands. Verdict line
returned: `ONBOARD VERDICT: YES-WITH-FRICTION`. State answers
matched the key (same in-review set, empty in-progress, S1 next
pull, ten deferred Gate A rows with the ruling wait-reason). Setup
commands ran clean from the docs alone: `boardkit check` OK,
`boardkit doctor` 20 passed with the dirty-tree warning,
`uv run pytest -q` 361 passed, `ruff` clean. Ten numbered friction
findings returned verbatim to the coordinator; the ones carried into
the hypothesis document: consumer-vs-developer README split absent;
model pins and reviewer availability undiscoverable from the repo;
the ten identical deferred Gate A rows read as stuck without the
evidence file; the orientation-canary procedure ships no brief
template or worked example; wave plans in `docs/plans/` reachable
only through card logs. Full transcript in the session scratchpad;
findings 1-10 are restated in the hypothesis document's evidence
section and action list.

## Probe 3: machine-local dependency sweep, Claude mid class

Model: a Claude mid-class explore agent (sonnet tier), fresh
context. Not a graded canary - an evidence sweep. Returned 33
numbered findings with file:line references across four categories
(machine-local references, gitignored-but-cited state, off-repo
dependencies, scaffold coverage), each tagged blocking, friction, or
cosmetic. The blocking set is folded into the hypothesis document's
dependency inventory: the pin-source trees with no bootstrap recipe,
the `--config` cwd bug already in FEEDBACK.md, the
`.claude/settings.local.json` and `.boardkit/local.toml` ignore
gaps, the untracked bench run, the missing operational clone URL,
doctor's never-executed preflights, and the two template-identical
REVIEW-TOOLING sections invisible to doctor's fill check.

## Family coverage note

The canaries cover two model families: one non-Claude flash-class
probe (probe 1) and two Claude probes (probes 2 and 3). The
adversarial review panel over the resulting document adds three more
non-Claude families (GPT, Kimi, GLM), whose reviewers read the repo
unaided during their reviews; their ledger lives in the
hypothesis document itself.
