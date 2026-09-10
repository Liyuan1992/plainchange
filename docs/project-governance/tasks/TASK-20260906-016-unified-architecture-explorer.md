# TASK-20260906-016: Unified architecture explorer

State: DONE
Tier: standard

## Approval and goal

The owner explicitly requested a single architecture image instead of separate first- and second-layer regions with chained buttons. Build one generic architecture explorer: a workflow component is the direct first-level entry, its mapped static implementation expands in the same canvas, and the right panel explains the current focus.

## Scope

1. Replace nested workflow action buttons and split static drill-down regions with direct workflow-card activation.
2. Keep the workflow overview visible while expanding its profile-mapped static section and implementation subdomains inline.
3. Move focus facts, static relationship prose, evidence boundaries, and optional raw-module reveal into the existing right inspector.
4. Preserve profile neutrality, static-import-only meaning, and explicit no-mapping/fallback states.
5. Validate on self-hosted and FastAPI artifacts at desktop and 390 px.

## Non-goals

- Do not alter profile schemas, source collection, static graph facts, target repositories, baseline state, or model boundaries.
- Do not synthesize runtime arrows, workflow-to-module causality, or a target-specific consumer branch.
- Do not commit, push, package, or release.

## Risks and acceptance

- A conceptual component can map to no static section or more than one. Preserve that state in the right panel; only direct-expand an unambiguous mapped group.
- Inline expansion must not cause SVG connectors to pass through cards. If the global relation drawing cannot remain unobscured while expanded, use the right-side textual relationship explanation instead.
- Both test artifacts must prove that the same generic renderer and profile mapping work without FastAPI-specific source logic.

## Result

The architecture tab is now one explorer workspace. A profile-mapped work-flow component is directly clickable; it retains its place in the work-flow map while its static section and implementation subdomains appear inside the same main canvas. The persistent right panel replaces the old lower-page relation and module drill-down path with the current focus, facts, evidence boundary, relationship prose, and an optional technical-module disclosure.

FastAPI and the self-hosted Change Passport sample use the same consumer: both open their selected static section in the canvas; FastAPI renders 7 subdomains and Change Passport renders 5. No nested conceptual implementation buttons remain. Live desktop browser checks confirmed the inline containment, focus transitions, zero warnings/errors, and 390 px layout with no horizontal overflow. Full pytest, compileall, JavaScript syntax, and diff checks pass.
