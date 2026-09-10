# TASK-20260906-017: Vertical architecture reading order

State: DONE
Tier: micro

## Approval and goal

The owner explicitly requested that the unified architecture explorer read from top to bottom rather than left to right. Apply that reading order as a generic presentation rule, without changing repository facts, profiles, or static-relationship meaning.

## Scope

1. Present every profile's conceptual work-flow cards in one top-to-bottom column at desktop and narrow widths.
2. Keep the selected static implementation expansion below the work-flow map in the same canvas and keep the right inspector as the explanatory surface.
3. Suppress decorative canvas arrows in this reader; retain the complete declared relationship text so branching, merging, and cyclic profiles are not falsely represented as one sequential path.
4. Regenerate and inspect the FastAPI and self-hosted reports using the same renderer.

## Non-goals

- Do not change target profiles, graph extraction, static-import facts, relation IDs, source evidence, baseline state, or the target repositories.
- Do not create a FastAPI-specific branch, infer runtime execution order, or claim that visual stage order proves causality.
- Do not commit, push, package, deploy, or release.

## Result

The unified architecture canvas now uses a full-width vertical reading spine for every conceptual layout mode. The stage number and deterministic component order guide readers from system purpose to implementation; the complete textual relationship list remains the topology source because it can truthfully describe branches, joins, and cycles without crossings or misleading sequential arrows. Selecting “应用与路由组织” in FastAPI still expands seven configured implementation subdomains below the workflow map in the same canvas, and the self-hosted Change Passport report uses the same behavior.

## Verification

- FastAPI live desktop browser: 9 cards, one column, strictly increasing vertical positions, no conceptual-canvas horizontal overflow, no visible SVG connector, zero console errors; selecting “应用与路由组织” expands the static section below the selected workflow card inside the canvas.
- Self-hosted Change Passport live desktop browser: 8 cards, one column, strictly increasing vertical positions, no conceptual-canvas horizontal overflow, no visible SVG connector, zero console errors.
- `uv run pytest -q`: 50 passed.
- `uv run python -m compileall -q src tests`, `node --check src/change_passport/templates/review.js`, and `git diff --check`: pass (Git emitted only pre-existing CRLF normalization warnings).
