# Implementation Plan

## Round

- Round number: 1
- Allowed focus: structure and progressive disclosure.

## Regions To Change This Round

- Module drill-down header and reading steps.
- Chinese path-derived area overview.
- Selected-area summary and optional technical module reveal.

## Files To Change

- `src/change_passport/templates/review.js`
- `src/change_passport/templates/review.css`
- `tests/test_html_renderer.py`
- Formal DigitalSelf review artifact and validation pack.

## Things Not To Change

- Snapshot/schema, node identities, relationships, counts, source paths, module inspector facts, theme tokens, APIs, network behavior, permissions, persistence, and change-review tab.

## Expected Screenshot Changes

- Opening modules first shows a small Chinese area map rather than 60 English technical cards.
- Selecting an area shows its purpose and verified counts.
- Technical names and paths appear only after `展开技术模块`.
- Mobile remains one column without horizontal overflow.

## Verification Commands

- `node --check src/change_passport/templates/review.js`
- `uv run pytest -q`
- `uv run python -m compileall -q src`
- Regenerate the frozen DigitalSelf artifact and verify snapshot identity/counts.
- Browser 1440 px: area overview, area selection, technical reveal, module inspector, Escape/back chain.
- Browser 390 px: no horizontal overflow and full text access.
