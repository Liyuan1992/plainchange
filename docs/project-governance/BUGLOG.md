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
