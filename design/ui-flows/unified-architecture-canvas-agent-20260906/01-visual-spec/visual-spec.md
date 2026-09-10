# Visual Spec

## Metadata

- Target page: architecture-review
- Target mode: agent
- Reference: Owner-confirmed interaction direction in `00-inputs/user-request.md`; no bitmap reference is required.
- Current before: Existing generated FastAPI report at the preview URL.
- Date: 2026-09-06

## Project Context Summary

- Current framework: deterministic single-file HTML rendered from packaged HTML, CSS, JavaScript, and embedded validated review JSON.
- Current theme entry: `src/change_passport/assets/review-theme.json` plus CSS custom properties in `src/change_passport/templates/review.css`.
- Current page component structure: conceptual system-workflow canvas, separate static-section canvas, sticky static inspector, and two below-canvas drill-down regions.
- Current usable resource paths: existing semantic colors, cards, CSS grid, and SVG-only arrows. No bitmap asset is available or needed.
- Business flows that must not change: profile-sourced conceptual architecture, static snapshot facts, static-import edge IDs, change overlay, reader identity, and source/claim boundaries.

## 1. Overall Page Layout

- Replace the sequential first-layer / second-layer layout with one architecture explorer workspace: one main canvas and one persistent right-side explanation panel.
- The initial canvas presents the profile-sourced work-flow cards as a single top-to-bottom reading spine. The displayed order is the deterministic profile/graph order; a mapped workflow card is its own drill-down control, with no nested “view implementation” button.
- Activating a workflow card keeps it in the reading spine and opens its mapped static section below the work-flow map in the same canvas. The reader therefore moves down from “what the system does” to “where that work is implemented”, instead of scanning horizontally or navigating to another page.
- A static section then exposes profile-declared implementation subdomains in that inline expanded region. Do not navigate or scroll into a separate reader section.

## 2. Left Sidebar Specs

- No unrelated left sidebar. The canvas is the sole primary reading region.

## 3. Main Content Specs

- Right panel is sticky on desktop and follows the canvas on narrow screens.
- It always explains the current reading focus: overview, workflow component, static section, or implementation subdomain.
- It owns facts, evidence boundaries, relationship prose, and the optional raw-module reveal. It replaces below-canvas relation cards and the second drill-down page.

## 4. Right Sidebar Specs

- Workflow cards retain component type, stage, label, and description but remove embedded action buttons. They occupy one full-width column at desktop and narrow widths; stage order is the primary visual guide.
- Selected workflow and expanded static-section cards use existing focus/blue borders; changed static content uses existing amber overlay only.
- Inline subdomain cards retain module count, change count, and aggregated static-import direction; no connector is drawn when it could obscure cards.

## 5. Card Specs

- Keep existing semantic heading and body scales. Remove visible labels such as “第 1 层” and “第 2 层” from the primary interaction path; use contextual labels such as “系统工作流” and “展开的静态实现”.

## 6. Typography Hierarchy

- Reuse existing panel, blue, amber, green, grey, border, radius, and shadow tokens. No new colors or images.

## 7. Colors, Backgrounds, Shadows, And Radii

- No icons or illustrations are needed. Use existing stage badges, CSS borders, and the complete textual relationship list. Do not rely on canvas arrows in this vertical reader, since a generic branching graph cannot be represented as one truthful sequential arrow without either occlusion or a false causal claim.

## 8. Icon And Illustration Placement

- Downplay or remove the separate implementation section heading, the below-canvas static-relation grid, the below-canvas module page, and nested conceptual implementation buttons.

## 9. Existing Features To Hide Or Downplay

- Do not create product flows, runtime arrows, new backend/API behavior, inferred labels, or target-specific consumer code.

## 10. Fake Or New Features That Must Not Be Added

-
