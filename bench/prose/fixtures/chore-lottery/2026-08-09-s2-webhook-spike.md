---
source: chore-lottery@0b0330e87bf8aca2e059c633665d17603a6be13a:docs/spikes/s2-vikunja-webhooks.md
date: 2026-08-09
artifact: doc-draft
note: webhook spike log, frozen as fresh-write source
---

# S2 spike: Vikunja webhook bucket-move observability

Decision record for card S2. Run against the seeded dev stack
(Vikunja 2.4.0, `chore-machinery reset` fixture) on 2026-08-02.

## TL;DR decision

**Hybrid: webhooks as the primary intake, with a poll backstop.** A
bucket move fires `task.updated`, and the payload's `task.buckets`
array carries the new bucket. But the same event fires for a title
edit, the payload carries no old bucket and no changed-fields diff, and
Vikunja has no persistent outbox across restarts. S6 will subscribe to
`task.updated` and `task.deleted`, read the current bucket from
`task.buckets[0]`, compare it to stored state to detect a move, and run
a 30s `GET /tasks?expand=buckets` poll as a backstop for missed
deliveries. Echo suppression keys off `data.doer.id` matched against the
bot account's user id.

## How to reproduce

The capture helper lives at
`machinery/src/chore_machinery/webhook_capture.py`. It appends every
incoming POST (headers plus body) as one JSON line to a file.

Vikunja 2.4.0 ships an SSRF filter
(`utils.NewSSRFSafeHTTPClient`; source-code inference, not reproducible
via curl, but consistent with the observed delivery failures to RFC1918
targets) that blocks delivery to RFC1918 addresses, so a host listener
on `127.0.0.1` is rejected. Run the capture inside a container on the
compose network and relax the filter for the dev stack:

```sh
# 1. Start a capture container on the compose network.
docker run -d --name capture --network chore-lottery_default \
  -v "$PWD/machinery/src/chore_machinery/webhook_capture.py:/capture.py" \
  -e WEBHOOK_PORT=18080 -e WEBHOOK_OUT=/tmp/hooks.jsonl \
  python:3.12-slim python /capture.py

# 2. Relax the SSRF filter for the dev stack (throwaway, localhost only).
cat > /tmp/override.yml <<'EOF'
services:
  vikunja:
    environment:
      VIKUNJA_OUTGOINGREQUESTS_ALLOWNONROUTABLEIPS: "true"
EOF
docker compose -f docker-compose.yml -f /tmp/override.yml up -d vikunja

# 3. Register a webhook on the Backyard project (id 2) pointing at the
#    capture container. PUT creates; POST is rejected with 405.
TOKEN=$(curl -sS http://localhost:34560/api/v1/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"parent-one","password":"dev-pass-one"}' \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["token"])')
curl -sS -X PUT http://localhost:34560/api/v1/projects/2/webhooks \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"target_url":"http://capture:18080/hook","events":["task.created","task.updated","task.deleted","task.comment.created","task.comment.edited","task.comment.deleted"]}'
```

The webhook target URL uses the container DNS name `capture`, not
`host.docker.internal`. Webhook IDs are DB-persisted; they survive a
`docker compose up -d vikunja` recreate (verified: webhook id 3 was
still listed after the recreate above).

## The bucket-move endpoint

A bucket move is NOT `POST /tasks/{id}` with a `bucket_id` field. The
`bucket_id` field on `Task` is `xorm:"-"` (not persisted; source-code
inference, not reproducible via curl, but consistent with the
join-table probe below); setting it on a task update echoes the input
back in the response but writes nothing to the `task_buckets` join
table. Confirmed against the Postgres store:

```
$ docker exec chore-lottery-postgres-1 psql -U vikunja -d vikunja -t -c \
    "select task_id, bucket_id from task_buckets where task_id=1;"
       1 |        10
# after POST /tasks/1 with {"bucket_id":12}:
       1 |        10          # unchanged
```

The real move endpoint is
`POST /projects/{project}/views/{view}/buckets/{bucket}/tasks` with
body `{"task_id": <id>}`. The bucket in the URL path is the target.
This updates the `task_buckets` row and dispatches the event:

```sh
# Move task 1 from Proposed (10) to Ready (12) on the kanban view 12.
curl -sS -X POST \
  "http://localhost:34560/api/v1/projects/2/views/12/buckets/12/tasks" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"task_id":1}'
```

## Available events

`GET /api/v1/webhooks/events` returns 19 event names. The task-relevant
subset:

- `task.created`
- `task.updated`
- `task.deleted`
- `task.comment.created`, `task.comment.edited`, `task.comment.deleted`
- `task.assignee.created`, `task.assignee.deleted`
- `task.attachment.created`, `task.attachment.deleted`
- `task.relation.created`, `task.relation.deleted`

There is no `task.bucket.moved` or `task.moved` event. A bucket move
fires `task.updated`, the same event as a title edit.

## Question 1: does a bucket move emit a webhook event?

Yes. Moving task 1 from `Proposed` (bucket 10) to `Ready` (bucket 12)
via the kanban endpoint fires one `task.updated` delivery. Captured
payload (trimmed to the task and doer; the full payload includes the
project and its views):

```json
{
  "event_name": "task.updated",
  "time": "2026-08-02T17:51:33.88383118Z",
  "data": {
    "doer": {"id": 1, "username": "parent-one"},
    "task": {
      "id": 1,
      "title": "rake leaves",
      "project_id": 2,
      "bucket_id": 0,
      "buckets": [{"id": 12, "title": "Ready", "project_view_id": 12}],
      "updated": "2026-08-02T17:51:33Z"
    }
  }
}
```

The new bucket is in `task.buckets[0]` (`Ready`, id 12). The
`task.bucket_id` field is `0` in every payload: it is `xorm:"-"` on the
`Task` struct (source-code inference, not reproducible via curl, but
consistent with every captured payload showing `bucket_id: 0`) and is
not enriched in the event-dispatch path. Read the bucket from
`task.buckets`, not `task.bucket_id`. The payload carries no old
bucket, so the source lane is not recoverable from the payload alone;
intake must compare against stored state.

## Question 2: can a move be distinguished from a title edit?

Not from the event name, and not from a diff. Editing the title of
task 1 with `POST /api/v1/tasks/1` `{"title":"rake leaves v2"}` fires
the same `task.updated` event. Captured (task 1 was in `Ready` at the
time):

```json
{
  "event_name": "task.updated",
  "data": {
    "doer": {"id": 1, "username": "parent-one"},
    "task": {"id": 1, "title": "rake leaves v2", "bucket_id": 0,
             "buckets": [{"id": 12, "title": "Ready"}]}
  }
}
```

Both events carry `event_name: "task.updated"`. Neither carries a
changed-fields list. The `buckets` field shows the current bucket in
both cases. Intake can detect a move only by comparing the payload's
`buckets[0]` to its stored bucket for that task: if they differ, the
task moved; if they match, the update was an edit (or a no-op move).
A comment create is distinguishable: it fires `task.comment.created`
with the comment body, a separate event name.

## Question 3: does the payload identify the acting user?

Yes. Every payload carries `data.doer` with `id` and `username`. For
parent-one the doer is `{"id": 1, "username": "parent-one"}`. This is
sufficient for echo suppression: S6's bot will use its own API token,
and intake drops any webhook whose `data.doer.id` equals the bot
account's user id. The doer is set from the auth that made the write
(`doerFromAuth`; source-code inference, not reproducible via curl, but
consistent with the doer matching the authenticated user on every
captured write), so a bot-originated write names the bot, not the
parent.

## Question 4: redelivery, ordering, and delivery semantics

At-least-once with bounded retries. Watermill wraps the delivery
handler in `middleware.Retry` with `MaxRetries: 5`,
`InitialInterval: 100ms`, `Multiplier: 2` (the constant names are
source-code inference, not reproducible via curl; the retry count and
timing below are observed behavior). With a capture endpoint returning
HTTP 500, Vikunja retried six times total (the initial attempt plus
five retries) over roughly four seconds, then moved the message to the
poison queue. The poison payload is logged in full, which is how the
first payloads in this spike were captured before the SSRF filter was
relaxed.

Ordering is preserved within one Vikunja process: the in-process
`gochannel` pubsub delivers synchronously. Two rapid moves on task 1
(Ready, then Done) produced two deliveries in the order issued, 18 ms
apart, each with its own `task.updated` timestamp. There is no
persistent outbox across restarts: a delivery in flight when the
container stops is lost. Intake must be idempotent and treat the
webhook as the primary source, with the poll backstop closing any gap
from a lost delivery.

### Outbox experiment: no redelivery after restart

Reproduction, run 2026-08-02 against the seeded dev stack with webhook
id 6 registered to `http://capture:18080/hook`:

```sh
# 1. Stop the capture listener so deliveries fail (listener DOWN).
docker stop capture

# 2. Move task 1 from Proposed (10) to Ready (12) with the listener down.
TOKEN=$(curl -sS http://localhost:34560/api/v1/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"parent-one","password":"dev-pass-one"}' \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["token"])')
curl -sS -X POST \
  "http://localhost:34560/api/v1/projects/2/views/12/buckets/12/tasks" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"task_id":1}'

# 3. Wait 2s for the in-memory retry loop to fail, then restart vikunja
#    inside the ~4s retry window.
sleep 2
docker compose restart vikunja

# 4. Wait for healthy, then bring the capture listener back up.
#    (loop on: docker inspect -f '{{.State.Health.Status}}' chore-lottery-vikunja-1)
docker start capture

# 5. Wait 30s for any redelivery, then check the capture file.
sleep 30
docker exec capture sh -c 'wc -l < /tmp/hooks.jsonl'
```

Observed output:

```
0
```

The capture file stayed empty for 30s after the listener came back up.
The in-flight delivery was lost when vikunja restarted; the in-memory
`gochannel` pubsub does not persist pending messages to the database,
and no redelivery arrived. Claim confirmed: there is no persistent
outbox across restarts. The webhook itself survived the restart (see
the persistence probe below); only the in-flight message was dropped.

Delivery headers (no secret set):

```
User-Agent: Vikunja/v2.4.0
Content-Type: application/json
Accept-Encoding: gzip
```

With a `secret` on the webhook, Vikunja adds
`X-Vikunja-Signature: <hex hmac-sha256 of the body>` (verified against
a recomputed HMAC). S6 should set a secret and verify the signature on
intake. The one-liner used to recompute the HMAC over the raw body and
compare it to the header (run inside the capture container, which has
the raw body on disk):

```sh
docker exec capture python3 -c '
import hmac, hashlib, json
for line in open("/tmp/hooks.jsonl"):
    r = json.loads(line)
    calc = hmac.new(b"spike-secret-s2", r["body_raw"].encode(), hashlib.sha256).hexdigest()
    sig = r["headers"].get("X-Vikunja-Signature", "")
    print("MATCH" if hmac.compare_digest(sig, calc) else "MISMATCH")
'
```

Observed output against webhook id 6 (secret `spike-secret-s2`):

```
MATCH
```

The signature is the hex HMAC-SHA256 of the raw request body, keyed by
the webhook `secret`. S6 must hash the exact bytes it received, before
any JSON re-serialization.

## Frontend and persistence

The Vikunja frontend exposes webhook management at the route
`project.settings.webhooks` (found in the bundled
`/assets/index-*.js` as `name:`project.settings.webhooks``). A parent
can create and list webhooks from the project settings UI; the API is
the same one used above.

Webhooks are DB rows in the `webhooks` table. They survive a
`docker compose up -d vikunja` container recreate (confirmed: webhook
id 3 was still listed after the recreate). They persist because the
Postgres volume persists, not because of any in-memory state.

### Persistence probe: webhook survives force-recreate

Reproduction, run 2026-08-02 against webhook id 6:

```sh
TOKEN=$(curl -sS http://localhost:34560/api/v1/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"parent-one","password":"dev-pass-one"}' \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["token"])')

echo "=== BEFORE force-recreate: GET /projects/2/webhooks ==="
curl -sS http://localhost:34560/api/v1/projects/2/webhooks \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

docker compose up -d --force-recreate vikunja
# wait for healthy: docker inspect -f '{{.State.Health.Status}}' chore-lottery-vikunja-1

echo "=== AFTER force-recreate: GET /projects/2/webhooks ==="
curl -sS http://localhost:34560/api/v1/projects/2/webhooks \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

Observed output (trimmed to the identifying fields):

```
=== BEFORE force-recreate: GET /projects/2/webhooks ===
[
    {
        "id": 6,
        "target_url": "http://capture:18080/hook",
        "events": ["task.created", "task.updated", "task.deleted",
                   "task.comment.created", "task.comment.edited",
                   "task.comment.deleted"],
        "project_id": 2,
        "created": "2026-08-02T17:57:18Z"
    }
]
=== AFTER force-recreate: GET /projects/2/webhooks ===
[
    {
        "id": 6,
        "target_url": "http://capture:18080/hook",
        "events": ["task.created", "task.updated", "task.deleted",
                   "task.comment.created", "task.comment.edited",
                   "task.comment.deleted"],
        "project_id": 2,
        "created": "2026-08-02T17:57:18Z"
    }
]
```

Webhook id 6 was still listed after `--force-recreate`, with the same
`id`, `target_url`, `events`, and `created` timestamp. The webhook
configuration is durable; only in-flight deliveries are not (see the
outbox experiment above).

## Decision: hybrid (webhooks primary, poll backstop)

Pure polling (a 15-30s diff of `GET /tasks?expand=buckets`) works but
adds latency to every parent gesture, including the lane moves that
drive the lottery. Pure webhooks are fast but have two gaps. First, a
lost delivery (container restart, network blip) is gone: there is no
persistent outbox. Second, the payload cannot name the old bucket, so
intake must hold prior state to detect a move rather than rely on the
event alone.

The hybrid uses each side for what it does well. S6 subscribes to
`task.updated` and `task.deleted` as the primary intake. On each
`task.updated`, it reads the current bucket from `task.buckets[0]`
and compares it to its stored bucket for that task, recording a move
only when they differ. Echo suppression drops any webhook whose
`data.doer.id` matches the bot account before the compare. A 30s
full-board `GET /tasks?expand=buckets` poll runs as a backstop: it
catches any move whose webhook was lost and self-heals drift between
the stored state and Vikunja. Move latency stays at webhook speed
(sub-second on the dev stack), and the system degrades to poll-only
behavior if delivery breaks.

## Dead ends

- `host.docker.internal` and any RFC1918 target are rejected by
  Vikunja's SSRF filter. The first capture attempts poisoned the
  delivery queue; the payloads were recoverable from the Vikunja error
  log, but a clean capture needed the filter relaxed and the listener
  moved onto the compose network.
- `POST /projects/{id}/webhooks` returns 405; creation is `PUT`.
- `POST /tasks/{id}` with `{"bucket_id": N}` does not move the bucket.
  The `bucket_id` field is `xorm:"-"` and is not persisted (source-code
  inference; the join-table probe above is the reproducible evidence);
  the response echoes the input but the `task_buckets` join table is
  unchanged. Use the kanban endpoint
  `POST /projects/{p}/views/{v}/buckets/{b}/tasks` instead.
- `swagger.json` / `openapi.json` are the SPA HTML at the
  root, not JSON. The event list comes from
  `GET /api/v1/webhooks/events`.
