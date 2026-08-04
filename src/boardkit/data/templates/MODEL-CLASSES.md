# Model classes

<!-- boardkit-contract: v2 -->

This is the delegation policy: which class of model runs which kind of
board work, and the invariants that hold regardless of which vendor or
harness is in play. Classes are the stable unit here. Named models drift
month to month; the class each one belongs to is what the board reasons
about.

The concrete model names in this file are dated worked examples, current as
of the examples date below. Treat them as illustrations of the
class, not as a pin. Update the examples when the models you actually use
change; the class definitions below them should rarely need to.

Examples last updated: 2026-07-18. Bump this date whenever you touch a
model example.

## Capability taxonomy

Two axes decide who gets a piece of work, and they are independent.
Class is how much capability a model brings and what it costs; that is
the axis a card's `executor` field encodes. Family is what a model is
comparatively good at; that is the axis reviewer selection turns on.
Model families are not interchangeable: they differ in what they are
good at, and picking one by price alone routes prose to a code model or
a diff to a model that reads it as prose.

The routing rule follows the shape of the artifact, not the topic:

- Language-shaped artifacts - plans, prose, specs, architecture
  documents, product and marketing material - go to the family strongest
  at natural language. What is being bought there is judgment about
  whether an argument holds and whether the document says what it means.
- Code diffs go to a code-specialized reviewer: a family tuned for
  reading diffs and reasoning about program behavior.
- The standing adversarial default, and the fallback after a stalled or
  failed delegation, is a frontier model from a family other than the
  one that authored the work under review.

This template names no vendors and no model ids, because the families a
repo has installed differ per repo and drift faster than these rules do.
Fill in the family-to-model bindings, and the harness transport each one
is reached through, in `REVIEW-TOOLING.md`.

## Class taxonomy

Frontier orchestrator class: the strongest available general-purpose
models. This class owns board-owner sessions and Gate F reviews, where the
cost of a mistake is highest and the review needs to catch what a smart-
class reviewer would miss. Worked examples as of this writing: Claude
Opus or Fable, GPT-5.x.

Smart writer/reviewer class: strong enough to author or review a
non-trivial card without supervision, but priced for volume rather than
reserved for the hardest calls. This class owns cards marked
`executor: smart` and Gate A reviews. Worked examples as of this writing:
GLM-5.2, Kimi K2.7-code.

Small explorer class: fast and cheap. It handles search and drift audits,
and takes any card marked `executor: any`. This class should never author
a card whose acceptance criteria assume smart-class judgment. Worked
example as of this writing: MiniMax M3.

## Executor field mapping

A card's `executor` frontmatter field names the minimum class allowed to
own it:

- `smart`: only the frontier orchestrator or smart writer/reviewer classes
  may take this card. Use it for cards whose acceptance criteria need
  judgment calls, not just mechanical execution.
- `any`: the small explorer class may take this card too, alongside the
  two stronger classes. Use it for search, drift audits, and mechanical
  or well-specified work.

Reviewer assignment is separate from this field. Gate A reviewer choice
follows the reviewer-differs-from-author invariant below, not the card's
`executor` value.

## Invariants

- The reviewer-differs-from-author invariant: a Gate A or Gate F reviewer's
  model must never be the same model that authored the diff under review.
  For a multi-commit range, the reviewer must differ from every model that
  wrote any commit in it. This holds regardless of class; a smart-class
  model may not review its own smart-class output, and a frontier model
  may not review its own frontier output.
- The adversarial-review procedure itself is stated once, in
  `REVIEW-TOOLING.md`: fresh reviewer context, numbered findings each
  carrying its own disposition, an explicit verdict line, an empty return
  or a missing verdict read as a failed delegation rather than a pass,
  and the stall protocol. That procedure names no models and holds
  whatever families a repo has installed, so this file does not restate
  it.
- Gate A routing follows what the artifact is judged on: a code diff goes
  to the `code-review` role, a plan, spec, or prose artifact goes to the
  `prose-review` role. A card carries no field recording which kind it
  produced, so the board owner decides at the gate; a dispatch brief prints
  both routes rather than guessing on the board owner's behalf.
- Gate D, the drift audit, runs on a lower-cost model in the board owner's
  own harness. It samples anchors and claims against the current repo
  state and needs no review skill loaded, so there is no reason to spend
  smart-class or frontier-class budget on it.

## Reviewer pre-vet checklist

Take this inventory at session start, before planning a wave or
promoting a card, not at the gate the reviewer serves. Read the
harness's own agent configuration, record which executors and reviewers
exist and what model each is pinned to, and confirm reachability for
anything the plan will depend on. The pins are a constraint on the plan:
the reviewer-differs-from-author invariant above decides which executor
may author which card and which reviewer can close its gate, so a wave
planned without knowing the pins can allocate work that no available
reviewer is allowed to review. Discovering that at the gate means the
work is already written by the wrong hand.

Before a wave or gate depends on an external reviewer, the board owner
pre-vets it:

- Reachability and auth: the reviewer's binary, server, or API is reachable
  and authenticated right now, not merely configured.
- Read probe under the staging contract: the pre-vet probe is shaped like
  the dispatch, not a bare echo. Stage one small file where the transport's
  `staging` contract says the packet will sit (`boardkit resolve-route
  <role>` prints it), and have the reviewer read it back - a nonce from the
  file's content, not from the prompt. An echo proves the model answers; it
  proves nothing about whether the reviewer can read the material, and a
  reviewer that cannot read the packet fails as silence, not as an error.
- Usage headroom: the reviewer has budget or quota left for this review. An
  exhausted cap discovered mid-gate is worse than catching it before
  dispatch.
- Permission profile: the reviewer can actually read the material it is
  reviewing. A reviewer whose bash allowlist blocks reading the diff it was
  asked to review is a documented failure mode, not a hypothetical one:
  point reviewers at a pre-generated review packet from `boardkit
  review-packet <id>` instead of assuming they can run `git diff`
  themselves.
- Model identity: verify the configured model actually is what the agent
  or persona name implies. Agent names drift out of sync with the model
  pinned underneath them, so check the harness's own agent-definition file
  rather than trusting the name.
- No model ids downstream: a recipe, card, brief, or doc that names a
  specific model id is a drift hazard. Ids outlive their accuracy, and a
  followed-literally recipe naming yesterday's reviewer can invert the
  reviewer-differs-from-author invariant once that id becomes the writer's
  pin. Docs record the role and the pin source to read it from; the cost
  ledger records the models actually used.

An unvetted, quota-exhausted, or under-permissioned reviewer counts as
unreachable. The gate defers per the Deferrals rule in `PROCESS.md`, and
the deferral surfaces at the next user gate.

## Attended and unattended policy

Unattended running is a class-level policy decision, not a per-session
judgment call:

- Frontier orchestrator class board owners may run long unattended, for an
  overnight batch or several unsupervised daytime hours, at the user's
  discretion.
- Smart writer/reviewer class board owners run attended only, and only on a
  wave a planner session has already vetted. Both conditions hold at once:
  vetting does not lift the attended requirement, and attendance does not
  substitute for the vetted wave.
- The user may override either default for a specific wave. Log the
  override on the card it applies to.

A repo may tighten these defaults. Requiring attended running for every
class is one option. Loosening the defaults needs a recorded user
decision.

## Budget etiquette

Use the cheapest class that can do the job correctly. Escalate on failure,
not by default. If a small explorer class model fails a search task, try
a smart-class model next; do not reach for frontier on the first miss.
Reserve frontier orchestrator class calls for board ownership and Gate F,
where the invariant above requires it.

## Wave-close cost duty

A delegated wave's closing handoff records the orchestrator model string,
every delegated session id, and per-session cost, duration, and token
totals. How to recover these numbers is harness-specific and belongs in
the repo's `REVIEW-TOOLING.md`, not here. Without this record the program
cannot answer whether the cheaper orchestrator is actually cheaper, and
every retro pays the recovery cost the closing session should have paid.
