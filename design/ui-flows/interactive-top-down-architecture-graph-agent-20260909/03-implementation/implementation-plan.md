# Implementation Plan

## Round

- Round number: 1
- Allowed focus: structure and interaction layout.

## Regions To Change This Round

- Concept graph: transpose topology ranks from columns into rows, with parallel components in columns inside each row.
- Connector layer: route arrows downward from source-bottom to target-top and retain obstacle-aware fallback.
- Node interaction: second click on a selected direct-mapping node collapses the inline implementation; first click selects and expands as before.

## Files To Change

- `src/change_passport/templates/review.js`
- `src/change_passport/templates/review.css`
- `tests/test_html_renderer.py`

## Things Not To Change

- Do not change profile schemas/data, extraction, graph facts, architecture snapshot/delta identities, static subdomains, evidence boundaries, or target repositories.
- Do not add target-specific identities or graph-library dependencies.

## Expected Screenshot Changes

- FastAPI changes from a full-width card list to a top-down graph: two inputs share the first row, processing branches share their topology ranks, and all safe configured relationships have visible unobstructed arrows.
- Change Passport renders its own topology with the same consumer. Node selection still expands implementation below the graph and updates the inspector.
- Narrow view remains a clickable one-column fallback with arrows hidden and no overflow.

## Verification Commands

- `uv run pytest -q`
- `uv run python -m compileall -q src tests`
- `node --check src/change_passport/templates/review.js`
- `git diff --check`
- Regenerate FastAPI and self-hosted reports, then run live browser geometry and interaction checks.
