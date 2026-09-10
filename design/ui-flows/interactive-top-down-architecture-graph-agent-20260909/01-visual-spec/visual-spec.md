# Visual Spec

## Metadata

- Target page: architecture-review
- Target mode: agent
- Reference: owner-stated interaction target in `00-inputs/user-request.md`; no bitmap reference was supplied or required.
- Current before: generated FastAPI report at the preview URL; its conceptual area is a one-column vertical card list with no visible edges.
- Date: 2026-09-09

## Project Context Summary

- Current framework: deterministic single-file HTML rendered from packaged HTML, CSS, JavaScript, and embedded validated review JSON.
- Current theme entry: `src/change_passport/assets/review-theme.json` and CSS variables in `src/change_passport/templates/review.css`.
- Current page component structure: one architecture workspace, conceptual workflow region, inline static implementation region, and persistent right inspector.
- Current usable resource paths: existing semantic tokens, clickable card components, CSS Grid, and inline SVG markers/paths.
- Business flows that must not change: profile-sourced conceptual nodes/relationships, static snapshot facts, change overlays, source/claim boundaries, direct implementation mapping, and inspector drill-down.

## 1. Overall Page Layout

- Keep one architecture workspace with a main graph and right explanation panel.
- The graph reads from top to bottom. Topology ranks become horizontal rows; nodes in the same rank form side-by-side branches; later ranks appear below.
- The static implementation expansion remains below the conceptual graph inside the same main canvas.

## 2. Left Sidebar Specs

- No separate left sidebar.

## 3. Main Content Specs

- Render every configured relationship as an arrow from the bottom edge of its source node toward the top edge of its target node.
- Prefer a direct vertical route; use an orthogonal mid-row route for branches and joins; never draw through an unrelated node.
- If routing is unsafe or the graph is cyclic, show clickable ordered nodes and the complete relationship list with an explicit fallback notice instead of pretending the diagram is complete.

## 4. Right Sidebar Specs

- Keep the right inspector sticky on desktop and below the graph on narrow screens.
- Clicking a node updates its explanation; clicking an already-selected directly mapped node collapses its implementation expansion.

## 5. Card Specs

- Nodes must read as diagram nodes rather than full-width list rows: bounded width, centered within a rank, clear selected state, stage badge, type badge, title, one-line responsibility, and mapping affordance.
- Branch nodes share a row. Inputs, automated processing, output, human gate, and persistent state retain existing semantic colors.

## 6. Typography Hierarchy

- Keep the existing type scale; node label is dominant, description secondary, and mapping affordance tertiary.

## 7. Colors, Backgrounds, Shadows, And Radii

- Reuse existing blue, green, amber, grey, border, focus, radius, and shadow tokens. Do not introduce a new palette.

## 8. Icon And Illustration Placement

- Use inline SVG arrowheads and orthogonal paths only. No bitmap, graph-library chrome, decorative icons, or floating edge labels.

## 9. Existing Features To Hide Or Downplay

- Keep the complete relationship prose as a verification/fallback surface, but visually subordinate it to the graph.
- Downplay prior wording that describes the view as only an ordered reading list.

## 10. Fake Or New Features That Must Not Be Added

- Do not add runtime claims, inferred graph edges, target-specific layout rules, graph editing, zoom/pan, model calls, or fake interaction states.
