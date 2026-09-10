# Asset checklist

## Metadata

- Target page: Change Passport generated owner report
- Target mode: agent
- Design pack: `owner-decision-expandable-flow-agent-20260910`
- Date: 2026-09-10
- Image generation workflow: not required

## Existing usable assets

| Path | Purpose | Mapping | Status |
| --- | --- | --- | --- |
| `src/change_passport/assets/review-theme.json` | Color, radius, shadow, focus tokens | both screens | reuse |
| `src/change_passport/templates/review.css` | Existing chips, cards, graph states | both screens | refine |
| `src/change_passport/templates/review.js` | Existing owner data projection and interaction | both screens | refine |

## Missing assets

None. The references use common interface icons that can be represented with accessible text/CSS glyphs without introducing image files.

## Assets that should not be generated

| Visual element | Preferred implementation | Reason |
| --- | --- | --- |
| Brand mark and status icons | Existing text/CSS | Keeps the report self-contained and themeable |
| Real copy and numbers | DOM text | Must remain source-bound and accessible |
| Buttons and tabs | Existing HTML controls | Must preserve real behavior |
| Card backgrounds and connector shapes | CSS/SVG | Smaller and responsive |
