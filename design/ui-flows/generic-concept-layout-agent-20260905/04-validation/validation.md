# Validation

Date: 2026-09-05

The local browser check renders three reports at 1440 x 1050 through a temporary localhost preview and one at 390 x 844:

- Self-hosted Change Passport: 8 components, 8 SVG flows, 8 relation rows, `story` mode, zero sampled connector/card intersections.
- Adversarial branch/merge/two-gate graph: 10 components, 11 SVG flows, 11 relation rows, `layered` mode, visible explanation of layered routing, zero sampled connector/card intersections.
- Same adversarial graph with a cycle: 10 components, 0 SVG flows, 12 relation rows, visible `fallback` state explaining that the complete relationship text remains available.
- Narrow view: 390 px document width, no horizontal overflow; decorative links and responsibility bands are intentionally hidden while cards remain in reader order.

All browser variants reported zero console warnings/errors. The verification fixture is generated from the same validated review model and never alters a target repository. Visual captures and the harness remain under `design/ui-flows/architecture-story-map-agent-20260905/04-validation/` because that existing browser harness is the source of the geometry checks.
