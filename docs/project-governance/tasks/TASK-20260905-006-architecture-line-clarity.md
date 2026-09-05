# TASK-20260905-006: Architecture relationship clarity

State: DONE
Tier: micro

## Trigger and authority

The owner supplied a screenshot of the formal DigitalSelf architecture view and reported: “架构这里不太好，看不清楚线，不够清晰”. This authorizes a bounded presentation correction to make existing verified section relationships legible. It does not authorize new topology, data-contract changes, baseline approval, commit, push, packaging, deployment, or DigitalSelf product integration.

## Evidence and diagnosis

- The screenshot shows relationship curves starting and ending at card centers, so opaque cards hide the real endpoints and arrowheads.
- Every visible curve uses nearly the same amber treatment; incoming/outgoing direction is not visually encoded.
- Multiple relations share the same center point and cross through the middle of the grid.
- Floating numeric labels have no pill/background and are easily detached from their line.
- The selected card is visible, but unrelated cards and lines remain equally prominent.
- The right inspector reports only aggregate in/out counts; it does not name direct related sections above the fold.

## Scope

1. Route SVG links between card boundaries instead of centers and distribute endpoints across stable ports.
2. Distinguish outgoing and incoming relations with separate existing theme colors, visible arrowheads, and Chinese direction labels.
3. When a section is selected, dim unrelated cards and show only its direct relations; allow a direct relation to be isolated from the inspector or relation list.
4. Render line counts as high-contrast SVG pills and expose a matching accessible text description.
5. Keep mobile's text-first fallback and all existing module drill-down behavior.

## Non-goals

- No changes to `SystemArchitectureSnapshot`, node/edge/group identities, grouping, counts, or authority.
- No inferred business flow, manual edges, runtime-call claims, new API, server, persistence, or network access.
- No raster assets or new design-token variables.
- No changes to the change-review tab.

## Files

- `src/change_passport/templates/review.js`
- `src/change_passport/templates/review.css`
- `tests/test_html_renderer.py`
- `design/ui-flows/system-architecture-line-clarity-agent-20260905/`

## Verification plan

- JavaScript syntax, Python compileall, and full pytest regression.
- Regenerate the frozen DigitalSelf formal HTML and preserve the system snapshot identity/counts.
- Browser desktop: overview, selected section, incoming/outgoing legend, relation isolation, module drill-down, and return state.
- Browser 390 px: no horizontal overflow and textual direct relations remain available while SVG is hidden.
- Screenshot comparison against the reported problem region; delivery requires at least 8/10.

## Stop conditions

- Any visual relation cannot be traced to an existing `group_edge_id`.
- Clarity would require inventing a flow direction beyond the source/target static-import direction.
- The change affects data authority, artifact containment, or the target repository.

## Implementation result

The initial boundary-routing correction improved arrow visibility but failed browser review because nine incident edges still converged around the selected card and count pills collided. The accepted second round replaces the selected grid with a deterministic three-column focus map:

- left: named sections that depend on the current section;
- center: one current-section card;
- right: named sections that the current section depends on;
- one relation card and one dedicated SVG path per original `group_edge_id`;
- a bidirectional peer appears once on each side so opposite directions do not overlap;
- clicking either a focus card, inspector row, or complete-list row isolates the same relationship;
- mobile hides SVG but preserves the current section and every named relation as HTML.

No snapshot, topology, count, schema, source edge, identity, token, network, persistence, baseline, or authority behavior changed.

## Verification evidence

- `node --check src/change_passport/templates/review.js`: passed.
- `uv run pytest -q`: 41 passed.
- `uv run python -m compileall -q src`: passed.
- Formal `finalize`: 8 accepted, 0 downgraded, 0 rejected.
- Formal HTML: 1,877,129 bytes; SHA-256 `B076E5BC6B4EE221A25AA9AC94B85B865A2866DC6BE15921C89EEC42131F0C56`.
- System snapshot SHA-256 remains `7484AFEE355CE286336044327C7DC9D0FE06AEF05980E55C8A7215D4CDED459C`; snapshot identity remains `23400d64e98911ba3093d3a46471883a791f75212cbf67fa1b348134de8aa1cc`.
- Coverage remains 1,057 modules, 1,768 static edges, 9 sections, 39 directed section-edge bundles, and 0 unclassified modules.
- Desktop 1440 × 900: the selected user-entry section renders 3 incoming plus 6 outgoing named relationship cards and 9 visible SVG paths without crossings or hidden endpoints.
- Single-relation isolation: selecting `记忆与知识系统 · 34 条` leaves one 4 px blue path and dims the other cards.
- Module drill-down and return to all 9 overview sections passed.
- Mobile 390 × 844: `scrollWidth === innerWidth`, the SVG layer is hidden, and the textual focus columns remain available.
- Browser console: zero warnings/errors.
- Accepted screenshot: `design/ui-flows/system-architecture-line-clarity-agent-20260905/04-validation/current-after.png`; visual score 9.3/10.

## Residual boundary

The six-item outgoing column extends below a 900 px viewport and uses ordinary vertical scrolling. This is intentional: shrinking the labels or compressing six paths into the first fold would recreate the readability defect. Independent non-coder comprehension testing remains part of TASK-20260904-004, not this micro presentation repair.
