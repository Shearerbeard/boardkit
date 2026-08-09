---
source: https://github.com/zed-industries/zed/pull/62335
date: 2026-08-09
artifact: pr-description
license: GitHub user-generated content - quoted verbatim for internal eval only
note: Mechanism-level problem statement in two sentences, edge case (pending mouse press) called out, regression coverage plus exact test commands and release note.
---

GPUI's declarative hover styles are recomputed from the current frame's hit test, but `on_hover` listeners previously updated only in response to mouse movement or the pointer leaving the window. When layout moved a different element beneath a stationary pointer, the new element looked hovered without receiving its hover-start callback.

This change reconciles each hover listener against the current hit test during painting and defers transitions until after the paint cycle, when application callbacks can safely update state. Reconciliation pauses while a mouse press is pending so hover-only controls remain mounted between mouse-down and mouse-up.

The regression coverage moves an element beneath and away from a stationary pointer and verifies both transitions. It also verifies that repainting during a stationary mouse press does not generate a spurious hover exit.

Testing:

- `cargo test -p gpui --lib`
- `cargo fmt --check -p gpui`
- `cargo check -p delta --bin delta` with Delta temporarily patched to the local GPUI checkout

Release Notes:

- Fixed hover interactions not updating when interface elements move beneath a stationary pointer.

