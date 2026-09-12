# Visual Spec

## Metadata

- Target page: readme-showcase-gif
- Target mode: agent
- Reference: `00-inputs/reference.png`
- Current before: `00-inputs/current-before.png`
- Date: 20260912

## Project Context Summary

- Current framework: GitHub Markdown README with an embedded animated GIF.
- Current theme entry: the generated PlainChange report UI shown in the owner-supplied screenshots.
- Current page component structure: one hero media asset linked from `README.md`; Chinese README keeps its existing Chinese GIF.
- Current usable resource paths: `docs/images/plainchange-self-demo-en.gif` and the two screenshots under `00-inputs/`.
- Business flows that must not change: the report remains a real offline artifact with two clickable tabs and English selected.

## 1. Overall Page Layout

- Preserve the full browser viewport from both supplied screenshots.
- Normalize both frames to one 1440-pixel-wide canvas without stretching.
- Show the change view first, then switch to the software workflow after 4000 ms.

## 2. Left Sidebar Specs

- Not applicable; preserve the report header exactly as captured.

## 3. Main Content Specs

- Frame 1 must make the change conclusion, completed checks, and remaining boundary immediately visible.
- Frame 2 must make the four-stage system workflow and selected changed stage immediately visible.

## 4. Right Sidebar Specs

- Preserve the remaining-boundary card in frame 1 and the selected-stage inspector in frame 2.

## 5. Card Specs

- Do not redraw, recolor, or fabricate cards; use the actual report screenshots.

## 6. Typography Hierarchy

- Preserve rendered browser text. Downscaling must keep headings and card labels readable on GitHub.

## 7. Colors, Backgrounds, Shadows, And Radii

- Preserve source colors. GIF quantization should avoid visible banding in the pale blue, green, and amber panels.

## 8. Icon And Illustration Placement

- Preserve the existing PlainChange icon and state icons; generate no replacement artwork.

## 9. Existing Features To Hide Or Downplay

- No additional cropping beyond the tiny common-edge normalization required by the two different viewport sizes.

## 10. Fake Or New Features That Must Not Be Added

- No fake provenance, validation state, workflow step, button, or transition overlay.
