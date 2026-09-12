# Bug source log

This is an append-only source ledger. Record every discovered or fixed bug; severity controls urgency, not whether it is retained. Root cause may be unknown. Correct prior facts with a linked later record instead of deleting them.

## Entry template

```text
ID: BUG-YYYYMMDD-001
Date: YYYY-MM-DD
Status: discovered | fixed | deferred | superseded
Domain: <domain>
Severity: low | medium | high | critical
Symptom fingerprint: <short stable description>
Trigger / reproduction: <known facts only>
Impact: <known impact>
Root cause: unknown | <confirmed cause>
Change made: <fix, or none>
Verification: <commands / observations / not run>
Links: <files, tasks, issues, commits, related BUG IDs>
Follow-up: <needed prevention or empty>
```

---

<!-- Append new entries below this line. -->

ID: BUG-20260904-001
Date: 2026-09-04
Status: fixed
Domain: project-governance
Severity: low
Symptom fingerprint: Evolution entries are complete but EVO-003 appears physically before EVO-002.
Trigger / reproduction: Read `docs/project-governance/EVOLUTION.md` after appending the implementation closeout record; the entry sequence was 001, 003, 002.
Impact: No implementation or evidence was lost, but a reader could mistake physical order for decision order.
Root cause: An ambiguous patch anchor matched an earlier repeated `Needs curation: no` line instead of the end of the append-only ledger.
Change made: Preserved all original ledger records and appended EVO-20260904-004 as a corrective sequencing note; future ledger appends must use the unique current tail as their anchor.
Verification: `rg -n "^ID: (BUG|EVO)-" docs/project-governance/BUGLOG.md docs/project-governance/EVOLUTION.md` shows the retained records and the corrective record at the end.
Links: `docs/project-governance/EVOLUTION.md`, `docs/project-governance/tasks/TASK-20260904-001-phase0-evidence-spine.md`, `EVO-20260904-004`
Follow-up: Use a unique EOF anchor for every append-only ledger edit.

ID: BUG-20260904-002
Date: 2026-09-04
Status: discovered
Domain: evidence-rendering
Severity: medium
Symptom fingerprint: A precise evidence-gap explanation becomes a generic attention sentence even when an unknown claim is accepted.
Trigger / reproduction: Finalize the first real DigitalSelf sample; `attention.test-evidence` has a precise `original_text`, `claim_type=unknown`, and status `accepted`, but its rendered `text` is replaced with the section-wide `UNKNOWN_TEXT` value.
Impact: The validator remains safe and preserves limitations/next-check, but the main human-readable sentence no longer explains that the missing authority is an actual test receipt rather than a generic evidence gap.
Root cause: `validate_raw_brief` unconditionally replaces every raw `claim_type == "unknown"` text with `UNKNOWN_TEXT[section]`, regardless of cited evidence, scope, or whether the original statement itself is a bounded epistemic claim.
Change made: None in this approved run; the behavior was documented without expanding scope into a validator redesign.
Verification: Raw input, validated `brief.json`, and rendered `brief.md` were compared after finalize; validator summary was 8 accepted, 0 downgraded, 0 rejected.
Links: `src/change_passport/validator.py`, `artifacts/digitalself-430c342/blind-review.md`, `docs/project-governance/tasks/TASK-20260904-002-first-digitals-self-sample.md`
Follow-up: Design deterministic, provenance-aware unknown templates that state the missing authority without trusting arbitrary model prose; add regression tests before changing rendering.

ID: BUG-20260904-003
Date: 2026-09-04
Status: fixed
Domain: project-governance
Severity: low
Symptom fingerprint: PRD revision state initially marked the idea unconfirmed while leaving the revised PRD confirmed.
Trigger / reproduction: Run the DigitalSelf UI workflow status command immediately after the v1.1 state edit; it reported `idea.confirmed=false` and `prd.confirmed=true` despite the revision contract requiring the opposite.
Impact: If left unfixed, the workflow gate could incorrectly permit M1.5 work while treating the already confirmed idea as pending. No implementation started under the incorrect state.
Root cause: A JSON patch used a non-unique `confirmed=true` anchor and changed the first stage occurrence instead of the PRD stage.
Change made: Restored `idea.confirmed=true`, set `prd.confirmed=false`, and appended a correction event to the DigitalSelf UI-flow run log.
Verification: Re-run `workflow-status --feature ai-coding-session-review --json` and require idea confirmed true, PRD confirmed false, and revision `1.1-draft`.
Links: `D:\Dev\Projects\DigitalSelf\design\ui-flows\ai-coding-session-review\workflow.state.json`, `D:\Dev\Projects\DigitalSelf\design\ui-flows\ai-coding-session-review\run-log.md`, `TASK-20260904-003`
Follow-up: Use stage-qualified JSON anchors for future workflow-state edits.

ID: BUG-20260904-004
Date: 2026-09-04
Status: fixed
Domain: architecture-rendering
Severity: medium
Symptom fingerprint: The first real M1.5 map contained 46 one-hop/context nodes and prioritized consumers by opaque node hash, making the graph too large and test-heavy for at-a-glance review.
Trigger / reproduction: Prepare immutable DigitalSelf range `d78f78b..430c342` with the initial M1.5 renderer; `analysis_stats.displayed_nodes` was 46 and many test modules appeared before production consumers.
Impact: The JSON remained evidence-backed, but the human main view did not satisfy the graph-first comprehension goal.
Root cause: The local neighborhood was bounded by depth but had no visual node budget or human-meaningful priority order.
Change made: Keep every changed node visible, cap the normal display at 14 nodes, prioritize production consumers before tests/scripts, add interface/responsibility change detail, and retain every folded node ID in `display_omissions` plus an explicit Mermaid folded node.
Verification: The same DigitalSelf range now reports 14 displayed and 32 folded nodes; all 7 changed nodes remain visible. `test_display_budget_keeps_changed_node_and_reports_folded_consumers` covers the rule.
Links: `src/change_passport/architecture.py`, `tests/test_architecture.py`, `artifacts/digitalself-430c342-m15/architecture-map.mmd`, `TASK-20260904-003`
Follow-up: Owner comprehension review is still required; a passing renderer test does not prove the chosen budget is subjectively sufficient.

ID: BUG-20260904-005
Date: 2026-09-04
Status: fixed
Domain: architecture-impact
Severity: medium
Symptom fingerprint: The first real delta produced 100 impact rows and duplicate dashed arrows because the same importer edge was collected independently from before and after snapshots.
Trigger / reproduction: Inspect the initial `d78f78b..430c342` architecture delta and Mermaid; unchanged importer relations appeared twice with different commit-scoped evidence refs.
Impact: The graph overstated the number of distinct impact paths and added redundant reverse arrows on top of existing import edges.
Root cause: Impact equality included the evidence-ref list instead of using the stable changed-node/consumer/relation identity.
Change made: Deduplicate by `(changed_node_id, impacted_node_id, relation)`, merge evidence refs, retain 50 unique paths in JSON, and use the existing before/after import edges plus impacted node styling instead of separate reverse arrows.
Verification: The same real sample now reports 50 unique impact paths with no dashed impact-arrow loop; JavaScript one-hop and full architecture tests pass.
Links: `src/change_passport/architecture.py`, `tests/test_architecture.py`, `artifacts/digitalself-430c342-m15/architecture-delta.json`, `TASK-20260904-003`
Follow-up: Treat these as static dependency consumers, not proof of runtime or behavioral impact.

ID: BUG-20260904-006
Date: 2026-09-04
Status: fixed
Domain: baseline-authority
Severity: high
Symptom fingerprint: A baseline decision named only `proposal_id`, so candidate content could be altered after the decision template was created without invalidating that decision.
Trigger / reproduction: Create a proposal and decision template, alter candidate-baseline content while retaining the proposal ID, and attempt approval with the original decision.
Impact: An attributable human decision could be applied to baseline content that the reviewer did not actually inspect.
Root cause: The proposal lacked a content hash, the decision did not bind that hash, and baseline loading trusted the stored baseline ID instead of recomputing it from content.
Change made: Recompute baseline identity on load, add deterministic `proposal_sha256`, require the decision to bind the same hash, and carry the decision/hash reference into the approved baseline source refs.
Verification: `test_approval_requires_attributable_decision_and_rejects_proposal_tamper` approves an unchanged proposal and rejects content tampering; the real proposal and decision template now contain the same SHA-256.
Links: `src/change_passport/architecture.py`, `tests/test_architecture.py`, `artifacts/digitalself-430c342-m15/architecture-baseline.proposal.json`, `TASK-20260904-003`
Follow-up: Keep proposal identity content-addressed if later schema versions add optional review metadata.

ID: BUG-20260904-007
Date: 2026-09-04
Status: fixed
Domain: architecture-rendering
Severity: low
Symptom fingerprint: Chinese diagram localization left `+function` and similar machine-oriented prefixes on the second and later interfaces of a new module.
Trigger / reproduction: Render a node whose change detail contains multiple interfaces such as `new module; +function:first, +method:Example.run`.
Impact: The graph remained correct but its human-facing annotation was only partially localized and harder to scan.
Root cause: The renderer removed the leading marker from the full comma-separated string instead of parsing and localizing each interface entry.
Change made: Parse each interface entry independently and render `function`, `class`, and `method` as `函数`, `类`, and `方法` while preserving the actual symbol name.
Verification: `test_bootstrap_emits_one_validated_graph_and_separate_pending_proposal` now covers a multi-interface localized label and rejects residual `+function`/`+method` markers.
Links: `src/change_passport/architecture.py`, `tests/test_architecture.py`, `artifacts/digitalself-430c342-m15/architecture-map.mmd`, `TASK-20260904-003`
Follow-up: Keep future machine relation/status values separate from their human display labels.

ID: BUG-20260904-008
Date: 2026-09-04
Status: fixed
Domain: project-governance
Severity: low
Symptom fingerprint: EVO-20260904-009 appeared between records 005 and 006 instead of at the physical end of the append-only evolution ledger.
Trigger / reproduction: Append a record using the non-unique line `Needs curation: yes` as the patch anchor when earlier records contain the same line.
Impact: The experiment record remains intact, but physical file position no longer represents chronology for records 006 through 010.
Root cause: The append patch used a repeated generic anchor rather than the unique final fields of EVO-20260904-008.
Change made: Retained the original entry as required by append-only governance and appended EVO-20260904-010 at the true end to make ID/link chronology authoritative.
Verification: `rg` shows EVO-20260904-010 after EVO-20260904-008 at EOF and links it explicitly to EVO-20260904-009 and this bug record.
Links: `docs/project-governance/EVOLUTION.md`, `EVO-20260904-009`, `EVO-20260904-010`
Follow-up: Use the unique final record ID plus its final fields as the anchor for future ledger appends.

ID: BUG-20260904-009
Date: 2026-09-04
Status: fixed
Domain: beginner-review
Severity: low
Symptom fingerprint: An evaluator-authored holdout exposed the internal authority enum `actual_test_receipt` and awkward double-colon punctuation in the beginner-facing attention card.
Trigger / reproduction: Finalize the unseen order-validation holdout with only `test.self_report` evidence while the raw claim asserts that tests passed.
Impact: The validator correctly downgraded the test claim, but a non-coder would still encounter an internal evidence enum on the default page.
Root cause: The beginner excerpt preserved the validator's safe downgrade reason without applying the presentation-only terminology mapping used for other technical terms.
Change made: Translate the exact missing-receipt reason to `没有可核对的独立测试收据`, keep the original enum in the technical claim details, and normalize adjacent Chinese whitespace.
Verification: `test_beginner_summary_hides_internal_authority_enum` covers the projection; the unseen holdout still reports 4 accepted, 1 downgraded, 0 rejected and keeps the target repository unchanged.
Links: `src/change_passport/review_model.py`, `tests/test_review_model.py`, `artifacts/evaluator-holdout-001/output/beginner-review.json`, `TASK-20260904-004`
Follow-up: Add future validator enums to the presentation vocabulary only when they first appear in a user-visible path; never alter the underlying technical record.

ID: BUG-20260904-010
Date: 2026-09-04
Status: fixed
Domain: project-governance
Severity: low
Symptom fingerprint: The architecture-tab feasibility event was inserted near the start of `run-log.md` and carried a drafted timestamp later than the actual clock.
Trigger / reproduction: Append through a repeated `implementation_blocked: true` patch anchor and type a future minute instead of reading the current UTC value before the patch.
Impact: Feasibility evidence remained intact, but physical event order and the original timestamp could mislead later workflow reconstruction.
Root cause: The append patch used a generic repeated anchor and a manually estimated timestamp, recurring after BUG-20260904-008's anchor-selection lesson.
Change made: Retained the original run-log record, appended an authoritative correction at the true end with the observed UTC time and final PRD SHA-256, and bound TASK-20260904-005 to that final hash.
Verification: The final run-log event names the misplaced header, observed event time, superseded hash, final hash, and feasibility metrics; the task points to the same final PRD hash.
Links: `D:\Dev\Projects\DigitalSelf\design\ui-flows\ai-coding-session-review\run-log.md`, `TASK-20260904-005`, `BUG-20260904-008`
Follow-up: Read the current UTC time first and anchor append patches with the unique final event title plus multiple final fields.

ID: BUG-20260905-011
Date: 2026-09-05
Status: fixed
Domain: architecture-rendering
Severity: medium
Symptom fingerprint: Selecting a high-degree system section produced overlapping curves, hidden arrow endpoints, and detached count labels, so the relationship direction could not be scanned reliably.
Trigger / reproduction: Open the formal DigitalSelf review, switch to `整体架构`, and select `用户入口与交互`, which has 3 incoming and 6 outgoing section-edge bundles.
Impact: The complete machine snapshot remained correct, but the main human architecture view recreated the dense graph-reading burden that the beginner-first product direction was intended to remove.
Root cause: The selected state reused the overview's fixed nine-card grid and center-to-center routing. Distributed boundary ports improved endpoints but could not prevent nine curves and labels from converging around a corner card.
Change made: Keep the quiet nine-section overview, but render a selected section as a deterministic three-column focus map with one card and one path per original relationship, counts inside the cards, explicit Chinese direction headings, and single-edge isolation.
Verification: The user-entry sample renders 9 named relationship cards and 9 non-crossing SVG paths at 1440 px; single-edge isolation, module drill-down, return state, 390 px no-overflow, 41 tests, JavaScript syntax, compileall, and zero browser warnings/errors passed. The system snapshot identity and counts are unchanged.
Links: `src/change_passport/templates/review.js`, `src/change_passport/templates/review.css`, `tests/test_html_renderer.py`, `design/ui-flows/system-architecture-line-clarity-agent-20260905/`, `TASK-20260905-006`
Follow-up: Preserve the focus-layout rule for any future graph renderer; adding more line styling to a dense fixed grid is not an acceptable substitute for readable routing.

ID: BUG-20260905-012
Date: 2026-09-05
Status: fixed
Domain: beginner-review
Severity: medium
Symptom fingerprint: The `为什么这样改` card said the reason was unclear whenever no validated `task_intent` claim existed, even when the prepared evidence already contained the user's task text and the AI's completion explanation.
Trigger / reproduction: Finalize the frozen DigitalSelf sample, whose constrained brief has no `task_intent` but whose generator packet contains `task.original` and `task.provider_completion`.
Impact: A beginner was told that context was absent when useful, role-labelled context was already available, making the report appear less capable and obscuring the distinction between user intent and AI interpretation.
Root cause: The beginner projection inspected only validated claims for the Why card and did not receive the already prepared task evidence. It therefore conflated `no reason claim` with `no task conversation`.
Change made: Pass packet task evidence into the derived review; add ready/available/unavailable context states; render bounded user and AI excerpts behind a zero-Token button; keep AI replies explicitly non-authoritative for user intent.
Verification: The frozen sample now shows `已有对话线索`; user and AI roles, sources, warning and order rule render correctly; 44 tests, compileall, JavaScript syntax, desktop and 390 px browser checks, Escape focus return, script escaping, and zero console warnings/errors passed. Validated claims and the architecture snapshot hash remain unchanged.
Links: `src/change_passport/review_model.py`, `src/change_passport/pipeline.py`, `src/change_passport/templates/review.js`, `tests/test_review_model.py`, `design/ui-flows/intent-context-recovery-agent-20260905/`, `TASK-20260905-008`
Follow-up: Implement the connected `从任务窗口提炼` action only when the host can bind an exact task slice to the change identity and can disclose Token/privacy cost before the user clicks.

ID: BUG-20260905-013
Date: 2026-09-05
Status: fixed
Domain: architecture-evidence
Severity: high
Symptom fingerprint: Every retained import edge reverified at a new Head commit was classified as modified because its evidence ref contained a different commit hash.
Trigger / reproduction: Rebuild the immutable DigitalSelf range `d78f78b..430c342`; 1,754 edge identities exist in both trees, and the old comparison marks all 1,754 modified even though only one source location moves. The bounded displayed artifact exposed the same defect as 95 modified edge IDs.
Impact: `architecture-delta.json`, the declared structured fact authority, overstated relationship change even though current UI code did not display the field.
Root cause: Retained-edge comparison used the complete `evidence_refs` string, conflating reverification identity with source-location identity.
Change made: Mask only the 40-character Git commit component when comparing retained-edge evidence locations. Keep source path and line in the signature so real movement remains visible.
Verification: The full reconstruction now finds exactly one differing retained edge, `edge.305a63dbc617414072cb`, whose `registry.py` import moves from line 8 to line 10. Formal output changed from 95 to 1 modified edge while added/removed stayed 14/1; 45 tests, compileall, JavaScript syntax, and target-worktree preservation passed.
Links: `src/change_passport/architecture.py`, `tests/test_architecture.py`, `artifacts/digitalself-430c342-m15/architecture-delta.json`, `TASK-20260905-009`
Follow-up: Treat verification provenance and structural identity as separate comparison dimensions in future architecture contracts.

ID: BUG-20260905-014
Date: 2026-09-05
Status: fixed
Domain: target-profile
Severity: low
Symptom fingerprint: Loading a valid target profile with `module_areas` raised a `NameError` before any architecture collection could begin.
Trigger / reproduction: Run the first profile-configuration regression after adding `PresentationProfile`; the parser referenced `module_areas` from the presentation-metadata scope before that field had been read from the profile root.
Impact: The newly added optional display metadata made an otherwise valid profile unusable. No target repository was read or changed, and no artifact was produced from the failed attempt.
Root cause: The profile parser placed the `module_areas` conversion next to nested presentation parsing rather than alongside other root-level profile fields.
Change made: Read and validate `module_areas` at the root profile scope, then construct immutable presentation metadata from that resolved collection. Keep strict field validation and generic fixture coverage.
Verification: `tests/test_target_profile.py` passes for a configured generic fixture and both packaged profiles; the full suite reports 48 passed, plus compileall, JavaScript syntax, profile-SHA binding, and the isolated self-hosted sample all pass.
Links: `src/change_passport/target_profile.py`, `tests/test_target_profile.py`, `TASK-20260905-010`
Follow-up: Keep every optional profile extension covered by a load-and-render test before it is used by the production reader.

ID: BUG-20260905-015
Date: 2026-09-05
Status: fixed
Domain: project-governance
Severity: low
Symptom fingerprint: The new EVO-20260905-019 material-change record appeared before older evolution entries instead of at the physical end of the append-only ledger.
Trigger / reproduction: Append an evolution record using only the repeated `Needs curation: yes` line as a patch anchor; the patch tool matched an earlier record.
Impact: The target-profile decision and verification remain intact, but simple file order no longer expresses chronology at that point in the ledger.
Root cause: A generic repeated terminal marker was used despite the existing governance rule requiring an exact, unique final-record anchor.
Change made: Retain the original raw record as required by append-only governance and append EVO-20260905-020 at the true end to make the correction and authoritative sequencing explicit.
Verification: `rg -n '^ID: EVO-20260905-0(18|19|20)$' docs/project-governance/EVOLUTION.md` shows the retained misplaced entry and the terminal correction; no prior records were rewritten.
Links: `docs/project-governance/EVOLUTION.md`, `EVO-20260905-019`, `EVO-20260905-020`, `BUG-20260904-008`, `BUG-20260904-010`
Follow-up: For raw-ledger appends, anchor only on the exact final record ID together with two unique final fields, then verify EOF immediately.

ID: BUG-20260905-016
Date: 2026-09-05
Status: fixed
Domain: test-contract
Severity: low
Symptom fingerprint: The no-network HTML test required profile-sourced conceptual-architecture text even when it rendered the generic review fixture, which intentionally has no conceptual architecture.
Trigger / reproduction: Add the concept-map template markup, then run `uv run pytest -q` with `test_single_file_html_embeds_valid_review_without_network_capabilities` using its default fixture.
Impact: Production rendering and profile parsing were correct, but the suite stopped at 48 passing tests and would have falsely reported a feature regression.
Root cause: The assertion confused template-level stable hierarchy labels with data-level copy that exists only when a profile declares a conceptual architecture.
Change made: Keep assertions for the stable first/second-layer markup; move profile-sourced conceptual content coverage to the configured target-profile end-to-end test.
Verification: `uv run pytest -q` reports 49 passed; the configured fixture exposes profile source, components, resolved static-group mapping, and flow identity.
Links: `tests/test_html_renderer.py`, `tests/test_target_profile.py`, `TASK-20260905-011`
Follow-up: Exercise optional profile data through a configured fixture, and reserve template tests for unconditional page contracts.

ID: BUG-20260905-017
Date: 2026-09-05
Status: fixed
Domain: architecture-understanding
Severity: medium
Symptom fingerprint: The first product/process architecture view rendered Bézier connectors and floating labels beneath cards, leaving a first-time reader unable to trace several configured relationships.
Trigger / reproduction: Open the self-hosted Change Passport architecture tab at desktop width after TASK-20260905-011; the evidence-spine-to-validation line and several labels pass through card territory and are occluded by the card layer.
Impact: The configured conceptual architecture remained present as data and text fallback, but its primary visual representation failed the beginner-comprehension objective.
Root cause: A generic free-form connector algorithm selected source/target centre directions without reserving connector gutters or accounting for intermediate cards; edge labels used the same occupied plane.
Change made: Render components into responsibility bands, route connectors orthogonally through dedicated gutters, redirect any otherwise blocked shortcut through a lower gutter, and move relationship wording into an ordered DOM relation key.
Verification: The regenerated self-hosted artifact has 8 cards, 8 SVG paths, 3 bands, 0 floating SVG labels, 8 textual relationship entries, and 0 sampled connector intersections with card interiors at 1440×1050. At 390×844 it stacks in story order with no horizontal overflow and hides decorative connectors. Full suite: 49 passed; console warnings/errors: 0.
Links: `src/change_passport/templates/review.html`, `src/change_passport/templates/review.css`, `src/change_passport/templates/review.js`, `design/ui-flows/architecture-story-map-agent-20260905/04-validation/capture.py`, `TASK-20260905-012`
Follow-up: Validate the story map through an independent non-coder retelling; geometric non-overlap is not comprehension evidence by itself.
Needs curation: yes

ID: BUG-20260912-055
Date: 2026-09-12
Status: fixed
Domain: model-contract
Severity: medium
Symptom fingerprint: Real model-assisted project understanding intermittently
passes the provider's structured-output gate but fails PlainChange validation
because workflows omit an adjacent edge, components cite unknown paths or source
IDs, or source-reference lists exceed the local contract.
Trigger / reproduction: Analyze the fixed PlainChange Git AI integration snapshot
with a compatible provider before the contract hardening; consecutive attempts
fail with `workflow must use one consecutive flow chain`, `unknown source or
path`, and `source_ids ... at most 12 items`.
Impact: Valid fixed Git evidence cannot produce a Change Passport even though the
failure is in the semantic response shape, and retrying consumes time and tokens.
Root cause: The JSON Schema exposed to the provider was looser than the local
validator for source/path membership and list bounds, while the prompt did not
make adjacent workflow edges explicit. The compatible endpoint also accepts only
a subset of JSON Schema and rejects `uniqueItems`.
Resolution: Bound source/path/flow/unknown lists in the provider schema, constrain
code paths to the supplied allowlist, state the consecutive-edge rule in the
prompt, and apply a loss-only normalizer that removes unknown, duplicate or
surplus values. Do not synthesize missing semantic edges; those still fail closed.
Omit unsupported `uniqueItems` and retain local deduplication.
Verification: Focused model/semantic tests pass, the complete 148-test suite exits
0, and the fixed self-review succeeds with `gpt-6-astra` without a target-specific
rule. Python and Windows portable builds also pass.
Links: `TASK-20260912-063`, `src/plainchange/model_adapter.py`,
`src/plainchange/semantic_analysis.py`, `tests/test_model_adapter.py`,
`tests/test_semantic_analysis.py`
Needs curation: yes

ID: BUG-20260911-033
Date: 2026-09-11
Status: fixed
Domain: report-localization
Severity: high
Symptom fingerprint: English mode translates the report shell but leaves PlainChange's own automatically generated owner headline, impact, risk and action text in Chinese whenever the target has no complete reviewed translation pack.
Trigger / reproduction: Generate the fixed DigitalSelf report with deterministic generation and no `report-translations.json`, switch `review.html` to English, and inspect the first-screen conclusion. Dynamic text containing 14 unsupported changes and `settings.json` remains Chinese even though its meaning already exists as deterministic state.
Impact: English readers cannot understand the decision layer, and the interface incorrectly makes PlainChange-authored Chinese look indistinguishable from project-provided source wording. Adding exact phrases per sample would fail again when counts, filenames or projects change.
Root cause: `auto_draft.py` composed final Chinese sentences directly into `software-control.json`; `html_renderer.py` could produce a body translation only from a complete authored pack. The browser dictionary could translate fixed shell strings but had no language-neutral ownership or semantic arguments for dynamic report text.
Change made: Add `plainchange.owner-presentation.v1` descriptors that bind stable message keys and bounded arguments to approved presentation paths only. Render a built-in English owner projection from those descriptors, keep project declarations/source text explicit and unchanged, and let complete identity-bound reviewed packs override the automatic projection. Reject descriptors that target identity, truth state, basis, evidence, source references or topology.
Verification: 113 tests pass, including dynamic count/filename rendering, blocked evidence paths, canonical immutability, generated responsibility translation and reviewed-pack precedence. Fresh fixed-range DigitalSelf generation completed in 2.111 seconds with 317 owned messages and 49 source-language paths. Real Edge passed both tabs, all capability expansions, desktop/390 px overflow, console and technical-canvas scrolling; the English headline is translated and the boundary states that project/source text remains original.
Links: `TASK-20260911-044`, `src/plainchange/owner_presentation.py`, `src/plainchange/auto_draft.py`, `src/plainchange/html_renderer.py`, `tests/test_owner_presentation.py`, `tests/test_pipeline.py`
Follow-up: Model-authored prose and project text still need an identity-bound reviewed translation when a translated view is desired. Do not silently machine-translate them or relabel them as PlainChange-owned deterministic text.
Needs curation: yes

ID: BUG-20260910-009
Date: 2026-09-10
Status: fixed
Domain: analysis-runtime
Severity: high
Symptom fingerprint: Large partial or shallow repositories could spend many minutes silently materializing Git objects, with no durable stage, progress, cache, or failure receipt.
Trigger / reproduction: Analyze the fixed vLLM range from a repository that does not contain the selected immutable tree, or repeat a complete analysis of the same 4,501-module snapshots.
Impact: A software owner could not tell whether analysis was running, blocked, or frozen, and repeated runs paid the full static parse cost.
Root cause: Git object availability, immutable evidence collection, full-snapshot parsing, and operational reuse were implicit inside one synchronous path.
Change made: Add explicit no-lazy-fetch preflight, managed bare-copy hydration outside the target, durable JSON progress/failure receipts, terminal stage events, and a content-addressed SQLite parse cache keyed by parser version, tree path, and immutable blob ID.
Verification: A shallow-clone regression automatically hydrates both required commits in the managed cache while preserving the source worktree. The fixed vLLM cold run completes in 9.406 seconds; the warm run completes in 3.808 seconds, with the architecture stage at 1.118 seconds and 9,002 cache hits / 0 misses. Failure-receipt and target-preservation tests pass.
Links: `BUG-20260909-006`, `TASK-20260910-028`, `src/change_passport/progress.py`, `src/change_passport/analysis_cache.py`, `src/change_passport/git_evidence.py`
Needs curation: yes

ID: BUG-20260910-010
Date: 2026-09-10
Status: fixed
Domain: review-rendering
Severity: medium
Symptom fingerprint: Owner-first reports eagerly embedded and parsed the complete static snapshot in the initial review model, producing a 12.9 MB vLLM HTML artifact.
Trigger / reproduction: Render the fixed vLLM sample with 4,501 modules and 21,091 static relationships.
Impact: The first owner screen carried technical evidence that was neither visible nor needed until explicit drill-down.
Root cause: The renderer treated one offline file as one eager JSON model instead of separating owner data from delayed technical evidence.
Change made: Remove `system_architecture` from initial review JSON, bind its identity into the packet/evidence bundle, encode it as deterministic gzip/base64 with compressed and uncompressed SHA-256, and decode/index it only when the technical implementation disclosure or fallback architecture screen is opened.
Verification: The generated report falls from 12,926,806 to 3,141,945 bytes (75.7% reduction) while preserving the 12,616,264-byte system snapshot. Tests decompress the embedded payload and match snapshot identity; tamper/error handling, no-network HTML, fallback, and JavaScript syntax checks pass. Browser click acceptance remains pending because Computer Use could not connect.
Links: `BUG-20260909-007`, `TASK-20260910-028`, `src/change_passport/html_renderer.py`, `src/change_passport/templates/review.js`
Needs curation: yes

ID: BUG-20260905-018
Date: 2026-09-05
Status: fixed
Domain: architecture-understanding
Severity: low
Symptom fingerprint: Immediately after switching to the architecture tab, the fixed toast overlapped the human-decision card; at the same time, responsibility-band subtitles could sit beneath the first-row card edge.
Trigger / reproduction: Select `整体架构` in the self-hosted report at the owner's 1280 px browser width. The toast `已切换到整体架构` occupies the lower-right screen area, and the 46 px story-canvas header leaves insufficient separation between band subtitles and cards.
Impact: The workflow itself remains intact, but feedback UI and decorative band copy partially obstruct the most important human-approval boundary.
Root cause: A global fixed success toast was used for a self-evident tab switch, while the new band-header copy was added without increasing the story grid's top inset.
Change made: Make normal page switches silent and reserve a 62 px header strip before the first story row.
Verification: At desktop, the capture reports `pageSwitchToastHidden=true`, `bandHeadersClearCards=true`, 0 connector/card intersections, and no horizontal canvas overflow. At 390 px, cards remain stacked with no page overflow. Full suite: 49 passed; console warnings/errors: 0.
Links: `src/change_passport/templates/review.js`, `src/change_passport/templates/review.css`, `design/ui-flows/architecture-story-map-agent-20260905/05-iterations/round-1.md`, `TASK-20260905-012`
Follow-up: Keep transient UI feedback out of diagram occupancy zones; verify both visible state changes and decorative labels at the owner's active viewport.
Needs curation: yes

ID: BUG-20260905-019
Date: 2026-09-05
Status: fixed
Domain: architecture-understanding
Severity: medium
Symptom fingerprint: A connector repair that was visually adequate for one linear profile could not explain whether it remained readable for branch, merge, multiple-gate, or cyclic conceptual architectures.
Trigger / reproduction: Replace the self-hosted profile's simple path with two inputs, a parallel analysis branch, a join, two human gates, and a shared persistent state. The fixed responsibility-band coordinates no longer express topology, and a direct connector approach either overlaps cards or implies an incomplete diagram.
Impact: A user could receive a visually polished but topology-specific map for a second project, defeating the product promise of quick understanding without code knowledge.
Root cause: The first renderer treated profile grid positions as the diagram layout and had no general graph rank, obstacle-aware routing, or safe failure state.
Change made: Derive ranks from directed relationships; retain grid positions only as deterministic tie-breakers; use an obstacle-aware orthogonal router for non-linear DAGs; and remove SVG arrows in favor of ordered cards plus complete relationship text for cycles or route exhaustion.
Verification: Parser regression accepts a 10-component branch/merge/two-gate profile. Browser validation records 11/11 visible flows with zero sampled card intersections in layered mode, and a cyclic variant records 0 arrows, 12 relation rows, and visible fallback copy. The self-hosted simple path remains 8/8 with zero intersections.
Links: `src/change_passport/templates/review.js`, `tests/test_target_profile.py`, `design/ui-flows/generic-concept-layout-agent-20260905/04-validation/validation.md`, `TASK-20260905-013`
Follow-up: Independent non-coder retelling remains required; geometric correctness is not by itself proof of comprehension.
Needs curation: yes

ID: BUG-20260905-020
Date: 2026-09-05
Status: fixed
Domain: architecture-understanding
Severity: medium
Symptom fingerprint: A non-cyclic, forward-only layered profile for an external project fell back to card-list mode even though a visible orthogonal route existed between every relationship.
Trigger / reproduction: Render the FastAPI `0.136.2..0.136.3` profile with two inputs, a routing hub, two processing branches, and two outputs. The conceptual graph has 9 components and 9 acyclic relations, but the first generic router returned no complete route and hid all SVG connectors.
Impact: The safe fallback prevented a misleading diagram, but a normal external project lost its architecture-at-a-glance view. A topology engine validated only with small fixture cards was not sufficient.
Root cause: The channel router considered each relationship's source and target cards to be obstacles and did not first test the ordinary forward, mid-gutter orthogonal route that the layered rank layout makes available.
Change made: Exempt only the current route endpoints from its obstacle set and add a profile-neutral forward-route candidate with an explicit card-intersection check before channel search. Other cards remain hard obstacles; cycles and route exhaustion still fall back.
Verification: FastAPI now renders `layered` with 9 cards, 9 SVG paths, 9 relation rows, zero sampled card intersections, zero desktop console issues, and no 390 px overflow. Existing self-hosted, branch/merge, and cyclic-fallback browser checks remain green; full suite reports 50 passed.
Links: `src/change_passport/templates/review.js`, `tests/test_html_renderer.py`, `artifacts/fastapi-0.136.2-to-0.136.3/review.html`, `TASK-20260905-014`
Follow-up: Add further independently selected repositories before claiming generalized comprehension or layout quality.
Needs curation: yes

ID: BUG-20260906-001
Date: 2026-09-06
Status: fixed
Domain: architecture-understanding
Severity: medium
Symptom fingerprint: The static implementation reader could expose only a coarse system section or an unstructured list of raw modules, so a section with many internally different responsibilities had no readable intermediate architecture.
Trigger / reproduction: Open a static section with several implementation concerns, such as FastAPI's framework core. The prior reader collapsed routing, dependency processing, response handling, documentation, and extension code into one 48-module block before showing raw files.
Impact: A non-coder could identify the broad section but not the internal structure or its evidence-bound static relationships; a repository with a large section looked less decomposed than it is.
Root cause: Target profiles could describe module areas only with broad directory prefixes, and the reader did not aggregate existing static imports at an implementation-subdomain layer.
Change made: Add generic exact-path and filename-prefix matching to module-area profiles, retain an explicit unmatched fallback, and render clickable implementation subdomains with cross-subdomain aggregates backed by exact static edge IDs.
Verification: FastAPI framework core renders 7 subdomains and 23 static aggregates; Change Passport evidence pipeline renders 5 and 8 with the same consumer. The browser has no duplicate legacy cards, selection expands raw modules only on request, and 390 px has no horizontal overflow. Full pytest: 50 passed; compileall and JavaScript syntax pass; consumer source contains zero FastAPI identities.
Links: `src/change_passport/target_profile.py`, `src/change_passport/templates/review.js`, `tests/test_target_profile.py`, `tests/test_html_renderer.py`, `TASK-20260906-015`
Follow-up: Evaluate comprehension with independent non-coders before treating subdomain labels as universally sufficient; profile labels remain declarative reader guidance.
Needs curation: yes

ID: BUG-20260906-002
Date: 2026-09-06
Status: fixed
Domain: architecture-understanding
Severity: medium
Symptom fingerprint: The architecture reader separated the profile workflow, static implementation map, relation list, and module drill-down into successive regions linked by nested buttons and scroll jumps.
Trigger / reproduction: Open a generated report with conceptual architecture, then select a mapped workflow component. The former interaction required a small “查看对应静态实现” button, moved the reader to a separate second layer, then required another button before implementation subdomains appeared.
Impact: The diagram did not behave like a single architecture image. A first-time reader had to preserve context across several visual regions and could lose the parent-to-implementation connection.
Root cause: The implementation reader was designed as a separate progressive page rather than as an expansion state of the work-flow component that selected it.
Change made: Render conceptual workflow and selected static implementation inside one explorer canvas; make mapped workflow cards direct controls; place subdomains inline and move facts, relationship prose, evidence boundaries, and optional source modules to the persistent inspector.
Verification: FastAPI opens 7 implementation subdomains from one workflow card and Change Passport opens 5 using the same consumer. The implementation section is contained by the sole architecture canvas; nested workflow action buttons are zero; desktop and 390 px browser checks report zero console issues and no horizontal overflow. Full pytest: 50 passed; compileall, JavaScript syntax, and diff check pass.
Links: `src/change_passport/templates/review.html`, `src/change_passport/templates/review.js`, `src/change_passport/templates/review.css`, `TASK-20260906-016`
Follow-up: Run independent beginner retelling before treating the visual reorganization as proof of comprehension.
Needs curation: yes

ID: BUG-20260906-003
Date: 2026-09-06
Status: fixed
Domain: architecture-understanding
Severity: medium
Symptom fingerprint: The first unified architecture explorer still arranged conceptual components from left to right on desktop, even though the intended beginner reading path is an explanation from system purpose down to its static implementation.
Trigger / reproduction: Open the FastAPI architecture tab at desktop width. The 9 workflow cards form a layered horizontal graph, forcing a reader to scan across the canvas before reaching the selected implementation below it.
Impact: A non-coder has to infer reading order from horizontal geometry and decorative routing. For branch, merge, and cyclic profiles, a single visual left-to-right path can also imply a causal sequence that the profile relationship data does not state.
Root cause: The unified explorer inherited the topology layout engine's desktop grid even after the product changed from a specialist dependency diagram to a beginner-first architecture explanation.
Change made: Apply one profile-neutral vertical workflow column to the unified explorer at every width; retain deterministic component order and stage badges, suppress decorative SVG connectors in this reader, and keep complete declared relationship text visible.
Verification: FastAPI is 9/9 vertical cards with no horizontal conceptual-canvas overflow; Change Passport is 8/8. Both have `connectorDisplay=none`, zero browser console errors, and FastAPI still expands 7 implementation subdomains below the selected workflow card in the same canvas. Full pytest: 50 passed; compileall, JavaScript syntax, and diff checks pass.
Links: `src/change_passport/templates/review.css`, `design/ui-flows/unified-architecture-canvas-agent-20260906/`, `TASK-20260906-017`
Follow-up: Test a non-coder retelling before treating the visual reading order as comprehension evidence.
Needs curation: yes

ID: BUG-20260909-001
Date: 2026-09-09
Status: fixed
Domain: architecture-understanding
Severity: medium
Symptom fingerprint: The “top-to-bottom architecture” correction displayed every conceptual component as a full-width one-column card list and suppressed all diagram edges, so the architecture surface stopped behaving like a graph.
Trigger / reproduction: Open either retained report's overall-architecture tab after TASK-20260906-017. Nodes are ordered vertically, but branches, joins, and relationship direction can be discovered only by reading the separate relationship list.
Impact: A reader cannot recognize system topology at a glance, and clicking list rows does not compensate for the missing graph structure. The result violates the owner's requirement that architecture remain a clickable, interactive picture.
Root cause: The correction conflated vertical reading direction with one-column list layout and treated all arrows as potentially misleading instead of changing the graph's rank orientation and preserving exact configured edges.
Change made: Transpose topology ranks into graph rows, place same-rank branches side by side, route source-bottom to target-top orthogonal arrows with obstacle checks, retain explicit cyclic/unsafe fallback, and keep node click/inline implementation/right-inspector interaction. Separate selected conceptual-node identity from mapped static-group identity so shared group mappings do not highlight every node.
Verification: FastAPI renders 9 nodes/9 arrows in 5 descending rows and Change Passport renders 8/8 in 7 rows; both report zero connector intersections and no canvas overflow. Only the clicked FastAPI node is selected, it expands 7 subdomains, and a second click collapses it. At 390 px, arrows hide, all 9 cards and relationship rows remain, and document width is 390 px. Browser console issues: 0; full pytest: 50 passed; compileall, JavaScript syntax, identity scan, and diff check pass.
Links: `src/change_passport/templates/review.js`, `src/change_passport/templates/review.css`, `tests/test_html_renderer.py`, `design/ui-flows/interactive-top-down-architecture-graph-agent-20260909/`, `TASK-20260909-018`
Follow-up: Independent beginner retelling remains required; geometry and interaction checks do not prove conceptual understanding.
Needs curation: yes

ID: BUG-20260909-002
Date: 2026-09-09
Status: fixed
Domain: software-control
Severity: high
Symptom fingerprint: The five-question text sample asked “这个软件是做什么的、主要怎样工作？”, but the participant-visible answer only summarized the product purpose. The actual five-step software workflow existed in structured JSON and was invisible to the reader.
Trigger / reproduction: Read Q1 in `change-passport-self-688fc5f.software-control.md` or `participant-card.md` before this correction. A participant could repeat that the product explains an AI change without seeing the ordered input, evidence-checking, output, and human-decision process.
Impact: The proposed comprehension test could incorrectly pass a participant who understood what the product is for but not how the software works. This violates PRD v2.0's first question and makes the initial blind-test kit unsuitable for measuring the product promise.
Root cause: Contract completeness was checked in JSON, while participant parity checked only the one-sentence `answer` field. `details.software_steps` was treated as supporting data instead of required first-screen content, and the Q1 rubric allowed a purpose summary to earn credit.
Change made: Render all five plain-language software steps as a visible top-to-bottom flow in both the source sample and participant card; remove implementation vocabulary from the previously hidden step wording; require exact step parity and four visible connectors; update the evaluator rubric so a purpose-only answer scores zero; regenerate the control identity, sample hashes, observation binding, and evaluation manifest.
Verification: Both user-visible documents contain all five exact `software_steps` and four down connectors. Control and observation schemas pass; canonical control identity is `21dcff469d5b0faf297dbe890eecd1e68b8eca939e18bf8b28f905c0561dd9cc`; all evaluation-manifest hashes match; the Q1 rubric rejects purpose-only answers; the first-screen banned technical-term scan remains zero; `git diff --check` passes with only existing line-ending warnings.
Links: `docs/product/samples/change-passport-self-688fc5f.software-control.md`, `docs/product/evaluations/change-passport-self-688fc5f/participant-card.md`, `docs/product/evaluations/change-passport-self-688fc5f/evaluator-guide.md`, `TASK-20260909-020`, `TASK-20260909-021`
Follow-up: Future renderers must treat Q1's ordered `software_steps` as required visible content, not optional drill-down data; independent human comprehension is still not run.
Needs curation: yes

ID: BUG-20260909-003
Date: 2026-09-09
Status: fixed
Domain: software-control
Severity: high
Symptom fingerprint: The five-question candidate was structurally complete but still required a non-coder to interpret engineer-facing abstractions such as “结构变化”, “同一条关系”, “核对版本”, “来源位置”, “内部关联线索”, “真实运行时”, and “已批准历史记录”. All five answers also carried similar visual weight, so no immediate conclusion dominated the first screen.
Trigger / reproduction: Read the corrected first-screen sample as a software owner without code-review ability. The reader can identify that an internal rule changed but still has to ask what relation or source position means and why a recheck could look like a software change.
Impact: The sample completed code-to-engineer translation but not engineer-language-to-owner-language translation. It could burden the target user, blur affected people with unverified facts, and expose test-case construction before the owner understands the result to confirm.
Root cause: The contract required five answers, states, sources, and plain-language term scanning, but it did not require decision-first information priority, a concrete before/after example for abstract changes, separation between affected people and unknown verification, or separation between owner checks and detailed test instructions.
Change made: Add a generic `first_screen_summary`, `comparison_example`, and `owner_checks` contract; lead user documents with confirmed change, user impact, and residual risk; rewrite five answers in owner language; split Q3 from Q4; move detailed test construction below the first screen; and reduce visible state prose to short labels without changing machine-readable state.
Verification: Revised JSON passes its schema and canonical identity recomputation. Both user documents show the summary before five questions, contain the same source answers, five software steps, before/after example, and owner checks. The old/new example keeps identical input steps and changes only the result. Q3/Q4 separation and detailed-action isolation pass. The first screen contains zero occurrences of the seven owner-rejected phrases and the prior implementation-term list. Manifest hashes match; human status remains `not_run`.
Links: `docs/product/software-control-v1-contract.md`, `docs/product/schemas/software-control.v1.schema.json`, `docs/product/samples/change-passport-self-688fc5f.software-control.md`, `docs/product/evaluations/change-passport-self-688fc5f/participant-card.md`, `TASK-20260909-022`
Follow-up: Production renderers must consume the generic summary/example/owner-check fields rather than recreate Change Passport-specific copy. Real owner comprehension remains a later gate; this correction does not claim a pass.
Needs curation: yes

ID: BUG-20260909-004
Date: 2026-09-09
Status: fixed
Domain: software-control
Severity: high
Symptom fingerprint: The owner-language correction completed only the “这次改了什么” first-screen candidate. “这个软件怎么工作” remained implicit in JSON and in the older engineering-oriented architecture report, with no equivalent owner-language second-screen artifact or node-inspector contract.
Trigger / reproduction: Open the revised first-screen sample and ask for the second screen. It links no complete owner-facing software map, cannot show where the current change sits in the whole product, and gives a future renderer no generic fields for explaining a selected node to a non-coder.
Impact: A user could understand the isolated change but still fail to form a mental model of the software they own. The product would continue solving change explanation without completing the promised software-control view.
Root cause: TASK-20260909-022 narrowed its validation to the five-question first screen. The existing `working_map` carried labels and topology but not an explicit screen overview or the owner-facing meaning/result/change/impact/unknown/check content required by the right inspector.
Change made: Add generic `working_map.screen_summary` and per-node `owner_view` fields; rewrite the self-hosted map in owner language; bind one changed node to direct claim and evidence IDs; create a standalone second-screen candidate containing the full graph, selected-node inspector, and delayed technical implementation section; link it from the first-screen sample.
Verification: Schema validation passes. The sample has 8 unique nodes, 8 valid flows, complete owner inspectors on all nodes, exactly one changed node (`static_extraction`) with direct retained claim/evidence binding, and a second-screen artifact containing every node and flow label. Overview, graph, inspector, and technical disclosure appear in order. Owner-layer rejected and implementation term scans return zero. Canonical and dependent identities match.
Links: `docs/product/samples/change-passport-self-688fc5f.software-map.md`, `docs/product/samples/change-passport-self-688fc5f.software-control.json`, `docs/product/schemas/software-control.v1.schema.json`, `TASK-20260909-023`
Follow-up: Implement this contract in the production two-screen HTML only as a separately approved UI task; browser interaction and visual comprehension are not proven by the Markdown candidate.
Needs curation: yes

ID: BUG-20260909-005
Date: 2026-09-09
Status: fixed
Domain: software-control
Severity: high
Symptom fingerprint: The first production owner view still led with the abstract label “变化识别规则”, repeated similar conclusions across a long default five-question report, and opened an eight-node process graph before giving a non-coder a four-step mental model.
Trigger / reproduction: Open the self-hosted owner report from TASK-20260909-024. A first-time software owner has to interpret the internal concept before the repaired outcome, distinguish several similar status words without a definition, scan all five full answers, and understand eight workflow nodes before locating the current change.
Impact: The page is accurate but does not meet the ten-second comprehension goal. A reader can also misread “暂未发现” as proof of no impact, or mistake recommended checks for work already completed.
Root cause: The first production pass rendered all correct contract fields with similar prominence. The contract had no separate immediate owner action, no per-label plain-language explanation, and no source-declared overview-to-detail partition for progressive graph depth.
Change made: Lead with the concrete repaired outcome and demote the internal concept to a secondary label; render only three compact owner answers after the explanation; add clickable state definitions; collapse the complete five questions; render audience impact as a table and checks as visibly unchecked items; require exactly four source-declared overview nodes that partition all detail nodes once; and expand/back within the same graph while preserving the changed-node focus.
Verification: 60 pytest tests pass. The sample validates against the checked-in Schema; exact four-step coverage, changed-overview binding, canonical identity, evaluation hashes, generated artifact identity, HTML parsing, offline-resource checks, Python compilation, JavaScript syntax, and diff checks pass. Visual screenshot acceptance remains pending because the current in-app browser blocks local `file://` interaction.
Links: `src/change_passport/software_control.py`, `src/change_passport/templates/review.html`, `src/change_passport/templates/review.js`, `src/change_passport/templates/review.css`, `docs/product/schemas/software-control.v1.schema.json`, `TASK-20260909-025`
Follow-up: Reload the generated report in an allowed browser surface and review desktop/narrow hierarchy, connector routing, state popovers, focus, and text density. Do not treat automated checks as a human comprehension pass.
Needs curation: yes

ID: BUG-20260909-006
Date: 2026-09-09
Status: open
Domain: evidence-pipeline
Severity: medium
Symptom fingerprint: Preparing a large partial-clone repository can spend many minutes materializing Git blobs without showing bounded progress, current path, object-fetch state, or an actionable distinction between active work and a hung process.
Trigger / reproduction: Run `prepare` for the fixed vLLM range in TASK-20260909-026 against a blob-filtered clone whose selected immutable tree is not locally materialized. The first attempt ran for more than ten minutes before manual interruption; after explicitly fetching the selected two-commit tree with full objects, prepare completed in about 11.4 seconds.
Impact: A user cannot tell whether Change Passport is working, blocked on network/object hydration, or frozen. This is especially harmful for the intended beginner audience and is likely to recur on large repositories, CI mirrors, and partial clones.
Root cause: The analyzer correctly uses immutable Git object reads but has no preflight for missing/promised objects and no phase/path progress contract around large-tree materialization and parsing.
Change made: None in this validation task. The selected immutable objects were prefetched as sample setup; the analyzer and renderer remain generic and unchanged.
Verification: The prefetched run produced 4,501 modules and 21,091 static edges in about 11.4 seconds, proving that the slow first run was dominated by object materialization rather than the final deterministic parse alone.
Links: `docs/project-governance/tasks/TASK-20260909-026-vllm-complex-project-validation.md`, `artifacts/vllm-a69e75b-to-a85d073/`
Follow-up: Add a read-only object-availability preflight and structured progress events with explicit fetch/network boundaries; preserve immutable-range and target-repository read-only rules.
Needs curation: yes

ID: BUG-20260909-007
Date: 2026-09-09
Status: open
Domain: review-rendering
Severity: medium
Symptom fingerprint: The single-file report embeds the complete system-architecture snapshot, causing report size to scale with every parsed module and static relationship even though the owner opens with a four-step map.
Trigger / reproduction: Finalize the vLLM sample from TASK-20260909-026. `system-architecture.json` is 12,657,291 bytes and the generated `review.html` is 12,924,883 bytes for 4,501 modules and 21,091 static relationships.
Impact: Large reports load, parse, transfer, and retain substantially more data than the first owner experience needs. Growth is repository-dependent and can degrade local interaction or sharing even when the visible owner map is intentionally shallow.
Root cause: The offline single-file renderer serializes the entire static snapshot, including repeated node and evidence metadata, instead of a compact aggregate plus deliberately loaded technical detail.
Change made: None. The full snapshot remains embedded so this task does not weaken evidence completeness or introduce a vLLM-specific truncation rule.
Verification: The report remains valid, offline, and identity-bound, but its measured byte size confirms the generic scaling gap.
Links: `docs/project-governance/tasks/TASK-20260909-026-vllm-complex-project-validation.md`, `artifacts/vllm-a69e75b-to-a85d073/review.html`, `artifacts/vllm-a69e75b-to-a85d073/system-architecture.json`
Follow-up: Design a profile-neutral compact transport that preserves aggregate counts, change overlays, omitted identities, and on-demand technical evidence without silently discarding source facts.
Needs curation: yes

ID: BUG-20260910-008
Date: 2026-09-10
Status: fixed
Domain: software-control
Severity: medium
Symptom fingerprint: The vLLM owner map treated entry types as a chronological “接收调用方式” step, described scheduling as “安排模型” as if vLLM dynamically selected a model, described output as if it completed before return, and left the selected-versus-changed visual distinction unexplained.
Trigger / reproduction: Open the TASK-20260909-026 report as a beginner. The detail map mentions command line as a request route, the scheduler card can be read as model selection, streaming is only weakly implied, and the deep-blue/amber state distinction has no nearby key.
Impact: A non-coder can build an incorrect mental model even though the underlying topology and colors are structurally consistent. The error is semantic and affects the product's main promise of shallow but dependable explanation.
Root cause: The first external profile compressed interface types, startup commands, scheduler/resource responsibilities, and output delivery into uniformly sequential owner cards. The generic renderer exposed two visual states without naming them.
Change made: Rewrite the profile/control projection around request entry, request/resource scheduling, and optional streaming return; add a generic two-item legend; and preserve both selected and changed styling when one node has both states.
Verification: Fixed-snapshot quickstart/V1/config sources support the new distinctions. Profile/Schema/canonical/source binding, new-copy presence, stale-copy absence, legend semantics, offline-resource scan, 60 tests, compileall, JavaScript syntax, target fingerprint, and diff checks pass. Visual screenshot acceptance remains pending because Computer Use could not connect to the current in-app browser.
Links: `examples/target-profiles/vllm.v1.json`, `docs/product/samples/vllm-a69e75b-to-a85d073.software-control.json`, `src/change_passport/templates/review.html`, `src/change_passport/templates/review.css`, `TASK-20260910-027`
Follow-up: Keep target-profile owner steps distinct from startup/configuration affordances, and retain an explicit non-color explanation wherever interactive selection and change overlay coexist.
Needs curation: yes

ID: BUG-20260910-011
Date: 2026-09-10
Status: fixed
Domain: project-governance
Severity: low
Symptom fingerprint: The TASK-028 resolution records BUG-20260910-009 and BUG-20260910-010 were appended after a repeated mid-file `Needs curation` anchor instead of the physical ledger tail.
Trigger / reproduction: Inspect BUGLOG physical order after recording TASK-028 completion; the new IDs appear before older retained entries even though their dates and links remain correct.
Impact: No source fact or implementation evidence was lost, but physical order again cannot be used as the chronology for those records.
Root cause: The patch anchor was not unique to the current EOF despite the existing BUG-20260904-001 warning.
Change made: Preserve both misplaced append-only records and add this linked tail correction. IDs, dates, links, and explicit dependency relationships remain the authoritative order.
Verification: `rg -n "BUG-20260910-009|BUG-20260910-010|BUG-20260910-011"` shows all three retained records and this correction at the current tail.
Links: `BUG-20260904-001`, `BUG-20260910-009`, `BUG-20260910-010`, `TASK-20260910-028`
Follow-up: Future ledger appends must anchor on the exact final record ID and link block, not a repeated field.
Needs curation: yes

ID: BUG-20260910-012
Date: 2026-09-10
Status: fixed
Domain: review-rendering
Severity: low
Symptom fingerprint: The first TASK-029 detailed owner-map screenshot showed both vertical and horizontal internal scrollbars even when the selected overview group contained only one detail node.
Trigger / reproduction: Open the fixed vLLM software screen, click the amber overview node, and inspect the left detail canvas at 1440×1000. The normal-flow node fit the canvas, but the canvas still exposed scrollbars.
Impact: No evidence or interaction was lost, but the empty scrollable area made a simple one-step drill-down look unfinished and added an unnecessary beginner interaction.
Root cause: The owner canvas retained `overflow: auto`, while SVG sizing used `scrollWidth`/`scrollHeight`; the scrollbar-reduced client box could feed a larger SVG dimension back into the scroll extent.
Change made: Let the document own scrolling, hide owner-canvas overflow, reduce generic branch-column minimum width, and size the owner SVG from the visible client box. Narrow layouts continue to hide SVG links and use a one-column fallback.
Verification: Final Edge capture reports equal 873 px canvas client/scroll widths, no canvas/document horizontal overflow, zero console problems, and no visible internal scrollbar. Four-step and selected-detail interactions remain valid.
Links: `src/change_passport/templates/review.css`, `src/change_passport/templates/review.js`, `TASK-20260910-029`
Follow-up: Keep graph SVG dimensions independent from their own scroll extent; validate both single-node and branched detail groups when future samples add topology.
Needs curation: yes

ID: BUG-20260910-013
Date: 2026-09-10
Status: fixed
Domain: review-rendering
Severity: medium
Symptom fingerprint: Opening a four-step owner-map item replaced the complete overview with a detail-only canvas and required `返回四步总览` to recover the software context.
Trigger / reproduction: Open the generated vLLM report, choose `这个软件怎么工作`, and click any four-step overview node in the TASK-029 UI.
Impact: A non-technical owner could inspect one step or retain the whole-system mental model, but not do both at once. The navigation also made a local explanation feel like a separate architecture screen.
Root cause: The renderer modeled overview and detail as mutually exclusive `ownerMapDepth` states rather than treating detail as an expandable child layer of an overview node.
Change made: Replace depth switching with one optional expanded-overview ID. Keep all four overview nodes and global links rendered, insert only declared mapped details beneath the open node, support same-node/button/Escape collapse, and synchronize the inspector from the selected source node.
Verification: Real Edge preserves four overview groups across initial, expanded, collapsed, and switched states; keeps all three global links on desktop; routes links around the inline panel; shows the correct one- and two-detail mappings; has zero console problems or horizontal overflow; and passes the 65-test suite.
Links: `src/change_passport/templates/review.js`, `src/change_passport/templates/review.css`, `src/change_passport/templates/review.html`, `TASK-20260910-030`
Follow-up: Validate a future source-bound group with many or branched detail nodes before adding any internal cap or mini-topology treatment.
Needs curation: yes

ID: BUG-20260910-014
Date: 2026-09-10
Status: fixed
Domain: review-rendering
Severity: medium
Symptom fingerprint: In the wide two-column five-question explanation, audience descriptions collapsed into a nearly one-character-wide strip and the tall right card pushed the next left card far down the page.
Trigger / reproduction: Open `查看完整说明` in the generated vLLM report at the owner's captured desktop width and inspect `谁会感觉到变化？` beside `这是什么软件？`.
Impact: Important user-impact explanations became difficult to read, and the large false blank area made the page appear broken despite sufficient viewport width.
Root cause: Audience rows forced three columns with two large minimum widths inside the already narrow secondary column. Separately, all five cards shared one CSS grid, so the tallest right card determined the height of the corresponding left grid row.
Change made: Give each audience explanation the full row beneath audience/state, add content-safe wrapping, and render questions 1–2 and 3–5 in independent semantic columns that merge at the existing responsive breakpoint.
Verification: Real Edge shows 289 px explanation width at 1560 px, 188 px at the risky 1100 px width, and 256 px at 390 px; both independent column gaps stay 14 px, no vertical-strip condition or horizontal overflow occurs, console output is clean, and 65 tests pass.
Links: `src/change_passport/templates/review.css`, `src/change_passport/templates/review.js`, `tests/test_html_renderer.py`, `TASK-20260910-031`
Follow-up: Keep nested card-width constraints independent from viewport width; include an intermediate-width capture when future owner cards add columns or status chips.
Needs curation: yes

ID: BUG-20260910-015
Date: 2026-09-10
Status: fixed
Domain: evidence-contract
Severity: medium
Symptom fingerprint: The first structured local-model run returned only three English `function` claims even though the generator instructions required four sections; the validator safely synthesized the missing areas as unknown.
Trigger / reproduction: Run the fixed vLLM packet with the initial Ollama adapter and `memdsl-qwen3-4b-32k:latest`. The JSON Schema constrained claim fields but allowed an array of any length, so the model stopped after 569 output tokens.
Impact: No unsupported fact escaped validation, but the model path could report generation success while omitting required explanation areas and degrading the owner experience.
Root cause: Section coverage existed only as natural-language instruction and post-validation completion, not as a structured minimum-output constraint or sufficiently explicit owner-language prompt.
Change made: Require 4–12 structured claims and explicitly require the first four to cover function, architecture, history, and attention in simplified Chinese with behavior-first phrasing. Existing validation and safe unknown synthesis remain active.
Verification: A second fixed vLLM run returned all four sections in Chinese with 1,505 output tokens; 8 claims were accepted, 1 downgraded, and 1 rejected for the existing per-section limit. Four schema/adapter tests and the full 72-test suite pass.
Links: `src/change_passport/model_adapter.py`, `tests/test_model_adapter.py`, `TASK-20260910-032`
Follow-up: Treat required semantic coverage as a validator-level generation-quality signal before evaluating larger or remote models; do not infer owner readability from schema compliance.
Needs curation: yes

ID: BUG-20260910-016
Date: 2026-09-10
Status: fixed
Domain: testing
Severity: low
Symptom fingerprint: The first configurable-provider test run failed on Windows before adapter assertions because new tests read UTF-8 generator packets using the process-local GBK default.
Trigger / reproduction: Run `pytest tests/test_model_adapter.py tests/test_pipeline.py` on the current Windows host after adding the parameterized provider-mode tests.
Impact: Four tests failed for test-harness decoding rather than product behavior; no runtime artifact or source evidence was corrupted.
Root cause: Two new `Path.read_text()` calls omitted the project's explicit `encoding="utf-8"` convention.
Change made: Read generated packet fixtures explicitly as UTF-8 in all new adapter tests.
Verification: The focused 15-test suite and full 73-test suite pass on the same Windows host.
Links: `tests/test_model_adapter.py`, `TASK-20260910-033`
Follow-up: Keep explicit UTF-8 on all JSON fixture reads and writes; do not rely on Windows locale defaults.
Needs curation: yes

ID: BUG-20260910-017
Date: 2026-09-10
Status: fixed
Domain: target-profile
Severity: high
Symptom fingerprint: Automatic analysis of VideoFactory completes with full static coverage but describes the product as a generic callable program, emits a generic four-step input/process/output map, and assigns 72 of 87 modules to `调用与用户入口`.
Trigger / reproduction: Run `change-passport analyze` without a supplied target profile on the fixed VideoFactory range `58d2149..d6594e3`, then inspect `target-profile.draft.json`, `software-control.json`, and the generated report.
Impact: A non-technical software owner cannot learn that VideoFactory is a configuration-driven video-production pipeline or see where planning, design, speech, timeline, rendering, QA, and delivery belong. The report is evidence-safe but fails the product's primary comprehension promise.
Root cause: Automatic module areas reuse the same broad `src/video_factory/` prefix and are resolved by first match, so intended areas are not mutually discriminating. Conceptual-profile generation also falls back to a generic callability template instead of extracting explicit project-declared workflow material already present in README documentation.
Change made: Automatic areas now use mutually discriminating prefixes plus exact-path fallbacks. A new fixed-commit declaration reader extracts only bounded root README purpose/workflow material, binds it to commit/path/SHA-256, and reconciles step support and order support separately from runtime. No VideoFactory-name branch was added.
Verification: The unchanged automatic path now classifies VideoFactory into entry 1, data 3, core 63, quality 15, delivery 5, and unclassified 0. It renders seven README-declared production steps with `代码支持`, marks the declared order `顺序部分支持`, and maps the fixed change uniquely to `渲染完整视频`. vLLM and FastAPI use the same implementation and retain automatic candidate workflows where declaration/order evidence is absent.
Links: `artifacts/videofactory-58d2149-to-d6594e3/target-profile.draft.json`, `artifacts/videofactory-58d2149-to-d6594e3/software-control.json`, `TASK-20260910-034`, `TASK-20260910-035`
Follow-up: Obtain owner and independent non-coder comprehension results; extend declaration formats only from observed cross-project failures rather than broadening extraction speculatively.
Needs curation: yes

ID: BUG-20260910-018
Date: 2026-09-10
Status: fixed
Domain: target-profile
Severity: high
Symptom fingerprint: Repository-wide keyword counts briefly classify vLLM as a video-production project and FastAPI as a model-serving project because incidental words outweigh the actual code shape.
Trigger / reproduction: Generate automatic profiles for the fixed vLLM and FastAPI samples after adding README reconciliation, then compare selected project kind and owner workflow with their source trees.
Impact: The owner map can describe the wrong class of software even though all referenced words exist somewhere in the repository.
Root cause: Project-kind detection used broad content occurrence counts without requiring multiple independent source-path signals or a declaration-heading signal.
Change made: Video-pipeline detection now requires a coherent path-signal combination plus declaration-head language. Model-serving detection requires at least two distinct code-path signals such as scheduler, model executor, inference, or KV cache. Web/command fallbacks remain path-derived and repository-name neutral.
Verification: VideoFactory selects the declared video workflow; vLLM selects the model-serving candidate; FastAPI selects the web-service candidate. A source scan finds no `VideoFactory`, `vLLM`, or `FastAPI` branch in `src/`.
Links: `src/change_passport/auto_draft.py`, `tests/test_auto_draft.py`, `TASK-20260910-035`
Follow-up: Add new class signals only with an unrelated failing fixture and preserve the generic unknown fallback.
Needs curation: yes

ID: BUG-20260910-019
Date: 2026-09-10
Status: fixed
Domain: software-control
Severity: high
Symptom fingerprint: A generic automatic workflow marks one business step as “本次改动” from broad implementation-group overlap even when several steps share the same groups and no unique source path supports the mapping.
Trigger / reproduction: Run the automatic vLLM or FastAPI samples and compare changed file paths with the generated workflow components and their shared group IDs.
Impact: A non-technical owner can be told that AI changed a specific part of the software without sufficient evidence.
Root cause: The mapper accepted non-unique group overlap as if it were a direct change-to-step link.
Change made: Current-change mapping now prefers exact component source-path overlap and accepts group overlap only when it uniquely identifies one evidence-backed step. Ambiguity returns no workflow overlay and an explicit unmapped-change headline.
Verification: VideoFactory uniquely maps the fixed change to `渲染完整视频`; the vLLM and FastAPI automatic candidates contain zero arbitrarily changed workflow nodes. Contract regression tests cover the fail-closed case.
Links: `src/change_passport/auto_draft.py`, `tests/test_pipeline.py`, `TASK-20260910-035`
Follow-up: Stronger semantic mapping may be added later as a constrained model interpretation, but it must not silently upgrade to verified evidence.
Needs curation: yes

ID: BUG-20260910-020
Date: 2026-09-10
Status: fixed
Domain: review-rendering
Severity: medium
Symptom fingerprint: The first tab can name the workflow step most likely changed, but reaching that step requires manually switching tabs, identifying its containing four-stage group, expanding it, and selecting the detail again; the second inspector repeats change-report content at full weight.
Trigger / reproduction: Open a report with one source-mapped changed workflow node, read the first-screen headline, then try to locate the same change in `这个软件怎么工作`.
Impact: The two tabs behave like separate reports instead of one owner journey, and the system view spends attention repeating impact/action material rather than establishing the selected step's place in the software.
Root cause: The renderer had no source-derived cross-tab location action. Inspector composition also treated change, audience, unknown, and checks as primary fields on both tabs.
Change made: Resolve a location only from one changed detail plus one `detail_node_ids` parent; render a conditional action that switches, expands, selects, scrolls, focuses, and textually marks that node. Recompose the inspector around responsibility, upstream/previous, result, downstream/next, change location, and evidence, with repeated decision content in a collapsed disclosure.
Verification: VideoFactory desktop and 390 px Edge checks reach `overview.stage-3` / `declared-render`, preserve four overview nodes, show the textual arrival marker, keep the target visible, and have no overflow or console problems. The unmapped FastAPI report renders zero actions. The full 78-test suite passes.
Links: `src/change_passport/templates/review.js`, `src/change_passport/templates/review.css`, `TASK-20260910-036`
Follow-up: Validate the same journey on a future branched workflow where a detail node has multiple incoming/outgoing edges; do not simplify that topology into a false single predecessor or successor.
Needs curation: yes

ID: BUG-20260910-021
Date: 2026-09-10
Status: fixed
Domain: software-control
Severity: high
Symptom fingerprint: A deterministic report receives fixed-patch evidence for newly added exception and non-zero failure branches, but summarizes only file count/location, labels unperformed user-impact interpretation as `目前没发现`, and gives one generic runtime check.
Trigger / reproduction: Analyze a fixed change that adds a conditional `raise` or explicit non-zero `return` with `--generator deterministic`, then inspect the first-screen conclusion, impact state, and owner actions.
Impact: A non-technical software owner can miss the most decision-relevant behavior risk already present in the evidence and misread “not analyzed” as “searched with no impact found”.
Root cause: The deterministic fallback consumed only file and architecture summaries. Generator coverage was not represented in owner-state language, and the pipeline did not pass packet-level behavior evidence into the software-control projection.
Change made: Extract conservative Python diff signals with source identity and strict limitations; include them in the generator packet; prioritize them in the deterministic brief; pass evidence into the owner projection; map only a uniquely supported primary path; distinguish `还没判断`; and provide normal-versus-stop checks. Diff hunk context now resets symbol ownership to prevent cross-hunk leakage.
Verification: 82 tests pass, including generic signal/condition/truncation/hunk fixtures, separate signature-compatibility versus stop/failure actions, and end-to-end no-model assertions. The fixed VideoFactory report binds `run_qa` to an added exception and `build_all` to an added non-zero return, highlights `检查视频质量`, and retains runtime/user impact as unverified. Compileall, JavaScript syntax, and diff checks pass.
Links: `src/change_passport/behavior_signals.py`, `src/change_passport/generator_contract.py`, `src/change_passport/auto_draft.py`, `src/change_passport/pipeline.py`, `tests/test_behavior_signals.py`, `TASK-20260910-037`
Follow-up: Expand behavior coverage only through separately bounded, known-answer categories; do not turn arbitrary syntax into a generic breaking-change verdict.
Needs curation: yes

ID: BUG-20260910-022
Date: 2026-09-10
Status: fixed
Domain: review-rendering
Severity: medium
Symptom fingerprint: The owner workflow badge says `代码支持`, which a non-technical reader can reasonably interpret as “the code is correct or verified” rather than “a corresponding code location was found”.
Trigger / reproduction: Open `这个软件怎么工作` and ask what the `代码支持` badge proves.
Impact: The interface collapses project declaration, source-location reconciliation, and runtime validation into an ambiguous phrase, weakening the evidence-state boundary for the target audience.
Root cause: A compact internal reconciliation status was exposed as the user-facing label without a permanently visible explanation.
Change made: Rename the declaration label to `来自项目说明`, the matched-location label to `找到对应代码`, and show both plain-language definitions beside the workflow map only when the current map contains the corresponding source states. Rename partial and declaration-only variants consistently.
Verification: 82 tests pass. The regenerated VideoFactory report renders `来自项目说明：项目自己这样描述` and `找到对应代码：代码里确实有相关位置`; its detail and overview badges use `找到对应代码`. Python compilation, JavaScript syntax, and diff checks pass.
Links: `src/change_passport/project_declarations.py`, `src/change_passport/auto_draft.py`, `src/change_passport/templates/review.html`, `src/change_passport/templates/review.js`, `src/change_passport/templates/review.css`
Follow-up: Preserve `已经运行验证` as a separate future state; never infer it from a source-location match.
Needs curation: yes

ID: BUG-20260910-023
Date: 2026-09-10
Status: fixed
Domain: distribution
Severity: medium
Symptom fingerprint: Building the renamed Alpha with current setuptools fails because `license = "MIT"` and the legacy `License :: OSI Approved :: MIT License` classifier are declared together.
Trigger / reproduction: Run `uv build` or allow `uv run` to rebuild the editable package after the PlainChange metadata change.
Impact: A source checkout or release package cannot be built, so the approved open-source Alpha cannot be installed.
Root cause: Current setuptools implements PEP 639 license expressions and rejects the redundant legacy license classifier.
Change made: Retain the SPDX `MIT` license expression and remove the superseded classifier.
Verification: Editable installation and the complete pytest suite rebuild successfully; final wheel/sdist and clean-environment installation remain release-gate checks.
Links: `pyproject.toml`, `LICENSE`, `TASK-20260910-038`
Follow-up: Keep build-backend compatibility in the clean-package release check rather than relying only on an existing development environment.
Needs curation: yes

ID: BUG-20260910-024
Date: 2026-09-10
Status: fixed
Domain: distribution
Severity: medium
Symptom fingerprint: The clean-installed Windows CLI completes analysis but Chinese stage labels are emitted using the host code page and appear garbled in UTF-8 consumers.
Trigger / reproduction: Run the wheel-installed `python -m plainchange .` through a non-interactive PowerShell/PTY capture and inspect progress JSON.
Impact: The generated Change Passport is valid, but the terminal experience is unreadable for the primary Chinese Alpha audience.
Root cause: Python inherited the Windows stream encoding while the consuming terminal decoded command output as UTF-8.
Change made: Reconfigure stdout and stderr to UTF-8 at the PlainChange CLI boundary when the stream supports it, with a fail-safe for test and embedded streams.
Verification: Clean-wheel direct-project analysis must show readable Chinese stage labels and finish with the human-facing Change Passport path.
Links: `src/plainchange/cli.py`, `TASK-20260910-038`
Follow-up: Preserve machine-readable receipts as UTF-8 JSON and test future native launchers on their actual console hosts.
Needs curation: yes

ID: BUG-20260910-025
Date: 2026-09-10
Status: fixed
Domain: report-localization
Severity: medium
Symptom fingerprint: English-selected report still contains Chinese workflow headings, node labels and inspector paragraphs.
Trigger / reproduction: Open the vLLM report, select English, then inspect the software workflow and expand nodes.
Impact: English readers cannot understand the owner-facing report despite a successful-looking language switch.
Root cause: The locale dictionary translated the UI shell but the renderer still consumed monolingual owner data; composed inspector sentences also bypassed exact phrase translation.
Change made: Add complete source-bound translation packs, select a translated presentation before rendering, localize composed context, and exclude evidence/script/style contents from DOM translation.
Verification: Real Edge checks cover both tabs, four overview nodes, eight detail nodes and inspector expansions at 1280/390 px: 28 states without Chinese owner-text remnants; language defaults, persistence and console checks pass.
Links: `TASK-20260910-040`, `src/plainchange/report_localization.py`, `scripts/verify-review-i18n.cjs`
Follow-up: New report packs require authored/reviewed translations; automatic model translation and semantic translation evaluation remain out of scope.
Needs curation: yes

ID: BUG-20260910-026
Date: 2026-09-10
Status: fixed
Domain: report-localization
Severity: medium
Symptom fingerprint: System workflow and Why this conclusion / technical details remain Chinese after owner-body translation.
Trigger / reproduction: Select English, expand technical explanations and technical implementation.
Impact: English readers cannot inspect the reasoning behind the translated owner summary.
Root cause: Translation covered software-control only, not beginner-review or lazy snapshot presentation; the browser checker explicitly excluded both legacy hosts. Several generated explanation strings were incorrectly protected as original evidence.
Change made: Add a review-identity-bound presentation translation set, apply it after snapshot integrity verification, expose original claims separately, localize dynamic wrappers, and include both disclosures in regression checks.
Verification: Script/DOM checks pass in 11 states including 8 workflow selections and expanded claims. Original JSON is unchanged. Browser launch was policy-blocked and the connector unavailable; no new browser-layout acceptance is claimed.
Links: `TASK-20260910-040`, `src/plainchange/report_localization.py`, `scripts/verify-review-dom.cjs`
Follow-up: Keep generated explanation translation separate from source quotations. Do not exclude whole technical panels from language coverage checks.
Needs curation: yes

ID: BUG-20260910-027
Date: 2026-09-10
Status: fixed
Domain: report-localization
Severity: medium
Symptom fingerprint: Change graph view instructions and decorated direct-code relationship labels remain Chinese in English mode.
Trigger / reproduction: Expand change details and switch before/after/diff views.
Impact: Readers cannot understand graph guidance despite translated summaries.
Root cause: Three view instructions were absent from the dictionary; arrow decoration prevented exact translation of relation labels. Prior DOM checks inspected summary/technical content but did not select change graph nodes.
Change made: Add all three instructions and translate relationship text before arrow composition; extend DOM checks across every displayed node in all three views.
Verification: 48 DOM states pass, 16 focused Python tests pass, JS syntax passes. The vLLM HTML is regenerated. No real-browser layout claim.
Links: `TASK-20260910-040`, `scripts/verify-review-dom.cjs`
Follow-up: Include all interactive graph views in translation coverage, not just summary panels.
Needs curation: yes

ID: BUG-20260910-028
Date: 2026-09-10
Status: fixed
Domain: report-localization
Severity: low
Symptom fingerprint: Expanded implementation badge remains Chinese in English mode.
Root cause: CSS ::after content bypassed DOM translation and text scanning.
Change made: Replace generated wording with a localized DOM span controlled by aria-expanded; retain its placement and styling.
Verification: 48 DOM states pass including an explicit English badge assertion; 17 focused tests pass, including a guard against Chinese CSS content. Report regenerated.
Links: `TASK-20260910-040`, `tests/test_html_renderer.py`
Follow-up: Keep user-facing wording out of CSS-generated content.
Needs curation: yes

ID: BUG-20260910-029
Date: 2026-09-10
Status: open
Domain: target-profile
Severity: high
Symptom fingerprint: Capability-rich projects without a short explicit README workflow render a generic four-step input/process/output map even when the README identifies the product clearly.
Trigger / reproduction: Analyze memdsl `7fc1d0b..a061bc4` or DigitalSelf `4da99fc..a662719`; compare the purpose answer with the software workflow.
Impact: Non-technical owners can see what the product calls itself but cannot understand how it works or where a change belongs. The visual arrows may look more informative than the explicit unverified label warrants.
Root cause: The deterministic declaration parser intentionally accepts only bounded explicit workflow forms. It does not reconcile narrative capability descriptions, recommended operating sequences, CLI/MCP surfaces, release/distribution boundaries or broader documentation into a workflow.
Current behavior: Fail-safe labels remain `自动候选` and `顺序未验证`; no changed step is invented. This protects evidence strength but does not meet the product comprehension promise.
Verification: memdsl produced 52 modules/215 edges in 1.28 s; DigitalSelf produced 1,140/2,058 in 5.16 s. Both browser checks pass technically but show the same generic four-step map. VideoFactory is the counterexample with an explicit declared workflow and a mapped changed step.
Links: `TASK-20260910-041`, `artifacts/memdsl-7fc1d0b-to-a061bc4`, `artifacts/digitalself-4da99fc-to-a662719-current`
Follow-up: Design a repository-neutral fallback that distinguishes capability maps from ordered workflows and can use model-generated candidates only through the existing evidence-constrained provider boundary. Do not add memdsl or DigitalSelf name rules.
Needs curation: yes

ID: BUG-20260910-030
Date: 2026-09-10
Status: fixed
Domain: target-profile
Severity: high
Symptom fingerprint: Projects that declare parallel capabilities are presented as a generic ordered four-step workflow.
Trigger / reproduction: Run the unchanged analyzer on memdsl `7fc1d0b..a061bc4` or DigitalSelf `4da99fc..a662719`, then compare their structured README capability material with the directional owner map. This follows and resolves BUG-20260910-029.
Impact: The arrows manufacture a mental model that is not supported by project or runtime evidence, while hiding information the repository already gives to its owner.
Root cause: The declaration boundary had only `workflow` or a fabricated generic workflow fallback. It could not represent parallel capability structure, and the software-control contract required exactly four overview nodes and directional flow semantics.
Change made: Added bounded README capability-list/table extraction, independent code-anchor reconciliation, an explicit flow-free `capability_map` contract, code-area orientation fallback, capability-aware owner copy/layout, and fail-closed change mapping for broad code-only areas. No repository-name branch was added.
Verification: 107 tests pass. Fresh memdsl and DigitalSelf reports render 5/10 capabilities and zero arrows; VideoFactory retains 7 ordered detail steps, four overview stages and its mapped quality-check change. Headless Edge passes every expansion at 1280/390 px without console errors or overflow. All target HEAD/status hashes are unchanged.
Links: `TASK-20260910-042`, `BUG-20260910-029`, `artifacts/memdsl-capability-fix`, `artifacts/digitalself-capability-fix`, `artifacts/videofactory-workflow-regression`
Follow-up: Test free-form capability prose and mixed workflow/capability projects separately; do not infer order from imports, path order or list order.
Needs curation: yes

ID: BUG-20260910-031
Date: 2026-09-10
Status: fixed
Domain: target-profile
Severity: high
Symptom fingerprint: Expanding a capability repeats the same broad capability instead of showing how it works, while loose token/prefix matching can attach unrelated benchmark, design or packaging files as corresponding code.
Trigger / reproduction: Expand `主聊天运行时` in the fixed DigitalSelf capability report; inspect its single identical child and broad source references. Compare a README capability containing generic words such as runtime or core against unrelated filenames.
Impact: The map looks interactive but does not increase understanding. False code support can make a detailed but fabricated explanation appear more trustworthy to a non-technical owner.
Root cause: The capability contract created one detail node per overview, and reconciliation accepted broad name resemblance without requiring an explicit capability code scope or multiple distinct responsibilities.
Change made: Preserve explicit Markdown code references, resolve exact files/directories or unique exact identifiers, ignore weak generic tokens, derive bounded unordered responsibility families only inside that scope, require at least two distinct children, and render unsupported capabilities as non-expandable leaves. Code-derived children are labelled separately from project declarations.
Verification: Synthetic positive and false-positive fixtures pass. Fresh fixed-range DigitalSelf, memdsl and VideoFactory reports show respectively 3 evidence-supported expandable capabilities, 5 honest leaf capabilities, and the unchanged declared workflow. Real Edge passes every node at 1280/390 px with zero console errors or horizontal overflow.
Links: `TASK-20260910-043`, `src/plainchange/project_declarations.py`, `src/plainchange/target_profile.py`, `src/plainchange/templates/review.js`, `tests/test_auto_draft.py`
Follow-up: Broader semantic decomposition may use a configured model only through the evidence-constrained candidate boundary; do not relax exact matching or convert candidates into facts.
Needs curation: yes

ID: BUG-20260911-032
Date: 2026-09-11
Status: fixed
Domain: report-ui
Severity: medium
Symptom fingerprint: The technical architecture conceptual row is visibly clipped, but the user cannot scroll horizontally to reach the remaining nodes.
Trigger / reproduction: Open the fixed DigitalSelf report, enter `这个软件怎么工作`, expand `查看技术实现结构`, and inspect the conceptual component canvas. At 1386 px viewport it has about 774 px client width and 2336 px content width while computed `overflow-x` is `hidden`.
Impact: Most conceptual nodes are rendered but unreachable, so the technical graph appears incomplete and its click-through implementation cannot be used.
Root cause: The unified-canvas override replaced the generic scrollable canvas rule with `overflow: hidden`, unintentionally suppressing horizontal user scrolling for every wide project graph.
Change made: Give the inner conceptual canvas `overflow-x: auto` and contained inline overscroll, retain vertical page ownership, and style the horizontal scrollbar with existing tokens. Extend the real-browser multi-project harness to require a scrollable computed style and non-zero movement from horizontal wheel input whenever content is wider than the canvas.
Verification: The regenerated DigitalSelf report reports 687 px client width, 2336 px scroll width and computed `overflow-x: auto`; real Edge horizontal input moves scrollLeft from 0 to 280. Desktop and 390 px document overflow remain false, console errors remain zero, and 110 tests plus JavaScript syntax checks pass.
Links: `src/plainchange/templates/review.css`, `scripts/verify-multi-project-browser.cjs`, `tests/test_html_renderer.py`, `design/ui-flows/technical-architecture-scroll-agent-20260911`
Follow-up: Preserve inner scroll ownership in future unified-canvas changes; do not solve wide graph content by reintroducing document-level horizontal overflow.
Needs curation: yes

ID: BUG-20260911-034
Date: 2026-09-11
Status: fixed
Domain: project-governance
Severity: low
Symptom fingerprint: The new BUG-20260911-033 source record was inserted after an earlier repeated `Needs curation: yes` line instead of at the physical end of the append-only ledger.
Trigger / reproduction: Search the ledger for BUG-20260911-033; its ID and date are correct, but its physical position precedes later historical entries.
Impact: No localization implementation fact or evidence was lost, but physical order again differs from ID/date order and can mislead a sequential reader.
Root cause: The patch used a repeated ledger line as its insertion anchor instead of the unique current tail, recurring the failure pattern already recorded in BUG-20260904-001.
Change made: Preserve BUG-20260911-033 unchanged as a source record and append this corrective record at the unique current tail. Treat IDs and dates as ordering authority when reading the ledger.
Verification: `rg -n "BUG-20260911-033|BUG-20260911-034" docs/project-governance/BUGLOG.md` retains both records; BUG-034 is physically last.
Links: `BUG-20260904-001`, `BUG-20260911-033`, `TASK-20260911-044`
Follow-up: Ledger patches must anchor on the unique final entry content or use an append-only helper; never anchor on repeated template fields.
Needs curation: yes

ID: BUG-20260911-035
Date: 2026-09-11
Status: fixed
Domain: report-localization
Severity: medium
Symptom fingerprint: English technical architecture still contains a generated Chinese title, candidate snapshot status and implementation-category labels while the owner screen is translated.
Trigger / reproduction: Open the fixed DigitalSelf v2 report in English mode, expand technical implementation and inspect the conceptual title, orange static-snapshot notice and `Implementation:` mappings.
Impact: The language boundary appears inconsistent and an English reader cannot distinguish intentionally preserved project declarations from PlainChange-owned untranslated text.
Root cause: TASK-044 projected only `software-control.json`. The technical view reads separate PlainChange-owned presentation fields from compact `beginner-review.json` and the lazy `system-architecture.json` payload; phrase translation also preserved nested category labels inside a translated wrapper.
Change made: Added an identity-bound generated-review presentation using stable map kind, snapshot status, automatic-profile origin and category/responsibility IDs. Apply compact-review patches before rendering and lazy-architecture patches after payload hash verification; use locale-appropriate implementation-list separators.
Verification: 114 tests pass, including a mutated-source-wording regression. Fresh DigitalSelf v3 completes in 2.192 s. Real Edge at 1280/390 px shows English conceptual title, boundary, candidate status and implementation categories, with no console/document-overflow failures and retained technical horizontal scrolling.
Links: `TASK-20260911-045`, `src/plainchange/review_presentation.py`, `src/plainchange/html_renderer.py`, `src/plainchange/templates/review.js`, `scripts/verify-multi-project-browser.cjs`
Follow-up: Project-authored source text needs a complete reviewed translation pack or a separately approved model-assisted translation workflow; do not disguise source text as deterministic English.
Needs curation: yes

ID: BUG-20260911-036
Date: 2026-09-11
Status: fixed
Domain: report-localization
Severity: low
Symptom fingerprint: A pure-English project still shows the Chinese character `能` inside every capability-card icon after switching the report to English.
Trigger / reproduction: Generate the generic automatic FastAPI `0.136.2..0.136.3` report with English-only task input, switch to English, and scan visible text on the system page.
Impact: One PlainChange-owned visual mark contradicts the promise that generated presentation follows the selected language and makes source-language attribution ambiguous.
Root cause: The capability node number slot used a hard-coded Chinese abbreviation as a decorative icon; it was outside the message-key and phrase-translation paths.
Change made: Replaced the abbreviation with the language-neutral `◆` mark, added a renderer regression assertion, and extended the real-browser harness with optional per-tab visible-Han scanning.
Verification: The regenerated FastAPI report has zero visible Han-bearing lines on both English tabs including lazy technical disclosure, excluding only the intentional native selector label `中文`. Real Edge desktop/narrow checks, 114 tests, compilation and JavaScript syntax pass.
Links: `TASK-20260911-046`, `src/plainchange/templates/review.js`, `scripts/verify-multi-project-browser.cjs`, `tests/test_html_renderer.py`
Follow-up: Keep source-language project text distinct from PlainChange-owned UI; validate what the user can see, not dormant bilingual resources in the offline file.
Needs curation: yes

ID: BUG-20260911-037
Date: 2026-09-11
Status: open
Domain: target-profile
Severity: medium
Symptom fingerprint: Automatic analysis of a bare public Git clone displays the managed/local directory name as the software name instead of the canonical project name.
Trigger / reproduction: Analyze the fixed FastAPI bare clone without a target profile; the owner headline says `change-passport-fastapi-0.136.3.git` rather than `FastAPI`.
Impact: A non-technical owner may not immediately know which product the report describes even though repository metadata, origin URL or package metadata can identify it.
Root cause: Automatic display-name selection falls back to the repository path basename and does not yet reconcile Git origin, package metadata and fixed-revision project documentation.
Current behavior: Localization is complete and evidence boundaries are honest, but the owner-facing name is awkward. No FastAPI-specific override was added.
Verification: Reproduced in `artifacts/fastapi-english-source-v3/review.html`; both fixed commits come from `https://github.com/fastapi/fastapi.git`.
Links: `TASK-20260911-046`, `artifacts/fastapi-english-source-v3`
Follow-up: Add a generic, fixed-revision project-identity resolver with explicit source precedence and provenance; do not branch on repository names.
Needs curation: yes

ID: BUG-20260911-038
Date: 2026-09-11
Status: fixed
Domain: report-localization
Severity: high
Symptom fingerprint: The English change tab appears translated until its technical disclosure is opened; summary cards, relationship nodes and inspector explanations then contain substantial PlainChange-owned Chinese text.
Trigger / reproduction: Open the pure-English FastAPI report in English, expand `Why this conclusion? View technical details`, switch relationship views and click nodes. The pre-fix strict browser scan reports Chinese headings, states, impact text, relationship labels and evidence-boundary prose.
Impact: An English owner encounters a mixed-language core decision path, while the previous acceptance result incorrectly reported complete language coverage because it scanned only the first tab's default state.
Root cause: Identity-bound generated presentation covered the system architecture but not several first-tab dynamic data paths. The browser harness opened only the system technical disclosure and did not accumulate findings across first-tab interaction states.
Change made: Extended generic presentation projection to summaries, task context, views, node details, branch groups and known automatic claims using stable IDs/counts/states. Added explicit before/after semantic states and strengthened real-browser coverage to expand, switch and click through the change view before scanning both tabs.
Verification: The failing browser evidence was preserved before the fix. The regenerated FastAPI report completes in 1.301 seconds with 2,242 cache hits; enhanced real Edge checks find zero visible Han-bearing lines across both English tabs, excluding only the native selector label `中文`. Focused presentation/render/model tests pass; full verification is recorded by TASK-047.
Links: `TASK-20260911-047`, `src/plainchange/review_presentation.py`, `src/plainchange/review_model.py`, `scripts/verify-multi-project-browser.cjs`, `tests/test_owner_presentation.py`
Follow-up: Every future localization acceptance must enumerate hidden disclosures and meaningful interactive states; never infer full report coverage from the initial viewport.
Needs curation: yes

ID: BUG-20260911-039
Date: 2026-09-11
Status: open
Domain: owner-explanation
Severity: high
Symptom fingerprint: A large product-feature commit is summarized primarily as several newly added exception branches, while its named product capability and dominant new backend/frontend surfaces are absent from the owner headline.
Trigger / reproduction: Analyze ChestnutDogAiThink `f76838f..0883fe0` (`feat: add product recommendation overview`). The 120-file, 10,159-insertion change produces the headline “新增了会抛出错误并提前停止处理的代码分支” and no change-to-capability mapping.
Impact: A non-technical owner is directed toward incidental defensive checks instead of the software behavior the change was mainly intended to add, so the central “what changed” promise fails despite factually valid low-level signals.
Root cause: Deterministic prioritization promotes available exception/signature behavior signals without first forming and comparing evidence-bound change themes across new public modules, changed surfaces, file/line distribution, fixed commit metadata and source declarations.
Current behavior: The report honestly says capability location, runtime behavior and user impact are unknown; no fabricated mapping is created. No fix or target-specific override was applied in this validation task.
Verification: Four syntactic signals come from `backend/app/clients/bigdata.py`, `backend/app/config.py` and `backend/app/llm/router.py`, while new `backend/app/tasks/product_recommendation_overview.py`, related services/tests and large frontend cards are present in the same fixed diff.
Links: `TASK-20260911-048`, `artifacts/chestnutdogaithink-product-recommendation/raw-brief.auto.json`, `artifacts/chestnutdogaithink-product-recommendation/review.html`
Follow-up: Add repository-neutral change-theme extraction and salience comparison before selecting a headline. Model output may explain a bounded packet but must not become evidence or hide unsupported surfaces.
Needs curation: yes

ID: BUG-20260911-040
Date: 2026-09-11
Status: open
Domain: project-declarations
Severity: high
Symptom fingerprint: A Markdown capability table is recognized, but its numeric count column is rendered as the visible capability description.
Trigger / reproduction: The fixed ChestnutDogAiThink README table uses columns `模块 | 数量 | 覆盖功能`. The generated eight-card capability map correctly labels `会员/订单/商品/...` but displays `4/5/3/...` as the description and inspector responsibility.
Impact: The owner can identify area names but cannot learn what any area does; the interface looks broken and fails the beginner-readable system-model goal.
Root cause: Generic table extraction treats the first non-label value as description and does not use normalized header semantics to prefer a purpose/responsibility/coverage column over count/status metadata.
Current behavior: Fixed-commit README identity and code-anchor states are preserved, but extracted presentation meaning is wrong. No ChestnutDogAiThink phrase or table override was added.
Verification: All eight overview descriptions equal the README count values: `4, 5, 3, 4, 5, 4, 12, 2`; the adjacent `覆盖功能` text is not used.
Links: `TASK-20260911-048`, `src/plainchange/project_declarations.py`, `artifacts/chestnutdogaithink-product-recommendation/software-control.json`
Follow-up: Select table fields by generic header roles, retain unused columns as metadata, and fail closed when no semantic description column exists.
Needs curation: yes

ID: BUG-20260911-041
Date: 2026-09-11
Status: open
Domain: architecture-coverage
Severity: high
Symptom fingerprint: A Vue full-stack change reports backend structure but omits the changed Vue single-file components and an MJS test from the architecture/change-location model.
Trigger / reproduction: Analyze ChestnutDogAiThink `f76838f..0883fe0`. Architecture unknowns list 43 unsupported changed files, including `ProductRecommendationOverviewCard.vue`, `ProductReplacementPlanCard.vue`, `ChatView.vue` and `frontend/tests/productReplacementPlan.test.mjs`.
Impact: The largest user-visible part of the feature is absent, preventing the report from connecting backend recommendation work to what store staff see and interact with.
Root cause: Current static architecture coverage is limited to module-level Python/JavaScript and does not parse Vue SFC script/import/component boundaries or the MJS extension.
Current behavior: Unsupported paths are disclosed and runtime/user impact stays unknown. No regex-only Vue guess or target-specific mapping was introduced.
Verification: The fixed diff contains 120 files and the report records 43 unsupported changed paths; the two new Vue product cards alone account for roughly 2,000 added lines but do not appear as architecture nodes.
Links: `TASK-20260911-048`, `artifacts/chestnutdogaithink-product-recommendation/architecture-delta.json`, `src/plainchange/architecture.py`
Follow-up: Add a bounded Vue SFC extractor and standard JavaScript module-extension support with source locations, import parity and explicit unsupported-language fallback tests.
Needs curation: yes

ID: BUG-20260911-042
Date: 2026-09-11
Status: open
Domain: architecture-scope
Severity: high
Symptom fingerprint: Tracked package dependencies are counted and grouped as first-party project modules in the system architecture.
Trigger / reproduction: Analyze the fixed ChestnutDogAiThink revision, which historically tracks `frontend/node_modules`. The system snapshot contains 868 nodes, of which 432 paths are under `frontend/node_modules`; all 432 land in `调用与用户入口`.
Impact: Half the architecture graph is third-party implementation noise, distorting module counts, group size, relationships and the apparent entry surface for a non-technical owner.
Root cause: Supported-file enumeration follows tracked paths but lacks repository-neutral dependency/build/generated-tree exclusion before parsing and grouping.
Current behavior: Oversized dependency files are disclosed as unknowns, but parseable dependency files still enter the authoritative static snapshot. No cleanup or target-repository change was performed.
Verification: Direct snapshot count finds `vendor_nodes=432` of `nodes=868`; the user-entry group has 463 nodes, 432 of them under `frontend/node_modules`.
Links: `TASK-20260911-048`, `artifacts/chestnutdogaithink-product-recommendation/system-architecture.json`, `src/plainchange/architecture.py`
Follow-up: Add explicit, auditable scope exclusions for standard dependency/build/generated roots before parsing; retain excluded-path counts and reasons so scope reduction remains visible.
Needs curation: yes

ID: BUG-20260911-043
Date: 2026-09-11
Status: fixed
Domain: project-declarations
Severity: high
Symptom fingerprint: A recognized capability table displays a numeric count instead of the semantic capability description.
Trigger / reproduction: Re-run the fixed ChestnutDogAiThink sample whose README uses `模块 | 数量 | 覆盖功能`.
Impact: The owner-facing capability cards previously named business areas but failed to explain what they do.
Root cause: Table extraction chose a positional non-label column rather than a column with a semantic header role.
Change made: Normalize table headers and prefer generic description/purpose/responsibility/coverage roles; retain conservative fallback behavior when no semantic field exists.
Verification: The generic rerun shows all eight `覆盖功能` descriptions, including customer, order, goods, stock, service, activity, report and payment responsibilities. Header-role regressions pass without target-name branches.
Links: `TASK-20260911-049`, `BUG-20260911-040`, `src/plainchange/project_declarations.py`, `tests/test_source_scope.py`
Follow-up: Exercise additional Markdown table layouts during real-model cross-project validation.
Needs curation: yes

ID: BUG-20260911-044
Date: 2026-09-11
Status: fixed
Domain: architecture-coverage
Severity: high
Symptom fingerprint: Vue single-file components and standard MJS/CJS modules are omitted from the static architecture model.
Trigger / reproduction: Re-run the fixed ChestnutDogAiThink full-stack sample containing Vue product cards and an MJS test.
Impact: User-visible frontend surfaces could not participate in source-bound project understanding or change-location validation.
Root cause: Supported-source selection was narrower than the existing JavaScript import/interface parser.
Change made: Centralized supported-source scope and route `.vue`, `.mjs` and `.cjs` through the bounded static JavaScript extractor. The result remains a source/import snapshot and does not claim Vue runtime behavior.
Verification: The rerun contains 79 Vue nodes and 3 MJS nodes; source-scope and full-suite regressions pass. Unsupported runtime, injection and network behavior remain explicit limitations.
Links: `TASK-20260911-049`, `BUG-20260911-041`, `src/plainchange/source_scope.py`, `src/plainchange/architecture.py`, `tests/test_source_scope.py`
Follow-up: Add framework-specific runtime evidence only through a separate evidence adapter, never by upgrading static syntax matches.
Needs curation: yes

ID: BUG-20260911-045
Date: 2026-09-11
Status: fixed
Domain: architecture-scope
Severity: high
Symptom fingerprint: Tracked dependency/build/generated trees are parsed as first-party architecture nodes.
Trigger / reproduction: Re-run a repository that tracks `frontend/node_modules` and other generated roots.
Impact: Module counts, group proportions and owner-facing architecture were dominated by third-party noise.
Root cause: Fixed-Git enumeration lacked a shared first-party source-scope predicate before parsing.
Change made: Exclude standard dependency/build/generated path segments before both full and incremental static parsing, and record the excluded file count in snapshot limitations.
Verification: The ChestnutDogAiThink rerun falls from 868 to 518 nodes, contains zero dependency/build-tree nodes and reports `excluded vendored/generated source files: 480`; generic exclusion regressions and the full suite pass.
Links: `TASK-20260911-049`, `BUG-20260911-042`, `src/plainchange/source_scope.py`, `src/plainchange/architecture.py`, `tests/test_source_scope.py`
Follow-up: Make project-specific generated directories configurable only as auditable source-scope input, not hidden name rules.
Needs curation: yes

ID: BUG-20260911-046
Date: 2026-09-11
Status: fixed
Domain: semantic-analysis
Severity: medium
Symptom fingerprint: A real structured project-understanding response chooses `capability_map` but emits a workflow role in one component's redundant `type` field, causing the entire source-bound result to fail validation.
Trigger / reproduction: Run the first model stage through the configured compatible provider on the fixed ChestnutDogAiThink context; the provider returns a capability map whose first component type is not `capability`.
Impact: Harmless disagreement in derived presentation metadata prevents a valid project model from reaching the report, even though the parent structure already determines every node's type.
Root cause: The contract represented capability kind twice and required the model to keep both copies synchronized; JSON schema enumerated both values but could not express the cross-field rule reliably across compatible gateways.
Change made: Derive every capability-map component type from `structure_kind` before validation and state the cross-field rule explicitly in the prompt. Workflow role values remain model-proposed and fail closed when invalid.
Verification: A regression supplies `process` types under a capability map and receives canonical `capability` types; focused semantic and mocked-provider tests pass. The subsequent real provider project-understanding stage succeeds and remains source-bound.
Links: `TASK-20260911-050`, `src/plainchange/semantic_analysis.py`, `src/plainchange/model_adapter.py`, `tests/test_semantic_analysis.py`
Follow-up: Remove other redundant model fields when their value is fully determined by a validated parent contract.
Needs curation: yes

ID: BUG-20260911-047
Date: 2026-09-11
Status: fixed
Domain: model-provider
Severity: high
Symptom fingerprint: Project understanding succeeds, but change interpretation repeatedly returns HTTP 502 when a complex change sends the complete 622 KB generator packet to a compatible provider.
Trigger / reproduction: Run model-first analysis on the 120-file ChestnutDogAiThink change through the configured provider. The second stage fails in about 3.5 seconds on repeated attempts while the smaller first stage succeeds.
Impact: The full product path cannot finish on the exact complex business changes for which semantic interpretation is most valuable; retrying wastes tokens without changing the request shape.
Root cause: The second model input duplicated the complete evidence collection and architecture delta, including a 194 KB patch and hundreds of evidence records, even though final validation remains local.
Change made: Build a provider-neutral bounded change context from change facts, highest-churn file records, task/behavior evidence, selected changed architecture nodes, counts, unknowns and limitations. Exclude the full patch and restrict all model evidence enums to the transmitted subset; validate the result against the complete local packet afterward.
Verification: The mocked request is below 150 KB and excludes `git.patch`. The real retry completes change interpretation in 12.468 seconds and the full report in 17.827 seconds; four claims are accepted, two are safely downgraded and no claim is rejected.
Links: `TASK-20260911-050`, `src/plainchange/model_adapter.py`, `tests/test_pipeline.py`, `artifacts/chestnutdogaithink-model-first-spark-v3`
Follow-up: Measure quality/cost across more large projects and make the evidence budget explicit in run telemetry before choosing a long-term default.
Needs curation: yes

ID: BUG-20260911-048
Date: 2026-09-11
Status: fixed
Domain: owner-presentation
Severity: medium
Symptom fingerprint: A valid model short headline is rendered as a long first-screen sentence because the renderer concatenates it with the detailed explanation and runtime boundary.
Trigger / reproduction: Run a valid model-first analysis whose semantic change summary provides both `headline` and `explanation`.
Impact: The primary software-owner decision surface violates the result-first, ten-second reading contract even when the model follows the constrained output schema.
Root cause: The same combined text value was used for both the five-question detail and the first-screen title.
Change made: Preserve the validated semantic headline as a distinct projection field and use it only for the first-screen title; retain the combined text in detailed explanation surfaces.
Verification: Mocked pipeline regression asserts the title/detail split. The fixed ChestnutDogAiThink rerun renders a 23-character title, keeps the detailed explanation, has four accepted/two downgraded claims and preserves runtime uncertainty. Full 124-test suite, compilation, JavaScript syntax and diff checks pass.
Links: `TASK-20260911-052`, `TASK-20260911-053`, `src/plainchange/auto_draft.py`, `tests/test_pipeline.py`, `artifacts/chestnutdogaithink-owner-language-v2-headline`
Follow-up: Evaluate headline usefulness with software owners across multiple business applications; schema validity alone is not comprehension acceptance.
Needs curation: yes

ID: BUG-20260911-049
Date: 2026-09-11
Status: fixed
Domain: owner-presentation
Severity: medium
Symptom fingerprint: A first-screen card can carry the green `已确认` label while its body says that available evidence is insufficient and includes a validator downgrade reason.
Trigger / reproduction: Run model-first analysis on the fixed memdsl MCP Registry release range; the valid headline and source-bound audience survive, but the confirmed-change claim body is replaced by an architecture-evidence fallback.
Impact: A software owner can mistake a safe unknown explanation for a confirmed result because the card's visual state and its rendered body disagree.
Suspected root cause: First-screen state appears to be selected from the original claim state before projection/validator fallback text is applied. Confirm against other fallback paths before changing the state contract.
Current mitigation: The detailed text remains honest; no target-specific wording, target modification or presentation suppression was used.
Links: `TASK-20260911-054`, `artifacts/memdsl-mcp-registry-owner-language-v2/software-control.json`, `src/plainchange/auto_draft.py`
Follow-up: Trace the generic claim-to-first-screen projection, make state derive from the final rendered statement, and add a regression that forbids confirmed/unknown text mismatch.
Needs curation: yes

Resolution update (2026-09-11): fixed by TASK-20260911-056. The confirmed card
now falls back to the deterministic fixed-Git file-change fact whenever no
accepted function claim exists, rather than carrying a validator-downgraded
architecture claim. Regression coverage asserts that an unknown architecture
claim cannot provide the green-card text or claim basis. A real memdsl rerun
renders the corrected text and preserves the target revision. The model schema
and prompt now also forbid blank limitation entries that caused the first
rerun to fail visibly. Needs curation: yes.

ID: BUG-20260911-050
Date: 2026-09-11
Status: fixed
Domain: model-language-contract
Severity: high
Symptom fingerprint: An English-labelled owner report and its README GIF can
still contain Chinese explanation text, candidate-profile labels, or a
Chinese template suffix.
Trigger / reproduction: Request `--human-language en` from a compatible
provider and render the model-assisted report. Some providers treat prompt
language as advisory; cached model understanding and PlainChange-owned
deterministic text can then retain a prior/default language. A provider may
also ignore nested JSON-schema `maxItems` limits.
Impact: A reader cannot trust the selected language, and an oversized evidence
list can make an otherwise useful report fail at the provider boundary.
Root cause: Language was requested but not validated as output contract;
generated/projection strings were incompletely language-aware; a template
sentence was split around a translated strong element; and nested cardinality
was trusted to the provider.
Resolution: TASK-057 validates English model-owned prose fail-closed while
excluding source/structural fields, validates cache hits, makes generated and
deterministic owner text language-aware, fixes the split literal, and bounds
known evidence arrays loss-only before validation.
Verification: 40 focused tests and the 130-test full suite pass. A real
unchanged PlainChange target produces a fully English v9 report; its refreshed
two-frame English GIF holds each view for 4000 ms. No key, target content, or
provider configuration is published.
Links: `TASK-20260911-057`, `src/plainchange/model_adapter.py`,
`src/plainchange/auto_draft.py`, `src/plainchange/semantic_analysis.py`,
`src/plainchange/templates/review-i18n.js`, `tests/test_model_adapter.py`,
`docs/images/plainchange-self-demo-en.gif`
Needs curation: yes

ID: BUG-20260912-051
Date: 2026-09-12
Status: fixed
Domain: first-run-onboarding
Severity: high
Symptom fingerprint: Selecting a Git project whose current branch has no
saved versions exposes `fatal: ... does not have any commits yet` in the
owner-facing project picker.
Trigger / reproduction: Initialize a Git repository without creating its first
commit, then choose it in the portable guided flow.
Impact: A non-technical software owner sees an unexplained implementation
error at the first step and cannot tell what action is required.
Root cause: Repository inspection ran `git log` before checking whether `HEAD`
exists, so Git's failure bypassed the intended friendly history guard.
Resolution: TASK-059 detects zero and one saved versions before constructing a
comparison and returns distinct owner-language guidance. The logic is generic
and does not inspect or special-case the reported repository name.
Verification: Focused onboarding suite: 11 passed. Full suite: 139 passed in
62.33 seconds. The rebuilt portable executable returned the friendly error
through its real HTTP endpoint for the unchanged reported zero-version
repository; no `fatal` or `commit` text appeared.
Links: `TASK-20260912-059`, `src/plainchange/onboarding.py`,
`tests/test_onboarding.py`
Needs curation: yes

ID: BUG-20260912-052
Date: 2026-09-12
Status: fixed
Domain: project-governance
Severity: low
Symptom fingerprint: The new `EVO-20260912-045` record was inserted after an
older ledger entry instead of being physically appended after
`EVO-20260912-044`.
Trigger / reproduction: Apply an underspecified patch anchored only on the
repeated `Needs curation: yes` line in the append-only evolution ledger.
Impact: File position no longer represents chronology for this entry, although
the unique ID, date and content remain intact.
Root cause: The patch matched the first repeated anchor rather than the end of
the file.
Resolution: Preserve the already written entry, because the ledger is
append-only, and append `EVO-20260912-046` to make the physical-order exception
and authoritative ID sequence explicit.
Verification: `rg -n "^ID: EVO-"` locates `EVO-20260912-045` at its retained
position and `EVO-20260912-046` at the physical end; no existing ledger entry
was moved or deleted.
Links: `EVO-20260912-045`, `EVO-20260912-046`
Needs curation: no

ID: BUG-20260912-053
Date: 2026-09-12
Status: mitigated
Domain: git-ai-integration
Severity: high
Symptom fingerprint: Invoking `git-ai install-hooks --help` performs a real
user-level hook/extension installation and starts a background scan instead of
showing command help; the scan created a multi-gigabyte local metrics database.
Trigger / reproduction: Run the official Git AI v1.7.5 Windows x64 binary as
`git-ai install-hooks --help` on a machine with Codex, Claude Code and VS Code.
Impact: The command changed global Agent configuration, installed an editor
extension, started a daemon and wrote user-level state despite the validation
task being explicitly scoped to an isolated repository.
Root cause: PlainChange's validation procedure assumed conventional nested
`--help` behavior without first confirming the command parser contract. Git AI
treats the trailing token as irrelevant and executes `install-hooks`.
Mitigation: Stop the Git AI daemon; run the documented `uninstall-hooks`;
uninstall the exact VS Code extension; move only the newly created `.git-ai`
state and extension residual to the recycle bin; verify both Agent configs parse
and contain zero Git AI references. The release EXE remains only under `E:`.
Verification: Final inventory reports zero Git AI processes, no user `.git-ai`
directory, zero Git AI references in Codex/Claude configuration and zero
registered VS Code Git AI extensions. The accidentally created state is
recoverable from the recycle bin.
Links: `TASK-20260912-061`, Git AI v1.7.5 CLI reference
Follow-up: Treat mutating subcommands as mutating even when passed `--help`;
inspect official reference/source before invoking them. A real integration must
be separately approved as a user-level installation.
Needs curation: yes

ID: BUG-20260912-054
Date: 2026-09-12
Status: fixed
Domain: git-ai-integration
Severity: medium
Symptom fingerprint: PlainChange reports Git AI as `invalid/nonzero_exit` on
Windows even though the installed `git-ai diff <base>..<head> --json` command
returns valid authorship data when invoked directly.
Trigger / reproduction: Let `shutil.which("git-ai")` resolve the command through
Windows `PATHEXT`; the returned path uses the uppercase suffix `git-ai.EXE`.
Git AI v1.7.5 dispatches by invocation name and proxies `diff` to ordinary Git
when called with that spelling, producing Git usage output and exit code 129.
Impact: Installed Git AI provenance is silently downgraded to invalid on a
normal Windows PATH, so users do not see valid authorship records.
Root cause: The adapter preserved the filesystem path but did not account for
Git AI's case-sensitive executable-name dispatch on a case-insensitive platform.
Resolution: Normalize only an already discovered Windows `.EXE` suffix to
lowercase `.exe`; do not rewrite the directory, executable base name, arguments
or target-repository behavior.
Verification: A dedicated regression covers Windows versus POSIX discovery.
The real fixed range now produces an `available` summary with 4 AI additions,
100% recorded coverage and one sanitized session; the full 146-test suite,
package build and Windows portable build pass.
Links: `TASK-20260912-061`, `src/plainchange/agent_provenance.py`,
`tests/test_agent_provenance.py`
Needs curation: yes

ID: BUG-20260912-056
Date: 2026-09-12
Status: mitigated
Domain: project-governance
Severity: low
Symptom fingerprint: `BUG-20260912-055` was appended after a repeated
`Needs curation: yes` anchor rather than at the physical end of the append-only
BugLog.
Trigger / reproduction: Apply a patch whose only context is a footer repeated by
many ledger entries.
Impact: The source record remains intact but its physical location does not match
the chronological ID order, which can confuse readers and append tooling.
Root cause: The closeout patch used a non-unique anchor and matched the first
eligible occurrence.
Mitigation: Preserve the already-written record and add this explicit correction
at the physical end; future appends must inspect and match the unique current tail.
Verification: `BUG-20260912-055` occurs once, this correction is the last BugLog
record, and neither record was deleted or rewritten.
Links: `BUG-20260912-055`, `TASK-20260912-063`
Needs curation: no

ID: BUG-20260912-057
Date: 2026-09-12
Status: fixed
Domain: owner-experience
Severity: high
Symptom fingerprint: A report with completed tests, builds and integration
checks still tells the software owner only that behavior is unverified and asks
them to perform engineering checks, so the report does not reduce decision work.
Trigger / reproduction: Analyze PlainChange's Git AI integration with real
historical test/build/integration results supplied only as unstructured task
context; inspect the first report tab.
Impact: The owner cannot distinguish completed verification from remaining
boundaries, cannot see why a gap exists or who should close it, and may repeat
checks that already passed.
Root cause: Test receipts had no strict packet contract or owner projection;
model unknown claims and generic attention cards were rendered without a fixed
evidence source that could take precedence. A downgraded receipt claim in a
non-attention section could also be misclassified as a new owner task.
Resolution: Add hash- and commit-bound structured verification receipts; carry
them through the packet, validated brief and review model; render completed
checks separately from explicit attention gaps; attach reason, method and
responsibility; and make supplied receipts override contradictory missing-
receipt prose. Only attention claims can become owner-facing verification gaps.
Verification: The Git AI self-report shows six passed checks, zero failures and
one cross-project/version/production boundary. Model prose no longer claims the
receipt is absent. The full 154-test suite, JavaScript syntax check, Python
package build and Windows portable build pass.
Links: `TASK-20260912-064`, `EVO-20260912-051`,
`src/plainchange/verification.py`
Needs curation: yes

ID: BUG-20260912-058
Date: 2026-09-12
Status: fixed
Domain: owner-experience
Severity: high
Symptom fingerprint: A report shows completed test receipts and declares no
remaining gap even though an accepted attention claim includes limitations and
an explicit next check such as final visual acceptance.
Trigger / reproduction: Analyze VideoFactory `58d2149..d6594e3` with fixed
receipts for the full suite, focused render tests and package build. The model
correctly states that a finished video still needs human visual acceptance, but
the verification control reports zero gaps.
Impact: The owner may interpret completed automated checks as sufficient and
miss the real-world acceptance step that the evidence explicitly preserves.
Root cause: The control builder only projected `claim_type=unknown` attention
claims. Verified receipt statements and supported attention inferences with a
`next_check` were discarded from the remaining-work view.
Resolution: Treat every explicit attention `next_check` as a remaining
verification step, while keeping receipt results in the completed-check list.
Non-unknown attention uses the next check as its gap label, retains the first
limitation as the reason, assigns human acceptance to the owner/actual user and
deduplicates identical checks.
Verification: The VideoFactory report now shows three passed checks and one
remaining human visual/delivery check with reason, method and responsibility.
PlainChange's 155-test suite and both release builds pass.
Links: `TASK-20260912-065`, `EVO-20260912-052`,
`tests/test_verification.py`
Needs curation: yes

ID: BUG-20260912-059
Date: 2026-09-12
Status: fixed
Domain: owner-experience
Severity: high
Symptom fingerprint: Different project reports with verification gaps show the
same “one decision” acceptance sentence without naming what remains unverified;
multiple gaps are also incorrectly counted as one.
Trigger / reproduction: Open the owner decision panel in the PlainChange Git AI
and VideoFactory verification reports, or build a control with two attention
claims containing distinct `next_check` values.
Impact: The owner must reread the technical gap panel to discover what they are
accepting, and may mistake a generic acceptance prompt for a project-specific
decision. The incorrect count can hide that several boundaries remain.
Root cause: `build_verification_control` hard-coded both the decision count and
body whenever `gaps` was non-empty; the decision object did not carry its source
items.
Resolution: Build the decision from the actual failed checks or gaps, retain the
real count, list each item and responsible party, localize PlainChange-owned
copy, and state that early acceptance does not change verification status.
Verification: Single-gap, multi-gap, failed-check and ready-state regressions
pass. Rebuilt PlainChange Git AI and VideoFactory reports contain different
concrete decision items and zero matches for the old template. The full 157-test
suite, JavaScript syntax check, Python package build and `git diff --check` pass.
Automated browser acceptance was not recorded because the browser connection
failed. The owner later inspected the Git AI v10 report in the real product
surface and accepted it for an update; this does not cover the separate
VideoFactory v3 visual state.
Links: `TASK-20260912-066`, `EVO-20260912-053`,
`src/plainchange/verification.py`, `tests/test_verification.py`
Needs curation: yes
