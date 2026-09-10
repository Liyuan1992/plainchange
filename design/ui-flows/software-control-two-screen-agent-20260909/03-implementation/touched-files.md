# Touched Files

| File | Reason | Round |
| --- | --- | --- |
| `src/change_passport/software_control.py` | Validate canonical control data and source bindings | 1 |
| `src/change_passport/html_renderer.py` | Safely embed optional control data | 1 |
| `src/change_passport/pipeline.py` | Load, validate, persist, and render optional input | 1 |
| `src/change_passport/cli.py` | Add generic `--software-control` option | 1 |
| `src/change_passport/templates/review.html` | Add owner-facing two-screen regions and technical disclosures | 1 |
| `src/change_passport/templates/review.css` | Add hierarchy, graph, inspector, and responsive styling | 1 |
| `src/change_passport/templates/review.js` | Render five questions and interactive working map | 1 |
| `tests/test_software_control.py` | Validate identity and graph safety failures | 1 |
| `tests/test_html_renderer.py` | Verify two-screen embedding and fallback | 1 |
| `tests/test_pipeline.py` | Verify optional end-to-end input path | 1 |
| `README.md`, product/governance/design records | Document usage, scope, and observed status | 1 |
| `docs/product/schemas/software-control.v1.schema.json` | Require the source-declared four-step owner overview and explainable summary states | 2 |
| `docs/product/samples/change-passport-self-688fc5f.software-control.json` | Supply the result-first summary, four-step overview, audience states, and owner action | 2 |
| `src/change_passport/software_control.py` | Enforce exactly four owner steps, exact detail coverage, and changed-step binding | 2 |
| `src/change_passport/templates/review.html` | Collapse the five-question explanation and add map-depth controls | 2 |
| `src/change_passport/templates/review.css` | Compress the first screen and style state disclosures, audience table, checklist, and overview graph | 2 |
| `src/change_passport/templates/review.js` | Render the ten-second summary and switch the same graph between four-step overview and eight-step detail | 2 |
| `tests/test_software_control.py`, `tests/test_html_renderer.py` | Regress the generic contract, overview mapping, interaction hooks, and fallback | 2 |
| Product sample, evaluation, PRD, and governance records | Keep copy, identities, hashes, and status aligned with round 2 | 2 |
