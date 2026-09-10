# TASK-20260905-011: Product-architecture-first system map

State: DONE
Tier: standard

## Trigger and approval

The owner reviewed the self-hosted report and found that its “overall architecture” page was only a source-code category view: a first-time reader could not identify the system’s components, inputs, outputs, flow, or human approval boundary. The owner explicitly approved the direction with “是的，按这个方向来改” on 2026-09-05.

## Goal

Make the first architecture view a readable system architecture for a non-coder, while retaining the existing full static-code map as a separately labelled implementation layer.

## Scope

1. Extend the strict target-profile asset with an optional, auditable conceptual architecture: named components, directed workflow relationships, source-code mapping hints, and explicitly external human gates.
2. Carry that profile-sourced architecture through the validated snapshot and reader model without treating it as a Git/import fact.
3. Render it first in the architecture tab with inputs, evidence spine, static extraction, constrained generation/validation, human-readable outputs, and the human approval gate visible as distinct components.
4. Make source-code grouping a second “implementation layer”; enable a concept component to enter its mapped static-code groups when such a mapping exists.
5. Add generic parser/model/HTML tests and browser screenshot acceptance for the Change Passport self-hosted artifact.

## Non-goals

- Do not invent runtime, deployment, database, network, or user-behaviour links.
- Do not convert profile-sourced conceptual relationships into `ArchitectureDelta` or baseline facts.
- Do not hard-code Change Passport nodes, labels, paths, or relationships in general rendering code.
- Do not add a model provider, live task connector, remote service, baseline approval, commit, push, or release.

## Risks and stop conditions

- Stop if profile configuration can modify static extraction results, claims, baseline authority, or target read-only behavior.
- Stop if a conceptual connection is labelled as a verified static import without matching evidence.
- Stop if a profile component claims an implementation mapping that cannot be resolved to the frozen snapshot; render it as an explicit unmapped external/product component instead.

## Verification plan

- Strict schema and identity tests for conceptual architecture profile data.
- Regression proof that conceptual architecture is marked profile-sourced and does not alter static node/edge facts.
- Full pytest, compileall, JavaScript syntax, no-network HTML checks, and Git diff check.
- Regenerate the isolated self-hosted report and inspect desktop and narrow browser screenshots: a first-screen reader must see inputs, core processing, outputs, and the human approval boundary before static modules.

## Commit boundary

This approval authorizes local implementation and verification only. It does not authorize a commit, remote, push, publication, release, provider integration, or baseline approval.

## Completion evidence

- Extended the strict profile contract with `conceptual_architecture`: named components, flow labels, grid positions, static-group mapping hints, and a distinct `human_gate` component. Unknown flow IDs, duplicate layout positions, and mappings to unknown configured sections fail closed.
- The review model emits a separate `conceptual_architecture` view carrying `source.kind=target_profile`, profile ID, and profile SHA. It does not modify `ArchitectureDelta`, static snapshot nodes/edges, claims, or baseline status.
- The architecture page now places the product/process map first and labels the static map as `第 2 层 · 实现层`. Its source note explicitly says profile-declared arrows are not static imports or runtime order. Mapped components can open the existing static-group drill-down; external inputs and the human gate do not pretend to be single source-code modules.
- Regenerated the isolated self-hosted `a4576ec..688fc5f` artifact. The target clone was clean before and after. The review contains 8 conceptual components, 8 flows, and profile SHA `928fcffe396d74ecfd73b49e6e8b968fdf0a8d90e1b10e17df80d8102ab30e26`, equal to the snapshot metadata.
- Browser capture at 1440 × 1050 confirms concept map visibility before static implementation, 8 SVG flows, 8 textual relation fallbacks, visible fixed-change/task-evidence/process/output/human-gate components, and working mapped-code drill-down. At 390 × 844, cards stack in order, SVG arrows intentionally hide, document width equals viewport width, and there were zero console warnings/errors. Review score: 8.8/10, delivery allowed.
- Final local verification: `uv run pytest -q` reported `49 passed`; `uv run python -m compileall -q src tests`, `node --check src/change_passport/templates/review.js`, and `git diff --check` exited successfully.

## Stop / handoff

Stop after the approved local implementation and verification. No commit, remote, push, release, provider integration, or baseline approval is authorized. The next gate is an independent non-coder retelling of the system architecture, followed by scored cross-repository samples.
