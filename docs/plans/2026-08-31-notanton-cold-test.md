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
role), and whether a one-token probe answers. Kinds only.

## Phase B - sandbox rehearsal (zero real-repo commits)

B1. Scratch clone of the first consumer:

```sh
git clone ~/dev/tang-nano-cores /tmp/tang-sandbox
cd /tmp/tang-sandbox && make hooks
```

B2. Canary-secret probe, before any scaffold commit exists. Stage a
fake key, attempt a commit, expect the hook to block it:

```sh
printf 'aws_access_key_id = AKIAIOSFODNN7EXAMPLE\n' > probe.txt
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
| review-tooling.filled ERROR | Expected: the scaffold ships prompts. Fill the four sections for notanton's real harnesses, or record as an open item for Mike. |
| roles.filled / routes.pin-source | Same: fill from notanton's actual lanes, kinds not model ids. |
| skills.installed | Depends on A4; record what is actually installed. |

B6. One scaffold commit in the sandbox, hooks live:

```sh
git add -A
git commit -m "chore: scaffold the boardkit board"
```

Expected: gitleaks clean (markdown only), `make lint` a no-op over
these files, commitlint accepts `chore:`. Record the output.

B7. Stop. File the run log. The mac board owner verifies the sandbox
read-only, and Mike approves the real sequence at U1 before any commit
touches `~/dev/tang-nano-cores` or `~/dev/snes-hello`.

## Phase C - U1 stop (Mike)

Present: the runbook findings, the sandbox evidence, and the exact
commit sequence for phase D. Nothing proceeds without explicit
approval.

## Phase D - live installs (after U1)

D1. tang-nano-cores: repeat B3, B4, B5, B6 on the real repo. Commit
messages: `chore: scaffold the boardkit board` then `docs: add the
boardkit dock to agents entry`.

D2. snes-hello, recipe-only. Same steps, no improvisation: any
deviation from D1's recipe is a finding against the recipe, not a
local fix to silently apply.

D3. Orientation canary per board: a fresh agent session (one with no
context from this run) reads `docs/board/cards/INDEX.md`, `board.md`,
and the PROCESS.md recovery section, then answers: which cards are
in-review and in-progress; what is the next pull; which gates are open
or deferred; who is the board owner and where it stops for the user.
Grade against what the views actually say. A miss is a finding on the
board's legibility, recorded, not silently absorbed.

## Phase E - close

Hand the run log and the canary answers to the mac board owner. The
findings ledger lands on S39's card log; kit-level gaps become
boardkit cards; S39 proceeds to Gate D and Gate U with the cold-test
as its acceptance evidence.
