# Model classes

This is the delegation policy: which class of model runs which kind of
board work, and the invariants that hold regardless of which vendor or
harness is in play. Classes are the stable unit here. Named models drift
month to month; the class each one belongs to is what the board reasons
about.

The concrete model names in this file are dated worked examples, current as
of the date this file was last edited. Treat them as illustrations of the
class, not as a pin. Update the examples when the models you actually use
change; the class definitions below them should rarely need to.

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
- An empty reviewer return is a failed delegation, never a clean pass. A
  review with no explicit verdict has not run. Zero findings is recorded
  as an explicit PASS line, distinguishable from a tool that silently
  returned nothing.
- Gate D, the drift audit, runs on a lower-cost model in the board owner's
  own harness. It samples anchors and claims against the current repo
  state and needs no review skill loaded, so there is no reason to spend
  smart-class or frontier-class budget on it.

## Reviewer pre-vet checklist

Before a wave or gate depends on an external reviewer, the board owner
pre-vets it:

- Reachability and auth: the reviewer's binary, server, or API is reachable
  and authenticated right now, not merely configured.
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
