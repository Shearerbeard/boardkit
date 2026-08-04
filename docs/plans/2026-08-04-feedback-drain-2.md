# Feedback drain: two inbox entries vetted and prioritized (2026-08-04)

Status: triaged 2026-08-04 by the maintainer session, same day the
entries landed. Queue entries deleted per the inbox contract; cards S8
and S9 on this repo's own board carry the accepted work.

## Verification notes

- Board-worktree colocation: both cited failures verified against
  today's unwind evidence rather than the entry's claims alone. The
  S59 branch-state split is the same contradiction class the clone
  deletion removed (thirteen statuses wrong across `-s59`/`-s73`,
  proof in `2026-08-04-board-unwind.md`); the gitignored `reviews/`
  fragility was independently flagged by the consolidation audit on
  the aura board the same day. The kit does reproduce colocation:
  `config.py` resolves `cards_dir` and the review `output_dir`
  relative to the consumer's toml. The proposed machine-dir pattern
  already runs in the field - `aura-session-docs/boards/<name>` is
  exactly that shape and survived today's consolidation well.
- Model-class examples drift: `MODEL-CLASSES.md` self-dates its
  examples to 2026-07-18 and still names MiniMax M3 as the explorer
  illustration while the fleet's live pins moved (both opencode
  explore and general run a DeepSeek flash model today). Propagation
  verified: the kit template and the dogfood copy are byte-identical,
  and the consumer copy was too until its 2026-08-04 refresh - a
  consumer that syncs verbatim inherits the kit's dated examples. The
  classification gap is real: the delegation-inventory step asks
  which providers are in play (added 2026-08-04) but nothing asks
  where the session's own model sits in the taxonomy, and the
  worked-examples lists are the only classification guide shipped.

## Priority 2 - accepted

### D1. Board-root portability (card S8)

From `2026-08-04 board-worktree-colocation` (terminalbench-aura via a
claude-code session). Accepted. The shipped docs document the
machine-dir board-root pattern as a first-class option (the init
scaffold already works from any directory); review-packet references
either resolve from any checkout or fail detectably instead of
dangling in fresh worktrees. Weigh, do not assume, a change to the `reviews/`
gitignore default: the aura lineage treats packets as ephemeral by
choice, so the fix may be a documented choice rather than a new
default. Intersects terminalbench S80: if that board adopts the kit,
it should adopt the portable shape, not the colocated one.

### D2. Model-class example freshness and session classification (card S9)

From `2026-08-04 model-class-examples-drift` (chore-lottery via a
Kimi-K3 opencode board-owner session). Accepted in two parts: the
delegation-inventory step gains a classify-the-session-model line
beside the provider question, resolving against the taxonomy's class
definitions rather than the example lists; the worked examples refresh
and the template states what to do when a model is absent from them
(classify by capability description, record the call in the session
log). Rejected alternative: auto-refreshing examples from live pins
was declined - the no-model-ids rule exists because pins move, and
examples that chase pins would churn every consumer diff.

## Sequencing

S8 and S9 are independent of each other and of the S1-S7 wave. S9
touches the same template text as S1 (inventory step) so they
serialize; S8 is docs plus review_packet changes and stands alone.
