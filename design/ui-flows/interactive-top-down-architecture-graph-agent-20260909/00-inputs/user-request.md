# User Request

- Target page: architecture-review
- Target mode: agent
- Platform / framework: single-file HTML/CSS/JavaScript
- Reference image: none; the owner supplied a direct interaction correction rather than a bitmap reference.
- Current screenshot: current generated report at the preview URL.
- Preview URL: file:///D:/Dev/Projects/change-passport-spike/artifacts/fastapi-0.136.2-to-0.136.3/review.html
- Functional boundary: Restore a real top-down node-and-edge graph; keep existing clickable node drill-down, right inspector, static evidence boundaries, and no target-specific renderer branches.
- Asset strategy: Use existing CSS and inline SVG only; no bitmap assets.
- Date: 2026-09-09

## Accepted target

- An actual top-to-bottom node-and-edge graph, not a vertical card list.
- Nodes remain clickable; mapped static implementation opens in the same canvas; the right panel explains the selected node.
- The renderer remains profile-neutral and preserves current architecture facts and evidence boundaries.

## Notes

- If the reference came from chat, keep using `00-inputs/reference.png` after the first save.
- Do not add fake functions or fake data from the reference image.
- Prefer existing assets before generating missing reusable bitmap assets.
