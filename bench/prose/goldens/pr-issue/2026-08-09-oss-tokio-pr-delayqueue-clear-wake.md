---
source: https://github.com/tokio-rs/tokio/pull/8320
date: 2026-08-09
artifact: pr-description
license: GitHub user-generated content - quoted verbatim for internal eval only
note: Lost-waker bug stated precisely, contrasts with the already-correct remove path, fix scoped to the nonempty-to-empty transition, regression test described; 109 words.
---

## Motivation

`DelayQueue::poll_expired` stores the caller's waker when a future item causes it to return `Pending`. Calling `clear` then makes the queue ready to return `None`, but previously discarded the active delay without waking that task. The consumer could remain pending indefinitely.

This differs from removing the final entry, which already wakes the registered task.

## Solution

Remember whether the queue had entries before clearing it. After resetting the queue state, wake the stored task only for a nonempty-to-empty transition, matching the existing behavior of `remove`.

Add a regression test that verifies the task is asleep before `clear`, is woken by it, and observes `Ready(None)` on the next poll.
