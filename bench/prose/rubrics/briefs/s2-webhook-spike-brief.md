# Defect brief: s2-webhook-spike (fresh-write source)

Fixture: `bench/prose/fixtures/chore-lottery/2026-08-09-s2-webhook-spike.md`
Source: `chore-lottery@0b0330e:docs/spikes/s2-vikunja-webhooks.md`
(2,100 words). Line numbers below refer to the source doc; the frozen
fixture body starts 7 lines later. This fixture is raw evidence plus
an embedded reference answer, staged for fresh-write tasks, not a
defect specimen for cleanup.

## Confirmed properties

1. Raw evidence present as hypothesized: captured webhook payloads
   (117-133, 151-160), curl repros for capture setup and bucket moves
   (32-57, 86-92), a psql probe of the `task_buckets` join table
   (73-79), the outbox restart experiment with observed output
   (204-241), the HMAC recompute one-liner with its MATCH output
   (265-280), and the persistence probe (299-353).
2. The doc carries its own decision twice: a "TL;DR decision" section
   (6-17) and a full "Decision: hybrid (webhooks primary, poll
   backstop)" section (355-375) restating it with rationale.
3. Observation, not graded as a defect: the disclaimer "source-code
   inference, not reproducible via curl, but consistent with..."
   recurs five times (machine-counted after unwrapping line breaks).
   Honest evidence-marking, but a tic a fresh write need not copy.

## Rejected or unconfirmed hypotheses

No defect hypotheses were assigned to this fixture and the full read
surfaced none worth grading. The doc does what a spike record should.

## What a good fresh-write does

Given the evidence sections only, a candidate decision record:

1. Lands on hybrid intake, webhooks primary with a poll backstop, and
   grounds it in the two gaps the evidence shows: the payload carries
   no old bucket, and no outbox survives a restart.
2. Reads the bucket from `task.buckets[0]`, never `task.bucket_id`,
   citing the `bucket_id: 0` payloads.
3. Detects a move by comparing the payload bucket to stored state,
   since a move and a title edit fire the same `task.updated` event.
4. Keys echo suppression on `data.doer.id` against the bot account's
   user id.
5. Verifies the `X-Vikunja-Signature` HMAC-SHA256 over the raw body
   bytes before intake trusts a payload.
6. Treats delivery as at-least-once with loss on restart, so intake is
   idempotent and the poll closes any gap.

## Reference answer and staging excisions

The reference answer is the TL;DR (6-17) plus the Decision section
(355-375): hybrid intake; subscribe to `task.updated` and
`task.deleted`; bucket from `task.buckets[0]`; move detection by
compare-to-stored-state; a 30s `GET /tasks?expand=buckets` poll
backstop; echo suppression on `data.doer.id`.

A staging run must excise before the candidate sees the doc:

- "## TL;DR decision", lines 6-17, whole section.
- "## Decision: hybrid (webhooks primary, poll backstop)", lines
  355-375, whole section.
- Residual leaks inside evidence sections, each a sentence stating
  part of the answer: the Question 4 closer (200-202, "Intake must be
  idempotent and treat the webhook as the primary source, with the
  poll backstop closing any gap"); the Question 1 closer (139-142,
  compare against stored state); the Question 3 prescription (174-176,
  drop webhooks whose `data.doer.id` equals the bot's); the HMAC
  prescriptions (260-261 "S6 should set a secret and verify the
  signature" and 283-284 "S6 must hash the exact bytes it received").

The payload captures, repro scripts, and observed outputs above those
sentences stay; they are the evidence the answer must be derived from.
A grader scoring an unexcised run must discount points 1, 3, 4, and 5
above as potentially copied.
