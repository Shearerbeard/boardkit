---
source: https://github.com/tokio-rs/tokio/pull/8323
date: 2026-08-09
artifact: pr-description
license: GitHub user-generated content - quoted verbatim for internal eval only
note: Problem in the first two sentences, exact scope (three zero-length cases), solution notes the preserved BrokenPipe precedence, verification commands quoted; 124 words.
---

## Motivation

Zero-length operations on in-memory streams can currently return `Pending` when a read buffer has no data or a write buffer has no capacity. Their completion therefore depends on stream state even though they cannot transfer any bytes.

This applies to zero-capacity reads, empty writes, and vectored writes where every buffer is empty.

Closes #8321.

## Solution

Return immediately from the shared `SimplexStream` implementation for zero-capacity reads and writes. The write-side closed check remains first, preserving `BrokenPipe` for writes to a closed stream.

Add integration tests covering all three zero-length operations and the closed-stream precedence for scalar and vectored writes.

Verified with:

```console
cargo test -p tokio --test io_mem_stream --features full
cargo clippy -p tokio --test io_mem_stream --features full -- -D warnings
```
