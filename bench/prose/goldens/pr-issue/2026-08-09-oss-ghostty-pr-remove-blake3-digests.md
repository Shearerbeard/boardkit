---
source: https://github.com/ghostty-org/ghostty/pull/13680
date: 2026-08-09
artifact: pr-description
license: GitHub user-generated content - quoted verbatim for internal eval only
note: Removal argued against what the existing format already detects, quantified encode/decode wins, honest AI-usage disclosure; 145 words, no filler.
---

Remove BLAKE3 prefix digests. Keep READY/FINISH as empty records since they're semantically important markers.

Our existing format (CRC32 per-record, declared counts, strict tag ordering requirements, etc.) already detect: accidental corruption, truncation, data omission, and duplication. 

BLAKE3 only protects against valid records being swapped or removed entirely.  It is heavy for just that, and callers can solve that anyways via their own transport (like, just use TCP). For more adversarial protection, callers can also add layers like TLS or their own alternate signing methods depending on their own threat models.

Removing the hash improves encode times by ~1.4x, decode times by ~1.3x. Time-to-READY decoding is effectively unchanged because it was such a  small package to begin with.

**AI usage:** I had it clean up the comments and the tests, but I did the blake3 removal and marker changes, and wrote the commit message myself. All reviewed.
