# Implementation plan

## Round

- Round number: 1
- Allowed focus: structure and layout, followed by bounded state-consistency details in the same three regions.

## Regions to change

1. Header and real two-tab navigation.
2. Owner conclusion plus three decision cards and collapsed explanation.
3. Four-step/detail workflow workspace, inspector, and collapsed relation list.

## Files to change

- `src/change_passport/templates/review.html`
- `src/change_passport/templates/review.css`
- `src/change_passport/templates/review.js`
- `tests/test_html_renderer.py`
- Generated ignored vLLM artifact after source verification.

## Things not to change

- Python evidence collection, schemas, source/control identities, cache, target profile, owner copy, or target repository.
- Fallback behavior without a software-control document.
- Lazy technical payload decoding and integrity verification.
- No fake reference navigation or metadata.

## Expected screenshot changes

- Compact header with the two real report views.
- One dominant result card followed by three equally scannable owner cards.
- Four-step default workflow remains visible; drill-down becomes a vertical detailed workflow with a synchronized inspector.
- Relation inventory is no longer a competing default block.

## Verification commands

- `.venv\Scripts\python.exe -m pytest -q`
- `.venv\Scripts\python.exe -m compileall -q src tests`
- `node --check src\change_passport\templates\review.js`
- `git diff --check`
- Regenerate and inspect the fixed vLLM single-file report.
