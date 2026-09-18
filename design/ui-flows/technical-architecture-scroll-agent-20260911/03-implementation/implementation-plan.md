# Implementation Plan

## Round

- Round number: 1
- Allowed focus: scroll ownership and interaction only.

## Regions To Change This Round

- Technical architecture conceptual canvas.
- Browser regression coverage for real user scrolling.

## Files To Change

- `src/plainchange/templates/review.css`
- `scripts/verify-multi-project-browser.cjs`
- Generated fixed-revision review artifact and this design pack's validation files.

## Things Not To Change

- Analysis data, schemas, extraction, labels, node order, node size, selection and inspector logic.
- The owner-facing map above the technical disclosure.
- Target repositories and all existing unrelated worktree changes.

## Expected Screenshot Changes

- Previously clipped cards are reachable through a visible inner horizontal scrollbar.
- Page width and right inspector remain unchanged.

## Verification Commands

- Generate the fixed DigitalSelf report.
- In real Edge, verify computed `overflow-x`, non-zero horizontal scroll movement, node click after scrolling, zero console errors and no document-level overflow at desktop and 390 px.
- Run focused/full automated tests and JavaScript syntax checks.
