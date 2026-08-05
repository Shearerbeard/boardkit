# S5 Gate T evidence: native opencode routing, live

Session under test: the user's native opencode board-owner session in
~/dev/chore-lottery, 2026-08-04. Board owner model
fireworks-ai/accounts/fireworks/models/kimi-k3; reviewer subagent
`general` pinned to DeepSeek-V4-Flash-0731 at session time (reviewer
session ses_030fb4f84ffeDxH0sc2qSsH2N7). Primary artifact: the session's
own review record, chore-lottery
`docs/board/retro/2026-08-04-model-classes-review.md`, corroborated by
`docs/board/retro/2026-08-04-s7-retro.md` (delegation and packet-duty
dimensions) and the `.review/` tree (S3, S5, S7 packet directories).

## The four behaviors

- (a) Pins read before routing. The review record states the board
  owner read the pins directly from the ~/.config/opencode config and
  documents the pin inventory (general/explore/rust-write-fast
  same-model collision, the GLM-5.2-Fast re-pin pending restart) -
  routing decisions were made from the config, not from agent names.
- (b) Reviewer dispatched through the in-session task tool. The Gate A
  prose review ran as an in-session subagent with its own session id
  (ses_030fb4f84ffe...); the S7 retro counts fourteen opencode subagent
  sessions dispatched this way across the wave.
- (c) No `opencode run` exec. The retro's packet-duty dimension records
  reviewers always pointed at staged or generated packets; no CLI
  invocation appears in the session records, and the review's
  staged-packet read path is proven by the nonce readback
  (LINNET-8362 quoted back).
- (d) Staged packet instead of escalation at a permission wall. The
  reviewer could not read the harness config from its seat; the board
  owner staged `.review/model-classes-review/` (context.md plus diff)
  and the reviewer worked from the packet, recording the config claim
  as UNVERIFIED rather than escalating to another transport.

## Failure signatures observed

One, and it was filed rather than smoothed over: the session had no
concept of Gate T itself, reported by the user. Adjudicated by the
maintainer session 2026-08-05: not a session failure - the kit's
shipped Gates section never defined T (boardkit's own S5 card was the
only place the letter appeared). Fixed in the 2026-08-05 drain: Gate T
is now defined in the shipped PROCESS.md and `boardkit doctor` warns on
gate letters the Gates section does not define
(`docs/plans/2026-08-05-feedback-drain-3.md`). Cold-read verified the
same day by a cross-harness canary (opencode, DeepSeek-V4-Flash-0731,
nonce IRIS-3382): the new definition and the failed-handout rule quoted
back verbatim.

## Verdict

All four behaviors shown on a real Gate A review of a live card, with
session date and models named. Gate T PASS.
