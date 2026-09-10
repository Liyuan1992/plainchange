# ADR-0003: Keep model generation local, optional, and downstream of frozen evidence

- Status: Accepted
- Date: 2026-09-10
- Decision owner: Project owner
- Related task: `TASK-20260910-032`

## Context

The deterministic `analyze` path is fast and safe but cannot explain a concrete change beyond generic file and area summaries. ADR-0001 reserved a provider adapter behind a separate plan and privacy approval. The owner explicitly requested a model integration, and a compatible Ollama model is already available on the same machine.

## Decision

1. Deterministic evidence collection, topology, validation, and rendering remain authoritative.
2. Model generation is an explicit `analyze --generator ollama` option; deterministic generation remains the default.
3. The local adapter may send only the validated generator packet to a loopback Ollama endpoint. It cannot read repository paths, hidden ground truth, environment variables, or unrelated files.
4. Structured output is untrusted. Provider metadata is injected from the actual response, evidence validation remains mandatory, and failures cannot silently fall back to rule text.
5. A model receipt binds provider/model, packet/output hashes, duration, endpoint origin, and token counters when supplied. It records generation, not correctness or human acceptance.

## Consequences

- A local model can produce substantially more specific change explanations without weakening the evidence boundary or creating upload cost.
- The current 4B model adds roughly forty seconds on the fixed vLLM packet and still uses engineering language. It is an optional candidate-writer, not the final owner-language authority.
- Remote providers, credentials, source upload, automatic provider selection, and model-authored topology still require separate approval and contracts.

## Approval

Accepted through the owner's explicit 2026-09-10 request “接入模型看看效果” after the deterministic-only boundary was explained. This approval is limited to the local adapter and fixed comparison run; it does not authorize remote data transfer, commit, push, deployment, or baseline approval.
