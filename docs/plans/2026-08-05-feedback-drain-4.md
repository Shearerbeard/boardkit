# Feedback drain 4 (2026-08-05)

Maintainer session drain of the four entries inboxed at 089d17c, all
filed from the Epoch bootstrap sessions (claude-code, fable-5): the
first public-repo consumer of the kit, plus the first split layout
(private board beside a public code repo). All four are accepted. Two
are feature-sized and become cards S12 and S13 on this board; one is a
skill-text defect fixed in this drain's commits; one folds into S12
because it is the same seam.

## Drained: public-repo-seam-for-contract-docs (accepted, carded S12)

Source: epoch-postgres `docs/adr/0009-private-tooling-seam.md` and the
codex adversarial review in that session. The contract docs
(PROCESS.md, MODEL-CLASSES.md, REVIEW-TOOLING.md) read as the
maintainer's AI-orchestration manual to an outside reader; a review
graded a tracked PROCESS.md as a publication blocker. The consumer
repo resolved it by hand: gitignore the three contract docs plus
`boardkit.toml`, add a repo-owned outsider-safe `docs/board/README.md`.

Disposition: this is a real seam the kit should own, not a per-repo
workaround. Card S12 (public-repo seam) carries the candidate fixes as
its scope. That covers a shipped outsider-safe board README template,
a doctor warning for a public remote with tracked contract docs, an
init `--public` mode that writes the gitignore lines, and the
unconditional PROCESS.md template paragraph stating that outside
contributors do not need this tooling.

## Drained: generated-view-headers-assume-process-doc (accepted, folded into S12)

Source: codex adversarial review round 2 over the same bootstrap. The
header prose `boardkit render` writes into `INDEX.md` and `board.md`
(`src/boardkit/board.py`, the view-header string lists) points readers
at "PROCESS.md, Delegation protocol" and "the session running the
board". In a public repo where PROCESS.md is untracked, the generated
views ship an unresolvable pointer plus session vocabulary, and the
never-hand-edit rule blocks a local fix.

Disposition: same seam as the entry above, so it rides S12 rather than
its own card. The deliverable there: the generated header either goes
neutral ("see the board README") or derives its doc pointer from a
`boardkit.toml` key, and either way stops assuming the reader can open
PROCESS.md.

## Drained: board-hygiene-step-one-assumes-path-install (accepted, fixed)

Source: epoch-board `docs/board/retro/2026-08-05-bootstrap-canary.md`.
A codex orientation canary obeyed the board-hygiene skill's step-one
fenced block literally, ran bare `boardkit doctor`, got
command-not-found, and hard-stopped per the skill's own stop rule
without reading the board. The prose four paragraphs down explains the
checkout bootstrap, but a literal-minded model executes the fence, not
the prose. The `boardkit canary-key` fence later in the skill had the
same shape.

Fix, in `plugins/board/skills/board-hygiene/SKILL.md`: both fenced
invocations now use the checkout-based form
(`uv run --project "${BOARDKIT_HOME:-../boardkit}" boardkit ...`),
step one opens by saying to resolve the invocation from the repo's
agent entry file first because bare `boardkit` is never on PATH, and
the stop rule now fires on the resolved invocation failing, not on the
bare name being absent.

## Drained: skills-prescribe-init-over-sibling-board (accepted, carded S13)

Source: claude-skills
`feedback/2026-08-05-claude-code-board-discovery-init/process-feedback.md`.
In a split layout (private board in `../epoch-board`, public code repo
with no tracked pointer by design), a session offered to bootstrap a
fresh board even after the user named the existing board's path. Both
board skills state "`boardkit.toml` at the repo root" as a hard
precondition and prescribe offering `boardkit init` when it is
missing; discovery is cwd-only, so a user-stated sibling path loses to
the precondition. The hand-bootstrapped board repo also lacked the
entry files init writes, so the right repo offered no CLI bootstrap.

Disposition: feature-sized because it spans CLI discovery and both
skill texts, so it becomes card S13 (board discovery beyond cwd). The
scope: a user-named board path, a local untracked pointer, and a
`BOARDKIT_BOARD` env var all win over offering init; a missing root
`boardkit.toml` reads as "check for a sibling board" rather than "no
board exists"; and in split layouts the tooling reminds that the code
repo needs an untracked pointer back to the board.
