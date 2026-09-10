# Implementation-subdomain map validation

Date: 2026-09-06

## Contract checked

- A target profile may classify the implementation reader layer with directory prefixes, exact source paths, and filename prefixes.
- An unmatched module is never dropped: it remains in a clearly named automatic fallback subdomain.
- A displayed cross-subdomain relationship is an aggregate of existing same-section static import edge IDs only. It does not claim runtime order or call behavior.
- No consumer source has FastAPI identity, path, or label logic. FastAPI is a fixture profile only.

## Live browser evidence

At desktop width, the FastAPI `framework_core` section showed seven target-profile subdomains, 23 static-import aggregates, no legacy duplicate area cards, and the `目标配置优先` source badge. Selecting `应用与路由` selected the matching summary; raw cards remained closed until the explicit optional expansion, then exposed two matching modules.

The self-hosted Change Passport `evidence_pipeline` section showed five target-profile subdomains and eight static-import aggregates, using exactly the same consumer behavior.

At 390 px, the FastAPI report had a 390 px viewport and 375 px document scroll width. Both subdomain cards and relationship entries formed one column; no horizontal overflow appeared. Browser console had no warnings or errors during the interactions.

## Automated checks

- `uv run pytest -q`: 50 passed.
- `uv run python -m compileall -q src tests`: exit 0.
- `node --check src/change_passport/templates/review.js`: exit 0.
- Profile-neutral source scan: zero `fastapi` matches in architecture/profile/renderer consumer sources.
