# boardkit

**Status: pre-release scaffold. Nothing here is usable yet.**

boardkit is a process kit for AI-assisted software development. It packages
three practices that were proven on a live project and extracts them into a
form any repository can adopt:

1. **A gated card board.** Work is tracked as one markdown card per task with
   validated frontmatter (dependencies, serialization constraints, executor
   class, review gates). A CLI validates the board, generates index and kanban
   views, and detects drift. A gate ladder (self-check, agent review, manual
   exercise, drift audit, frontier review, user gate) controls when work may
   advance and when a human must be pulled in.
2. **The typed-holes dev flow.** Domain types are designed first (in the style
   of *Domain Modeling Made Functional*), landed as a compile-clean skeleton
   with `todo!()` bodies, adversarially design-reviewed, and only then filled
   in - often by smaller, cheaper models.
3. **Model-class delegation.** A written policy for which class of model
   handles which size of job (frontier orchestrators, mid-class writers,
   small-class explorers), with the invariant that a reviewer never shares a
   model with the author of the diff it reviews.

You can run the board from Claude Code or OpenCode. Codex support is a named
deferral, not an omission (see `EXTRACTION.md`).

The language skills the flow's writers and reviewers load (rust-*, python-*,
docs-*) are not part of this kit; they install alongside it from
[claude-skills](https://github.com/Shearerbeard/claude-skills).

See `EXTRACTION.md` for where every piece of this kit comes from and what
remains to build.
