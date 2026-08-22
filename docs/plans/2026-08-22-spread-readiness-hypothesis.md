# Spread-readiness hypothesis and action list (2026-08-22)

Assessment answering one question from Mike: how close is boardkit to
spreading to another machine and another consumer repo, and could a
new engineer onboard from the repo alone? The known blocker: board
state has no way to be synced and verified visually.

The evidence is fresh-context canary runs, checked against the
FEEDBACK.md inbox and the wave-2 plan. The three-reviewer panel Mike
named then attacked the draft; the ledger sits at the end. Nothing
here is implemented; actions propose, Mike disposes.

## Method

Three fresh-context probes, none on the coordinator itself (no
Fable canaries, per the session directive): one on a non-Claude
flash-class model, two on smaller Claude tiers. All were graded by
the coordinator against deterministic keys. The non-Claude coverage
widens at review time: the three panel lanes (GPT, Kimi, and GLM
families) each read the repo unaided while verifying this document.

- An orientation-plus-setup canary on the opencode explore lane's
  flash-class pin (the baseten DeepSeek flash model), cold-starting
  from `AGENTS.md` with repo files only, graded against
  `boardkit canary-key`.
- A cold onboarding simulation on a small-class Claude model
  (fresh context, no memory), playing a new engineer working from
  `README.md`/`AGENTS.md` alone, allowed to run the documented
  read-only commands.
- A machine-local dependency sweep on a mid-class Claude explore
  agent, inventorying what breaks on a fresh machine, a fresh clone,
  or a consumer repo.

Claude-memory reliance was audited directly: the session's project
memory directory is empty, so no operational knowledge about this
repo lives in harness memory. Every claim below traces to repo files
or to a canary transcript.

## Evidence

1. `boardkit check`: OK, 29 cards valid, views current.
2. `boardkit doctor`: 20 passed, 0 errors, 1 warning - the host
   repo's dirty tree (the wave-2 plan is untracked and the Gate A
   evidence addendum uncommitted), meaning the board's newest state
   exists on one machine only. Doctor itself names the hazard.
3. Flash-class canary: 4/4 against the computed key (in-review set,
   empty in-progress, S1 next pull, all ten deferred Gate A entries
   with the correct wait-reason, board-owner rules). It also
   reconstructed the full fresh-machine dependency list from the
   docs alone: uv, the kit checkout, claude-skills, the three
   harness config trees under `~/`, and the `opencode`/`codex`/`agy`
   binaries. One real ambiguity found: the docs never state that
   this repo is itself the kit, so `BOARDKIT_HOME`'s `../boardkit`
   default resolving to the repo itself goes unexplained.
4. Small-class onboarding canary: verdict YES-WITH-FRICTION. State
   answers matched the key; the documented setup commands ran clean
   from the docs alone (361 tests pass). Ten friction findings; the
   ones that change the answer: the README quick start describes
   consuming the
   kit, never developing it; model pins and reviewer availability
   are undiscoverable from the repo; the ten identical deferred
   Gate A rows read as "stuck" without the evidence file's context;
   the orientation-canary procedure ships no brief template or
   worked example; wave plans in `docs/plans/` hang off card logs
   with no navigation.
5. Dependency sweep: see the inventory below.
6. FEEDBACK.md holds thirteen undrained entries, every one already
   dispositioned in the wave-2 plan (proposed drain 8, at Gate U).

## Hypothesis

Readiness differs sharply by axis, and the blocker Mike named is
narrower than it looks.

### Another consumer repo: closest, about one wave away

`init` scaffolds, `doctor` fails loudly on placeholders by design,
the `.boardkit/` docking manifest resolves boards without per-clone
setup, and three consumer postures (committed, gitignored, invisible
via info/exclude) are field-proven per the inbox. What is missing is
already carded and scheduled: the versioned docking spec (S31), the
consumer-posture docs, and the next-id race note all sit in the
wave-2 plan. The un-scheduled residue is S17 (satellite-repo
convention) and the template canary (S6). No new work needs
inventing for this axis; it needs wave 2 to run. The acceptance test
for this axis is already designed: PLAN.md's north star, the
user-triggered agent-driver conversion run, which converts a real
repo's ADRs into a fresh board and watches where the converting
agent stumbles. PLAN.md conditions offering that run on its build
Phases 1-5 passing, and the board's wave structure has since
superseded that phase numbering without restating the trigger; when
to offer the run is a question for Mike at the wave-2 gate, not a
claim this assessment can make.

### Another machine, same operator: the real gaps are off-repo

A fresh clone passes `check` immediately; the board itself is
portable. Three things do not travel:

- The delegation contract's live ends: `~/.config/opencode/`
  (dotfiles-managed, so reconstructable, but nothing in this repo
  says so), `~/.codex/config.toml`, `~/.config/agy-mcp/`, plus
  provider auth for every lane. No bootstrap recipe exists in the
  kit, and doctor cannot vouch for any of it: the CLI prints
  preflight commands (in `resolve-route` and `dispatch-brief`) and
  by explicit design never executes them, and doctor neither runs
  them nor checks that the pin-source config trees exist on disk,
  so a green doctor run does not mean a fresh machine can dispatch. The planned
  notanton bootstrap (inbox, 2026-08-11) is the named cold-test and
  has not run.
- The kit's own clone URL appears in no operational doc (its only
  tracked occurrence is captured fixture prose in a bench golden).
  Consumer AGENTS.md files say
  `export BOARDKIT_HOME=/path/to/boardkit`, and no doc a fresh
  reader would follow says how to obtain that checkout - a
  chicken-and-egg a second machine hits on day one.
- Gate evidence: review packets and reviewer transcripts are
  gitignored machine-local state (the 159-file audit-trail finding).
  The receipts-plus-sidecar design (wave-2 decision 2, Phases 4-5)
  is the accepted fix and is not yet built.
- Right now, the board's most important artifact - the wave-2 plan
  itself - is untracked, so machine two would plan the next wave
  blind. This is a commit away from fixed.

### A new engineer: furthest, but agent-onboarding already works

Two model families oriented correctly from repo files alone (one
non-Claude, one Claude), and three more non-Claude families later
verified the repo's claims unaided as reviewers, so the agent-facing
surface passes. The human-facing surface has known,
mostly-carded gaps: the outsider-safe board README and public-repo
seam (S12, ready, unscheduled), the ranked review guide a human
needs at a U gate (S15, wave-2 Phase 2), the README's missing
kit-developer path, and - uncarded anywhere - the subscription and
account inventory a second operator would need before the routes
resolve: the providers and plans by kind, and where the keys live.
Model pins are
deliberately off-repo per the no-model-ids rule; what the kit lacks
is a template section saying what *kind* of accounts a route needs.
For an engineer outside this machine's trust boundary there is a
further precondition the kit already tracks: the publish-gate
obligations in EXTRACTION.md (strip `snapshots/`, genericize the
golden fixtures, sweep machine paths, cold-pass the README bus
test) - none started.

### The visual sync-and-verify blocker: one decision plus one small card

The render layer substantially exists: `board.md` is
Obsidian-kanban-format, `graph.md` and `boardkit dag --render` are
Mermaid (GitHub renders both natively), `INDEX.md` and `deferred.md`
cover state and exceptions, S16 (gate position in views) is
in-review, and `check` already proves views match cards. What
"visually verify board state is in sync" actually lacks:

1. **A freshness stamp.** No rendered view says which card state it
   reflects or whether the tree was dirty at render time. A reader
   on machine two cannot tell a current render from a stale one
   without running the CLI. A stamp line in the generated views plus
   a `check` rule makes the views self-verifying - with the stamp
   defined recomputably (a content digest of the card sources, or
   the last commit touching the cards dir), never the view's own
   commit sha, which is unknowable at render time. The stamp also
   touches wave 2 Phase 3's golden-view byte-identical requirement,
   so it lands after that phase or regenerates the goldens with it.
2. **A chosen surface.** Whether the visual home is GitHub's native
   rendering of the committed views, Obsidian's kanban plugin, or a
   generated static-HTML board is an undecided product question, not
   a build gap. It deserves a design card with "lean on GitHub
   rendering, build nothing" as an acceptable outcome - the same
   shape as the wave-gate decision card (S34).
3. **Cross-machine trust in gate decisions**, which is the receipts
   work already approved in wave-2 decision 2, not new scope.

So the hypothesis on the blocker: it decomposes into a small
implementation card plus a design decision; the rest is work wave 2
already owns. It is not a project.

## Machine-local dependency inventory

(Evidence from the mid-class sweep, abridged to the items a fresh
machine or clone actually depends on.)

- Tracked docs that depend on off-repo state: `AGENTS.md` and
  `README.md` require the uv toolchain and a kit checkout;
  `REVIEW-TOOLING.md` pin sources point at three `~/` config trees;
  README names claude-skills as the sibling install for language
  skills. All are documented as dependencies; none carries an
  install recipe in-kit.
- Absolute `/Users/` paths in tracked files are confined to
  `EXTRACTION.md` provenance, `snapshots/`, and `tests/golden/` -
  deliberate capture material that nothing at runtime reads.
- Gitignored-but-referenced state: `docs/board/reviews/` packets and
  ledgers are cited from card logs and evidence files; those
  references dangle on any other machine (S8's detectable-dangling
  acceptance covers this).
- Untracked-but-cited: the wave-2 plan.
- Four defects the sweep newly surfaced, none previously carded or
  in the inbox:
  1. `.boardkit/local.toml` is described as gitignored in four
     places (README, config.py, S13's card, the board-hygiene
     skill) but the repo's `.gitignore` does not cover it and
     `init` never writes the line - a consumer following the
     documented overlay convention can commit a machine path.
  2. `.claude/settings.local.json` carries an absolute machine path
     and is hidden only by the operator's global git excludesfile,
     not by this repo's `.gitignore`.
  3. `.bench-runs/prose-2026-08-11/` holds a complete prose-bench
     evaluation run (scripts, keys, grades, packets) as gitignored
     state with zero tracked trace; losing this machine loses the
     run. S10, the card meant to promote bench output into tracked
     evidence, is ready but unscheduled.
  4. This board's own `REVIEW-TOOLING.md` still carries two
     template-identical sections, one of which its own prose calls
     "not optional" (the wave-close cost record), and doctor's
     fill-check does not include those headings - so doctor reports
     the file as filled. A silent blind spot, self-inflicted on the
     kit's own board.

## Claude-memory reliance: none found

The audit's scope, stated precisely: the project memory directory
for this repo is empty, the repo carries no `CLAUDE.local.md`, and
the user-level Claude instructions hold commit and memory policy,
nothing boardkit-operational. The Claude entry file (`CLAUDE.md`)
is a one-line shim to `AGENTS.md`, in-repo. The non-Claude
cross-check: the flash-class canary completed orientation and setup
reconstruction from repo files alone, and the three review lanes
(GPT, Kimi, and GLM families) verified this document's claims
against the repo unaided. The one Claude-side soft dependency is
the skills marketplace (claude-skills sibling repo), which is a
documented install, not memory.

## Action list

Vetted against all thirteen inbox entries and the wave-2 plan;
each action names whether it is already scheduled or new, so nothing
here double-books work the board already owns.

- **A1 - commit the local-only board state** (new, immediate,
  trivial): the wave-2 plan, the evidence addendum, the canary
  evidence record
  (`docs/board/evidence/2026-08-22-spread-readiness-canaries.md`),
  and this assessment. Doctor
  already warns; this is the single cheapest spread win available
  today. Blocked only by Mike's pending Gate U on the plan text
  itself - committing the proposal is still safe, it is a proposal
  either way.
- **A2 - run wave 2** (scheduled, at Gate U): Phases 0-2 deliver
  the docking spec, review guide, canary fallback, and supersession
  parsing; Phases 4-5 deliver receipts. Most of the spread story is
  already inside the approved-pending plan; the fastest path to
  "spreadable" is Mike clearing that gate.
- **A3 - view freshness stamp** (new card candidate): generated
  views carry source commit and tree state; `check` validates the
  stamp. Directly attacks the visual-verify half of the blocker.
- **A4 - visual-surface design card** (new card candidate, decision
  card): pick the board's visual home (GitHub-native rendering of
  committed views / Obsidian kanban / generated static HTML), with
  build-nothing as an acceptable outcome. Depends usefully on S16
  landing. S27 (architecture flowchart) folds in or stays separate
  per the decision.
- **A5 - slot S8, S10, S6, and S17** (existing cards, currently
  unscheduled): S8 (board-root portability) and S17 (satellite-repo
  convention) are the another-repo axis, S6 (template canary) is
  its residue, and S10 (prose-reviewer bench) is what rescues the
  orphaned bench run from machine-local limbo. S12's public-repo
  seam is deliberately absent here: the wave-2 Phase 4 ADR already
  owns its design, so slotting it separately would double-book it.
  Recommend deciding placement explicitly at the wave-2 Gate U
  instead of leaving S8 as the named cut.
- **A6 - machine-bootstrap recipe** (cards EXTRACTION.md's
  never-shipped Phase 4 sibling-install obligation, so an existing
  debt, not an invention): a
  REVIEW-TOOLING template appendix plus doctor pointer naming what a
  second machine needs and where each piece comes from (dotfiles
  opencode group, claude-skills install, codex and agy config,
  provider accounts by kind). Cold-tested by the already-planned
  notanton bootstrap. Folds the account-inventory gap for a second
  operator into the same card.
- **A7 - README developer path + canary brief template** (small,
  prose-only; deliberately pulls part of PLAN.md's Phase 6
  publish-gate README work forward): the kit-developer quick start
  beside the consumer quick start; a shipped orientation-canary
  brief template with a worked example (adjacent to S6, not blocked
  by it); the kit's clone URL stated in README and the AGENTS
  template; and a navigation pointer to `docs/plans/` so wave plans
  stop hanging off card logs alone.
- **A8 - ignore-line and doctor-truthing batch** (new, mechanical,
  a natural addition to wave 2's Phase 1 small-fix card): add
  `.boardkit/local.toml` and `.claude/settings.local.json` to this
  repo's `.gitignore` (the only lines actually missing - `.review/`
  and `.bench-runs/` are already covered) and teach `init` to
  scaffold all four; extend doctor's required-fill
  sections to every heading the template itself calls mandatory,
  and fill this board's own two template-identical sections (the
  wave-close cost recipe and an evidence-receipt canary row for
  bench runs) rather than only making their absence visible;
  and decide whether doctor should at least stat the pin-source
  config paths it points at (running preflights stays the caller's
  job by design - the check would be existence, not execution).

Ordering: A1 today; A2 is Mike's gate; A3, A7, and A8 are small and
slot into wave 2's Phase 1-2 shape if Mike wants them this wave;
A4-A6 are mint-as-backlog candidates for Phase 0.

## Assumption register

For the adversarial panel to attack:

1. Board legibility for agents is proven by one graded orientation
   canary plus one graded onboarding simulation; the board itself
   needs no legibility changes, and the remaining agent-onboarding
   gaps are the shipped-template items A7 names.
2. The empty project memory store, the absence of a
   `CLAUDE.local.md`, and the non-Claude runs (one canary, three
   reviewer lanes) are together sufficient evidence that repo files
   alone carry the operational knowledge.
3. Receipts-plus-sidecar (wave-2 decision 2) is the accepted
   direction for cross-machine gate-evidence trust; its sufficiency
   is decided by the S32 ADR and proven by Phase 5's Gate M, and
   pre-wave-2 decisions stay unverifiable from a second machine
   under the default start-fresh backfill (wave-2 open item 2). The
   visual blocker adds only the stamp (A3) and the surface decision
   (A4).
4. Consumer-repo spread needs no new invention: wave 2, S8
   (board-root portability), S17 (satellite-repo convention), S6
   (template canary), and the A8 mechanical batch cover it, with
   S12's seam design already owned by the wave-2 Phase 4 ADR.
5. Committing the wave-2 plan before its Gate U ruling (A1) is safe
   and does not pre-empt the ruling.
6. The interface/render problem is a card-sized gap, not a project.

## Review ledger

Adversarial review per the standing rule; three lanes ordered by
Mike, all from non-author families. Author: claude-fable-5 (Claude
family). All three reviewers judged identical pre-fix bytes of this
document on 2026-08-22; the fix pass below their findings is the
current text. Transport record: the Kimi lane needed one retry (its
first run exited 0 with the stream truncated and no verdict - a
recorded failed delegation, not a pass); the GLM lane reached its
model through openrouter under Mike's conditional approval after the
zai-coding-plan provider failed pre-vet (the subscription is the
start plan, which only the zcode app can reach) and three
opencode-go attempts each truncated the same way; a dispatch-shaped
smoke run preceded each successful full run.

### Lane 1: codex CLI, GPT family (gpt-5.6-sol) - FAIL, 8 BLOCKING / 2 MINOR

1. BLOCKING, canary runs unauditable (no filed key, answers, or
   grades). Fixed: evidence record filed at
   `docs/board/evidence/2026-08-22-spread-readiness-canaries.md`;
   the Evidence and Method sections cite it.
2. BLOCKING, model-family count false ("three non-Claude
   families"). Fixed: Method, the new-engineer section, the memory
   section, and assumptions 1-2 now state one non-Claude canary,
   two Claude probes, and three non-Claude reviewer lanes.
3. BLOCKING, north-star timing contradicted PLAN.md's Phases-1-5
   precondition. Fixed: the conflict is stated and the trigger
   handed to Mike instead of asserted.
4. BLOCKING, A3's commit-sha stamp self-referential. Fixed: A3
   respecified as a recomputable stamp (cards content digest or
   last commit touching the cards dir).
5. BLOCKING, A6/A7 overlapped PLAN Phases 4 and 6. Fixed: both
   relabeled as carding existing never-shipped obligations.
6. BLOCKING, S6/S17 residue omitted from the action list. Fixed:
   both join A5 and assumption 4.
7. BLOCKING, assumption 3 pre-empted the S32 ADR and Gate M.
   Fixed: softened to accepted-direction with sufficiency assigned
   to the ADR and Gate M.
8. BLOCKING, A8 detected the unfilled REVIEW-TOOLING sections
   without filling them. Fixed: A8 now fills both live sections.
9. MINOR, `.review/` and `.bench-runs/` already gitignored. Fixed:
   A8 names only the missing lines.
10. MINOR, clone URL does appear in one tracked bench golden.
    Fixed: claim narrowed to operational docs.

### Lane 2: opencode, Kimi K3 (kimi-for-coding) - FAIL, 5 BLOCKING / 6 MINOR

1. BLOCKING, same family-count error as lane 1 finding 2. Fixed
   there.
2. BLOCKING, assumption 1 miscounted its probes and its "no further
   legibility work" overclaim contradicted A7. Fixed: assumption 1
   rewritten.
3. BLOCKING, same S6 omission as lane 1 finding 6. Fixed there.
4. BLOCKING, A1 omitted the assessment's own untracked evidence.
   Fixed: A1 now names the canary evidence record and this
   document.
5. BLOCKING, the intro claimed a completed panel while the ledger
   was a placeholder. Fixed: this ledger is the completion; the
   intro tense now matches the record.
6. MINOR, preflight printing misattributed to doctor. Fixed:
   attributed to `resolve-route` and `dispatch-brief`.
7. MINOR, same gitignore duplicate as lane 1 finding 9. Fixed
   there.
8. MINOR, the wave-plan navigation friction had no action. Fixed:
   folded into A7.
9. MINOR, assumption 3 ignored the undecided R-wave backfill.
   Fixed: the backfill condition is named.
10. MINOR, A3 sizing ignored the self-reference and the golden-view
    collision. Fixed: both stated in A3.
11. MINOR, memory audit scope covered one store only. Fixed: scope
    stated precisely in the memory section.

### Lane 3: GLM 5.3 (openrouter, conditional approval) - FAIL, 1 BLOCKING / 7 MINOR

1. BLOCKING, same family-count error as lane 1 finding 2. Fixed
   there.
2. MINOR, same clone-URL absolute claim as lane 1 finding 10.
   Fixed there.
3. MINOR, same gitignore duplicate as lane 1 finding 9. Fixed
   there.
4. MINOR, A5's S12 slot double-booked the wave-2 Phase 4 ADR's
   ownership of the seam design. Fixed: S12 removed from A5 with
   the ownership stated.
5. MINOR, same assumption-4 S6 omission as lane 1 finding 6. Fixed
   there.
6. MINOR, same north-star trigger conflict as lane 1 finding 3.
   Fixed there.
7. MINOR, same A1 under-scope as lane 2 finding 4. Fixed there.
8. MINOR, same assumption-1 miscount as lane 2 finding 2. Fixed
   there.

### Convergence

Three independent FAIL verdicts over the same draft, with heavy
overlap converging on the family-count error, the assumption
miscounts, and the action-list wording defects. Every finding was
accepted and fixed; none was rejected. Per the wave-2 convergence
discipline this closes round one; whether the fixed text earns a
re-review round is Mike's call at the gate.
