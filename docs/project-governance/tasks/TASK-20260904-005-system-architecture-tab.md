# TASK-20260904-005: System architecture tab

State: DONE — IMPLEMENTED AND BROWSER VERIFIED
Tier: standard

## Trigger and authority

The owner requested a switchable tab that directly shows the overall system architecture. This is a material scope expansion: confirmed PRD v1.2 and ADR-0002 explicitly excluded a complete architecture visualization, while the current `ArchitectureDelta` contains only a changed-node neighborhood.

The request initially authorized analysis and a bounded PRD amendment. The owner's later instruction “直到完成之前不需要我确认” explicitly enabled fast mode for the remaining v1.3 design and implementation stages. That authority covers local implementation and verification only; it does not approve the pending architecture baseline or authorize commit, push, packaging, deployment, or DigitalSelf product integration.

## Evidence observed before planning

- Current review sample: 14 displayed nodes and 32 explicit omitted IDs.
- Current pending candidate baseline: 46 bounded-neighborhood nodes and 109 edges.
- Frozen DigitalSelf Head: 1,057 supported Python/JavaScript/TypeScript files were parsed by the current bootstrap analysis.
- `ArchitectureBaseline.scope` is `bounded-module-neighborhood`; presenting the 46-node proposal as the whole system would be misleading.
- High-level path counts show stable candidate group boundaries, including `web` 168, `memory` 163, `tests` 313, `agents` 51, `core` 43, `cli` 36, `skills` 27, and `scripts` 27.
- A read-only full-Head feasibility run completed in 2.536 seconds: 1,057/1,057 supported files parsed, 0 failures, 1,768 verified import edges, and an estimated 1.52 MiB full JSON payload.
- Raw path grouping yields 82 groups and 183 cross-group edge bundles, which is too dense for the first screen. The confirmed product glossary must coarsen them to roughly nine human sections while retaining complete module and source-edge mappings.
- The DigitalSelf target Git-status SHA-256 was `76CCA76FC1B3F8C515D86D168BE75F6880979DF64D0D30396D818396D821FF79` before and after the feasibility run.
- A proposed nine-section glossary assigned all 1,057 modules exactly once with zero unclassified paths. The 1,768 source edges aggregate to 39 directed section-edge bundles while retaining 1,000 cross-section and 768 internal source-edge identities.
- The seven changed modules map deterministically to `能力与工具` (5), `Agent 与执行核心` (1), and `测试与质量保障` (1), giving the overall tab a source-backed change overlay.

## Goal

Add a first-class `整体架构` tab beside the existing `变化解读` experience. It must give a non-coder a one-screen system overview, allow deterministic one-level drill-down, highlight the current change in system context, and provide a complete machine-readable static snapshot for later system use.

## Planned scope

1. Add a versioned `SystemArchitectureSnapshot` over all successfully parsed supported modules at the frozen Head commit.
2. Preserve every node and verified static import edge in `system-architecture.json` with coverage and limitation metadata.
3. Deterministically aggregate modules into project sections; every group edge retains its source edge IDs.
4. Add `system_architecture` to the beginner review projection and bind its change overlay to the same `ArchitectureDelta` node IDs.
5. Add top-level `变化解读 / 整体架构` tabs; retain the current Before / After / Diff controls inside change review only.
6. Render a complete section overview first, then allow one-level section-to-module drill-down and node inspection.
7. Keep the artifact local, read-only, no-network, single-file, and independent from baseline approval.

## Non-goals

- Claiming a runtime, deployment, database, network, dynamic-call, or cross-repository architecture without corresponding evidence.
- A raw 1,057-node first-screen spider graph, full symbol/call graph, or generic knowledge-graph platform.
- LLM-created nodes, edges, system boundaries, or unverified business responsibilities.
- Automatic baseline approval, target-repository mutation, commit, push, package, deploy, or DigitalSelf production integration.
- Silently treating unsupported or failed-to-parse files as covered.

## Planned files after all UI gates are confirmed

- `src/change_passport/architecture.py`: full supported Head snapshot and deterministic group aggregation.
- `src/change_passport/review_model.py`: system architecture projection and delta overlay parity.
- `src/change_passport/pipeline.py`: emit `system-architecture.json` and pass the snapshot into final review generation.
- `src/change_passport/templates/review.html`: top-level tabs and system architecture region.
- `src/change_passport/templates/review.css`: responsive overview canvas, group and drill-down states.
- `src/change_passport/templates/review.js`: tab state, group selection, one-level drill-down and return-state preservation.
- `tests/test_architecture.py`, `tests/test_review_model.py`, `tests/test_html_renderer.py`, `tests/test_pipeline.py`: identity, coverage, aggregation, overlay and UI contract checks.

## Verification plan

1. Unit/property tests: every parsed module belongs to exactly one group; group totals equal coverage; every group edge resolves to source edges; snapshot identity is stable.
2. Parity tests: changed node IDs and statuses match `ArchitectureDelta`; view projection cannot add topology or promote candidate baseline authority.
3. Full regression, compileall and JavaScript syntax checks.
4. Formal immutable DigitalSelf regeneration with target Git-status fingerprint before and after.
5. Desktop and mobile browser smoke for tab switching, system overview, group selection, module drill-down, return-state retention and change highlighting.
6. Human check: a non-coder can point to the changed system section and describe at least three major sections without opening technical IDs.
7. Performance/size check: formal DigitalSelf generation stays within 10 seconds and the no-network HTML stays within 2.5 MiB without dropping machine snapshot nodes, edges, or evidence IDs.

## Risks and stop conditions

- The full snapshot makes generation, HTML size, or browser interaction impractical without a bounded aggregation layer.
- Deterministic paths are too weak to support understandable section names without an explicitly confirmed project glossary.
- UI says “overall system” while coverage excludes material code or runtime relationships without a visible limitation.
- Grouping or rendering creates edges that cannot be traced to source edges.
- The change requires baseline approval, server state, remote upload, or target-repository writes.

## Approval and completion evidence

- Fast-mode authority: the owner explicitly said “直到完成之前不需要我确认”.
- Final v1.3 PRD amendment: `D:\Dev\Projects\DigitalSelf\design\ui-flows\ai-coding-session-review\01-prd\prd-v1.3-architecture-tab-draft.md`, SHA-256 `B4B97D38C0BEF959D7D0EA19E4F82CA36BF7F20D9753BE8B7804A1D1177676DF`.
- Tokens: unchanged; all 22 confirmed CSS custom properties were reused.
- Final implementation spec: SHA-256 `B7B2348819E04E189A4AA9CAE4F1E45327BCE9FAD1CCDC7E6437E0CFF45D0AD8`.
- Formal machine snapshot: `artifacts/digitalself-430c342-m15/system-architecture.json`, SHA-256 `7484AFEE355CE286336044327C7DC9D0FE06AEF05980E55C8A7215D4CDED459C`.
- Formal review model: SHA-256 `C70A21D9E990120FC7C34B5C4AFCB3B0AD0E98DA5C4AB4A90CCA18673B098759`.
- Formal HTML: SHA-256 `75C30C2941A1D6D37BA195ED82D64E090798E725A3ED81FC68F7358F85769C1A`; 1,856,555 bytes.

## Implementation outcome

- `SystemArchitectureSnapshot` covers all 1,057 / 1,057 supported DigitalSelf Head modules and 1,768 verified static import edges.
- All modules are assigned exactly once across 9 Chinese system sections; 0 paths remain unclassified.
- 39 directed section-edge bundles retain every cross-section source edge ID exactly once.
- The same delta IDs drive both views. Seven changed modules map to 能力与工具 5, Agent 与执行核心 1, and 测试与质量保障 1.
- The generated page defaults to the existing change explanation and adds a first-class `整体架构` tab with system overview, section focus, module drill-down, node inspection, gradual Escape return, and responsive fallback.
- The page visibly states that this is a candidate supported-code static snapshot, not a complete runtime/deployment/database/network architecture.

## Verification outcome

- `uv run pytest -q`: 41 passed.
- `uv run python -m compileall -q src`: passed.
- `node --check src/change_passport/templates/review.js`: passed.
- Formal `prepare + finalize`: 6.3 seconds, below the 10-second gate; HTML stayed below 2.5 MiB.
- DigitalSelf formal-generation Git-status fingerprint before/after: identical.
- Browser desktop: top-level tab switch, full overview, section selection, 55-module drill-down, and 5 changed-module Chinese labels passed.
- Browser mobile at 390 px: page scroll width equaled viewport width; SVG relation tangle was hidden while the complete textual relation list remained available.
- Browser console: 0 warnings/errors.

The pending baseline proposal remains pending and was not promoted.
