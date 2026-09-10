# Round 1: remove residual visual occlusion

## Observed at the owner's current width

- The fixed page-switch toast covered the right-side human-decision card immediately after selecting `整体架构`.
- Responsibility-band subtitles shared the first-row card boundary and could be partially hidden by the card layer.

## Correction

- Make page-switch announcements silent by default; the selected tab is already a visible state change.
- Reserve 16 additional pixels above the story grid so every band title and subtitle occupies its own header strip.

## Boundary

No conceptual component, configured flow, static implementation mapping, or evidence statement changed.
