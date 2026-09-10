# Implementation Plan

## Round

- Round number: 1
- Allowed focus: structure/layout and generic data integration.

## Regions To Change This Round

- Hero and primary tab labels when software-control data is present.
- First-screen conclusion, five questions, comparison, and owner checks.
- Second-screen working-map canvas and owner inspector.
- Technical disclosure wrapper and narrow-width fallback.

## Files To Change

- `src/change_passport/software_control.py`
- `src/change_passport/html_renderer.py`
- `src/change_passport/pipeline.py`
- `src/change_passport/cli.py`
- `src/change_passport/templates/review.html`
- `src/change_passport/templates/review.css`
- `src/change_passport/templates/review.js`
- Focused tests and generated self-hosted artifact.

## Things Not To Change

- Existing brief/review identities and facts.
- Existing fallback report without software-control input.
- Target profiles, source repositories, networking/security model, or package dependencies.

## Expected Screenshot Changes

- Default screen opens with one plain-language conclusion and three compact state rows.
- Architecture tab becomes one clickable top-to-bottom software map with the changed step visible and a right-side explanation.
- Technical code structure remains available but no longer dominates the first view.

## Verification Commands

- `uv run pytest -q`
- `uv run python -m compileall src tests`
- `node --check src/change_passport/templates/review.js`
- `git diff --check`
