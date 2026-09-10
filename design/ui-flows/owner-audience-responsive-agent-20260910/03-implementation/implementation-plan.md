# Implementation plan

Region: affected-audience rows only.

Files:

- `src/change_passport/templates/review.css`: replace the forced three-column row with a content-safe two-column heading and full-width explanation.
- `src/change_passport/templates/review.js`: render the five question cards into independent semantic columns so a tall right card cannot stretch the left column's row.
- `tests/test_html_renderer.py`: lock the responsive CSS contract.

Expected screenshot difference: the right-column card becomes compact and readable; explanation text wraps in normal lines, and both columns stack independently without a false blank area.

Do not change content, data contracts, static HTML structure, or other report regions.
