# Evidence contract

## Active source-backed constraints

- Target repositories are read-only. Git collection uses fixed argument arrays, `shell=False`, explicit timeouts, and `GIT_OPTIONAL_LOCKS=0`. Source: ADR-0001, EVO-20260904-003.
- The generator can see only `generator-packet.json`. The packet omits repository paths, manifest paths, hidden-ground-truth IDs, paths, and content. Source: ADR-0001, EVO-20260904-003.
- Input evidence and hidden ground truth cannot share the same resolved file path or exact content hash. Source: EVO-20260904-003.
- Raw model claims are untrusted. Unknown evidence IDs are rejected; missing authority classes and invalid section/scope combinations are downgraded to safe `unknown` text. Source: ADR-0001, EVO-20260904-003.
- A verified user-behavior claim requires both `original_task` and `git_fact`; test status requires `actual_test_receipt`; a history relation requires both `approved_history` and `git_fact`. Source: ADR-0001, EVO-20260904-003.
- `finalize` and `score` may write only inside the prepared artifact directory. Source: EVO-20260904-003.
- M1.5 architecture facts come from immutable Git tree/blob identities and supported Python/JavaScript static imports. The model may explain them but cannot add a verified node, edge, or impact path. Source: ADR-0002, EVO-20260904-008.
- `modified_edge_ids` compares retained-edge evidence locations after masking only the Git commit component. A new verification commit alone is not a topology change; source-path or line movement still is. Source: BUG-20260905-013, TASK-20260905-009.
- An approved baseline requires matching repository/base commit/schema/tracked blob identities plus an attributable approval decision bound to the exact proposal SHA-256. Candidate, tampered, or stale baselines fail closed. Source: ADR-0002, BUG-20260904-006, EVO-20260904-008.
- Mermaid and the graph-first Markdown section render from the same validated delta JSON. Display folding is explicit and retains omitted IDs in JSON. Source: ADR-0002, BUG-20260904-004, EVO-20260904-008.
- `beginner-review.json` and `review.html` are deterministic derived views over the validated brief and the same `ArchitectureDelta`. They preserve claim/node/evidence identity, may only maintain or lower truth state, retain every folded ID, and cannot write view state back into evidence or baseline authority. Source: TASK-20260904-004, BUG-20260904-009.
- `system-architecture.json` is a candidate full supported-code static snapshot for the frozen Head. Every parsed module belongs to exactly one confirmed display section, every cross-section relationship retains its source edge IDs exactly once, and the change overlay reuses `ArchitectureDelta` IDs. It is not an approved baseline or proof of runtime/deployment/database/network architecture. Source: TASK-20260904-005, EVO-20260904-014.

## Regression checks

- Manifest and copied-content leakage: `tests/test_models.py`.
- Immutable read-only Git collection and truncation: `tests/test_git_evidence.py`.
- Generator-packet exclusion and tamper detection: `tests/test_generator_contract.py`.
- Evidence-ID, authority, section/scope, and safe-unknown validation: `tests/test_validator.py`.
- File-bridge end to end and artifact-path containment: `tests/test_pipeline.py`.
- Precision, recall, unsupported, authority, and leakage metrics: `tests/test_scoring.py`.
- Baseline approval/hash binding/staleness, incremental reuse, Python/JavaScript import impact, retained-edge reverification versus source-line movement, graph parity, display folding, and target-repository preservation: `tests/test_architecture.py`.
- Batched immutable Git blob reads: `tests/test_git_evidence.py`.
- Beginner-summary truth/identity/omission checks: `tests/test_review_model.py`.
- Single-file HTML escaping, no-network, theme, and embedded-identity checks: `tests/test_html_renderer.py`.
- Full-system snapshot identity, complete assignment, source-edge aggregation, review embedding, top-level architecture tab, and formal DigitalSelf browser smoke: `tests/test_architecture.py`, `tests/test_pipeline.py`, `tests/test_html_renderer.py`, TASK-20260904-005.

## Known gaps

- No automatic model provider is implemented or authorized.
- Historical evidence has no cryptographically enforced “existed before base/head” provenance yet.
- Exact copied content is blocked, but paraphrased answer leakage requires human evaluation.
- No real DigitalSelf sample or real model output has been scored.
- Static `imports` proves a dependency edge, not runtime execution or behavioral impact; dynamic imports, reflection, configuration injection, and runtime routing remain unknown.
- The first M1.5 DigitalSelf baseline proposal is not approved, so the required real consecutive-change reuse sequence remains pending owner review.
- Browser layout/interaction acceptance passed for the formal generated HTML on desktop and 390 px responsive layout. An independent human 30-second retelling remains pending; passing automated and browser rendering tests is not equivalent to that human outcome.

## Source index

- ADR-0001: three-layer evidence/generator/validator architecture.
- EVO-20260904-002: owner-approved correction from model-free to constrained-model generation.
- EVO-20260904-003: locally verified Phase 0-M1 implementation.
- ADR-0002: approved bounded architecture baseline/delta authority contract.
- EVO-20260904-008: M1.5 core implementation and first real graph-first sample.
- EVO-20260904-014: complete supported-code system snapshot and browser-verified overall architecture tab.
