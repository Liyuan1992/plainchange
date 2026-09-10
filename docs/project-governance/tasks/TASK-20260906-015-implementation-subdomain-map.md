# TASK-20260906-015: Generic implementation-subdomain map

State: DONE
Tier: standard

## Approval and goal

The owner confirmed the need for a finer implementation layer on 2026-09-06 and explicitly required that the resulting change solve this class of problem rather than target FastAPI. Build a generic third reading level between a system section and raw modules: profile-declared implementation subdomains with aggregated, evidence-bound static import relationships.

## Scope

1. Extend the versioned target-profile presentation asset so module-area rules can match exact source paths and filename prefixes as well as directory prefixes.
2. Use those generic rules to group the selected static-code section into named implementation subdomains, preserving an explicit unmatched fallback.
3. Render subdomain counts, change overlays, and cross-subdomain static-import aggregates before optional raw module cards.
4. Update the FastAPI analysis profile only as an external verification fixture, and prove the UI contains no FastAPI identities or paths.
5. Cover profile parsing, static facts, browser interaction, self-hosted sample, and FastAPI sample.

## Non-goals

- Do not infer semantic labels with a model, hard-code any repository identity into the consumer, or modify Git-derived nodes/edges/impact/baseline facts.
- Do not turn static imports into runtime, deployment, request, or user-behavior claims.
- Do not commit, push, release, modify an analyzed target repository, or approve a baseline.

## Risks and acceptance

- A profile rule can be too broad, so unmatched modules must remain visible rather than silently disappearing.
- Every displayed subdomain relation must aggregate exact existing static edge IDs; no relationship may be synthesized.
- FastAPI is only one validation fixture. Acceptance requires profile-neutral source checks and the existing self-hosted plus adversarial layout regressions.

## Result

Implemented a profile-neutral implementation-subdomain layer. A module-area rule may now use a directory prefix, exact source path, or filename prefix; unmatched modules stay visible in a deterministic `其他…模块` fallback. The reader aggregates only existing same-section static-import edge IDs between those subdomains, shows change counts and direction summaries, and keeps raw module cards closed until the reader selects a subdomain.

FastAPI `0.136.2..0.136.3` is an external fixture only: its framework-core section renders 7 configured subdomains and 23 aggregated static relationships. The self-hosted Change Passport fixture renders 5 configured subdomains and 8 relationships. Consumer source has no FastAPI name or path. Live browser checks confirmed selection, optional raw-module expansion, zero duplicated legacy cards, no console warnings/errors, and 390 px layouts with no horizontal overflow. Full pytest, compileall, and JavaScript syntax checks pass.
