# Implementation Plan

## Round

- Round number: 1
- Allowed focus: relationship structure, routing, hierarchy and inspector clarity.

## Regions To Change This Round

- Architecture canvas SVG routing and label rendering.
- Section selected/related/unrelated states.
- Architecture inspector direct-relation controls and legend.

## Files To Change

- `src/change_passport/templates/review.js`
- `src/change_passport/templates/review.css`
- `tests/test_html_renderer.py`

## Things Not To Change

- Snapshot/review schemas, frozen data, grouping, counts and authority states.
- Change-review page, module data, network/persistence behavior and existing 22-token theme.
- Mobile text-first architecture fallback.

## Expected Screenshot Changes

- Lines terminate visibly at card borders with arrowheads outside opaque fills.
- Selected view shows only direct relationships, colored by incoming/outgoing direction.
- Unrelated cards fade; related cards remain clear.
- Bare numbers become high-contrast `N 条` label pills.
- Right inspector names direct related sections and can isolate one line.

## Verification Commands

- `node --check src/change_passport/templates/review.js`
- `uv run python -m compileall -q src`
- `uv run pytest -q`
- Regenerate `artifacts/digitalself-430c342-m15/review.html` and browser-check desktop + 390 px.
