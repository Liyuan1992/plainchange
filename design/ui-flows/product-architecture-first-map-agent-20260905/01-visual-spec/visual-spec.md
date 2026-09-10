# Visual specification

## Page and mode

- Target: generated `review.html`, `整体架构` tab.
- Mode: agent refinement of the existing local single-page report.
- Current reference: owner-provided screenshot of the current source-category overview.

## Required hierarchy

1. The first visible graph is `系统如何工作`, not a directory/module grouping.
2. It shows five readable zones: external inputs, evidence and analysis core, constrained explanation/validation, human-readable outputs, and an explicit human approval gate.
3. Directed arrows carry plain-language workflow labels. The approval gate is visually distinct and says it is outside automatic execution.
4. Each configured concept component may show a small `对应实现` mapping chip. This lets a reader descend to static code without confusing the two kinds of relation.
5. The current static-code map remains available below the concept map under `实现层：静态代码结构`, with its static-import limitation retained.

## Visual rules

- Use the existing white card, low-contrast grid, blue/amber/green tokens, rounded cards, and responsive stack.
- Concept cards are larger and flow left-to-right on desktop; they stack in source-to-output order on narrow screens.
- Use solid arrows only for profile-sourced workflow relations, with a visible legend saying they are product/process relations, not import edges.
- Preserve amber styling for the human gate and candidate baseline state.
- Do not add bitmap assets: icons are simple CSS text markers and all labels are real DOM text.

## Typography and copy

- Main heading: `先看系统如何工作，再核对实现结构`.
- Concept layer eyebrow: `第 1 层 · 系统工作流`.
- Static layer eyebrow: `第 2 层 · 实现层`.
- The profile source and SHA binding are disclosed in a compact note, not as the main explanation.
