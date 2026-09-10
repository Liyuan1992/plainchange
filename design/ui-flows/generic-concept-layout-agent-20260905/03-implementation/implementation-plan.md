# Implementation plan

1. Replace type-forced story placement with a deterministic topology-derived rank layout.
2. Add a route planner that treats cards as obstacles and produces only orthogonal, collision-free SVG paths.
3. Add explicit non-visual fallback for cyclic or route-exhausted profiles.
4. Add a branched/merged/multi-gate fixture and browser geometry validation.

No changes to target profiles, extraction contracts, or static code architecture facts are needed for the rendering engine itself.
