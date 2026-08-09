---
source: https://github.com/zed-industries/zed/pull/62220
date: 2026-08-09
artifact: pr-description
license: GitHub user-generated content - quoted verbatim for internal eval only
note: Root cause of the measurement error and its user-visible impact up front; fix plus a regression test that fails against the old implementation, under 200 words.
---

`ThreadedDispatcher::run_until` - the completion mechanism under `BenchAppContext` async task benchmarks (`bench_task` / `bench_batched_task`, added in #62180) - drained the entire main queue before checking its readiness predicate. Main-thread work that re-queues itself (an idle-time sweep, a polling loop) keeps the queue non-empty until it finishes every iteration, so a task benchmark's measured interval silently extended past the awaited task's completion until all such deferred work settled. Benchmarks of UI workloads that schedule follow-up idle work could report several times their true completion latency.

This changes `run_until` to step main-thread runnables one at a time and check readiness before each, so it returns at the completion it awaits rather than at queue quiescence, making async task benchmarks more accurate. The regression test spawns a task that re-queues itself 10,000 times plus a one-shot completion task, and asserts `run_until` returns without draining the re-queued work; it fails against the previous drain-first implementation.

Release Notes:

- N/A

