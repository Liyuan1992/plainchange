# TASK-20260909-018: Interactive top-down architecture graph

State: DONE
Tier: standard

## Approval and goal

The owner rejected the vertical card list on 2026-09-09 and explicitly stated: “我希望架构是图，是可点击可交互的，你现在是从上到下排列，我觉得不太对”. This approves restoring an actual node-and-edge graph whose primary direction is top to bottom, while retaining direct node interaction and the existing explanation panel.

## Scope

1. Convert topology-derived ranks into graph rows and place parallel components side by side within each row.
2. Draw directional top-to-bottom connectors between exact configured relationships, with obstacle checks and an explicit no-arrow fallback when a truthful route cannot be found.
3. Keep workflow nodes clickable, synchronize selection with the right inspector, and let a second click collapse a directly mapped implementation expansion.
4. Preserve inline static implementation drill-down below the conceptual graph in the same architecture canvas.
5. Validate the generic renderer on the self-hosted Change Passport and external FastAPI artifacts, including branch/merge routing, interaction, console state, and narrow fallback.

## Non-goals

- Do not infer runtime order, introduce new profile facts, change static-import evidence, or modify target repositories.
- Do not hard-code FastAPI or Change Passport node IDs, labels, paths, counts, or topology.
- Do not add graph editing, zoom/pan, physics layout, model calls, backend APIs, or new image assets.
- Do not commit, push, package, deploy, or release.

## Risks and stop conditions

- Stop and retain the complete textual relationship fallback if any visible connector crosses a non-endpoint card or a configured relationship cannot be routed.
- A topological rank is a presentation order, not proof of runtime execution; preserve the existing profile-source and evidence-boundary language.
- Narrow screens may use an ordered clickable card fallback with relationships in text; do not squeeze an unreadable desktop graph into mobile width.

## Verification plan

- Run the full test suite, Python compileall, JavaScript syntax check, and Git diff check.
- Regenerate both retained reports from their existing evidence packets.
- In a real browser verify node/edge counts, top-to-bottom row progression, zero connector/card intersections, node selection/second-click collapse, inline implementation expansion, right-inspector synchronization, zero console errors, and narrow no-overflow behavior.

## Handoff condition

Complete only after implementation, browser evidence, and append-only bug/evolution records are present. Independent beginner retelling remains a separate product-validation gate.

## Result and observed verification

The conceptual architecture is again a real graph. Deterministic topology ranks progress downward, parallel components share a row, and every safely routed configured relationship has a source-bottom to target-top arrow. A node remains the interaction entry: clicking it selects only that node, opens its mapped static implementation below the graph, and updates the right inspector; clicking the same node again collapses the implementation.

- FastAPI: 9 nodes, 9 arrows, 9 relationship rows, 5 descending graph rows, 0 connector intersections with unrelated nodes, no canvas overflow, and 7 inline implementation subdomains.
- Self-hosted Change Passport: 8 nodes, 8 arrows, 8 relationship rows, 7 descending graph rows, 0 connector intersections, and no canvas overflow.
- Narrow FastAPI at 390 px: one clickable card column, arrows hidden, 9 relationship rows retained, document width 390 px.
- Node-state regression found and fixed during browser review: multiple workflow nodes mapped to the same static group no longer all appear selected; only `application_routing` was selected/expanded in the interaction check.
- `uv run pytest -q`: 50 passed. Compileall, JavaScript syntax, target-identity source scan, and Git diff check passed. The diff check emitted only existing LF/CRLF normalization warnings.
- Persistent screenshots: `design/ui-flows/interactive-top-down-architecture-graph-agent-20260909/04-validation/current-after.png` and `mobile-after.png`. Node Playwright capture was unavailable; the existing Python Playwright installation produced the images without adding a project dependency.
