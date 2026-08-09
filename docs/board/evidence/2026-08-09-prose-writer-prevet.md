# 2026-08-09 prose writer pre-vet

Transport pre-flight for the prose lane's first consumer run (the
writer mini-eval). One throwaway nonce-readback run per seat, caller
owning every deadline (240s per call; this host has no timeout
binary).

| Seat | Transport | Result |
|------|-----------|--------|
| gemini-3.1-pro | opencode `-m opencode/gemini-3.1-pro` (Zen) | FAIL: CreditsError, insufficient Zen workspace balance |
| gemini-3.1-pro (swap) | opencode `-m google/gemini-3.1-pro-preview` | PASS, nonce read back |
| gpt-5.5 | `codex exec --sandbox read-only -m gpt-5.5` | PASS, run header confirms model |
| gpt-5.6-sol | `codex exec --sandbox read-only` (default model) | PASS, run header confirms model |
| deepseek-v4-pro | opencode `-m opencode-go/deepseek-v4-pro` | PASS, nonce read back |
| deepseek-v4-flash | opencode `-m opencode-go/deepseek-v4-flash` | PASS, nonce read back |
| claude-opus-5 (verbosity control) | opencode `-m anthropic/claude-opus-5` via 127.0.0.1:3456 | PASS; proxy answered HTTP 200 first |
| k3 (grader-side vertical QC) | opencode `-m kimi-for-coding/k3` | PASS, nonce read back |

Notes:

- The gemini writer seat runs on `google/gemini-3.1-pro-preview` until
  the OpenCode Zen workspace is funded; the Zen route stays recorded
  here as the preferred ID.
- The anthropic proxy lives inside a running opencode process and dies
  with it. Re-curl `http://127.0.0.1:3456/v1/models` before any run
  that uses the Opus control.
- k3 is grader-side and never joins the writer roster
  (`bench/README.md`, hidden-material rules).
