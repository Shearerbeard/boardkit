---
source: https://github.com/tokio-rs/tokio/issues/8321
date: 2026-08-09
artifact: ticket
license: GitHub user-generated content - quoted verbatim for internal eval only
note: Version, minimal repro with exact rev, expected vs actual, correctness argued from AsyncRead/AsyncWrite docs and prior fixes, narrow fix proposed; the report the fix PR (8323) was built from.
---

**Version**

`tokio v1.53.1` from current master (`460dc16d19b020a5601c118d167c2252c3729a91`).

**Description**

Zero-length operations on `DuplexStream` and `SimplexStream` can return `Pending`:

- a zero-capacity read when no data is available
- an empty write when the internal buffer is full
- an all-empty vectored write when the internal buffer is full

The same operations return `Ready` when data or buffer capacity happens to be available. Their completion therefore depends on stream state even though they cannot transfer any bytes. Both public stream types use the same internal `SimplexStream`, so the three cases have the same underlying cause.

**Reproduction**

```toml
[dependencies]
futures-util = "0.3"
tokio = { git = "https://github.com/tokio-rs/tokio", rev = "460dc16d19b020a5601c118d167c2252c3729a91", features = ["io-util", "macros", "rt"] }
```

```rust
use futures_util::FutureExt;
use std::io::IoSlice;
use tokio::io::{duplex, AsyncReadExt, AsyncWriteExt};

#[tokio::main(flavor = "current_thread")]
async fn main() {
    let (mut reader, _peer) = duplex(1);
    let mut empty = [];
    dbg!(reader.read(&mut empty).now_or_never());

    let (mut writer, _peer) = duplex(1);
    writer.write_all(b"x").await.unwrap();
    dbg!(writer.write(&[]).now_or_never());

    let (mut writer, _peer) = duplex(1);
    writer.write_all(b"x").await.unwrap();
    let bufs = [IoSlice::new(&[]), IoSlice::new(&[])];
    dbg!(writer.write_vectored(&bufs).now_or_never());
}
```

All three calls print `None`. I expected `Some(Ok(0))` in each case. These are first-poll results rather than timing-dependent timeouts. Awaiting any of the operations waits until another task changes the otherwise irrelevant stream state.

**Why this appears incorrect**

The `AsyncRead` documentation describes a zero-capacity buffer as a normal zero-byte `Ready(Ok(()))` outcome. This is also consistent with the empty `File` read fix in #7133 and #7139 and the zero-capacity handling added to `Chain` in #8251.

`AsyncWrite::poll_write_vectored` is documented to behave like `poll_write` over the concatenated buffers. The concatenation of all-empty buffers is itself empty.

The [internal methods](https://github.com/tokio-rs/tokio/blob/460dc16d19b020a5601c118d167c2252c3729a91/tokio/src/io/util/mem.rs#L248-L307) currently check data or buffer availability before checking whether the operation has zero capacity.

A narrow fix would return immediately for zero-capacity reads and writes. For writes, the existing closed-state check can remain first to preserve `BrokenPipe` precedence. Keeping the early returns in the internal methods also preserves the existing tracing and cooperative-budget wrappers.
