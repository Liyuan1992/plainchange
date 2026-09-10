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
