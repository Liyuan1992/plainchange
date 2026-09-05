# ADR-0001: Build the deterministic evidence spine before semantic generation

- Status: Accepted
- Date: 2026-09-04
- Decision owner: Project owner
- Source: confirmed Evidence Spike PRD, SHA-256 `643F7A632523F831B0C90E5A9D6543A9CF4ADB456485DCBDB8B2A08C33199C7E`
- Related task: `TASK-20260904-001`

## Context

The experiment must distinguish frozen Git facts, task claims, test receipts, prior approved history, and hidden after-the-fact ground truth. Starting with semantic generation would make failures ambiguous: a wrong result could come from evidence collection, authority classification, leakage, or model behavior.

## Decision

Build a three-layer slice with explicit authority boundaries:

1. A deterministic local evidence spine resolves immutable Git identities, validates manifest authority classes, prevents hidden-ground-truth overlap, and builds the only packet visible to the generator.
2. A constrained model turns that packet into strict JSON claims. The first integration is a provider-neutral file bridge operated by the current Codex task; it has no direct repository or hidden-ground-truth access.
3. A deterministic validator rejects unknown evidence IDs, enforces authority requirements, downgrades unsupported claims, renders the four-section brief, and computes annotation metrics.

The program does not embed an API key or automatically send source data to a remote endpoint in this task. A later provider adapter requires its own plan and explicit privacy approval.

## Considered alternatives

1. Let an LLM read the repository and write an unconstrained brief: rejected because it confounds evidence correctness with prose quality and can leak ground truth.
2. Start with a UI: rejected because the confirmed PRD explicitly makes factual fidelity the first gate.
3. Integrate Hunch or a coding assistant immediately: deferred because it would add external contracts before the experiment proves a minimal increment.

## Consequences

- The model is present in the first usable slice, but it is only a writer over an audited packet.
- Evidence collection and semantic generation remain independently testable.
- Unsupported model claims are preserved in raw output for evaluation but cannot appear as verified facts in the rendered brief.
- Later automatic provider integration remains optional and must consume the same frozen evidence contract.

## Approval

Accepted by the user on 2026-09-04 after the three-layer design was explained in Chinese; the user replied “嗯，对的”. This approval does not authorize a remote model API, source upload, commit, push, CI, or deployment.
