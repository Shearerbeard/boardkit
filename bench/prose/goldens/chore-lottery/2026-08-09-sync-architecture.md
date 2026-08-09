---
source: chore-lottery@0b0330e87bf8aca2e059c633665d17603a6be13a:docs/design/sync-architecture.md
date: 2026-08-09
artifact: other
note: whole doc, in-repo golden
---

# Sync architecture: Vikunja <-> chore-lottery

How state moves between Vikunja and this service, where the seam
sits, and what would change if a second board backend ever appeared.

Sources of truth for details: the S2 spike record
(`docs/spikes/s2-vikunja-webhooks.md`) for wire behavior, and
`crates/domain/DESIGN.md` for the types named here.

## The ownership rule

The event store owns the FSM. Vikunja is a projection parents
interact with, plus an inbox for their gestures. Nothing reaches the
kid view or the lottery without passing through our event stream
first.

## The flow

```
PARENT (in Vikunja)                          KID (PWA on LAN)
      |                                            |
      | gesture: create card, drag lane,           | scan QR, view card,
      | comment, delete                            | submit photos
      v                                            v
+-------------------------------- OUR SERVICE ----------------------------------+
|                                                                               |
|  intake (webhook receiver + 30s poll backstop)         kid/parent HTTP routes |
|       |                                                                      |
|       v                                                                      |
|  +------------------+      +----------------------+      +-----------------+ |
|  | GestureValidator |----->|  Epoch event store   |----->| read projections| |
|  |                  |      |  (postgres, S3)      |      | (kid view,      | |
|  | - echo check:    |      |                      |      |  lottery pool,  | |
|  |   doer == bot?   |      |  ChoreDecider        |      |  parent UI)     | |
|  | - dedupe:        |      |  KidDecider          |      +-----------------+ |
|  |   VikunjaEventKey|      |  Lottery             |               ^         |
|  | - FSM check      |      +----------------------+               |         |
|  +------------------+               |                             |         |
|       |                             v                             |         |
|       | Accept(ChoreCommand)   +---------------------+            |         |
|       |----------------------->| command application |------------+         |
|       |                        +---------------------+                      |
|       | Revert(restore lane,   +---------------------+                      |
|       |        bot comment)    | Projector           |                      |
|       +----------------------->| VikunjaProjectionOp |                      |
|                                +---------------------+                      |
+---------------------------------------|--------------------------------------+
                                        |
----------------------------------------|--------------------------------------
              THE SEAM: VikunjaPort     |  (trait boundary)
----------------------------------------|--------------------------------------
                                        v
                              vikunja-adapter (S6)
                              - POST .../buckets/{b}/tasks  (lane moves)
                              - labels, comments, task CRUD
                              - webhook registration + HMAC verify
                                        |
                                        v
                               VIKUNJA SERVER
                          (parent-facing board UI)
```

## The seam

Everything below the line speaks Vikunja: bucket ids, task ids,
webhook payload shapes, HMAC headers. Everything above it speaks only
domain types (`Lane`, `ChoreCommand`, `VikunjaProjectionOp`,
`ParentGesture`) and never sees a Vikunja payload.

The seam is one trait (name indicative, exact shape is S6's skeleton):

```rust
trait BoardPort {
    // outbound (Projector -> adapter)
    async fn apply(&self, op: &ProjectionOp) -> Result<(), PortError>;
    // inbound (adapter -> GestureValidator)
    async fn gestures(&self, since: &Cursor) -> Result<Vec<AttributedGesture>, PortError>;
}
```

`VikunjaPort` is the first implementation. A second backend (a
different kanban tool, a flat-file mirror, a test double) implements
the same trait and nothing above the seam changes. Rules that keep
the seam honest:

- Domain types never carry Vikunja payload fields; the adapter
  translates `bucket_id` <-> `Lane` via `LaneMap` at the boundary.
- Echo suppression (`BotIdentity::is_own_write`) and idempotency
  (`VikunjaEventKey`) live ABOVE the seam: they are sync policy, not
  Vikunja mechanics. The adapter only has to report the doer and the
  raw body faithfully.
- The revert path crosses the seam as an ordinary
  `VikunjaProjectionOp::MoveToLane` + `PostComment`; the adapter
  cannot tell a revert from a projection, which is what keeps it dumb.

## Intake mechanics (from the S2 spike)

- Primary: Vikunja webhooks. Bucket moves fire `task.updated` with
  the NEW bucket in `task.buckets[0]`; there is no old-bucket field,
  so the intake compares against our stored state to detect a move.
- Backstop: 30s poll of `GET /tasks?expand=buckets` per watched
  board, reconciling drift from lost deliveries (delivery is
  at-least-once with a ~4s retry window and no outbox across
  restarts).
- Payloads are HMAC-SHA256 signed; the adapter verifies before the
  validator sees anything.

## Failure posture

| Failure | Behavior |
|---|---|
| Webhook lost / service down | Poll backstop converges within 30s |
| Duplicate delivery | `VikunjaEventKey` dedupe: no-op |
| Our own write echoes back | Dropped at the validator (`doer == bot`) |
| Parent makes an illegal move | API revert to the FSM-legal lane + explanatory bot comment; the revert is itself an event |
| Vikunja unreachable | Projection retries; intake continues to accept kid/parent UI reads from our own store |
