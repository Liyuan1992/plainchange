# Implementation plan

## Regions

1. Replace the concept canvas’ free-form grid with responsibility bands and a deterministic stage layout.
2. Replace Bézier paths and SVG edge labels with gutter-routed orthogonal paths and numbered stage affordances.
3. Render the relation key in main-path order and preserve all secondary relation text.

## Files

- `src/change_passport/templates/review.html`
- `src/change_passport/templates/review.css`
- `src/change_passport/templates/review.js`
- focused HTML/UI tests and this task’s validation records

## Not changing

Profile parsing, architecture extraction, the static implementation layer, Git collection, model bridge, and baseline semantics.

## Expected result

On desktop, the reader can trace the architecture from inputs to human approval without an arrow crossing a card. On narrow screens, the existing stack becomes a numbered story and the relation key stays readable.
