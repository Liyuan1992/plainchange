# TASK-20260905-013: Generic conceptual-architecture layout and safe fallback

State: DONE
Tier: standard

## Trigger and approval

The owner rejected treating the current connector repair as a general solution and explicitly requested the missing cross-project capability with “嗯，我觉得这个功能需要补上” on 2026-09-05. That authorizes this bounded local implementation only.

## Goal

Render any supported target-profile conceptual architecture as a readable, deterministic layered diagram without repository-specific layout rules; if a complete non-overlapping route cannot be produced, retain the complete text relationship model and visibly fall back instead of drawing a misleading graph.

## Scope

1. Derive reader order and layout ranks from configured directed relationships, with profile grid coordinates used only as deterministic tie-breakers.
2. Render parallel branches, joins, multiple inputs, and multiple human gates as layered columns rather than forcing a single pipeline.
3. Route visible connectors through obstacle-aware orthogonal channels; prevent paths through card interiors and prefer unused channels.
4. Detect unsupported cyclic or route-exhausted shapes and render an explicit safe fallback: ordered components plus grouped relationship text, without decorative SVG arrows that imply clarity.
5. Add adversarial target-profile fixtures and browser validation for a branched/merged multi-gate graph, in addition to the self-hosted Change Passport sample.

## Non-goals

- Do not turn conceptual profile arrows into Git/static-import/runtime facts.
- Do not implement a general knowledge-graph platform, visual editor, graph persistence, model provider, or remote service.
- Do not change target read-only behavior, profile provenance binding, baseline authority, static implementation map, commit, push, or release state.

## Risks and stop conditions

- Stop if layout depends on project name, source paths, known component IDs, or the Change Passport sample topology.
- Stop if a cycle or route failure is silently rendered as an apparently complete flow.
- Stop if added layout metadata changes the profile's evidence/source boundary or changes system snapshot facts.

## Verification plan

- Parser and profile-neutrality regression tests, including a branching/merge/two-gate fixture.
- Browser geometry checks at desktop and narrow widths for both self-hosted and adversarial fixture reports: no SVG connector enters a card interior; all relationships remain in DOM text; fallback state is explicit if invoked.
- Full pytest, compileall, JavaScript syntax, diff check, and target clone preservation check.

## Commit boundary

This approval authorizes local implementation and verification only. It does not authorize a commit, remote, push, publication, provider integration, baseline approval, packaging, or release.

## Result

- The renderer now derives diagram rank from the profile's directed relationships; configured grid coordinates only break otherwise equal ordering.
- A simple acyclic path keeps its compact reader-first story route. Branches, joins, multiple inputs, and multiple human gates use a layered layout and an obstacle-aware orthogonal router that prefers unused channels.
- Cycles, missing boxes, and route exhaustion switch visibly to a card-and-relation fallback with no decorative SVG arrows.
- The profile parser now has a ten-component branch/merge/two-gate regression, and browser validation covers the self-hosted sample, the adversarial layered sample, and a cyclic fallback.

Verification is recorded in `design/ui-flows/generic-concept-layout-agent-20260905/04-validation/validation.md`. No target repository, profile source, static architecture fact, baseline, commit, or remote state changed.
