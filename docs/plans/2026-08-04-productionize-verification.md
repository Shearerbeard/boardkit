# Plan: productionize the verification loop (2026-08-04 audit wave)

Status: authored 2026-08-04 from the four-agent topology audit and the
codex second opinion (VERDICT: REVISE, findings applied to stage 6's
shape). Cards S1-S7 on this repo's own board are the execution units;
this file owns sequencing, gates, and the Gate T handout. The board
itself was initialized this session - the kit now dogfoods its own
process, and these are its first cards.

## Scope

- Core problem: the delegation machinery fails in ways prose rules have
  not fixed (two burns with the recipes installed), wave close collects
  no human input and requires no retro, template changes ship to
  consumers undetected, and one shipped fix (native opencode routing)
  has never been verified live.
- Audience: this repo's maintainer sessions; consumer repos that sync
  templates; internal devs consuming claude-skills without boardkit.
- Success: every card's acceptance section passes; the control seam's
  deterministic steps run through the CLI instead of agent memory; the
  63% external-lane baseline has a measurement bed that can move it.
- Non-goals: no MCP surface for the transport wrapper (codex finding 6:
  thin wrapper first, measure, then decide); no change to the
  no-model-ids rule; no boardkit execution of repo-configured commands.

## Verification

- Smoke test: `boardkit check` and `boardkit doctor` clean on this
  repo's own board at every stage boundary; `uv run pytest -q` green.
- Deterministic checks: `uv run pytest -q`, `uv run ruff check`, `vale`
  on every markdown file a stage touches; `bin/check-skills` for the
  claude-skills card.

## Blast Radius

- This repo: templates, board-hygiene and delegating-work skills,
  doctor/contract/cli/board modules, new golden-brief tree, this new
  live board.
- External: `~/dev/claude-skills` (S3), `~/dev/rust-holes` (S4), one
  new wrapper repo (S7). External cards carry `lineage: none` and log
  their own commits.
- Coverage gaps the cards close: no test regenerates briefs against the
  templates (S6); no structured record of transport outcomes (S7); no
  retro artifact at wave close (S1).

## Delegation inventory (taken at planning time)

Provider question first, per the inventory's new opening step: no
provider directive is on record for this planning session, so the
harness configuration stands as-is - opencode and codex lanes as pinned
in their own configs, agy budget-gated. Author of the plan and cards:
the Claude session (route `claude-session`). Reviewers resolve at
dispatch time via `boardkit resolve-route`; code review routes
opencode-first with codex fallback, prose review routes agy-first.
Every reviewer lane differs from the authoring family, so the
reviewer-differs-from-author invariant holds on any allocation above.

## Implementation Stages

#### Stage 1: wave-close retro (card S1)
- Goal: the retro step, tough-area snapshots, and the driver question
  land in the shipped PROCESS template and board-hygiene; FEEDBACK
  gains the `reporter` field with an explicit skip rule.
- Gates: S -> A -> U
- [ ] Gate S: load skill `gate-probes`, then `uv run pytest -q`,
  `uv run ruff check`, `vale` on touched files.
- [ ] Gate A: adversarial review per S1's focus question, reviewer from
  `boardkit resolve-route prose-review`.
- [ ] Gate U: contract-doc wording and the reporter field are the
  user's call. 🛑 USER GATE
- Done when: S1's acceptance section passes and the card is Done.

#### Stage 2: CLI wiring trio (card S2)
- Goal: `pre-vet`, `deferrals`, and `stage-packet` subcommands replace
  the three prose recipes whose inputs the kit already holds.
- Gates: S -> A
- [ ] Gate S: load skill `gate-probes`, then `uv run pytest -q`,
  `uv run ruff check`; crossed-contract refusal test present.
- [ ] Gate A: adversarial review per S2's focus question, reviewer from
  `boardkit resolve-route code-review`.
- Done when: S2's acceptance passes; skills and templates point at the
  commands.

#### Stage 3: external-repo hygiene (cards S3 + S4, parallel)
- Goal: claude-skills' dangling-router and pinning defects closed; the
  typed-holes skill declared canonical over PLAYBOOK.
- Gates: S -> A (each card separately)
- [ ] Gate S (S3): `bin/check-skills`, `vale`.
- [ ] Gate A (S3): per S3's focus question.
- [ ] Gate S (S4): `vale`; never-publish rule intact.
- [ ] Gate A (S4): per S4's focus question.
- Done when: both cards' acceptance sections pass in their own repos.

#### Stage 4: the never-run Gate T (card S5) 🛑 USER TEST
- Goal: live proof of native opencode routing, closing the 2026-07-27
  plan's unchecked stage 4.
- Gates: M -> T
- [ ] Gate M: agent dry run per the handout below, transcript saved to
  `docs/board/evidence/`.
- [ ] Gate T: the user runs one real review per the handout.
- Gate T handout:
  - Config diff: none - this verifies deployed state as-is. Confirm
    `~/.config/opencode/AGENTS.md` resolves (it is a dotfiles symlink)
    before starting; if it dangles, stop and file that instead.
  - Run command: `cd ~/dev/chore-lottery && opencode` then, in the
    session: ask it to run an adversarial Gate A review of a live card
    with a fresh diff. Venue moved from this repo to chore-lottery by
    user ruling 2026-08-04: a real consumer board makes the review
    real, and that board is v2 and doctor-clean.
  - Reference prompt: "Act as board owner. Run Gate A on the staged
    diff for the current in-review card using this repo's
    REVIEW-TOOLING bindings."
  - Expected observations, in order: (1) the session reads
    `~/.config/opencode/agent/*.md` or `opencode.json` and states the
    reviewer pin; (2) it dispatches the reviewer through its own task
    tool; (3) a verdict with numbered findings returns; (4) no
    `opencode run` appears anywhere in the transcript.
  - Failure signatures: `opencode run` executed from inside the
    session; a review answered by an agent other than the pinned
    reviewer (silent `--agent` substitution); escalation to agy after
    a permission refusal instead of staging into `.review/`; an empty
    return treated as a pass.
  - Revert steps: none needed for a read-only review. If the session
    misbehaves, kill it and file the transcript as a FEEDBACK entry
    with `reporter` set to you.
- Done when: the evidence file exists showing all four behaviors, or
  the failure is filed as feedback.

#### Stage 5: template canary machinery (card S6)
- Goal: kit baseline digest, `template-diff`, and checked-in golden
  briefs make a template change visible to consumers before it ships.
- Gates: S -> A
- [ ] Gate S: load skill `gate-probes`, then `uv run pytest -q`,
  `uv run ruff check`; negative control recorded in the card log.
- [ ] Gate A: per S6's focus question, code-review route.
- Done when: S6's acceptance passes, including the one-word-edit
  negative control.

#### Stage 6: transport wrapper spike (card S7) 🛑 USER GATE
- Goal: the thin wrapper and canary harness, shaped by the codex
  REVISE findings (strict result protocol, deadline-based cancellation,
  liveness as telemetry, `--agent` refusal, per-job record).
- Gates: S -> A -> U
- [ ] Gate S: wrapper test suite; boardkit suite if adapter naming
  lands.
- [ ] Gate A: per S7's focus question.
- [ ] Gate U: adopt-or-drop on canary numbers vs the 63% baseline.
- Done when: S7's acceptance passes and the user has ruled on adoption.

## Sequencing

S1, S2, S3, S4, and S5 have no dependencies and can run as separate
sessions in any order; S5 first is the cheapest information. S6
serializes with S1 (both move template text that golden briefs would
pin). S7 depends on S2's staging materialization and should not start
before the canary harness has something to measure against.

## Rollback

Each card is its own commit set; in-repo stages revert with `git
revert`. External cards revert in their own repos. The board itself is
additive - removing `boardkit.toml` and `docs/board/` returns the repo
to the pre-dogfood state with no effect on shipped templates.
