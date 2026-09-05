# Visual Spec

## Metadata

- Target page: architecture-module-layer
- Target mode: agent
- Reference: `00-inputs/reference.png`
- Current before: `00-inputs/current-before.png`
- Date: 20260905

## Project Context Summary

- Current framework: deterministic Python projection rendered as one local HTML file with packaged HTML/CSS/JavaScript templates.
- Current theme entry: `src/change_passport/assets/review-theme.json` plus existing CSS custom properties in the generated document.
- Current page component structure: architecture section -> selected section focus map -> right inspector -> module drill-down -> individual module inspector.
- Current usable resource paths: `src/change_passport/templates/review.js`, `review.css`, `review.html`, and the embedded `SystemArchitectureSnapshot` node paths/interfaces.
- Business flows that must not change: nine-section overview, relationship focus/isolation, module selection, inspector evidence boundary, mobile text fallback, and read-only/no-network output.

## 1. Overall Page Layout

- Preserve the existing architecture card and selected-section context.
- Replace the immediate 227-card wall with a three-step reading sequence: system section -> Chinese reading area -> optional technical modules.
- The grouping is a deterministic view over existing source paths, explicitly labelled as a reading aid rather than runtime order.

## 2. Left Sidebar Specs

- No left sidebar exists. Use the first column of reading-area cards as part of the main content rather than inventing navigation.

## 3. Main Content Specs

- Begin with a horizontal three-step rail: `1 系统分区`, `2 子区域`, `3 技术模块（可选）`.
- Default module drill-down shows 4–8 Chinese area cards instead of raw module cards.
- For `用户入口与交互`, expected areas are: 网页功能界面、聊天与对话界面、桌面与浏览器入口、命令行入口、语音与数字人、网页背后的服务、其他用户入口.
- Selecting an area exposes a plain-language summary and counts; raw modules remain behind a second explicit action.
- Technical modules render only for the selected area, initially capped at 18 and expandable in bounded batches.

## 4. Right Sidebar Specs

- Keep the existing right inspector as the evidence/detail surface for a selected technical module.
- Area selection itself should not overwrite the current section inspector with invented module facts.

## 5. Card Specs

- Area cards: large Chinese title, one-sentence purpose, module count, optional `本次涉及 N` badge.
- Selected area uses the existing focus ring and a numbered marker. Non-selected cards remain fully readable.
- Module cards become a compact technical list under an explicit `技术细节` heading; paths stay secondary and monospace.

## 6. Typography Hierarchy

- Page title 20–22 px; step title 12–14 px; area title 15–16 px; area description 12 px; technical module title 11–12 px.
- Chinese labels lead. English identifiers never appear in the first area-selection view.

## 7. Colors, Backgrounds, Shadows, And Radii

- Reuse paper white, navy ink, muted blue, green evidence state, amber scope warning, existing radii, shadows, and focus ring.
- Do not add new CSS variables. Use light tinted number plates and a single selected outline to avoid decorative noise.

## 8. Icon And Illustration Placement

- Use numbered CSS plates (`01`–`08`) and simple arrow separators; no raster illustrations, emoji, or new icon library.

## 9. Existing Features To Hide Or Downplay

- Hide raw module names, paths, stable-ID ordering, and the `60 / 227` counter until a reading area is selected and technical details are explicitly opened.
- Downplay code paths even in the technical list; keep them available for audit.

## 10. Fake Or New Features That Must Not Be Added

- Do not invent runtime layers, call order, product capabilities, dependency edges, translations of individual module behavior, search, edit, approval, or write actions.
- Do not change the architecture snapshot/schema. Area labels are view-only path buckets and must be disclosed as such.
