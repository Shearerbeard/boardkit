# New developer onboarding: acceptance script

Who runs this: someone new to the codebase, on a machine that has
never touched it before. The only inputs are the repo's URL and
their own AI-agent account - nothing else.

The actual pass condition: they complete every row below without
asking the maintainer, or anyone else who already knows the system, a
single question. The first time they have to ask "what does this
mean" or "can you check this for me," that is the finding. Log it and
keep going; do not stop the run over one gap.

| # | Step | Action | Expected result | Pass/Fail |
|---|------|--------|------------------|-----------|
| 1 | Install | Clone the repo. Follow the written setup instructions to a working command-line tool, and connect at least one AI provider account so it can actually run. | They reach a working setup using only what is written down. Nothing is left as an unwritten step or an "oh, you also need X" surprise. | |
| 2 | Orient | Point an AI agent at the repo with zero extra instructions and ask it what is going on. Separately, have the human read the top-level doc start to finish. | The agent's summary of current state is accurate with no hints from a human. The human can explain, unprompted, what the project is and how work is organized. | |
| 3 | Verify | Run the project's built-in health-check commands. | They pass clean, or any warning is explained well enough in the docs that the tester knows whether it matters. | |
| 4 | See | Open whatever visual or dashboard view the project produces of its own current state. | It agrees with what the health-check commands just reported - no contradictions, nothing obviously stale. | |
| 5 | Trust | Pick one past decision recorded in the repo's own history and try to confirm it was actually reviewed, using only files in the repo - no access to anyone's private logs or machine. | They can find the record and reconstruct enough reasoning to trust it was not rubber-stamped. | |
| 6 | Run | Pick up one small, ready piece of work from the board and complete it using their own AI agent(s), through whatever review steps the process requires. | It is completed and passes its own review, driven entirely by their tools and accounts. | |
| 7 | No lifeline | Outcome check across rows 1-6, not a separate action. | At no point did they contact the maintainer. | |

Verdict: pass only if all seven rows pass. A single fail does not end
the run - get the tester past that one step and keep collecting data
on the rest, so one gap does not hide the others.

Source: this repo's `docs/board/cards/s41-co-worker-consumption.md`
epic, restated with no card ids or board vocabulary so it stays
readable to someone who has never seen this board.
