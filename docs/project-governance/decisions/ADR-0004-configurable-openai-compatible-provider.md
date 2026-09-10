# ADR-0004: Use a configurable OpenAI-compatible provider boundary

- Status: Accepted
- Date: 2026-09-10
- Decision owner: Project owner
- Related task: `TASK-20260910-033`
- Supersedes: ADR-0003 as the active provider interface; retains TASK-032 as historical experiment evidence

## Context

The loopback Ollama experiment proved that a model can add semantic specificity without becoming evidence authority. It also made one runtime and one model name look like product defaults. The product needs an interface that users can configure after installation and that works across domestic, international, hosted, and local compatible services.

## Decision

1. Expose one strict provider-config contract based on OpenAI-compatible Chat Completions rather than provider-specific adapters or defaults.
2. Users supply the compatible base URL, model name, response-format capability, timeout, and the name of an environment variable containing the credential.
3. Support `json_schema`, `json_object`, and `prompt_only` modes. These are compatibility levels, not changes in evidence authority; all outputs still pass the same local validator.
4. Keep deterministic analysis as the default. A request is transmitted only when the user explicitly selects the model generator and provides a config path.
5. Never store a key in provider JSON, generated artifacts, logs, or receipts. Receipts retain only provider/model identity, sanitized config hash, endpoint origin, timing, token counters, packet hash, and output hash.

## Consequences

- Change Passport no longer selects or privileges a model vendor. Provider and model choice remain user-owned runtime configuration.
- Services that advertise OpenAI compatibility can use the same adapter, but their actual protocol fidelity and structured-output support remain the provider's responsibility.
- A future settings UI can bind to this stable config contract without changing the analysis pipeline.
- Azure-specific query/header conventions, vendor account setup, billing, and provider discovery remain outside this first compatible interface.

## Approval

Accepted through the owner's explicit correction: “不用跑本地模型，直接给一个接口就行，要什么模型用户自己去配。支持国内外的模型兼容。” No real model execution or remote transmission is authorized by this implementation task.
