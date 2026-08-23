---

kanban-plugin: board

---

%% CHARTER - owns: the kit family: boardkit itself, rust-holes, and the prose bench / Not here: consumer-repo process fixes and aura-family work / Route aura -> aura-family cards, epics, and consolidation work / Admission test: where does the diff land. %%

## Ready
- [ ] **S1** [Wave-close retro with snapshots and driver input](s1-wave-close-retro.md)
	Depends: none. Gates: S -> A -> U @ S. Executor: any.
- [ ] **S2** [Wire pre-vet, deferrals, and packet staging into the CLI](s2-wiring-trio.md)
	Depends: none. Gates: S -> A @ S. Executor: smart.
- [ ] **S3** [claude-skills defect sweep from the topology audit](s3-skills-defect-sweep.md)
	Depends: none. Gates: S -> A @ S. Executor: any.
- [ ] **S4** [Declare the typed-holes skill canonical over PLAYBOOK](s4-rust-holes-canonical.md)
	Depends: none. Gates: S -> A @ S. Executor: any.
- [ ] **S8** [Board-root portability and checkout-independent references](s8-board-root-portability.md)
	Depends: none. Gates: S -> A @ S. Executor: smart.
- [ ] **S9** [Session-model classification and example freshness](s9-model-class-freshness.md)
	Depends: none. Gates: S -> A @ S. Executor: any.
- [ ] **S10** [Prose-reviewer bench over snapshotted external prose](s10-prose-reviewer-bench.md)
	Depends: none. Gates: S -> A -> M -> U @ S. Executor: any.
- [ ] **S12** [Public-repo seam for contract docs and generated views](s12-public-repo-seam.md)
	Depends: none. Gates: S -> A @ S. Executor: smart.
- [ ] **S17** [Satellite-repo convention - no canonical-looking TODO beside a board](s17-satellite-repo-convention.md)
	Depends: none. Gates: S -> A @ S. Executor: smart.
- [ ] **S26** [rust-holes HOLES ledger with a hook-grade check](s26-rust-holes-ledger.md)
	Depends: none. Gates: S -> A -> U(code-review) @ S. Executor: smart.
- [ ] **S38** [Pick the board's visual home](s38-visual-surface-decision.md)
	Depends: S16. Gates: S -> A -> D -> U @ S. Executor: smart.
- [ ] **S39** [Machine-bootstrap recipe and account inventory](s39-machine-bootstrap-recipe.md)
	Depends: none. Gates: S -> A -> D -> U @ S. Executor: smart.
- [ ] **S40** [README developer path, canary brief template, plan navigation](s40-readme-developer-path.md)
	Depends: none. Gates: S -> A @ S. Executor: any.

## In Progress
- [ ] **S30** [Wave-2 small-fix batch with the ignore and doctor truthing items](s30-small-fix-batch.md)
	Depends: none. Gates: S -> A -> D -> U(code-review) @ D. Executor: smart.

## In Review
- [ ] **S15** [Restore the human review guide to generated packets](s15-review-packet-guide.md)
	Depends: none. Gates: S -> A -> U(code-review) @ U. Executor: smart.
- [ ] **S29** [Decide how strictly doctor should classify an entry-file shim](s29-shim-classification-hardening.md)
	Depends: none. Gates: S -> A -> U(code-review) @ U. Executor: smart.
- [ ] **S31** [Versioned docking-convention spec with the three consumer postures](s31-docking-convention-spec.md)
	Depends: none. Gates: S -> A -> D -> U(code-review) @ D. Executor: smart.

## Backlog
- [ ] **S6** [Template baseline digest, template-diff, and golden briefs](s6-template-canary.md)
	Depends: none. Gates: S -> A. Executor: smart.
- [ ] **S7** [Thin transport wrapper spike with a canary harness](s7-transport-wrapper-spike.md)
	Depends: S2. Gates: S -> A -> U. Executor: smart.
- [ ] **S27** [Maintained architecture flowchart of the kit and its skills](s27-architecture-flowchart.md)
	Depends: none. Gates: S -> A. Executor: any.
- [ ] **S28** [Wire the CLI core through the CardStore seam](s28-store-seam-wiring.md)
	Depends: none. Gates: S -> A -> U(code-review). Executor: smart.
- [ ] **S32** [ArtifactStore ADR - receipts, postures, sidecar mechanics](s32-artifact-store-adr.md)
	Depends: S28. Gates: S -> A -> D -> U. Executor: smart.
- [ ] **S33** [Receipts and sidecar implementation per the ADR](s33-receipts-and-sidecar.md)
	Depends: S32. Gates: S -> A -> M -> D -> U(code-review). Executor: smart.
- [ ] **S34** [Decide whether the wave-level Gate F packet is worth generating](s34-wave-gate-design.md)
	Depends: S32. Gates: S -> A -> D -> U. Executor: smart.
- [ ] **S35** [Before/after canary extension for the PROCESS templates](s35-before-after-canary.md)
	Depends: S34. Gates: S -> A. Executor: smart.
- [ ] **S36** [rust-holes adopts the docking convention as second consumer](s36-rust-holes-docking.md)
	Depends: S31. Gates: S -> A -> U(code-review). Executor: smart.
- [ ] **S37** [Recomputable freshness stamp on the generated views](s37-view-freshness-stamp.md)
	Depends: S28. Gates: S -> A -> U(code-review). Executor: smart.
- [ ] **S41** [Co-worker consumption readiness](s41-co-worker-consumption.md)
	Depends: none. Gates: S -> U. Executor: smart.
- [ ] **S42** [Fix doctor host checks that misfire on in-repo board homes](s42-doctor-docked-board-misfires.md)
	Depends: none. Gates: S -> A -> U(code-review). Executor: smart.

## Done
- [ ] **S5** [Run the never-run Gate T on native opencode routing](s5-gate-t-native-opencode.md)
	Depends: none. Gates: M -> T. Executor: any.
- [ ] **S11** [Tier the vale prose gate by artifact class](s11-vale-tiering.md)
	Depends: none. Gates: S -> A. Executor: any.
- [ ] **S13** [R5' .boardkit resolution with the CardStore seam](s13-board-discovery.md)
	Depends: none. Gates: S -> A -> U(code-review). Executor: smart.
- [ ] **S14** [Bound the adversarial review cycle with a convergence rule](s14-review-cycle-convergence.md)
	Depends: none. Gates: S -> A. Executor: smart.
- [ ] **S16** [Render each card's current gate position in the generated views](s16-gate-position-in-views.md)
	Depends: none. Gates: S -> A -> U(code-review). Executor: smart.
- [ ] **S18** [R4 boards registry - the manifest is the registry](s18-boards-registry.md)
	Depends: S13. Gates: S -> A -> U(code-review). Executor: smart.
- [ ] **S19** [R1 lanes as first-class card data](s19-lanes-first-class.md)
	Depends: none. Gates: S -> A -> U(code-review). Executor: smart.
- [ ] **S20** [R10 board charters with the bk dogfood charter](s20-board-charters.md)
	Depends: S18. Gates: S -> A -> U(code-review). Executor: smart.
- [ ] **S21** [R3 qualified cross-board references](s21-cross-board-refs.md)
	Depends: S18. Gates: S -> A -> U(code-review). Executor: smart.
- [ ] **S22** [R9 goal-directed dag queries with Mermaid renders](s22-dag-queries.md)
	Depends: S13, S19. Gates: S -> A -> U(code-review). Executor: smart.
- [ ] **S23** [R2 epic cards and epic membership](s23-epic-grouping.md)
	Depends: none. Gates: S -> A -> U(code-review). Executor: smart.
- [ ] **S24** [R6/R7 doctor checks - host-repo hazards and harness parity](s24-doctor-host-hazards.md)
	Depends: none. Gates: S -> A -> U(code-review). Executor: smart.
- [ ] **S25** [R8 fix - card titles truncated at an inline hash](s25-title-hash-truncation.md)
	Depends: none. Gates: S -> A -> U(code-review). Executor: any.

%% Generated by boardkit render. Card frontmatter is the source of truth; a kanban drag here is DRIFT that --check reports. Update the card file, then regenerate. %%
