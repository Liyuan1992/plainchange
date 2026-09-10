# TASK-20260905-014: FastAPI external layout validation

State: DONE
Tier: standard

## Trigger and bounded authorization

The owner requested “尝试分析解构一下比较出名的一个开源库，看看效果” on 2026-09-05. This authorizes one local, read-only external-repository analysis and any directly necessary generic renderer correction found by that validation. It does not authorize a commit, remote, push, package, deployment, model provider, or baseline approval.

## Scope and method

- Fixed a public FastAPI release comparison at `0.136.2` (`22b02e2`) to `0.136.3` (`8206485`) in a local bare Git clone.
- Read Git trees/blobs only; did not populate or run a FastAPI worktree or its test suite.
- Used a versioned display profile derived from FastAPI's public documentation and the fixed source layout. The conceptual processing view is profile-sourced and explicitly not a static-import or runtime claim.
- Generated an isolated report and inspected desktop/narrow browser geometry.

## Result

The snapshot covers 1,121 successfully parsed modules and 1,545 static import edges in four reader sections with zero unclassified modules. The fixed release range changes four files, including `fastapi/dependencies/utils.py` and its associated regression test. The profile maps two inputs through routing, dependency/security resolution, model processing, path operations, responses, OpenAPI generation, and interactive documentation.

The initial real profile exposed a generic route-planning defect: endpoints were needlessly constrained by their own cards and a simple forward layered route was not attempted before full-channel search. The renderer now attempts a geometry-checked forward route for any layered edge, then uses obstacle-aware channel routing only when needed. This is topology-based and contains no FastAPI paths, names, or IDs.

## Verification

- FastAPI desktop: `layered`, 9 cards, 9 SVG relations, 9 relation rows, zero sampled connector/card intersections, zero browser console warnings/errors.
- FastAPI narrow: 390 px document width, no horizontal overflow; decorative links intentionally hidden and cards remain readable.
- Existing self-hosted, branch/merge/two-gate, and cyclic-fallback browser fixtures still pass.
- Full project test suite: 50 passed; compileall, JavaScript syntax, and diff check pass.

This is one known public external sample, not a blind holdout or evidence of cross-project generalization.
