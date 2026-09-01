# Notanton cold-test runbook (S39)

Date: 2026-08-31. Card: S39 (machine-bootstrap recipe), in-progress.
Who runs this: an agent session ON notanton, with Mike present to
launch it. Nothing here runs from the mac; the mac board owner
verifies read-only over SSH and keeps every board write on the
boardkit side.

Ground rules, read before the first command:

- These two repos belong to Mike and carry live hooks. Every commit
  fires `gitleaks git --pre-commit --staged` plus `make lint`, and the
  commit message passes commitlint (types `feat fix refactor test docs
  chore`) with no AI-attribution or sign-off trailers. Do not bypass a
  hook, ever, including in the sandbox.
- Show Mike the exact commit message and get his approval before each
  real-repo commit. The sandbox phase commits nothing real.
- Record every command's verbatim output into a run log at
  `~/dev/boardkit-coldtest-run.md` (create it in phase A). A step whose
  output is not recorded did not happen. Findings are logged inline as
  `FINDING n:` entries with a one-line statement and the evidence that
  grounds them.
- The pass condition is the recipe, not improvisation. When the recipe
  is wrong or incomplete, record the finding and do the smallest
  correct thing; note what the recipe should have said.

## Phase A - machine bootstrap (recipe exercise)

A1. Install uv, which notanton does not have yet:

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
uv --version
```

A2. Clone the kit, once, to one canonical location:

```sh
git clone git@github.com:Shearerbeard/boardkit.git ~/dev/boardkit
git -C ~/dev/boardkit log --oneline -1
```

One checkout. The recorded cost of the opposite is thirteen
contradictory clone statuses; do not add a second.

A3. Verify the board runs. The export is its own line; a same-line
prefix silently targets the wrong checkout:

```sh
export BOARDKIT_HOME=~/dev/boardkit
uv run --project "${BOARDKIT_HOME}" boardkit check
```

Expected: `OK: 49 cards valid, views current` (plus known WARN lines).
Anything else is a finding before work continues.

A4. Skills, by harness, as available on notanton:

```sh
claude plugin marketplace add Shearerbeard/boardkit
claude plugin install board@boardkit
```

If Claude Code is not on notanton, record that and skip; the board
runs without plugins, doctor will name the gap.

A5. Account inventory, by kind, never by model id. For each harness
present (Claude Code, opencode, codex, agy if installed), record:
which provider account kind answers (subscription, API key, Bedrock
role), and prove each lane live with the dispatch-shaped read probe
from `MODEL-CLASSES.md`: stage one small file where that lane's
staging contract puts packets, and have the lane read a nonce back
from the file's content. Kinds only; an answer probe alone does not
vet a lane.

## Phase B - sandbox rehearsal (zero real-repo commits)

B1. Scratch clone of the first consumer:

```sh
git clone ~/dev/tang-nano-cores /tmp/tang-sandbox
cd /tmp/tang-sandbox && make hooks
```

B2. Canary-secret probe, before any scaffold commit exists. AWS's
documented example keys are on gitleaks' allowlist and will NOT trip
it; generate a fresh GitHub-token-shaped canary instead (verified
against default gitleaks rules):

```sh
printf 'github_token = ghp_%s\n' \
  "$(tr -dc 'A-Za-z0-9' </dev/urandom | head -c 36)" > probe.txt
git add probe.txt
git commit -m "chore: probe"
```

Expected: gitleaks exits nonzero and names the finding. Record the
output, then `git reset` and delete `probe.txt`. If the hook does not
fire, that is a FINDING and a stop: the guardrail is the precondition
for everything after it.

B3. Scaffold the board in the sandbox:

```sh
export BOARDKIT_HOME=~/dev/boardkit
uv run --project "${BOARDKIT_HOME}" boardkit init
```

Expected: `boardkit.toml` and `docs/board/` scaffolded; the NOTE that
AGENTS.md and CLAUDE.md were left untouched (that NOTE is the recipe's
cue for B4); four ignore lines appended to `.gitignore`; views
generated; `boardkit check` clean inside the sandbox.

B4. The merge block. Append to the existing AGENTS.md, after the
wiki-kit dock block at the end of the file, preserving the repo's
AGENTS.md-first pattern (CLAUDE.md stays untouched):

```markdown
<!-- boardkit:dock:start -->
This repo carries a boardkit card board at `docs/board/`. Read
`docs/board/PROCESS.md` for the process and `docs/board/cards/INDEX.md`
for current state before starting work; `boardkit check` (via the
BOARDKIT_HOME export in that file) validates the board.
<!-- boardkit:dock:end -->
```

B5. Doctor, with the expectation sheet applied finding by finding:

```sh
uv run --project "${BOARDKIT_HOME}" boardkit doctor
```

| Doctor finding | Expected disposition |
|---|---|
| entry.parity WARN on CLAUDE.md | Keep. Their shim wording is the repo's own; the check warns, never errors. |
| review-tooling.filled ERROR | Expected at first: the scaffold ships prompts. Fill the four sections for notanton's real harnesses, kinds not model ids. |
| roles.filled / routes.pin-source | Same: fill from notanton's actual lanes. |
| skills.installed | Depends on A4; record what is actually installed. |

Then rerun doctor to completion: the sandbox does not proceed to B6
until doctor runs green, or until every remaining red item is an
exception Mike has named and accepted in the run log. Record the final
run verbatim either way.

B6. Two scaffold commits in the sandbox, hooks live, named paths only
(`git add -A` can sweep strays):

```sh
git add boardkit.toml .gitignore docs/board
git commit -m "chore: scaffold the boardkit board"
git add AGENTS.md
git commit -m "docs: add the boardkit dock to agents entry"
```

Expected: gitleaks clean (markdown only), `make lint` a no-op over
these files, commitlint accepts `chore:` and `docs:`. Record the
output of both commits.

B7. Stop. File the run log. The mac board owner verifies the sandbox
read-only, and Mike approves the real sequence at U1 before any commit
touches `~/dev/tang-nano-cores` or `~/dev/snes-hello`.

## Phase C - U1 stop (Mike)

Present: the runbook findings, the sandbox evidence, and the exact
commit sequence for phase D. Nothing proceeds without explicit
approval.

## Phase D - live installs (after U1)

D1. tang-nano-cores: repeat B3, B4, B5, B6 on the real repo, the same
two-commit split and the same messages as B6.

D2. snes-hello, recipe-only. Same steps, no improvisation: any
deviation from D1's recipe is a finding against the recipe, not a
local fix to silently apply.

D3. Orientation canary per board, run to the letter of the
orientation-canary procedure in `docs/board/PROCESS.md`: compute the
key first with `boardkit canary-key` (via the same BOARDKIT_HOME
export), then dispatch a fresh agent session - one with no context
from this run - on exactly the cold-start surface: `INDEX.md`,
`board.md`, the PROCESS.md roles and recovery sections, and
`deferred.md` unconditionally (when the view is absent, the brief says
so and states that absence reads as no deferred gates). The canary
answers the four questions from the procedure verbatim. Grade against
the computed key, never the canary's confidence; file the key, the
answers, and the grade as evidence. A miss is graded by the two miss
classes in the procedure and recorded, not silently absorbed.

## Phase E - close

Hand the run log and the canary answers to the mac board owner. The
findings ledger lands on S39's card log; kit-level gaps become
boardkit cards; S39 proceeds to Gate D and Gate U with the cold-test
as its acceptance evidence.
