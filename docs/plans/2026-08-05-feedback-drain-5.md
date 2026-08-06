# Feedback drain 5 (2026-08-05)

Maintainer session drain of the two entries inboxed after 089d17c, both
filed from the Epoch board sessions (claude-code, fable-5) running the
kit's review machinery in anger for the first time: a five-round
adversarial review cycle and the first generated review packet a human
actually worked from. Both are accepted and feature-sized, becoming
cards S14 and S15 on this board.

## Drained: review-cycle-convergence-rule (accepted, carded S14)

Source: claude-skills
`feedback/2026-08-05-claude-code-review-loop-protection/process-feedback.md`.
A plan artifact took five adversarial review rounds to PASS (finding
counts 7, 5, 6, 1, 0; ~354k reviewer tokens) and nothing in the kit
bounded the cycle. The fix-commit re-review duty (PROCESS.md, Gate A)
says a fresh review must cover fixes but never says when a cycle ends,
so an unattended board owner either loops or stops silently. The
session improvised a convergence instruction in the reviewer prompt
(verify dispositions, re-raise only failed ones, no scope expansion
past accepted ground) and a backstop (a FAIL that is all new scope
after several rounds goes to the user with the disagreement on the
ledger). The user flagged the loop risk mid-run.

Disposition: the improvised discipline worked and belongs in the kit,
not in one session's prompt. Card S14 carries it: the PROCESS.md
template (and this board's copy) gains convergence rules beside the
re-review duty plus a round bound with a named escalation, the
dispatch brief carries the discipline into the reviewer prompt, and
the review ledger records per-round finding counts and cumulative
spend so the cycle's shape is auditable.

## Drained: review-packet-human-guide (accepted, carded S15)

Source: claude-skills
`feedback/2026-08-05-claude-code-review-packet-guide/process-feedback.md`.
The E1 review packet came out as commit stats plus hunk coordinates,
and the board owner hand-wrote the 80/20 review guide the
pre-extraction tooling used to provide. The user confirmed both
regressions: packets used to suggest review order, and they surfaced
the type design prominently; neither survived the port into
`review_packet.py`.

Disposition: a packet a human cannot work from fails its purpose, so
the regression is kit-owned. Card S15 restores the human side of
the packet: REVIEW.md leads with a ranked review guide (generated
churn-supersession flags where mechanical, author-supplied otherwise),
a card with a typed-holes design record gets it linked near the packet
top, and log-like content renders its diff and file references as
relative markdown links so editors that follow them (the user reviews
in nvim/LazyVim) jump straight from a log line to the diff it names.
