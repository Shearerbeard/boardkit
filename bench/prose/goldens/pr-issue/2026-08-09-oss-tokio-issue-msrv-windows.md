---
source: https://github.com/tokio-rs/tokio/issues/8299
date: 2026-08-09
artifact: ticket
license: GitHub user-generated content - quoted verbatim for internal eval only
note: MSRV break pinned to the exact call, stabilization version, and cfg(windows) scope; compiler error quoted, expected behavior stated, downstream breakage cited, CI-gap hypothesis offered.
---

**Version**

tokio v1.53.0 (crates.io, published 2026-07-17)

**Platform**

Windows (x86_64-pc-windows-msvc) — the affected code is behind `cfg(windows)`; other platforms are unaffected.

**Description**

tokio 1.53.0 declares `rust-version = "1.71"` in its manifest, but `src/signal/windows/sys.rs:112` (at tag `tokio-1.53.0`) calls [`OnceLock::wait`](https://doc.rust-lang.org/std/sync/struct.OnceLock.html#method.wait):

```rust
let Ok(registry) = REGISTRY.wait().as_ref() else {
```

`OnceLock::wait` was stabilized in **Rust 1.86**, so any Windows build of tokio 1.53.0 with a toolchain in the declared-supported range `1.71..1.86` fails:

```
error[E0599]: no method named `wait` found for struct `OnceLock` in the current scope
   --> tokio-1.53.0/src/signal/windows/sys.rs:112:33
    |
112 |     let Ok(registry) = REGISTRY.wait().as_ref() else {
    |                                 ^^^^ method not found in `OnceLock<Result<Registry, i32>>`
```

I expected `cargo check` with any toolchain ≥ the declared `rust-version` to succeed; instead it fails on Windows for every toolchain below 1.86. Since the code path is `cfg(windows)`-gated, I suspect the MSRV CI job doesn't cover the Windows signal module.

Observed in the wild: this began breaking downstream MSRV CI on Windows the day 1.53.0 published (e.g. open-telemetry/opentelemetry-rust's `msrv (windows-latest)` job, verifying an example against Rust 1.75 — [failing job](https://github.com/open-telemetry/opentelemetry-rust/actions/runs/29684156505/job/88185441506), diagnosis in [open-telemetry/opentelemetry-rust#3599 (comment)](https://github.com/open-telemetry/opentelemetry-rust/pull/3599#issuecomment-5015466054)).

(Disclosure: this report was drafted with AI assistance; the source facts — the tag's manifest `rust-version`, the `sys.rs` call site, and the publish date — were verified directly against the `tokio-1.53.0` tag and crates.io.)

