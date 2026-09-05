# Visual Spec

## Metadata

- Target page: system-architecture-review
- Target mode: agent
- Reference: `00-inputs/reference.png`
- Current before: `00-inputs/current-before.png`
- Preview URL: `file:///D:/Dev/Projects/change-passport-spike/artifacts/digitalself-430c342-m15/review.html`
- Date: 20260905

## Project Context Summary

- Current framework: Python-generated local single-file HTML with native HTML controls, CSS, inline SVG, and JavaScript.
- Current theme entry: `src/change_passport/assets/review-theme.json` rendered through 22 existing CSS custom properties.
- Current page component structure: top-level tabs → architecture card → 3×3 section grid + SVG overlay → sticky inspector → full relation list → module drill-down.
- Current usable resource paths: `src/change_passport/templates/review.html`, `review.css`, `review.js`; no image asset is needed.
- Business flows that must not change: deterministic snapshot identity, nine-section coverage, change overlay, section/module selection, Escape return, no-network single file, and candidate-baseline warning.

## 1. Overall Page Layout

- Preserve the existing page, heading, warning, 3×3 section grid, and right inspector.
- Treat the graph as a focusable relationship explorer: overview is quiet; selecting a section creates one clear local relationship view.
- Do not enlarge the canvas or require zoom/pan for nine sections.

## 2. Left Sidebar Specs

- Not applicable. The architecture canvas is the left/main region.

## 3. Main Content Specs

- Link endpoints must touch card boundaries, never disappear under card centers.
- Selected-section links use stable distributed ports so several links do not share one pixel.
- Outgoing static dependencies use blue; incoming dependencies use amber. Arrowheads must inherit the same color and remain outside card fill.
- Unselected overview shows only the strongest verified product/runtime relationships in low emphasis; selecting a section hides unrelated links.
- A selected relation isolates one path and dims other related cards.
- Each visible selected-state line shows a `N 条` label with a white/soft background pill and a text alternative.

## 4. Right Sidebar Specs

- Keep current responsibilities and numeric facts.
- Add a compact “直接关系” list divided by direction semantics: `依赖 →` and `← 被依赖`.
- Each row names the other section and count; clicking it isolates/restores the corresponding line.
- Include a two-item legend explaining that direction is static import direction, not runtime order.

## 5. Card Specs

- Selected section: existing focus ring plus stronger border.
- Directly related sections: full opacity with a subtle blue outline.
- Unrelated sections during focus: reduced opacity but still readable and clickable.
- Changed-section amber background remains unchanged and must not be confused with incoming-line amber.

## 6. Typography Hierarchy

- Section names and counts keep current sizes.
- Relation buttons use 11–12 px labels with bold other-section name and secondary count.
- SVG labels use compact bold text with `N 条`, not a bare number.

## 7. Colors, Backgrounds, Shadows, And Radii

- Reuse `--blue`, `--blue-line`, `--amber`, `--amber-line`, `--panel`, `--panel-soft`, `--ink`, and `--muted` only.
- Selected lines need at least 2.5 px stroke and near-opaque color; overview lines may remain 1.5–2 px and subdued.
- Count labels use panel fill plus a matching colored stroke so grid lines cannot reduce contrast.

## 8. Icon And Illustration Placement

- Use SVG arrowheads and small CSS direction swatches only. No illustration or bitmap.

## 9. Existing Features To Hide Or Downplay

- Downplay non-related cards and non-selected lines while a section or relation is focused.
- Do not render bare floating numbers without a line-label background.

## 10. Fake Or New Features That Must Not Be Added

- No manually curated “main flow”, inferred service order, runtime timing, or invented edges.
- No zoom minimap, search, edit mode, export, or baseline-approval control.
- No relation that is absent from `system_architecture.group_edges`.
