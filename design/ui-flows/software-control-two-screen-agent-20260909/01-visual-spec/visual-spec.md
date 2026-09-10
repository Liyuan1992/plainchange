# Visual Spec

## Metadata

- Target page: software-control-two-screen-report
- Target mode: agent
- Reference: `00-inputs/reference.png`
- Current before: `00-inputs/current-before.png`
- Date: 2026-09-09

## Project Context Summary

- Current framework: dependency-free Python renderer plus one embedded HTML/CSS/JavaScript file.
- Current theme entry: `src/change_passport/assets/review-theme.json` CSS custom properties.
- Current page component structure: top bar, hero, two tabs, report panels, technical drawer, static architecture explorer.
- Current usable resource paths: `src/change_passport/templates/review.html`, `review.css`, `review.js`, and the existing conceptual top-down graph/router.
- Business flows that must not change: validated brief and evidence identities, read-only local rendering, technical drill-down, static/runtime boundary, and no network requests.
- UI prototype preflight: no callable `figmaPrototypeDirector` was available on 2026-09-09. This task implements the already confirmed HTML direction and does not create or revise Figma work.
- Reference use: `reference.png` supplies the accepted white/blue/green system, page chrome, card language, and one-canvas architecture treatment. `current-before.png` supplies the latest obstacle-avoiding top-down connection pattern.

## 1. Overall Page Layout

- Keep one centered desktop shell, maximum readable width about 1440px, with 20-24px outer gutters.
- Preserve one compact top bar and one compact hero; the report content is visually dominant.
- Use exactly two primary destinations: `这次改了什么` and `这个软件怎么工作`.
- Technical details remain in the same document but below a deliberate disclosure control.

## 2. Navigation Specs

- No permanent left sidebar.
- Two large segmented tabs sit directly below the hero and maintain independent scroll positions.
- The active tab uses the established blue underline/fill and a visible keyboard focus ring.

## 3. Main Content Specs

- First screen: a dominant headline, three status rows (`已确认`, `暂未发现`, `仍需验证`), then five questions in reading order.
- Question 2 includes a before/after example; questions 3 and 4 are distinct; question 5 shows short owner checks before detailed actions.
- Second screen: one top-to-bottom clickable graph. Two input cards may share the first rank; all following ranks follow declared flows.
- Every graph node shows a plain-language label and short outcome. Only `change_state=changed` may receive the current-change highlight.
- Lines sit behind cards, avoid card interiors, use arrows and a separate complete relation list as the non-visual fallback.

### Owner review correction for round 2

- The result sentence must precede the internal concept name. The concept is a secondary `涉及内部` label, never the headline.
- The default first screen must be scannable in about ten seconds: what changed, likely user impact, residual risk, and what the owner should do now.
- The full five questions are collapsed under `查看完整说明` and remain source-equivalent when opened.
- Each visible state includes a one-sentence explanation. `目前没发现` must explicitly say that absence of evidence is not proof of no impact.
- The default software map has four source-declared mental-model steps. Clicking one step replaces the same canvas with the eight detailed steps and focuses the mapped detail; a back control restores the four-step overview.
- The changed overview step is the dominant visual landmark. Audience impact is a table; owner checks use empty checklist markers without persistence.

## 4. Right Sidebar Specs

- On the second screen, a sticky inspector explains the selected step: what it means, what the owner sees, current change, affected people, unknowns, and checks.
- The inspector starts with the changed step when one exists; otherwise it starts with the first declared node.
- Technical implementation groups appear only after the owner-language explanation and require an explicit action.
- At narrow widths the inspector moves below the graph.

## 5. Card Specs

- Owner summary cards use 14-18px padding, 12-16px radius, 1px neutral border, and no decorative imagery.
- Confirmed/changed content uses green or amber only as semantic accents; unknown content remains neutral/grey.
- Graph cards are buttons with minimum 44px interaction height, clear selected state, changed badge, and visible focus.

## 6. Typography Hierarchy

- Product title 13-14px; hero headline 28-34px desktop and 24-28px narrow.
- Main section headings 22-26px; question headings 17-20px; body 14-16px with 1.65 line height.
- Technical IDs and hashes use the existing monospace treatment only inside technical details.

## 7. Colors, Backgrounds, Shadows, And Radii

- Reuse all current theme tokens; do not introduce target-specific colors.
- Page background remains soft grey; report panels are white; graph canvas uses the existing quiet grid.
- Use the existing shadow and radius tokens. No gradients, glass effects, or heavy illustrations.

## 8. Icon And Illustration Placement

- No raster asset is required. Use CSS dots, status pills, arrowheads, and simple text markers.
- Decorative icons must not compete with the conclusion or graph labels.

## 9. Existing Features To Hide Or Downplay

- Hide the old equal-weight summary and code relationship graph from the default owner screen when software-control data exists.
- Keep them inside `为什么这么判断 / 查看技术细节`.
- Hide module names, import counts, paths, hashes, and baseline terminology from the default two screens.

## 10. Fake Or New Features That Must Not Be Added

- No approve/reject mutation, model generation button, live runtime status, user-impact certainty, or automatic testing claim.
- No project-specific copy in templates or JavaScript.
- No network requests, local storage, telemetry, or external fonts/assets.
