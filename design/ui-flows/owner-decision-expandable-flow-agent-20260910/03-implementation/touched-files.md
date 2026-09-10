# Touched files

- `src/change_passport/templates/review.html`: moved the two real tabs into the product header, separated the decision-card region, and collapsed the relation inventory.
- `src/change_passport/templates/review.css`: implemented the conclusion/card hierarchy, responsive header, top-to-bottom workflow, coherent selected/changed states, and desktop/narrow layouts.
- `src/change_passport/templates/review.js`: limited detail expansion to the selected overview group and centralized change presentation from `change_state`.
- `tests/test_html_renderer.py`: added regression assertions for the new hierarchy, progressive disclosure, selected detail subset, and single-source change presentation.
- `docs/project-governance/tasks/TASK-20260910-029-owner-decision-and-expandable-flow-ui.md`: retained approved scope and observed verification.
- `design/ui-flows/owner-decision-expandable-flow-agent-20260910/`: retained the visual spec, scope lock, capture script, screenshots, and review.

No evidence collector, schema, target profile, software-control source document, or target repository was changed.
