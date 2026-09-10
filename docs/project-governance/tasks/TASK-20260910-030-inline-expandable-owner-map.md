# TASK-20260910-030: Inline-expandable owner map

State: DONE
Tier: standard

## Trigger and authority

The owner explicitly rejected the current `四步总览 → 详情替换画布 → 返回四步总览` interaction and requested an inline interaction: the four-step global map must remain visible, a clicked step must extend its detailed steps in place, and the same step must be collapsible. This authorizes a bounded presentation and interaction change without another confirmation. It does not authorize new evidence, target-specific behavior, commits, pushes, deployment, or target-repository mutation.

## Source facts

- `software-control.v1` declares four overview nodes and maps every detailed workflow node to one overview node through `detail_node_ids`.
- Overview and detail change states already come from the same source-bound workflow nodes.
- The current renderer replaces the overview with one detail-only graph and exposes a `返回四步总览` action, so selecting one step removes the surrounding software context.
- The owner needs local expansion to preserve the answer to both “整个软件怎么工作” and “这一步里面发生什么”.

## Approved plan

1. Keep all four overview nodes rendered at all times.
2. Make an overview click toggle its source-declared detail group directly beneath that node; clicking another overview moves the single open group, and clicking the open overview collapses it.
3. Keep one explicit `收起当前步骤` action and Escape-key collapse as secondary exits, without requiring either one for normal use.
4. Synchronize the right inspector with the selected overview/detail node while preserving changed-versus-selected state semantics.
5. Preserve generic topology, offline rendering, collapsed relation evidence, narrow fallback, and the no-target-special-case boundary.

## Non-goals

- No change to the `software-control.v1` schema, automatic drafting, evidence authority, target profile, or technical payload.
- No invented workflow steps or connections; inline details and their relation labels must come only from `detail_node_ids` and declared flows.
- No vLLM, FastAPI, repository-name, framework-name, or fixed-node conditional.
- No nested multi-group accordion, free-form graph editor, animation library, persisted user preference, or runtime claim.

## Risks and stop conditions

- Stop if expanding a group removes or hides any overview node.
- Stop if an inline detail can appear under an overview that does not declare it.
- Stop if changed styling and inspector language can disagree with the selected source node.
- Stop if narrow mode introduces horizontal scrolling or depends on SVG connectors to remain understandable.

## Verification plan

- Add focused renderer assertions for persistent four-step overview, toggleable inline detail, explicit collapse, state parity, and absence of the old replacement-depth state.
- Run full tests, compileall, JavaScript syntax, offline-resource scan, artifact payload/hash checks, and `git diff --check`.
- Regenerate the fixed vLLM artifact and use real Edge to verify initial, expanded, collapsed, switched, selected-detail, and narrow states with zero console errors.

## Rollback

The change is limited to report templates/styles, focused tests, generated ignored artifacts, this task record, and its design/validation evidence. Reverting these edits restores the previous replacement-style drill-down without touching evidence or target repositories.

## Handoff condition

Complete when the four overview nodes remain visible before, during, and after detail interaction; inline expansion toggles correctly; inspector state remains source-coherent; automated checks pass; and desktop/narrow browser evidence is recorded.

## Observed result

- The four overview nodes are now permanent graph nodes. Clicking one inserts only its `detail_node_ids` beneath it instead of replacing the graph.
- Clicking the open overview node, `收起当前步骤`, or Escape collapses the inline group. Clicking another overview moves the single open group to that node.
- The right inspector switches from overview explanation to the selected mapped detail. Selected and changed presentation still derive from the same source node and `change_state`.
- Global overview connectors remain rendered while a group is open and route around the expanded detail panel. Narrow mode keeps the same document-flow hierarchy and intentionally hides SVG links.
- The fixed vLLM report was regenerated without changing its 4 accepted / 1 safely downgraded / 0 rejected claim result.

## Verification evidence

- Full suite: 65 tests pass. `compileall`, JavaScript syntax, and `git diff --check` pass; diff check reports only existing LF-to-CRLF notices.
- Real Edge at 1440×1000 reports four overview groups before, during, and after interaction; one open inline group; three retained global links; working same-node collapse; two details when switching to the first overview group; no document/canvas overflow; and zero console problems.
- Selected detail state and inspector state agree for both the changed (`changed`) and unchanged (`not_observed`) examples.
- Real Edge at 390×844 retains four overview groups plus the inline detail, uses the explicit no-SVG narrow fallback, and has no horizontal overflow.
- Opening `查看技术实现结构` in Edge completes compressed-payload verification/decompression with the failure status hidden and no console problem.
- The 3,178,188-byte report has no external script, external stylesheet, runtime `fetch`, or old `返回四步总览` route.
- Screenshot review scores the bounded interaction 9.1/10. Independent human comprehension and runtime behavior remain untested.
