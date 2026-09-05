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
