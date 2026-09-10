# Implementation plan

1. Replace detail-only depth state with one optional expanded overview ID.
2. Render overview wrappers as the permanent graph nodes and insert the mapped detail panel inside the expanded wrapper.
3. Keep SVG overview links anchored to permanent overview buttons; render declared internal detail relations in the inline panel.
4. Synchronize inspector, explicit collapse, Escape, focus, and selected/change presentation.
5. Update focused tests, regenerate the vLLM report, and capture browser evidence at desktop and narrow widths.
