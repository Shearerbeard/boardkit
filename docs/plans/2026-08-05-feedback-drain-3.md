# Feedback drain 3 (2026-08-05)

Maintainer session drain of the two entries inboxed at 4e01af5, both
filed from the chore-lottery S7 wave (opencode, kimi-for-coding/k3),
plus one finding the maintainer session raised itself. All three are
accepted and fixed in this drain's commits; the fixes ride the shipped
templates, so consumers pick them up at their next contract-doc sync.

## Drained: canary-read-list-phrasing (accepted, fixed)

Source: `docs/board/retro/2026-08-04-orientation-canary.md`
(chore-lottery). The template's cold-start sentence made `deferred.md`
conditional ("when that view exists"), a brief built from it omitted
the view, and the canary abstained on the deferral question instead of
answering "none".

Fix, in `templates/PROCESS.md` (Orientation canary): the brief now
includes `deferred.md` unconditionally, and an absent view is stated in
the brief as reading "no deferred gates", so the canary answers
outright.

## Drained: cost-recovery-recipe-bar (accepted, fixed)

Source: `docs/board/retro/2026-08-04-s7-retro.md` cost appendix
(chore-lottery). The wave-close cost duty assumed a working recovery
recipe; the chore-lottery recipe (opencode export into a strict JSON
sum) broke on raw control bytes, and 12 of 14 sessions lost their
per-session figures.

Fix, in `templates/MODEL-CLASSES.md` (Wave-close cost duty): the duty
now requires proving the `REVIEW-TOOLING.md` recipe against one real
transcript before a wave depends on it, names the raw-control-bytes
failure mode, and defines the degrade path (aggregate plus per-model
figures, with the recipe failure logged as process feedback).

Related user ruling, recorded here so it is not re-litigated: the
codex-side dollar-cost gap from the S20/S7 retros is accepted as-is.
Codex runs on a codex account today, and that transport is planned to
sunset in favor of Claude plus OSS models; no kit work is owed on
codex cost capture.

## Maintainer finding: gate-vocabulary hole (fixed alongside)

Found while adjudicating the chore-lottery report that a native
opencode session had no concept of Gate T. The shipped Gates section
defined S, A, M, D, F, and U only, while boardkit's own S5 card
declared `gates: "M -> T"`; nothing validated card gate letters against
the Gates section, so the undefined token would have surfaced only as a
`dispatch-brief` refusal at dispatch time.

Fixes in this drain: the Gates section now defines Gate T (user
testing, handout-shaped, with the failed-handout rule), and `boardkit
doctor` grew a `board.gate-vocabulary` check that warns per card on any
gate letter the Gates section does not define. The contract digest
moves with the doc change; consumers re-sync as usual.
