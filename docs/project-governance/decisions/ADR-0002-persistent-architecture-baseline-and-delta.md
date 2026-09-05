# ADR-0002: Add an approved bounded architecture baseline and per-change delta

- Status: Accepted
- Date: 2026-09-04
- Decision owner: Project owner
- Source: confirmed PRD v1.1, SHA-256 `995E5701B2438A08ED9E32FBE68E54E197DB7F126BCDCECE0B6F3D953D3C1B9C`
- Related task: `TASK-20260904-003`
- Supersedes: the prose-only sufficiency assumption in PRD v1.0; does not supersede ADR-0001

## Context

The first real DigitalSelf run preserved the intended evidence boundary: the model saw only a frozen packet, the validator accepted eight cited claims, and provider self-reported tests were not presented as verified facts. That supports keeping ADR-0001's deterministic evidence/model/validator split.

The same run showed that a fixed four-section prose brief is not sufficient for architecture comprehension. The owner could not see before/after topology, changed responsibility, or direct impact at a glance. The prose also provides no durable machine-readable project structure for the next run, so an agent would repeatedly rebuild its understanding from source.

The response must not become a full symbol graph or a generic knowledge-graph platform. The missing layer is a bounded, evidence-backed architecture state at module/component/responsibility/interface level, plus a per-change delta.

## Decision

Extend the existing evidence spine with five bounded contracts after the revised PRD is confirmed:

1. `ArchitectureBaseline` stores a versioned, machine-readable local structure for the approved repository commit. Nodes represent modules/components/services/datastores/external systems and carry owned paths, responsibilities, interfaces, invariants, evidence refs, and `last_verified_commit`. Edges represent only supported verified relations.
2. A run loads the approved baseline, verifies repository/base identity and relevant path/structure hashes, and invalidates stale nodes. With no baseline, it creates a bounded bootstrap candidate instead of pretending the project is already understood.
3. Deterministic extraction computes added/removed/modified nodes and edges. Impact is limited to verified paths from changed nodes, defaulting to one hop. Dynamic or unsupported behavior remains unknown.
4. A single validated `ArchitectureDelta` JSON renders both a Mermaid before/after map and the four-section explanation. The model may explain or propose responsibility wording, but cannot create verified topology or an independent diagram.
5. Structural changes produce a separate `BaselineProposal`. Only attributable human approval creates the next approved baseline; candidates never become authority by reuse or model confidence.

The architecture baseline is a revalidatable projection over Git/code evidence, not code authority. A conflict with Git identity, schema, source refs, or structural hashes fails closed as stale/invalid.

## Scope boundary

M1.5 supports only the minimum DigitalSelf Python/JavaScript module-level slice needed to evaluate the first sample and a short consecutive-change sequence. It does not build a full repository graph, symbol-level call graph, interactive graph UI, cross-repository service, editor integration, cloud platform, or automatic approval workflow.

## Considered alternatives

1. Keep the four prose sections as the only output: rejected because the first real sample did not make topology and impact visible and gave the system no reusable structure.
2. Persist the model's narrative as project memory: rejected because prose is not a validated topology, can drift, and would let model confidence masquerade as architecture authority.
3. Build a full symbol/knowledge graph first: rejected because it exceeds the validated need, enters mature competitor territory, and would make the experiment depend on deep multi-language analysis.
4. Render Mermaid directly from model output: rejected because the graph could disagree with JSON, evidence, or prose and could not be deterministically verified.

## Consequences

- The human gets a graph-first review while retaining the existing evidence and unknown semantics.
- The system can reuse approved unchanged nodes and focus analysis on changed paths and a bounded neighborhood.
- Baseline identity, invalidation, proposal review, and graph/prose consistency become new acceptance gates.
- M1.5 introduces more deterministic extraction work, but it remains isolated from the model and product UI.
- ADR-0001 remains active for the evidence boundary. This decision does not itself start TASK-20260904-003 implementation.

## Approval

Accepted by the owner on 2026-09-04 through the explicit reply “确定” after PRD v1.1, ADR-0002, and TASK-20260904-003 were presented. This acceptance confirms the bounded architecture contract; following the established PRD gate, it does not by itself authorize implementation, product UI, full knowledge-graph scope, commit, push, packaging, or deployment.
