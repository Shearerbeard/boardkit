# Gate A review cycle over the R-wave, and the ruling that closed it

Board owner session, 2026-08-16. This record covers the batched Gate A
that ten cards had been holding open since 2026-08-09, the four fix-review
rounds that followed it, and the ruling that ended the cycle without a
pass verdict. Cards: S13, S16, S18, S19, S20, S21, S22, S23, S24, S25.

## Reviewer and transport

The board's `code-review` role resolves to `opencode-reviewer` with
`codex-reviewer` declared as its fallback. The opencode lane failed its
contract-shaped read probe four times across three models
(`openai/gpt-5.6-terra` twice at 180s and 300s, the fireworks
`kimi-k3` at 240s, `DeepSeek-V4-Flash-0731` returning exit 0 with no
output). `opencode models` answered throughout, so the CLI ran and the
model calls did not. That is the recorded stall signature plus a
zero-exit empty return, which the validity rule counts as a failed
delegation rather than a pass.

The declared fallback took the work. Every round below ran through
`codex exec --sandbox read-only`, pre-vetted by a nonce read-back under
the route's staging contract, on `gpt-5.6-sol`. The whole wave was
authored by `claude-fable-5`, so reviewer-differs-from-author holds for
every commit in every range.

Every round reported `pytest` and the `uv`-prefixed board commands as
UNVERIFIED: the read-only sandbox has no writable temporary directory or
uv cache. Per the Gate A rule those are the board owner's to run, and
they were, board-side, at every round: the suite went 337 to 361 green
across the cycle, with `ruff check` and `boardkit check` clean at each
commit.

## The rounds

| Round | Object | Verdict | Findings |
| --- | --- | --- | --- |
| 1 | the ten card diffs, one packet each | 10 FAIL | 24, all dispositioned |
| 2 | six fix commits | 1 PASS, 5 FAIL | 5 |
| 3 | `2121d41` | FAIL | 3 |
| 4 | `8487140` | FAIL | 2 BLOCKING, 1 MINOR |
| 5 | `3a4b001` | FAIL | 1 |

Round 1's 24 findings were dispositioned per card in each card's own log:
fixed, rejected with a recorded reason, resolved by amending an
acceptance line the implementation had correctly diverged from, or carded
(S28, the CardStore wiring gap). Rounds 2 through 5 reviewed the fix
commits, per the fix-commit re-review duty.

From round 3 onward the findings were no longer about the cards' reviewed
diffs. Round 5 states it plainly: the recorded fixes and all three round-4
residues are resolved. What each later round returned was one further
evasion of `_is_shim`, the text heuristic in the S24 fix code that decides
whether an entry file is a pointer or a second instruction set:

- round 3: one mention of AGENTS.md anywhere counted as proof
- round 4: a directive written as a Markdown heading passed
- round 5: prose after a mid-line comment close passed

Each was real and each was fixed, the last by stripping comment spans
rather than comment lines, which removes that class rather than its
latest instance. Each round produced exactly one new evasion, narrower
than the one before.

## The ruling

The kit has no rule for when an adversarial fix-review cycle terminates.
That gap is S14's subject, and this cycle is its evidence. The three-attempt
cap in `REVIEW-TOOLING.md` governs repeated dispatch attempts against a
stalled transport, not iteration depth against a reviewer that is working
correctly and finding real things.

Ruling, made by the board owner and open to the user's revision:

1. The cycle ends at round 5. Round 5's finding is fixed in `732c1c8`,
   which no review has covered.
2. Every finding against each card's own reviewed diff is resolved. That
   is what Gate A's object is, and the wave is clean against it.
3. The residual hardening of `_is_shim` is carded as S29, a design
   decision between a stated convention and a signal with stated limits,
   rather than patched a sixth time in-cycle. Its residual risk is a
   missed warning, never a false failure.
4. **Gate A does not tick on any of the ten cards.** The reviewer never
   signed off explicitly, and the kit's own rule is that a failed or
   silent return is never read as a pass. The gate stays open-deferred
   with this record as its reason.
5. The pass decision goes to the user at each card's `U(code-review)`
   gate, which eight of the ten still owe in any case. The user has the
   full ledger here and per-card in the logs, and may tick Gate A on this
   record, ask for a sixth round, or send S29 back into the wave first.

The board owner did not substitute a transport for the canary's declared
route on its own authority, and did not tick a gate its reviewer had not
passed. Both are deliberate, and both are the reason this record exists.

## Where the material lives

Per-card packets and reviewer verbatims sit under the board's gitignored
`docs/board/reviews/`: `<ID>/` for round 1, and `S25-fix` through
`S25-fix4` plus the five sibling `-fix` directories for the later rounds.
Each holds `REVIEW.md`, the diffs, the staged `prompt.md`, and
`gate-a-output.txt`. Regenerate them at will; the durable record is the
card logs and this file.

One transcript hazard is worth naming, because it cost a wrong reading
mid-session. A reviewer that reads other cards' review outputs quotes
their verdict lines into its own transcript, so
`grep 'VERDICT:' <output> | tail -1` can report a verdict that belongs to
a different review. Read the reviewer's own final message instead.

> Addendum 2026-08-19: the deferred canary below ran once the opencode
> transport recovered. Pre-vet nonce read-back passed under the
> working-dir staging contract, and the canary answered 4/4 against
> `boardkit canary-key`, with citations and no invented answers. Output:
> `docs/board/reviews/canary-2026-08-19/canary-output.txt` (machine-local).
> The deferral this section records is resolved.

## Session close: the orientation canary did not run

`board-hygiene` makes the canary a hard stop before close. The board's
contract binds `roles.canary` to `opencode-reviewer` and declares no
fallback, and that transport is the one that failed four read probes
above. `code-review` survived the same outage only because it names
`codex-reviewer` behind it.

So the canary is recorded as deferred rather than run. The board owner
did not route it to codex on its own authority: the router's rule is that
a session takes the declared fallback or defers, and substituting a
transport the contract does not name would make the next session's
reading of that contract wrong. The gap is queued for the maintainer in
the feedback inbox.

What did run, board-side, so the close is not bare: `boardkit check`
clean at 29 cards with views current, `boardkit doctor` at 20 passed and
0 errors with only the expected `host.tree-state` warning for unpushed
commits, `uv run pytest -q` at 361 green, `ruff check` clean, and `vale`
clean on every markdown file this session wrote. The key the canary would
have been graded against is reproducible with `boardkit canary-key`; at
close it lists the ten cards in review with their gate positions, S1 as
the next pull, and the ten open deferrals.

The one board-legibility defect this session found and fixed was in the
deferred view: the ten resolved 2026-08-09 batch deferrals rendered
beside the current ones, so every card claimed to be waiting on a batch
that had already run. Their markers are annotated as superseded, and the
kit's missing supersession vocabulary is in the inbox.

## Fix commits

`fa9db37` S25, `b9e74d1` S16, `1214b10` S13, `fe308d0` S18, `99cfd4a`
S19/S20/S21, `6af06a7` S22/S23/S24, then the cycle commits `2121d41`,
`8487140`, `3a4b001`, `732c1c8`. Each carries its card trailers. None
extends any card's `commit-range`: the fix commits are separated by
foreign commits, and an `A..B` range cannot express a non-contiguous set,
so each was reviewed through its own `--suffix` packet instead. That
limit is itself queued for the maintainer in the feedback inbox.
