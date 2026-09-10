# Visual specification

## Metadata

- Target page: generated Change Passport owner report, both owner screens
- Target mode: agent
- References: the two local screenshots recorded in `00-inputs/user-request.md`
- Current before: fixed vLLM generated report
- Preview URL: `file:///D:/Dev/Projects/change-passport-spike/artifacts/vllm-a69e75b-to-a85d073/review.html`
- Date: 2026-09-10

## Project context summary

- Framework: deterministic Python single-file HTML renderer with embedded vanilla JavaScript and CSS.
- Theme entry: `src/change_passport/assets/review-theme.json`.
- Page structure: shared header, two owner tabs, owner change summary, collapsed five-question explanation, four-step/detail software map, lazy technical evidence, legacy fallback.
- Reusable resources: existing theme tokens, CSS shapes, text marks, current state chips and graph renderer. No bitmap asset is required.
- Business flows that must not change: five-question source binding; four overview nodes cover all detail nodes exactly once; changed overview contains the changed detail; technical payload remains lazy, hash-checked, offline, and read-only.

## 1. Overall page layout

- Use one compact top header containing the real brand and the two real report tabs.
- In owner-control mode remove the redundant generic hero so the active screen begins with its own answer.
- Keep a centered wide desktop canvas and a single-column narrow layout.
- Preserve the two-screen model rather than adding a left application sidebar.

## 2. Header and navigation

- Brand remains left aligned.
- The two real tabs read `这次改了什么` and `这个软件怎么工作` and sit beside the brand on desktop.
- Evidence-state chips remain on the right but are visually secondary.
- Do not add project, comparison, search, account, help, or dropdown controls.

## 3. Change decision screen

- Lead with one wide conclusion card: concrete headline, one confirmed statement, and a small source/state label.
- Place three equal decision cards below it: current impact, residual risk, and next action.
- Each card has a compact icon tile, plain-language question, state disclosure, and one answer.
- Keep `查看完整说明` collapsed by default; use a two-column explanation layout on wide screens and one column on narrow screens.
- Keep `为什么这么判断` beneath the complete explanation.

## 4. Software workflow screen

- Lead with the owner-language software purpose and a short “no technical background required” boundary.
- Use a top-to-bottom clickable workflow on the left and one sticky selected-step inspector on the right.
- Default to four overview steps. Clicking one replaces the same canvas with only its mapped detailed steps; a visible action returns to four steps.
- Selected state uses a deep-blue outer border. Changed state uses amber fill/stripe/badge. A selected changed node preserves both signals.
- Collapse the textual relation list because it duplicates the visible graph.

## 5. Cards and inspector

- Cards use white or lightly tinted surfaces, restrained borders, 12–18 px radii, and light shadows.
- Inspector begins with the selected step and its change state, followed by: what it means, what changed, who may be affected, what remains unknown, and what to check.
- The change-state heading and badge are derived only from the selected node's `change_state`.

## 6. Typography hierarchy

- Concrete page conclusion: 30–36 px desktop, 24–28 px narrow.
- Screen heading: 28–34 px desktop.
- Decision-card questions: 16–18 px.
- Workflow node titles: 15–17 px; explanations: 12–14 px.
- Technical labels remain smaller and visually muted.

## 7. Colors, backgrounds, shadows, and radii

- Navy/blue for navigation, focus, and current selection.
- Amber only for source-bound current change and unresolved risk.
- Green for confirmed evidence and recommended next action, never for unexecuted completion.
- Page background stays light with subtle blue tint; use current project tokens only.

## 8. Icons and illustration placement

- Use text/CSS glyphs already available in the single-file report.
- No generated raster image, product illustration, or copied logo is required.

## 9. Existing features to hide or downplay

- Hide the generic report hero in owner-control mode.
- Downplay global status chips and relation text.
- Keep legacy technical maps inside disclosures.

## 10. Fake or new features that must not be added

- No project hub, model comparison, saved-follow list, search, user account, help link, release version/date, or persisted checklist.
- No claimed runtime result or owner approval.
