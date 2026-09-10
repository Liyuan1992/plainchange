# Evolution source log

This append-only ledger records material completed changes and decisions. It is not a roadmap and it does not replace ADRs. A later entry may supersede an earlier one, but must link to it rather than remove it.

## Entry template

```text
ID: EVO-YYYYMMDD-001
Date: YYYY-MM-DD
Domain: <domain>
Type: behavior | architecture | interface | data | dependency | test | operations | decision
What changed: <observed change>
Why now: <source-backed reason>
Impact / tradeoff: <known consequence>
Verification: <commands / observations / not run>
Links: <files, task, ADR, related BUG/EVO IDs>
Needs curation: yes | no
```

---

<!-- Append new entries below this line. -->

ID: EVO-20260904-001
Date: 2026-09-04
Domain: project-governance
Type: architecture
What changed: Created the `change-passport-spike` serious-project root, local Git repository, shared Codex/Claude governance entrypoints, project facts, append-only source ledgers, proposed ADR, and the first bounded task plan.
Why now: The user authorized creation of a new engineering project from the confirmed Evidence Spike PRD, and the shared `AGENT.md` requires a governed repository baseline before implementation.
Impact / tradeoff: Both coding agents receive the same approval gates and evidence rules; standard implementation cannot start until the owner explicitly approves `TASK-20260904-001` and `ADR-0001`.
Verification: Initializer reported all baseline files created; `git status --short --branch` showed a new local repository with untracked baseline files; `git remote -v` returned no remote.
Links: `README.md`, `AGENTS.md`, `CLAUDE.md`, `docs/project-governance/PROJECT.md`, `docs/project-governance/tasks/TASK-20260904-001-phase0-evidence-spine.md`, `docs/project-governance/decisions/ADR-0001-deterministic-evidence-spine.md`
Needs curation: no

ID: EVO-20260904-003
Date: 2026-09-04
Domain: evidence-generation
Type: architecture
What changed: Implemented the Phase 0-M1 three-layer vertical slice: immutable read-only Git evidence collection, hidden-ground-truth separation, provider-neutral model packet/file bridge, deterministic claim validation and Chinese rendering, annotation templates, and fidelity scoring.
Why now: The owner approved testing semantic usefulness without giving the model direct repository or ground-truth access.
Impact / tradeoff: The executable spine is locally testable and model-provider neutral. It deliberately stops before automatic API integration and real-sample evaluation; temporal provenance for historical inputs remains an explicit gap.
Verification: `uv run pytest -q` reported 24 passed after boundary hardening; compileall and CLI help exited 0; safety scan found no shell=True or network/API integration; target-repository read-only and artifact-containment tests passed.
Links: `src/change_passport/`, `tests/`, `docs/project-governance/tasks/TASK-20260904-001-phase0-evidence-spine.md`, `docs/project-governance/domains/evidence-contract.md`, `docs/project-governance/decisions/ADR-0001-deterministic-evidence-spine.md`
Needs curation: no

ID: EVO-20260904-002
Date: 2026-09-04
Domain: evidence-generation
Type: decision
What changed: Replaced the proposed model-free brief with an approved three-layer design: deterministic evidence packet, constrained model JSON generation through a file bridge, and deterministic claim validation/rendering.
Why now: The owner identified that a model-free system could only produce mechanical templates and could not test the intended human-comprehension value.
Impact / tradeoff: The first slice now tests semantic usefulness while retaining a hard evidence boundary. Automatic provider APIs and source upload remain outside scope, so the first real generator is orchestrated through the current Codex task.
Verification: ADR-0001 and TASK-20260904-001 were updated; approval evidence is the user's 2026-09-04 response “嗯，对的” after the revised architecture explanation.
Links: `docs/project-governance/decisions/ADR-0001-deterministic-evidence-spine.md`, `docs/project-governance/tasks/TASK-20260904-001-phase0-evidence-spine.md`
Needs curation: no

ID: EVO-20260904-004
Date: 2026-09-04
Domain: project-governance
Type: operations
What changed: Recorded that EVO-20260904-003 was physically appended before EVO-20260904-002 and established EVO IDs, links, and stated chronology—not file position alone—as the authoritative sequence for those two retained records.
Why now: Append-only governance forbids silently moving or rewriting the already recorded entries, so the sequencing mistake requires an explicit later correction.
Impact / tradeoff: The raw audit trail remains intact and the intended order is unambiguous; the file intentionally retains the visible 001, 003, 002, 004 order.
Verification: `rg -n "^ID: EVO-" docs/project-governance/EVOLUTION.md` shows all four records with this correction at the current end of file.
Links: `BUG-20260904-001`, `EVO-20260904-002`, `EVO-20260904-003`, `docs/project-governance/tasks/TASK-20260904-001-phase0-evidence-spine.md`
Needs curation: no

ID: EVO-20260904-005
Date: 2026-09-04
Domain: evidence-generation
Type: operations
What changed: Completed the first real DigitalSelf file-bridge run for immutable change `d78f78b..430c342`, producing a frozen generator packet, eight validated four-section claims, an annotation template, and a post-freeze qualitative comparison against the later `44cf378` documentation patch.
Why now: The owner explicitly requested one DigitalSelf run after approving the three-layer evidence/model/validator design.
Impact / tradeoff: The run demonstrates readable semantic coverage and correct abstention from self-reported test success on one real sample. It remains unscored and cannot establish general fidelity; it also exposed generic unknown rendering as a readability defect.
Verification: `prepare` and `finalize` exited 0; packet forbidden-string scan found no hidden comparison identifiers; validator reported 8 accepted, 0 downgraded, 0 rejected; the hidden patch was opened only after raw JSON was frozen; project tests and target-worktree preservation were checked at closeout.
Links: `docs/project-governance/tasks/TASK-20260904-002-first-digitals-self-sample.md`, `artifacts/digitalself-430c342/blind-review.md`, `BUG-20260904-002`
Needs curation: yes

ID: EVO-20260910-010
Date: 2026-09-10
Domain: analysis-runtime
Type: onboarding-and-scale
What changed: Added a generic `analyze` operation that turns a fixed Git range into a candidate owner report without requiring a hand-authored target profile or an external model. It combines automatic class-based project/workflow drafting, source-bound owner language, observable stages, managed Git-object recovery, immutable-blob parse reuse, and lazy technical evidence.
Why now: The vLLM validation proved that the renderer contract could scale semantically, but the first setup still required manual profile/control authoring, could wait silently on partial-clone hydration, repeated parsing, and produced a 12.9 MB eager report.
Impact / tradeoff: A new repository can now produce a reviewable first draft in one command, and repeated large-project analysis is materially faster. The deterministic classifier deliberately exposes its output as a candidate and cannot provide the semantic quality of a project declaration or model-assisted refinement. The single offline HTML still carries compressed technical evidence rather than moving it to a network sidecar.
Verification: 65 tests pass. An unrelated model-serving fixture selects model-request/scheduling/streaming owner language without a repository-name rule. The fixed vLLM run automatically yields 4,501 modules, 21,091 edges, zero unclassified modules, a 9.406-second cold path, a 3.808-second warm path, and a 75.7% smaller report. Independent human comprehension and browser click acceptance remain pending.
Links: `TASK-20260910-028`, `src/change_passport/auto_draft.py`, `src/change_passport/pipeline.py`, `src/change_passport/analysis_cache.py`, `src/change_passport/progress.py`
Needs curation: yes

ID: EVO-20260905-019
Date: 2026-09-05
Domain: architecture-understanding
Type: architecture
What changed: Replaced repository-specific core grouping and reader presentation with strict, versioned target profiles, then made Change Passport's own immutable retained-edge fix the primary public local showcase.
Why now: The owner identified this fast-moving project as the highest-confidence initial test bed because its task context and intended change are directly known, while explicitly prohibiting code that special-cases the project just to improve its own report.
Impact / tradeoff: Profiles now carry sections, Chinese labels, terminology, brand, and module areas; each profile's raw SHA-256 is embedded in the snapshot and bound to every group source. The generic pipeline still produces identical Git and architecture facts with or without a profile. The self-hosted `a4576ec..688fc5f` run is easier for an external reader to inspect, but remains a known-context correctness sample rather than independent evidence of generalization.
Verification: An isolated detached clone stayed clean before and after prepare/finalize. Its report has 2 modified modules, 0 added/removed/modified static edges, 23 modules, 48 static edges, 2 groups, 0 unclassified paths, `change-passport` profile SHA `21b8920167785aee47065c61995882ebc63e0e22ff0650eed3e5778ca143d742`, dynamic Change Passport branding, and 3/1/0 claim validation. Generic profile tests, 48 full tests, compileall, JavaScript syntax, HTML safety coverage, profile-binding checks, and Git diff check pass.
Links: `docs/project-governance/tasks/TASK-20260905-010-self-hosted-showcase-and-target-profile.md`, `docs/showcase/change-passport-self-688fc5f.md`, `src/change_passport/target_profile.py`, `examples/target-profiles/change-passport.v1.json`, `tests/test_target_profile.py`, `BUG-20260905-014`
Needs curation: yes

ID: EVO-20260904-012
Date: 2026-09-04
Domain: architecture-understanding
Type: experiment
What changed: Continued EVO-20260904-011 after the owner registered a CodeAtlas account and completed authenticated click-through of the fixed DigitalSelf commit range, including commit selection, 12-step replay, system/feature/file/function navigation, global search, Windows path routing, and flow-node clicks.
Why now: The signed-out run could inspect the local structured interface but could not establish the actual human interaction quality that the owner wanted to borrow.
Impact / tradeoff: Persistent navigation, breadcrumbs, red/green function-flow overlays, and file-to-function drill-down are useful interaction references. The same run also showed forced auto-replay, unrelated cross-layer items presented as modified, a 531-to-470 route-count change unsupported by the seven-file Git diff, a newly added file without an ADDED marker, slash/backslash route divergence, search results that did not navigate, and no persistent evidence sidebar when clicking a branch node. The recommendation remains a local change-first canvas over validated M1.5 JSON, not adoption of CodeAtlas facts or scope.
Verification: The authenticated picker selected exact `d78f78b..430c342`; server logs reported 1,112 base files, 1,115 head files, 7 changed files, and 20,344 diffed graphs. The browser completed 12 replay steps, opened the new `argument_validation.py` only through a backslash route, displayed 32 file nodes and 26 `validate_arguments` flow nodes, and preserved the original DigitalSelf repository boundary. AI review, LLM refinement, API tests, account settings, baseline approval, PRD revision, implementation, commit, and push were not performed.
Links: `EVO-20260904-011`, `docs/experiments/codeatlas-digitalself-product-experience-20260904.md`, `docs/project-governance/tasks/TASK-20260904-003-m15-architecture-baseline-delta.md`
Needs curation: yes

ID: EVO-20260904-009
Date: 2026-09-04
Domain: architecture-understanding
Type: experiment
What changed: Paused M1.5 before baseline approval and ran the open-source ClaudeMap 0.1.0 against isolated base/head snapshots of the same immutable DigitalSelf range, producing offline interactive HTML, JSON, and five static views plus a product-experience comparison.
Why now: The owner asked to compare the same project with an open-source third-party decomposition before continuing, with special attention to product experience rather than only graph correctness.
Impact / tradeoff: ClaudeMap demonstrates a stronger onboarding and exploration experience through whole-project architecture, search, zoom, multiple views, node details, minimap, and export. M1.5 remains stronger for evidence-backed before/after change visibility and governed impact. ClaudeMap's file-scale views overload at 2,918 nodes, and its heuristic risk/feature labels produced observed false or overly broad signals.
Verification: ClaudeMap source was pinned to `c2e1424`, audited as MIT/zero-runtime-dependency with no observed network/telemetry path, and passed 28/28 built-in checks. Exact clean DigitalSelf snapshots produced 2,915→2,918 files, 928,905→929,522 LOC, 2,527→2,540 links, and unchanged 11 modules/28 subsystems. Five SVG/PNG views and both offline HTML/JSON snapshots were generated locally.
Links: `docs/experiments/claudemap-digitals-self-product-experience-20260904.md`, `docs/project-governance/tasks/TASK-20260904-003-m15-architecture-baseline-delta.md`, `artifacts/third-party/claudemap/`
Needs curation: yes

ID: EVO-20260904-006
Date: 2026-09-04
Domain: architecture-understanding
Type: decision
What changed: Drafted PRD v1.1, proposed ADR-0002, and planned TASK-20260904-003 to promote a bounded approved architecture baseline and per-change before/after delta above the existing four-section explanation.
Why now: The first real DigitalSelf sample preserved evidence safety but the owner found that prose alone did not make changed topology or impact visible and could not provide reusable project understanding for later runs.
Impact / tradeoff: The proposed M1.5 keeps the deterministic evidence/model/validator boundary while adding baseline identity, invalidation, bounded impact, graph/JSON parity, and human approval. It explicitly avoids a full symbol graph or generic knowledge-graph platform. Implementation remains blocked until PRD v1.1 is confirmed.
Verification: PRD v1.1 SHA-256 is `939A5E398297BC7A59A19178D2223CCE44B521642E8367A42E478B65CD9D6F47`; DigitalSelf workflow state and PRD metadata were reset to `confirmed=false`; no source implementation was changed for M1.5.
Links: `docs/project-governance/decisions/ADR-0002-persistent-architecture-baseline-and-delta.md`, `docs/project-governance/tasks/TASK-20260904-003-m15-architecture-baseline-delta.md`, `EVO-20260904-005`
Needs curation: no

ID: EVO-20260904-007
Date: 2026-09-04
Domain: architecture-understanding
Type: decision
What changed: Confirmed PRD v1.1 and accepted ADR-0002 for the bounded approved architecture baseline, before/after delta, graph-first review, and four-section explanation contract.
Why now: After reviewing the revised PRD and its implementation boundary, the owner explicitly replied “确定”.
Impact / tradeoff: The M1.5 architecture contract is now normative, but the implementation task remains PLANNED until a separate start/implementation approval is given. Full knowledge graphs, product UI, automatic baseline approval, commit, push, packaging, and deployment remain outside this confirmation.
Verification: DigitalSelf `workflow-confirm` returned `confirmed=true`; `workflow-status` reported PRD revision `1.1`, SHA-256 `995E5701B2438A08ED9E32FBE68E54E197DB7F126BCDCECE0B6F3D953D3C1B9C`, and `confirmation_required=false`.
Links: `docs/project-governance/decisions/ADR-0002-persistent-architecture-baseline-and-delta.md`, `docs/project-governance/tasks/TASK-20260904-003-m15-architecture-baseline-delta.md`, `EVO-20260904-006`
Needs curation: no

ID: EVO-20260904-008
Date: 2026-09-04
Domain: architecture-understanding
Type: architecture
What changed: Implemented the M1.5 bounded architecture baseline/delta core, explicit human approval materialization, deterministic graph-first rendering, and the first real DigitalSelf architecture sample.
Why now: The owner explicitly approved implementation after confirming PRD v1.1 and ADR-0002, and the earlier prose-only sample did not make topology or impact visible or reusable.
Impact / tradeoff: Initial bootstrap parses supported Python/JavaScript files once, then an approved baseline can reuse unchanged nodes and reparse a bounded changed neighborhood. The main graph always shows changed nodes and prioritized production consumers while retaining folded IDs in JSON. Static import consumers are deliberately not presented as proven runtime impact.
Verification: Full suite reports 31 passed; immutable DigitalSelf `d78f78b..430c342` produced 3 added, 4 modified, 36 consumer nodes, 50 unique one-hop paths, 14 displayed/32 folded nodes, and an 8/0/0 validated brief. Target worktree status hash was unchanged before/after. The baseline proposal remains pending owner review, so the real consecutive-change gate is not complete.
Links: `src/change_passport/architecture.py`, `src/change_passport/pipeline.py`, `tests/test_architecture.py`, `docs/project-governance/tasks/TASK-20260904-003-m15-architecture-baseline-delta.md`, `BUG-20260904-004`, `BUG-20260904-005`
Needs curation: yes

ID: EVO-20260904-010
Date: 2026-09-04
Domain: project-governance
Type: operations
What changed: Recorded that EVO-20260904-009 was physically inserted after EVO-20260904-005 instead of at the end of the append-only ledger; established EVO IDs, links, and stated chronology—not file position alone—as the authoritative order for records 006 through 010.
Why now: The append used the repeated line `Needs curation: yes` as an anchor, which matched EVO-20260904-005 before the actual end of file. Append-only governance forbids moving or silently rewriting the already recorded entry.
Impact / tradeoff: The original audit trail remains visible and EVO-20260904-009 remains authoritative for the ClaudeMap comparison, but readers must follow IDs rather than physical position for this retained sequencing defect.
Verification: `rg -n "^ID: EVO-20260904-00(5|6|7|8|9|10)$" docs/project-governance/EVOLUTION.md` exposes the retained physical order, with this correction at the true end of file.
Links: `EVO-20260904-009`, `BUG-20260904-008`, `docs/experiments/claudemap-digitals-self-product-experience-20260904.md`
Needs curation: no

ID: EVO-20260904-011
Date: 2026-09-04
Domain: architecture-understanding
Type: experiment
What changed: Corrected the best-in-class comparison target from ClaudeMap to CodeAtlas.live and ran its current build against an isolated exact DigitalSelf head, combining signed-out browser observation with read-only local MCP queries over the same index.
Why now: The owner clarified that borrowing should use CodeAtlas as the strongest interaction reference, especially for clickable architecture branches and progressive project understanding.
Impact / tradeoff: CodeAtlas validates the value of a persistent canvas, layered overlays, bounded drill-down, and one human/machine graph contract. It does not justify copying full-graph scope: the DigitalSelf run exposed login-gated diagrams, proprietary licensing, invasive default setup, Windows path-separator sensitivity, and file-path-labelled Feature clusters. The resulting recommendation is a local change-first HTML view over M1.5 validated JSON, not a CodeAtlas clone.
Verification: OpenVSX 9.3.0 VSIX hash matched its published SHA-256; the run indexed 1,068 files and returned `ready`. The fixed diff produced 7 changed files. Impact returned 0/0 with forward-slash paths and 69 direct symbols/6 transitive functions with Windows paths; the new argument-validation cluster contained its source and test but 0 entry points/subsystems. MCP and main UI files matched the latest VSIX hashes. No account data, LLM review, original DigitalSelf workspace write, baseline approval, commit, or push occurred.
Links: `docs/experiments/codeatlas-digitalself-product-experience-20260904.md`, `docs/experiments/claudemap-digitals-self-product-experience-20260904.md`, `docs/project-governance/tasks/TASK-20260904-003-m15-architecture-baseline-delta.md`, `EVO-20260904-009`
Needs curation: yes

ID: EVO-20260904-013
Date: 2026-09-04
Domain: project-governance
Type: operations
What changed: Recorded that EVO-20260904-012 was physically inserted after EVO-20260904-005 instead of at the end of the append-only ledger; established EVO IDs, links, and stated chronology—not file position alone—as the authoritative sequence for the authenticated CodeAtlas continuation.
Why now: The append again matched an earlier repeated `Needs curation: yes` anchor. Append-only governance forbids moving or silently rewriting the already recorded EVO-20260904-012 entry.
Impact / tradeoff: The raw audit trail and authenticated findings remain intact, but readers must follow EVO-20260904-011 → EVO-20260904-012 → EVO-20260904-013 rather than physical position for this retained sequencing defect.
Verification: `rg -n "^ID: EVO-20260904-0(11|12|13)$" docs/project-governance/EVOLUTION.md` exposes the retained physical placement and this correction at the true end of file.
Links: `EVO-20260904-011`, `EVO-20260904-012`, `BUG-20260904-008`, `docs/experiments/codeatlas-digitalself-product-experience-20260904.md`
Needs curation: no

ID: EVO-20260904-014
Date: 2026-09-04
Domain: architecture-understanding
Type: architecture
What changed: Completed the v1.3 overall-system architecture tab as a versioned full supported-code static snapshot, deterministic nine-section human overview, complete source-edge aggregation, change overlay, and responsive interactive drill-down in the generated local HTML.
Why now: The owner concluded that change-only explanations were insufficient for one-glance impact understanding and reusable project comprehension, then explicitly enabled fast mode with “直到完成之前不需要我确认”.
Impact / tradeoff: Humans now start from nine Chinese system sections and can drill into a section and module, while the machine artifact retains all 1,057 parsed modules and 1,768 verified static import edges. The page clearly remains a candidate static snapshot rather than an approved baseline or complete runtime architecture; unknown dynamic, database, network, deployment, and cross-repository relationships are not invented.
Verification: Formal DigitalSelf `d78f78b..430c342` generation completed in 6.3 seconds with 9 sections, 39 directed section-edge bundles, 0 unclassified modules, and change placement 5/1/1. The HTML is 1,856,555 bytes. Forty-one tests, compileall, JavaScript syntax, unchanged target status, desktop tab/section/module interactions, 390 px no-overflow, Chinese change labels, and zero browser warnings/errors all passed.
Links: `docs/project-governance/tasks/TASK-20260904-005-system-architecture-tab.md`, `src/change_passport/architecture.py`, `src/change_passport/review_model.py`, `src/change_passport/templates/review.js`, `artifacts/digitalself-430c342-m15/system-architecture.json`
Needs curation: yes

ID: EVO-20260905-015
Date: 2026-09-05
Domain: architecture-understanding
Type: architecture
What changed: Replaced the selected-section spider web with a beginner-readable three-column focus map that separates incoming relationships, the current section, and outgoing relationships while preserving every original section-edge identity.
Why now: The owner could not clearly see the architecture lines in the first formal overall-system view; live browser review of the first correction also showed that boundary routing alone left nine relations crowded around the selected card.
Impact / tradeoff: A selected section now has a stable scan direction, visible arrow endpoints, named counts, and click-to-isolate branches. The overview stays compact and the machine snapshot stays complete. High-degree columns may extend below the first fold, preferring vertical scroll over smaller text or crossed lines.
Verification: Formal DigitalSelf generation retained snapshot identity `23400d64e98911ba3093d3a46471883a791f75212cbf67fa1b348134de8aa1cc`, 1,057 modules, 1,768 static edges, 9 sections, 39 section-edge bundles, and 0 unclassified modules. The accepted 1440 px capture scored 9.3/10; 390 px had no horizontal overflow; 41 tests, compileall, JavaScript syntax, relation isolation, module drill-down, return state, and zero console warnings/errors passed.
Links: `docs/project-governance/tasks/TASK-20260905-006-architecture-line-clarity.md`, `BUG-20260905-011`, `src/change_passport/templates/review.js`, `design/ui-flows/system-architecture-line-clarity-agent-20260905/04-validation/current-after.png`
Needs curation: yes

ID: EVO-20260905-016
Date: 2026-09-05
Domain: architecture-understanding
Type: experience
What changed: Replaced the selected-section raw module wall with a progressive three-stage view: system section, Chinese reading area, and optional technical modules. All areas are deterministic first-match source-path buckets and the original module identities remain available only after explicit drill-down.
Why now: The owner found that exposing 60 of 227 English identifiers and source paths still required too much code knowledge and asked for a structured or layered view that a beginner could understand.
Impact / tradeoff: The first view now explains what kinds of parts exist and where the current change lands before exposing code. This lowers entry cost without inventing runtime order or changing the machine snapshot. Path grouping is transparent but remains a reading aid, not a semantic or runtime architecture claim.
Verification: The user-entry view has 7 areas covering 227/227 modules exactly once, 0 raw modules by default, and 18 after explicit reveal. All nine section totals reconcile; the frozen snapshot identity and SHA-256 are unchanged. Forty-one tests, compileall, JavaScript syntax, 8/0/0 generation validation, desktop interactions, Escape/return flow, 390 px no-overflow, 9.4/10 visual review, and zero browser warnings/errors passed.
Links: `docs/project-governance/tasks/TASK-20260905-007-progressive-module-layer.md`, `src/change_passport/templates/review.js`, `design/ui-flows/architecture-module-layer-agent-20260905/04-validation/current-after.png`
Needs curation: yes

ID: EVO-20260905-017
Date: 2026-09-05
Domain: beginner-understanding
Type: experience
What changed: Split the Why card into reason-ready, task-clues-available, and task-context-unavailable states, then added a progressive task-evidence layer that shows user requests separately from AI replies without spending tokens.
Why now: The owner correctly challenged that an existing task window can contain enough information to help explain a change even when the constrained generator did not produce a validated intent claim.
Impact / tradeoff: The offline report now reuses evidence it already owns and stops falsely claiming the context is absent. It remains conservative: AI explanations cannot become confirmed user intent, excerpts are bounded, and a future model-assisted extraction is click-only, Token-labelled, and tied to an exact task/change identity. The static report itself does not gain a live task connector.
Verification: The formal DigitalSelf sample exposes one user and one AI evidence item, retains 8/0/0 claim validation and the unchanged architecture snapshot identity/hash, passes 44 tests, compileall, JavaScript syntax, desktop expand/Escape behavior, 390 px no-overflow, safe embedding, and zero console warnings/errors.
Links: `docs/project-governance/tasks/TASK-20260905-008-intent-context-recovery.md`, `BUG-20260905-012`, `src/change_passport/review_model.py`, `design/ui-flows/intent-context-recovery-agent-20260905/current-after.png`, `D:\Dev\Projects\DigitalSelf\design\ui-flows\ai-coding-session-review\01-prd\prd-v1.4-intent-context-draft.md`
Needs curation: yes

ID: EVO-20260905-018
Date: 2026-09-05
Domain: project-governance
Type: operations
What changed: Froze further UI work, preserved the previously untracked spike in local commit `a4576ec`, and moved the active gate back to factual-fidelity evaluation after correcting retained-edge classification.
Why now: The owner supplied an independent review showing that presentation work had outrun the PRD's first evidence gate and that the entire implementation had no Git baseline. A read-only audit confirmed both the preservation risk and the modified-edge defect; the owner approved the two-local-commit sequence.
Impact / tradeoff: The implementation and its design evidence are now recoverable, and the formal delta distinguishes commit-only reverification from a real source-line move. Product polish, profile extraction, provider integration, and architecture refactoring remain deliberately deferred until three samples and independent retelling establish usefulness.
Verification: Baseline commit `a4576ec` contains 97 files and passed 44 tests before preservation. The correction passes 45 tests and regenerates the immutable DigitalSelf sample at 14 added, 1 removed, and 1 modified edge with 8/0/0 claim validation and an unchanged target-worktree fingerprint.
Links: `docs/project-governance/tasks/TASK-20260905-009-preserve-and-fix-edge-delta.md`, `BUG-20260905-013`, `src/change_passport/architecture.py`, `tests/test_architecture.py`
Needs curation: yes

ID: EVO-20260905-020
Date: 2026-09-05
Domain: project-governance
Type: correction
What changed: Retained EVO-20260905-019 in its accidental earlier physical position and recorded this terminal correction so the target-profile and self-hosted-showcase decision has an explicit chronological endpoint.
Why now: The append operation matched a repeated `Needs curation: yes` marker rather than the unique final fields of EVO-20260905-018, recreating a known append-only sequencing defect.
Impact / tradeoff: No material decision, implementation fact, or prior record is rewritten. Readers must follow EVO-20260905-019 together with this correction rather than infer its chronology solely from its file position.
Verification: EVO-20260905-019 remains unchanged; this record is appended after EVO-20260905-018 at true EOF. `BUG-20260905-015` preserves the root cause and prevention rule.
Links: `EVO-20260905-019`, `BUG-20260905-015`, `BUG-20260904-008`, `docs/project-governance/tasks/TASK-20260905-010-self-hosted-showcase-and-target-profile.md`
Needs curation: no

ID: EVO-20260905-021
Date: 2026-09-05
Domain: architecture-understanding
Type: experience
What changed: Reframed the architecture tab as two explicitly different layers: a profile-sourced system work-flow map first, followed by the existing full static-code implementation map.
Why now: The owner correctly rejected a source-category map as an architecture diagram because it did not let a non-coder identify the system inputs, components, outputs, or the human approval boundary.
Impact / tradeoff: The first view now shows fixed code change and explicit evidence inputs, read-only evidence spine, static extraction, constrained explanation/validation, readable outputs, a distinct human approval gate, and approved-baseline state. These eight configured components and eight arrows are visually labelled as a target-profile product/process architecture, not static imports or runtime order. The static module/import map remains complete and is reachable through mapped concept cards.
Verification: Regenerated the isolated `a4576ec..688fc5f` artifact with profile SHA `928fcffe396d74ecfd73b49e6e8b968fdf0a8d90e1b10e17df80d8102ab30e26`; the target clone remained clean. Playwright at 1440×1050 observed 8 components, 8 SVG arrows, 8 text relationship fallbacks, concept map before static implementation, and working drill-down; 390×844 had no horizontal overflow and intentionally hid only decorative SVG links. Console warnings/errors: 0. Forty-nine tests, compileall, JavaScript syntax, and diff check passed.
Links: `docs/project-governance/tasks/TASK-20260905-011-product-architecture-first-map.md`, `src/change_passport/target_profile.py`, `src/change_passport/review_model.py`, `src/change_passport/templates/review.html`, `design/ui-flows/product-architecture-first-map-agent-20260905/04-validation/current-after.png`, `BUG-20260905-016`
Needs curation: yes

ID: EVO-20260905-022
Date: 2026-09-05
Domain: architecture-understanding
Type: experience
What changed: Replaced the product/process map's free-form arrow field with a responsibility-banded architecture story: numbered primary route, short input branches, a distinct human decision band, and a relation key outside the drawing.
Why now: The owner correctly identified that visible arrows were still hidden by cards, so the diagram failed as an architecture explanation even though every relationship existed in its textual fallback.
Impact / tradeoff: The view makes the automatic path and human approval boundary traceable at a glance, while preserving all eight configured relationships and the separate static-code layer. A shortcut relationship takes a longer gutter route instead of a misleading straight line; the profile remains the sole source of the conceptual relationship data.
Verification: The isolated `a4576ec..688fc5f` artifact renders 8 components, 8 orthogonal flows, 3 responsibility bands, zero floating edge labels, and zero sampled path/card intersections at 1440×1050. At 390×844 it has no horizontal overflow and preserves ordered cards with decorative arrows intentionally hidden. Browser console: zero errors/warnings. Full tests: 49 passed.
Links: `docs/project-governance/tasks/TASK-20260905-012-architecture-story-map.md`, `BUG-20260905-017`, `src/change_passport/templates/review.js`, `design/ui-flows/architecture-story-map-agent-20260905/04-validation/current-after.png`
Needs curation: yes

ID: EVO-20260905-023
Date: 2026-09-05
Domain: architecture-understanding
Type: correction
What changed: Removed the architecture-tab success toast and separated responsibility-band headers from the first story row with a dedicated header strip.
Why now: Owner review at the actual active viewport found residual occlusion after the connector correction.
Impact / tradeoff: Tab selection remains obvious through the selected control, so suppressing its redundant toast removes a diagram obstruction without losing status information. Band descriptions now remain visible above their cards.
Verification: Desktop capture records `pageSwitchToastHidden=true` and `bandHeadersClearCards=true`; 8 flows retain zero card intersections. Mobile remains 390 px wide with no horizontal overflow and zero console warnings/errors. Full tests: 49 passed.
Links: `BUG-20260905-018`, `src/change_passport/templates/review.css`, `src/change_passport/templates/review.js`
Needs curation: yes

ID: EVO-20260905-024
Date: 2026-09-05
Domain: architecture-understanding
Type: capability
What changed: Replaced topology-specific conceptual-diagram placement with a deterministic, profile-neutral graph layout: relationship-derived ranks, a compact path mode, a layered branch/join mode, obstacle-aware orthogonal routing, and an explicit no-arrow fallback.
Why now: The owner asked whether the prior occlusion correction solved the class of problem or only the current sample. It did not cover arbitrary project topology, so the capability needed to exist before treating the architecture view as reusable.
Impact / tradeoff: A configured product/process architecture can now show multiple inputs, parallel automated work, joins, and several human decisions without adding repository-specific rules. Cyclic or unrouteable relationships stay fully visible as text but deliberately lose decorative arrows, which favors truthful readability over a false appearance of diagram completeness. Conceptual flows remain target-profile presentation data and never alter static-import, runtime, Git, or baseline facts.
Verification: The self-hosted report remains `story` mode with 8 cards, 8 arrows, 8 relation rows, and zero sampled card intersections. An adversarial 10-card/11-flow branch-merge-two-gate report is `layered` with 11 arrows and zero sampled intersections. Its 12-flow cyclic variant is `fallback` with 0 arrows, 12 relation rows, visible fallback copy, no console warnings/errors, and no 390 px overflow. Parser regression, renderer regression, full pytest (50 passed), compileall, JavaScript syntax, and diff check pass.
Links: `docs/project-governance/tasks/TASK-20260905-013-generic-concept-layout.md`, `BUG-20260905-019`, `src/change_passport/templates/review.js`, `tests/test_target_profile.py`, `design/ui-flows/generic-concept-layout-agent-20260905/04-validation/validation.md`
Needs curation: yes

ID: EVO-20260905-025
Date: 2026-09-05
Domain: architecture-understanding
Type: external-validation
What changed: Ran the first public external architecture-report exercise against FastAPI `0.136.2..0.136.3`, then corrected a topology-neutral route-planning gap that the real profile exposed.
Why now: The owner requested a well-known open-source project to see whether the diagram improved actual comprehension rather than only the Change Passport sample. FastAPI was selected because its public documentation describes routing, dependency injection, validation, OpenAPI generation, and automatic documentation as distinct but related capabilities.
Impact / tradeoff: The resulting profile gives a beginner a compact explanation of how developer declarations and an ASGI request relate to routing, dependency/model processing, path operations, API responses, and documentation. The 1,121-module static code snapshot stays distinct below it. The source remains a fixed release range; the conceptual arrows come from the versioned display profile, do not prove runtime execution, and do not change static facts. One public example is useful falsification evidence but is not a generalization result.
Verification: Fixed bare Git refs are `22b02e2` and `8206485`; static collection reports 1,121 parsed modules, 1,545 static edges, four sections, zero unclassified modules, and four changed files. Desktop browser checks see `layered`, 9 cards, 9 paths, 9 relation rows, zero sampled intersections, and zero console warnings/errors. At 390 px there is no overflow and connectors hide deliberately. Existing topology fixtures, 50 project tests, compileall, JavaScript syntax, and diff check pass.
Links: `docs/project-governance/tasks/TASK-20260905-014-fastapi-external-layout-validation.md`, `BUG-20260905-020`, `artifacts/fastapi-0.136.2-to-0.136.3/review.html`, `src/change_passport/templates/review.js`
Needs curation: yes

ID: EVO-20260906-001
Date: 2026-09-06
Domain: architecture-understanding
Type: capability
What changed: Added a third, profile-neutral reading level between a static system section and raw modules: named implementation subdomains with static-import aggregates, change overlays, optional drill-down, and explicit unmatched fallback.
Why now: Owner review of a real external report identified that a single section containing many technical responsibilities still did not expose its implementation architecture. The owner explicitly required a class-level capability rather than a FastAPI-specific correction.
Impact / tradeoff: A profile can now classify source paths with directory, exact-file, and filename-prefix rules; the generated report then summarizes only exact existing static imports between those groups. This supports finer architecture comprehension without inventing labels from a model or upgrading static imports into runtime behavior. Profiles still carry the cost of declaring useful reader-oriented names, and unmatched code remains visibly grouped instead of silently forced into a misleading label.
Verification: Live browser checks on FastAPI `0.136.2..0.136.3` showed 7 framework-core subdomains and 23 relationships; the self-hosted Change Passport sample showed 5 and 8. In both, selection and optional raw-module expansion worked with zero duplicate legacy cards; 390 px had no horizontal overflow or browser console issues. Full pytest (50 passed), compileall, JavaScript syntax, and source identity scan pass.
Links: `docs/project-governance/tasks/TASK-20260906-015-implementation-subdomain-map.md`, `BUG-20260906-001`, `src/change_passport/target_profile.py`, `src/change_passport/templates/review.js`, `design/ui-flows/implementation-subdomain-map-agent-20260906/04-validation/validation.md`
Needs curation: yes

ID: EVO-20260906-002
Date: 2026-09-06
Domain: architecture-understanding
Type: experience
What changed: Replaced the architecture tab's sequential workflow/static/module drill-down with a single expandable explorer canvas and persistent right-side explanation panel.
Why now: Owner review correctly identified that visual separation into “first layer”, “second layer”, and nested action buttons increased the comprehension burden even though all facts were present.
Impact / tradeoff: A workflow card now directly opens its profile-mapped static section and implementation subdomains in the same canvas; the inspector holds fact, boundary, relationship, and optional technical-module detail. This preserves the meaning of profile workflow mapping and static imports while avoiding a false runtime link. The relationship key remains textual rather than being placed on arrows, preserving the prior no-occlusion guarantee.
Verification: Live FastAPI browser interaction: no nested implementation buttons; direct workflow selection opens an inline section with 7 subdomains; selecting one changes the inspector to its facts and 5 static relation entries. The self-hosted sample opens 5 subdomains from its mapped workflow. At 390 px, scroll width is 375 px for a 390 px viewport; console warnings/errors are zero. Full pytest (50 passed), compileall, JavaScript syntax, and diff check pass.
Links: `docs/project-governance/tasks/TASK-20260906-016-unified-architecture-explorer.md`, `BUG-20260906-002`, `design/ui-flows/unified-architecture-canvas-agent-20260906/04-validation/screenshot-review.md`
Needs curation: yes

ID: EVO-20260906-003
Date: 2026-09-06
Domain: architecture-understanding
Type: experience
What changed: Standardized the unified architecture explorer's first reading path as a single top-to-bottom workflow spine and kept selected static implementation below it in the same canvas.
Why now: Owner review identified that the horizontal work-flow map still made a beginner scan sideways before understanding what the system is and how the selected work reaches code.
Impact / tradeoff: The view now leads from the visible system purpose through ordered workflow components to static implementation. It deliberately replaces decorative canvas arrows with the complete relationship list, because a general branching, merging, or cyclic topology cannot honestly be reduced to one sequential arrow chain. This is a presentation-only rule; it neither changes profile relations nor upgrades static imports into runtime claims.
Verification: FastAPI renders 9 full-width workflow cards in one desktop column; Change Passport renders 8. Both have no conceptual-canvas horizontal overflow or browser console errors. FastAPI selection still opens 7 static implementation subdomains below the workflow map in the same canvas. Full pytest (50 passed), compileall, JavaScript syntax, and diff checks pass.
Links: `docs/project-governance/tasks/TASK-20260906-017-vertical-architecture-reading-order.md`, `BUG-20260906-003`, `src/change_passport/templates/review.css`, `artifacts/fastapi-0.136.2-to-0.136.3/review.html`
Needs curation: yes

ID: EVO-20260909-001
Date: 2026-09-09
Domain: architecture-understanding
Type: correction
What changed: Replaced the mistaken vertical workflow list with an interactive top-down node-and-edge graph while preserving the single-canvas implementation drill-down and right-side explanation.
Why now: The owner clarified that “from top to bottom” describes the graph's direction, not permission to remove graph topology. Architecture must remain visually recognizable as a graph and directly interactive.
Impact / tradeoff: Topological ranks now progress downward and parallel nodes share a row, making branches and joins visible without repository-specific layout rules. Exact profile relationships render as orthogonal arrows only when routing is safe; cyclic, unrouteable, and narrow layouts retain clickable nodes plus complete relationship prose. The graph remains explanatory profile data and does not claim runtime order. A second node click collapses its mapped implementation, and only the actual clicked node carries selection state even when several nodes map to one static group.
Verification: FastAPI: 9 nodes, 9 arrows, 5 rows, 0 connector/card intersections, 7 subdomains on click, isolated selected state, clean second-click collapse. Change Passport: 8 nodes, 8 arrows, 7 rows, 0 intersections. Mobile: 390 px, no overflow, arrows hidden, all nodes/relationship prose retained. Persistent desktop/mobile screenshots and Python Playwright capture evidence are in the design pack. Full pytest (50 passed), compileall, JavaScript syntax, source identity scan, and diff check pass; browser console issues are zero.
Links: `docs/project-governance/tasks/TASK-20260909-018-interactive-top-down-architecture-graph.md`, `BUG-20260909-001`, `design/ui-flows/interactive-top-down-architecture-graph-agent-20260909/04-validation/current-after.png`, `src/change_passport/templates/review.js`
Needs curation: yes

ID: EVO-20260909-002
Date: 2026-09-09
Domain: software-control
Type: product-direction
What changed: The owner confirmed PRD v2.0, repositioning Change Passport from a code-change explanation surface to an AI-built software control layer for people who remain responsible for software without complete code-review ability. The first source-bound five-question contract and self-hosted text sample were then frozen without changing production UI.
Why now: AI Coding separates the ability to build software from the ability to understand or safely judge it. Recent architecture work improved technical navigation but did not establish that a non-technical owner could explain the software, the change, affected people, unknowns, and the next verification action.
Impact / tradeoff: The default product subject becomes software behavior and owner action; code entities move to progressively disclosed evidence. The contract preserves observed facts, supported interpretations, project declarations, and unknowns, and it forbids presenting recommended checks as completed tests. This requires stronger product-context inputs and real human comprehension testing; the first sample is manually edited and cannot establish automatic generation quality.
Verification: The self-hosted sample validates against the checked-in JSON Schema, contains exactly five ordered questions and three `recommended_not_run` actions, references only source claim/evidence/component IDs, matches four retained source hashes and brief/review identities, has matching JSON/Markdown answer text, and has a valid canonical control identity. The marked first screen contains zero banned implementation terms. Independent human comprehension remains pending.
Links: `docs/product/PRD-v2.0-software-control-layer-draft.md`, `docs/product/software-control-v1-contract.md`, `docs/product/samples/change-passport-self-688fc5f.software-control.md`, `TASK-20260909-019`, `TASK-20260909-020`
Needs curation: yes

ID: EVO-20260909-003
Date: 2026-09-09
Domain: software-control
Type: evaluation-capability
What changed: Added a blind 60-second comprehension-test kit for the first five-question Change Passport sample, with participant-visible material isolated from evaluator-only scoring guidance and a schema-valid untouched observation template.
Why now: The product direction makes independent non-technical retelling the first gate. Automated layout, schema, and source checks cannot supply that evidence, but the absence of a reproducible test kit should not leave the gate informal or invite coached/self-scored results.
Impact / tradeoff: A real evaluator can now run the same five prompts, preserve verbatim answers, record hints and timing, apply a 4/5 rule, and fail critical misunderstandings such as converting unknown user impact into confirmed no impact. The kit deliberately records `not_run` until a qualified participant exists, so it advances readiness without manufacturing validation.
Verification: Observation JSON validates against its schema; all five answer slots remain blank and unscored; participant material has zero rubric, threshold, source-identity, path, or banned technical-term leaks; evaluator guidance contains all prompts and critical overrides; every file hash and the source control identity match the evaluation manifest.
Links: `docs/product/evaluations/change-passport-self-688fc5f/participant-card.md`, `docs/product/evaluations/change-passport-self-688fc5f/evaluator-guide.md`, `docs/product/evaluations/change-passport-self-688fc5f/evaluation-manifest.json`, `TASK-20260909-021`
Needs curation: yes

ID: EVO-20260909-004
Date: 2026-09-09
Domain: software-control
Type: product-language
What changed: Promoted software-owner language from a copywriting preference to a versioned data-contract requirement. The first screen now leads with one change headline, likely user impact, and residual risk; abstract changes receive a concrete before/after comparison; affected people, unknown verification, owner checks, and detailed test construction are separate data fields.
Why now: Direct owner review showed that a valid five-question structure could still stop at engineer-readable natural language. A target user should not have to decode relation, source-position, revalidation, runtime, or baseline terminology before understanding what changed and what decision remains.
Impact / tradeoff: The contract carries more explicit presentation semantics and some sourced conclusions repeat information from the five answers, but future renderers can preserve a reliable shallow-to-deep hierarchy without project-specific copy branches. Technical precision remains available below the first screen, and each summary statement retains its own evidence state so simpler language cannot strengthen a claim.
Verification: Schema validation, canonical identity, source and evaluation hashes, summary/five-question parity, old/new example invariants, Q3/Q4 separation, participant detail isolation, and two first-screen term scans pass. No production renderer or source code changed, and no human pass is claimed.
Links: `docs/product/PRD-v2.0-software-control-layer-draft.md`, `docs/product/software-control-v1-contract.md`, `docs/product/schemas/software-control.v1.schema.json`, `docs/product/samples/change-passport-self-688fc5f.software-control.json`, `TASK-20260909-022`, `BUG-20260909-003`
Needs curation: yes

ID: EVO-20260909-005
Date: 2026-09-09
Domain: software-control
Type: product-structure
What changed: Defined the second screen as an owner-language software map distinct from the first-screen change summary. The same source-bound model now carries a complete top-to-bottom workflow, one directly supported current-change location, and a generic right-inspector contract for every node.
Why now: The owner's “第二屏的呢” exposed that simplifying the change summary alone does not help someone understand the software as a whole. The second screen must create a durable mental model and show how one change fits into it.
Impact / tradeoff: The working-map contract becomes richer and requires each project profile/projection to supply owner meaning, visible result, current change, affected people, unknowns, and checks for every node. This adds authoring work but prevents the renderer from inventing explanations or falling back to modules. The map remains project-declared and does not claim observed runtime order.
Verification: The standalone second-screen candidate contains all 8 source-bound nodes and 8 flows, highlights one directly evidenced changed node, places technical IDs after the owner layer, and passes rejected-term scans. The revised Schema, canonical control identity, evaluation bindings, and file hashes pass. Production click behavior remains pending.
Links: `docs/product/samples/change-passport-self-688fc5f.software-map.md`, `docs/product/software-control-v1-contract.md`, `docs/product/PRD-v2.0-software-control-layer-draft.md`, `TASK-20260909-023`, `BUG-20260909-004`
Needs curation: yes

ID: EVO-20260909-006
Date: 2026-09-09
Domain: software-control
Type: production-projection
What changed: Added a generic optional `software-control.v1` finalize input and projected it into two owner-facing screens: a conclusion-first change view and one clickable top-to-bottom software working map with a persistent owner-language inspector. Existing engineering evidence and static implementation views remain available only after explicit disclosure, and the old report remains the default fallback when no control document is supplied.
Why now: The semantic candidates established the correct beginner-first hierarchy, but the production report still opened with engineering-oriented summaries and architecture. The owner confirmed the direction and asked to continue to implementation.
Impact / tradeoff: Any target repository can provide the same versioned contract without renderer branches, and the renderer no longer needs to invent project explanations. This adds a separately validated input and more HTML/CSS/JavaScript surface. It does not automate generation of that input, prove runtime behavior, or replace independent human comprehension testing.
Verification: 57 pytest tests pass, including canonical identity tampering, missing-node flow, changed-node evidence, safe embedding, fallback, and optional end-to-end pipeline cases. Python compilation and JavaScript syntax pass. The self-hosted artifact regenerates with control identity `9608afd53e26cdd07a52ac23f2f6e9f9ed5ae96dcef229725798089337658967`. Real screenshot review remains pending because the current in-app browser blocks local file URL interaction; the barrier was not bypassed.
Links: `src/change_passport/software_control.py`, `src/change_passport/templates/review.html`, `src/change_passport/templates/review.js`, `src/change_passport/templates/review.css`, `TASK-20260909-024`
Needs curation: yes

ID: EVO-20260909-007
Date: 2026-09-09
Domain: software-control
Type: product-hierarchy
What changed: Reframed the production owner view around a ten-second decision hierarchy and a progressive software map. The concrete outcome now precedes the internal concept; three compact owner answers precede a collapsed five-question explanation; each evidence state explains itself; and one source-declared four-step graph expands to the complete eight-step graph in the same canvas.
Why now: Owner review showed that correct plain-language content can still feel like an audit report when repeated at equal weight, and that an eight-node default graph asks a beginner to learn the product before locating the change.
Impact / tradeoff: A software owner can scan what changed, likely impact, remaining risk, and next action before choosing depth. Four overview nodes must partition all detail nodes exactly once, preventing renderer-specific summarization or lost steps. This adds contract authoring and validation requirements, while deliberately leaving automatic generation, persistent check state, and human comprehension unproven.
Verification: 60 pytest tests pass. PowerShell Schema validation, canonical/source identity, evaluation manifest hashes, regenerated artifact identity, HTML parsing, offline-resource checks, Python compilation, JavaScript syntax, and diff checks pass. The source and renderer contain no FastAPI/self-sample routing branch. Real screenshot acceptance remains pending because the current in-app browser blocks local `file://` interaction.
Links: `docs/product/PRD-v2.0-software-control-layer-draft.md`, `docs/product/software-control-v1-contract.md`, `docs/product/schemas/software-control.v1.schema.json`, `src/change_passport/software_control.py`, `src/change_passport/templates/review.js`, `TASK-20260909-025`, `BUG-20260909-005`
Needs curation: yes

ID: EVO-20260909-008
Date: 2026-09-09
Domain: software-control
Type: cross-project-validation
What changed: Added a fixed-revision vLLM target profile and owner-language control sample, then generated the same four-step-to-eight-step interactive report over a substantially larger public repository without adding project-specific renderer behavior.
Why now: The self-hosted sample was intentionally favorable because the product knows its own change. The owner requested a more complex project to test whether the shallow owner experience survives thousands of modules and relationships.
Impact / tradeoff: The generic contract classified all 4,501 supported modules into 9 profile-declared implementation groups and located one two-file change inside “准备模型输入”, while keeping 21,091 static relationships as delayed technical evidence. The sample improves portability evidence but does not prove automatic profile generation, runtime correctness, visual comprehension, or performance at arbitrary scale. It also exposed missing partial-clone progress and a 12.9 MB single-file report.
Verification: Fixed commit identities, two-file patch, target status fingerprint preservation, zero unclassified supported modules, profile hash binding, software-control Schema/canonical/source binding, 4/8 exact map coverage, one changed-node evidence binding, offline HTML, absence of vLLM-specific renderer strings, 60 tests, compileall, JavaScript syntax, and diff checks pass.
Links: `examples/target-profiles/vllm.v1.json`, `docs/product/samples/vllm-a69e75b-to-a85d073.software-control.json`, `docs/project-governance/tasks/TASK-20260909-026-vllm-complex-project-validation.md`, `BUG-20260909-006`, `BUG-20260909-007`
Needs curation: yes

ID: EVO-20260910-009
Date: 2026-09-10
Domain: software-control
Type: owner-map-clarity
What changed: Tightened the external-project owner-map language so interface types are presented as ways requests enter, scheduling is presented as request/cache/execution coordination rather than model selection, and output can be complete or streaming. Added a generic legend that explains interactive selection and AI-change overlay without relying on color alone.
Why now: Direct owner review found that the first portable vLLM map was visually readable but still allowed three incorrect software mental models and one ambiguous interaction state.
Impact / tradeoff: The target profile becomes more source-faithful without adding topology or renderer special cases, while every owner map gains a small persistent legend. The legend consumes a narrow strip of space but removes a first-use interpretation burden; optional streaming wording avoids overclaiming universal runtime behavior.
Verification: Fixed-vLLM source check, profile hash binding, control canonical/source identity, 4/8 coverage, one changed-step binding, regenerated artifact copy and offline checks, generic renderer scan, target preservation, 60 tests, compileall, JavaScript syntax, and diff checks pass. Computer Use visual acceptance remains pending after repeated browser-provider connection failure.
Links: `docs/project-governance/tasks/TASK-20260910-027-vllm-owner-map-wording-and-state-legend.md`, `BUG-20260910-008`, `examples/target-profiles/vllm.v1.json`, `src/change_passport/templates/review.html`, `src/change_passport/templates/review.css`
Needs curation: yes

ID: EVO-20260910-011
Date: 2026-09-10
Domain: project-governance
Type: operations
What changed: Recorded that EVO-20260910-010 was physically inserted before older retained evolution records when a repeated append anchor matched mid-file.
Why now: The evolution ledger is append-only, so the misplaced record must remain and its chronology must be corrected by a later linked entry rather than moving or deleting it.
Impact / tradeoff: The implementation record remains intact; EVO IDs, dates, and this explicit relationship—not physical position—define chronology for EVO-20260910-010.
Verification: `rg -n "EVO-20260910-010|EVO-20260910-011"` shows the retained implementation record and this corrective record at the current tail.
Links: `EVO-20260910-010`, `BUG-20260910-011`, `TASK-20260910-028`
Needs curation: yes

ID: EVO-20260910-012
Date: 2026-09-10
Domain: software-control
Type: owner-experience
What changed: Reorganized the generated report around one compact two-view header, a dominant change conclusion plus three owner decisions, and a top-to-bottom software workflow that starts with four steps and expands only the selected step's mapped details. Changed badges, inspector wording, and selected-state metadata now share one `change_state` projection.
Why now: The owner's references demonstrated a friendlier decision-first and workflow-plus-inspector experience, while review identified that copying their visual state and explanatory text independently could create a trust-breaking contradiction.
Impact / tradeoff: A non-coder sees less default material and keeps the current change located inside a stable software mental model. Detail groups with few nodes can leave deliberate whitespace, and the report still requires source-bound owner copy rather than inventing a polished story. Reference-only application navigation and fake metadata remain out of scope.
Verification: Real Edge interaction and screenshots pass at 1440×1000 and 390×844 with four overview nodes, one changed node, selected/changed/inspector parity, closed deeper disclosures, no horizontal overflow, and zero console problems. Full 65-test, compileall, JavaScript syntax, offline/payload, and diff checks pass. Human comprehension and runtime behavior remain not run.
Links: `design/ui-flows/owner-decision-expandable-flow-agent-20260910/`, `src/change_passport/templates/review.html`, `src/change_passport/templates/review.css`, `src/change_passport/templates/review.js`, `TASK-20260910-029`, `BUG-20260910-012`
Needs curation: yes

ID: EVO-20260910-013
Date: 2026-09-10
Domain: software-control
Type: owner-map-interaction
What changed: Recast owner-map drill-down as a local inline expansion. The source-declared four-step overview remains the permanent graph; one clicked step reveals its mapped details in place, can be collapsed by clicking again, and keeps the right explanation synchronized.
Why now: Direct owner use showed that replacing the overview forced a false choice between global understanding and local detail, adding a return-navigation burden to a beginner-first control surface.
Impact / tradeoff: Owners retain “where am I in the whole software?” while inspecting “what happens inside this step?”. Only one group opens at a time to control page length. Large mapped groups can still create a tall page, and branched detail topology needs a future real sample before further generalization.
Verification: Four-step persistence, inline membership, same-node collapse, group switching, inspector parity, global-link retention, obstacle routing, narrow fallback, technical-payload opening, no-network report checks, 65 tests, compileall, JavaScript syntax, diff checks, and zero-console Edge captures pass. Human comprehension and target runtime behavior remain untested.
Links: `design/ui-flows/inline-expandable-owner-map-agent-20260910/`, `src/change_passport/templates/review.html`, `src/change_passport/templates/review.css`, `src/change_passport/templates/review.js`, `TASK-20260910-030`, `BUG-20260910-013`
Needs curation: yes

ID: EVO-20260910-014
Date: 2026-09-10
Domain: software-control
Type: responsive-owner-explanation
What changed: Made the expanded five-question explanation structurally responsive at both the card-content and column-flow levels. Audience/status headings now sit above full-width explanations, while the primary and secondary question stacks lay out independently.
Why now: Direct owner inspection exposed a layout that passed prior 1440/390 smoke checks but failed at the real content width because nested minimum columns, not viewport width alone, controlled readability.
Impact / tradeoff: User-impact explanations remain readable and left-column content no longer inherits right-card height. At intermediate widths the secondary column stays compact until the existing 1080 px breakpoint, preserving the wide hierarchy without adding another breakpoint.
Verification: 1560, 1100, and 390 px Edge captures, measured explanation widths/heights, fixed 14 px independent-column gaps, zero overflow/console problems, regenerated artifact validation, 65 tests, compileall, JavaScript syntax, and diff checks pass. Human comprehension remains untested.
Links: `design/ui-flows/owner-audience-responsive-agent-20260910/`, `src/change_passport/templates/review.css`, `src/change_passport/templates/review.js`, `TASK-20260910-031`, `BUG-20260910-014`
Needs curation: yes

ID: EVO-20260910-015
Date: 2026-09-10
Domain: evidence-contract
Type: model-integration
What changed: Added an explicit loopback-only Ollama candidate-writer to the one-command analysis path. It receives only the frozen generator packet, produces schema-constrained raw claims, records actual model/timing/token/hash metadata, and remains downstream of deterministic topology and upstream of deterministic validation.
Why now: The owner asked to test real model assistance after confirming that deterministic tooling alone could not automatically produce sufficiently specific owner language.
Impact / tradeoff: On the fixed vLLM sample, the local 4B model changed a generic “2 files / two areas” summary into a concrete explanation of the offline multimodal special-token default and duplicate-marker risk. Total time rose from 4.137 to 47.275 seconds, and the result still contains engineering terminology; model generation therefore remains optional and unapproved as final owner copy.
Verification: 72 tests, compileall, JavaScript syntax, diff checks, request isolation, loopback enforcement, failure receipt, two real Ollama runs, model token/timing receipts, evidence-validator counts, and exact target status-hash preservation pass.
Links: `src/change_passport/model_adapter.py`, `src/change_passport/pipeline.py`, `src/change_passport/cli.py`, `ADR-0003`, `TASK-20260910-032`, `BUG-20260910-015`
Needs curation: yes

ID: EVO-20260910-016
Date: 2026-09-10
Domain: evidence-contract
Type: provider-interface
What changed: Replaced the provider-specific local-model entrypoint with one user-configured OpenAI-compatible Chat Completions interface. Provider/model/base URL and structured-output capability now come from a strict runtime config; credentials remain environment-only; deterministic analysis remains the no-network default.
Why now: The owner clarified that Change Passport should provide an interface, not choose or run a local model, and that users must be able to configure domestic or international compatible services after installation.
Impact / tradeoff: One adapter now covers strict JSON Schema, JSON Object, and prompt-only compatibility levels without vendor branches. This broadens provider choice but cannot guarantee that every service advertising compatibility implements identical response formats. A visual settings surface remains future work.
Verification: 73 tests, compileall, JavaScript syntax, CLI help, diff checks, provider-name removal scan, configuration rejection, three mocked protocol modes, secret redaction, missing-key fail-closed behavior, and pipeline/CLI routing pass. No real model request was executed.
Links: `src/change_passport/model_adapter.py`, `examples/model-provider.template.json`, `README.md`, `ADR-0004`, `TASK-20260910-033`, `BUG-20260910-016`
Needs curation: yes

ID: EVO-20260910-017
Date: 2026-09-10
Domain: software-control
Type: cross-project-semantic-validation
What changed: Added VideoFactory as a fixed-range, read-only external validation sample for the unchanged automatic analysis path. The run demonstrates that speed, Git completeness, static coverage, evidence validation, and a compact report can all pass while the beginner-facing project model remains materially wrong.
Why now: The owner asked to parse a different real project after adding configurable model support, specifically to see whether the tool-only path generalizes without project-specific tailoring.
Impact / tradeoff: The sample gives a strong regression target because VideoFactory declares a concrete production workflow in its README and has distinct planning, rendering, QA, and delivery subsystems. It also shows that `0 unclassified` is not a sufficient quality metric when broad overlapping rules can classify nearly everything into the wrong area.
Verification: Fixed-range analysis succeeded in 0.806 seconds with 87 nodes, 158 edges, 0 parse failures, a 298,829-byte self-contained report, and an unchanged target status hash. Manual semantic inspection rejected the auto-generated purpose, four-step map, and 72-module entry grouping; no VideoFactory-specific correction was applied.
Links: `artifacts/videofactory-58d2149-to-d6594e3/`, `TASK-20260910-034`, `BUG-20260910-017`
Needs curation: yes

ID: EVO-20260910-018
Date: 2026-09-10
Domain: software-control
Type: declaration-code-reconciliation
What changed: Automatic project understanding now treats bounded root README material as a source-bound declaration and reconciles its purpose, individual workflow steps, and declared order independently against fixed-version code anchors. The owner map exposes `代码支持`, `仅项目说明`, `自动候选`, and order-state labels while preserving runtime as unknown.
Why now: The owner pointed out that reading existing documentation is useful but unsafe when README content is stale or wrong, and that a general solution must be tested on more than one project.
Impact / tradeoff: VideoFactory now yields a recognizable seven-step production workflow without a target-name exception, while vLLM and FastAPI remain safely generic where declaration evidence is weaker. Exact-path fallbacks make generated profiles larger, and the bounded Markdown extractor intentionally misses unsupported documentation formats rather than over-claiming.
Verification: 78 automated tests, compileall, JavaScript syntax, diff checks, a clean repository-name scan, and three fixed-project runs pass. Real Edge interaction at desktop and 390 px confirms four persistent overview nodes, inline expansion/collapse, visible evidence badges, and no horizontal overflow. Target repositories remain unchanged.
Links: `src/change_passport/project_declarations.py`, `src/change_passport/auto_draft.py`, `src/change_passport/software_control.py`, `TASK-20260910-035`, `BUG-20260910-017`, `BUG-20260910-018`, `BUG-20260910-019`
Needs curation: yes

ID: EVO-20260910-019
Date: 2026-09-10
Domain: software-control
Type: cross-tab-owner-journey
What changed: Connected the decision-oriented change view to the location-oriented system view. A uniquely mapped change now opens its containing four-stage group, selects and focuses the exact detail step, scrolls it into view, and shows a short textual arrival marker. The system inspector now presents responsibility, predecessor/input context, result, successor/output context, change location, and evidence before optional impact/check detail.
Why now: Owner review identified that the stable tab names already represent an event model and a world model, but the missing transition forced users to rebuild the mapping manually and made the two tabs feel like duplicate reports.
Impact / tradeoff: The common journey becomes `发生了什么 → 现在怎么办 → 它在整个软件哪里` without weakening evidence identity. Reports with ambiguous mappings deliberately show no shortcut. The system view derives relationship language from existing map edges, so it can describe declared/static context but still cannot assert runtime data flow.
Verification: 78 tests, compileall, JavaScript syntax, diff checks, clean repository-name scan, desktop/390 px Edge interaction, focus/scroll/arrival-state assertions, unmapped FastAPI absence, and zero console/overflow problems pass. Independent comprehension remains untested.
Links: `src/change_passport/templates/review.js`, `src/change_passport/templates/review.css`, `README.md`, `TASK-20260910-036`, `BUG-20260910-020`
Needs curation: yes

ID: EVO-20260910-020
Date: 2026-09-10
Domain: software-control
Type: behavior-semantic-coverage
What changed: The deterministic path now carries conservative source-bound behavior signals for newly added exception raises, explicit non-zero returns, and callable-signature changes into the owner report. It distinguishes missing semantic interpretation from a negative impact finding and derives separate normal/stop-condition checks.
Why now: A VideoFactory fixed-range review showed that the tool already possessed the decisive patch lines but hid them behind file counts and architecture placement, causing a high-value owner warning to disappear without any missing Git or graph data.
Impact / tradeoff: Owners receive a more useful warning without requiring a model or inventing runtime facts. Coverage is intentionally narrow and Python-focused; signal presence may indicate intentional defensive behavior and therefore never upgrades to breaking or user impact by itself.
Verification: 82 tests, compileall, JavaScript syntax, diff checks, generic known-answer fixtures, and the regenerated fixed VideoFactory report pass. The real report now maps the primary signal to `检查视频质量`, says `还没判断`, and recommends normal plus stop-condition checks in 0.784 seconds with warm cache.
Links: `src/change_passport/behavior_signals.py`, `src/change_passport/auto_draft.py`, `tests/test_behavior_signals.py`, `TASK-20260910-037`, `BUG-20260910-021`
Needs curation: yes

ID: EVO-20260910-021
Date: 2026-09-10
Domain: distribution
Type: guided-alpha-entry
What changed: Added a packaged, dependency-free local first-run page that turns repository path, two human-readable commit choices, and optional task context into the existing deterministic report without requiring a hand-authored manifest. It includes durable progress, registered report access, a Windows source launcher, build checksums, and clean-wheel installation guidance.
Why now: The current report had become useful enough for invited evaluation, but installation and manifest/Git terminology still prevented the intended software-owner audience from reaching it independently.
Impact / tradeoff: The product now has a real entry experience while preserving target read-only and evidence authority. The Alpha deliberately stays loopback-only and model-free on the beginner path; native installers, automatic updates, cloud collaboration, and public distribution remain out of scope.
Verification: 88 tests pass, including token/origin/output guards and a complete HTTP analysis journey. The wheel contains all onboarding assets, a clean Python 3.12 environment starts it successfully, and real browser checks at 1280 px and 390 px show no horizontal overflow or console errors.
Links: `src/change_passport/onboarding.py`, `src/change_passport/templates/onboarding.html`, `docs/INSTALL.md`, `TASK-20260910-038`
Needs curation: yes

ID: EVO-20260910-022
Date: 2026-09-10
Domain: distribution
Type: product-identity
What changed: Renamed the distributable product, Python package, import namespace, CLI, guided UI, cache, and current self-profile to PlainChange while retaining Change Passport as the evidence-backed generated artifact and stable report protocol family. Added direct `plainchange analyze .`, shorthand `plainchange .`, and the distinct web command `plainchange serve`.
Why now: The owner decided to open source the Alpha but found the former product name occupied, then clarified that a global Chinese-only translation and `start` server command would misstate both the international product and the user action.
Impact / tradeoff: The brand can grow beyond one report while existing artifact schemas retain continuity. The pre-public Alpha intentionally makes a clean package/CLI break; historical evidence keeps its original names and paths where rewriting would falsify history.
Verification: Distribution, clean-install, direct-project CLI, shorthand CLI, loopback UI, report generation, browser branding, full tests, compilation, JavaScript syntax, package-content, and checksum checks are required before the local Alpha tag.
Links: `ADR-0005`, `pyproject.toml`, `src/plainchange/cli.py`, `src/plainchange/onboarding.py`, `README.md`, `TASK-20260910-038`
Needs curation: yes
