# Implementation Plan

## Round

- Round number: 2
- Allowed focus: structure/layout.

## Regions To Change This Round

- Keep the existing one-explorer interaction intact while changing the workflow map into a vertical reading spine.
- Remove desktop-only horizontal grid placement and decorative canvas arrows from this reader; retain the complete textual relationship list as the truthful topology expression.
- Keep selected static content below the workflow map and retain the right inspector unchanged.

## Files To Change

- `src/change_passport/templates/review.css`

## Things Not To Change

- Do not change schemas, profile contracts, architecture extraction, Git facts, target profiles, or evidence/baseline authority.

## Expected Screenshot Changes

- The page begins with one vertical workflow spine rather than a left-to-right graph. Selecting a workflow component expands its mapped implementation below that spine in the same canvas and changes the right-side prose without navigating to a different section.

## Verification Commands

- `uv run pytest -q`
- `uv run python -m compileall -q src tests`
- `node --check src/change_passport/templates/review.js`
- Regenerate FastAPI and self-hosted artifacts; live desktop and 390 px browser checks for drill-down, relationship truth labels, no overflow, and no console issues.
