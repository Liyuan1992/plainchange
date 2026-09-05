# TASK-20260905-007: Progressive beginner module layer

State: DONE
Tier: micro

## Trigger and authority

The owner supplied the current `用户入口与交互 · 模块层` screenshot and asked whether it can be structured or layered because the raw module wall still has too high a beginner threshold. The earlier instruction “直到完成之前不需要我确认” remains the active fast-mode authority for this bounded UI refinement.

This authorizes a deterministic presentation change in the generated local review. It does not authorize architecture schema/topology changes, inferred runtime layers, baseline approval, commit, push, packaging, deployment, or DigitalSelf product integration.

## Evidence and diagnosis

- The current first module view exposes 60 of 227 items immediately.
- Most titles are English package names or source docstrings; every card also exposes a path.
- The flat three-column wall has no intermediate concept between a nine-section overview and individual source files.
- The existing node paths are sufficient to form bounded, reproducible reading buckets without changing the source snapshot.
- For `用户入口与交互`, all 227 nodes can be assigned once across seven path-derived areas: webpage features, chat UI, desktop/browser entry, CLI, voice/digital-human, web-backed services, and other user entry code.

## Scope

1. Add an explicit three-step reading rail: system section -> reading area -> optional technical module.
2. Derive mutually exclusive reading areas from each node's existing first owned path using ordered local rules and a transparent fallback.
3. Show Chinese area title, plain-language grouping purpose, module count, interface count, and current-change involvement.
4. Require an area selection and a second explicit action before raw module identifiers and paths appear.
5. Preserve the existing module inspector, bounded pagination, keyboard/Escape chain, and mobile fallback.

## Non-goals

- No runtime order, new dependency edge, new module responsibility, individual module translation, or product-feature assertion.
- No changes to `SystemArchitectureSnapshot`, `BeginnerReviewModel`, stored evidence, baseline, counts, IDs, or source files in DigitalSelf.
- No new API, server, network request, search, edit, approval, persistence, raster asset, or design token.

## Files

- `src/change_passport/templates/review.js`
- `src/change_passport/templates/review.css`
- `tests/test_html_renderer.py`
- `design/ui-flows/architecture-module-layer-agent-20260905/`

## Verification plan

- JavaScript syntax, Python compileall, and full pytest regression.
- Frozen DigitalSelf formal regeneration with unchanged snapshot identity and 1,057/1,768/9/39/0 coverage.
- Programmatic census proving every node in every section belongs to exactly one displayed area and area totals equal the section module count.
- Browser desktop: area overview, area selection, technical reveal, module selection/inspector, Escape and return chain.
- Browser 390 px: no horizontal overflow and no inaccessible content.
- Screenshot review requires at least 8/10.

## Stop conditions

- A node falls into zero or multiple areas.
- A Chinese label would require inferring behavior beyond the source path family.
- The implementation needs a schema, authority, topology, or target-repository change.

## Completion evidence

- The default `用户入口与交互` module view now contains seven Chinese reading areas whose counts sum to 227; it contains zero raw module cards and zero source paths.
- Selecting an area shows a four-fact summary but still exposes zero raw modules. A second explicit action reveals 18 modules and bounded `再显示` pagination.
- The same deterministic first-match/fallback assignment was exercised across all nine sections; every displayed area total equals the original section node count.
- Escape closes technical details before clearing the selected area; the existing return actions and module inspector remain functional.
- Formal regeneration kept snapshot identity `23400d64e98911ba3093d3a46471883a791f75212cbf67fa1b348134de8aa1cc` and `system-architecture.json` SHA-256 `7484AFEE355CE286336044327C7DC9D0FE06AEF05980E55C8A7215D4CDED459C` unchanged, with 1,057 nodes, 1,768 edges, 9 groups, 39 group-edge bundles, and 0 unclassified nodes.
- `node --check`, compileall, 41 tests, 8/0/0 formal validation, desktop interaction, 390 px no-overflow, screenshot review 9.4/10, and zero browser warnings/errors passed.
- No baseline approval, target-repository mutation, commit, push, package, deployment, or DigitalSelf integration occurred.
