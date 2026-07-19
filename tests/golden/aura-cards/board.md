---

kanban-plugin: board

---

## Ready
- [ ] **S36** [Re-anchor ARCHITECTURE.md to the accepted head 7a0f0651](s36-architecture-reanchor.md)
	Depends: none. Gates: S -> A. Executor: any.

## In Progress
- [ ] **S9** [Coordinator thread shape (W17)](s9-coordinator-thread-shape.md)
	Depends: S2, MILESTONE. Gates: U(mockup) -> S -> A -> U(launch) -> M -> U(baseline). Executor: smart.

## In Review

## Backlog
- [ ] **S10** [Delegation-contract reconciliation (W18)](s10-delegation-contract.md)
	Depends: S9. Gates: U(mockup) -> S -> A -> U(launch) -> M -> U(baseline). Executor: smart.
- [ ] **S11** [Worker contract blocks](s11-worker-contract-blocks.md)
	Depends: S9, S10. Gates: scope at promotion -> U(mockup) -> S -> A -> U(launch) -> M -> U(baseline). Executor: smart.
- [ ] **S12** [Evidence-frame fix-or-remove decision (W19)](s12-frame-decision.md)
	Depends: S9, S10. Gates: S -> A -> U(decision). Executor: smart.
- [ ] **S13** [Replan-boundary continuity decision](s13-replan-continuity.md)
	Depends: S9, S10. Gates: S -> A -> U(decision). Executor: smart.
- [ ] **S14** [Error-path defect fixes](s14-error-path-fixes.md)
	Depends: S3, MILESTONE. Gates: S -> A -> U(run-decision). Executor: any.
- [ ] **S15** [Assistant-turn fidelity](s15-assistant-turn-fidelity.md)
	Depends: S9, S10. Gates: U(mockup) -> S -> A -> U(launch) -> M -> U(baseline). Executor: smart.
- [ ] **S19** [Bound and poll keystrokes waits](s19-keystrokes-wait-bounding.md)
	Depends: MILESTONE. Gates: scope at promotion -> S -> A -> U(launch) -> M -> U(baseline). Executor: smart.
- [ ] **S20** [Bedrock prompt caching with cache points](s20-bedrock-prompt-caching.md)
	Depends: MILESTONE. Gates: scope at promotion -> S -> A -> U(launch) -> M -> U(baseline). Executor: smart.
- [ ] **S21** [Real default for per_call_timeout_secs](s21-per-call-timeout-default.md)
	Depends: MILESTONE. Gates: S -> A -> U(run-decision). Executor: any.
- [ ] **S22** [Backoff and visibility for the transient planning retry](s22-planning-retry-backoff.md)
	Depends: MILESTONE. Gates: S -> A -> U(run-decision). Executor: any.
- [ ] **S28** [Comment provenance sweep before PR re-cut](s28-comment-provenance-sweep.md)
	Depends: MILESTONE. Gates: S -> A. Executor: any.
- [ ] **S32** [Turn-limit nudge benchmark variable (PR 380)](s32-turn-limit-nudge-variable.md)
	Depends: MILESTONE. Gates: scope at promotion -> S -> U(launch) -> M -> U(baseline). Executor: smart.
- [ ] **S33** [Discover-then-fan-out planning + nudge fold-in decision (ai-experiments PR 17)](s33-fanout-nudge-config-candidate.md)
	Depends: none. Gates: S -> A -> U(decision). Executor: any.
- [ ] **S34** [No config-path override in AuraOrchestratedAgent](s34-config-override-gap.md)
	Depends: none. Gates: S -> A -> U(run-decision). Executor: any.
- [ ] **S35** [Fix templates chained .replace() re-substitution (Gate F1)](s35-templates-replace-fix.md)
	Depends: none. Gates: S -> A. Executor: any.
- [ ] **S37** [Bound operator task scope and terminal pane observation on hard tasks](s37-operator-scope-pane-fault.md)
	Depends: none. Gates: scope at promotion -> S -> A. Executor: smart.

## Done
- [ ] **S0** [Card registry and board guardrails](s0-card-registry.md)
	Depends: none. Gates: S -> A -> M -> U. Executor: smart.
- [ ] **S1** [Fresh-agent orientation proof](s1-orientation-proof.md)
	Depends: S0. Gates: S -> A. Executor: any.
- [ ] **S2** [Experiment worktree and golden-frame harness](s2-golden-frame-harness.md)
	Depends: S0. Gates: S -> A -> U. Executor: smart.
- [ ] **S3** [Unified bounding module](s3-unified-bounding.md)
	Depends: S2. Gates: S -> A. Executor: smart.
- [ ] **S4** [Template unification](s4-template-unification.md)
	Depends: S2. Gates: S -> A. Executor: any.
- [ ] **S5** [Artifact module consolidation](s5-artifact-consolidation.md)
	Depends: S2. Gates: S -> A. Executor: smart.
- [ ] **S6** [Dead-code sweep](s6-dead-code-sweep.md)
	Depends: S3, S4, S5. Gates: S -> A. Executor: any.
- [ ] **S7** [Stream assistant text deltas](s7-stream-assistant-text.md)
	Depends: S2. Gates: S -> A -> M. Executor: any.
- [ ] **S8** [Latency profile investigation](s8-latency-profile.md)
	Depends: none. Gates: S -> A. Executor: smart.
- [ ] **S16** [sre-hard regression harness](s16-sre-hard-harness.md)
	Depends: none. Gates: S -> A. Executor: smart.
- [ ] **S17** [Orchestration test-suite replacement](s17-test-suite-replacement.md)
	Depends: S2. Gates: S -> A -> U(deletion-list). Executor: smart.
- [ ] **S18** [Rolling ADR batches](s18-adr-batches.md)
	Depends: S3. Gates: S -> A. Executor: smart.
- [ ] **S23** [Instrument persistence writes with spans](s23-persistence-write-spans.md)
	Depends: S2. Gates: S -> A. Executor: any.
- [ ] **S24** [Remove the prompt-journal diagnostic](s24-remove-prompt-journal.md)
	Depends: S2. Gates: S -> A. Executor: any.
- [ ] **S25** [Parse timing SSE events in aura-e2e](s25-timing-sse-parser.md)
	Depends: none. Gates: S -> A. Executor: any.
- [ ] **S26** [Re-measure TerminalBench latency with timing SSE](s26-sre-hard-timing-remeasure.md)
	Depends: S25, S16. Gates: S -> A -> U(launch) -> M -> U(baseline). Executor: smart.
- [ ] **S27** [Harden SSE timing partition invariants](s27-sse-timing-partition-hardening.md)
	Depends: S25. Gates: S -> A. Executor: any.
- [ ] **S29** [Grade the next orchestrator wave against a sealed rubric](s29-orchestrator-retro.md)
	Depends: none. Gates: S -> A. Executor: smart.
- [ ] **S30** [Re-verify ARCHITECTURE.md line anchors](s30-architecture-anchor-reverify.md)
	Depends: none. Gates: S -> A. Executor: any.
- [ ] **S31** [Record benchmark-runner relocation to aura-bench-runner](s31-benchmark-runner-relocation.md)
	Depends: none. Gates: S -> A. Executor: any.
- [ ] **MILESTONE** [Track A replication gate](milestone-track-a-replication.md)
	Depends: S6, S17, S16. Gates: U(launch) -> M -> U(acceptance). Executor: smart.

%% Generated by boardkit render. Card frontmatter is the source of truth; a kanban drag here is DRIFT that --check reports. Update the card file, then regenerate. %%
