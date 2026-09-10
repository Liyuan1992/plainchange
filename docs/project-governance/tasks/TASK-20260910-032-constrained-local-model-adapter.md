# TASK-20260910-032: Constrained local model adapter

State: DONE
Tier: high-risk

## Trigger and authority

The owner asked to connect a model and inspect the result after confirming that the current one-command path uses deterministic tooling only. This explicit request authorizes the bounded local-model implementation and one fixed vLLM comparison run without further confirmation.

## Source facts

- `analyze` currently records `deterministic_local_no_model` and builds all owner wording with rules.
- ADR-0001 already defines the permitted boundary: the model may read only `generator-packet.json`; deterministic validators remain authoritative.
- Ollama is running locally at `127.0.0.1:11434` and exposes `memdsl-qwen3-4b-32k:latest`; no remote model credential was found in the project environment.
- The fixed vLLM packet is about 68 KB and fits the local model's declared 32K context, but real generation latency and output validity are not yet known.

## Goal

Add an explicit, provider-neutral model-generation boundary with a real local Ollama implementation, durable generation receipts, strict output validation, and a fixed vLLM result that can be compared with the deterministic candidate.

## Approved implementation

1. Add a model adapter contract and an Ollama JSON-schema implementation using only the Python standard library.
2. Add `analyze --generator ollama --model ... --model-base-url ... --model-timeout ...`; preserve deterministic behavior as the default.
3. Send only the validated generator packet. Do not expose the manifest path, target repository path, hidden ground truth, local environment, or unrelated files.
4. Inject actual provider/model/time metadata outside the model response, then run the existing raw-brief and software-control validators.
5. Write `model-run-receipt.json` with packet/output hashes, timing, token counters when available, endpoint origin, and failure state; never record secrets.
6. Do not silently fall back to deterministic wording when model generation fails.

## Non-goals

- No remote API call, API-key storage, account integration, model download, target runtime execution, baseline approval, commit, push, deployment, or vLLM-specific prompt branch.
- No model-authored topology, software workflow, user-impact fact, or automatic human approval.
- No claim that a valid JSON response is accurate, comprehensible, or production-ready.

## Risks and stop conditions

- Stop if the request would send content outside the configured local endpoint without an explicit provider choice.
- Fail closed if structured output is invalid, evidence IDs are unknown, the packet hash changes, the endpoint is unavailable, or the model times out.
- Keep the target repository read-only and preserve unrelated dirty-worktree changes.

## Verification plan

- Unit-test request isolation, JSON-schema use, metadata injection, receipt success/failure, CLI routing, and no silent fallback.
- Run the full test suite, compileall, JavaScript syntax, and `git diff --check`.
- Run the fixed vLLM sample through local Ollama into a new artifact directory and compare model metadata, validation counts, first-screen wording, duration, and target Git status with the deterministic artifact.

## Rollback

The deterministic generator remains the default. Removing the new adapter and CLI options restores the previous behavior without changing evidence or target repositories.

## Handoff condition

Complete when the adapter is tested and one real local-model run either produces a validated report or leaves an explicit reproducible failure receipt. Model quality and human comprehension remain separate gates.

## Implementation result

- Added a provider protocol and standard-library Ollama adapter with loopback-only endpoint enforcement, JSON Schema output, injected provider metadata, and atomic model receipts.
- Extended `analyze` with explicit generator/model/base-URL/timeout options while preserving deterministic generation as the default.
- The first real run exposed that unconstrained array length allowed an otherwise structured response to omit three required sections and answer in English. The generic contract now requires 4–12 claims and instructs the model to cover all four sections in simplified Chinese, behavior-first owner language.
- The software workflow/topology remains profile/deterministic and the model only improves raw change claims. The existing validators remain the sole path into the rendered report.

## Verification evidence

- Full suite: 72 tests pass. Python compileall, JavaScript syntax, and `git diff --check` pass.
- Request-isolation tests prove that the model user message equals the validated packet and omits the absolute target repository path. Remote Ollama origins are rejected.
- Failure tests preserve `model-run-receipt.json` and prove there is no deterministic fallback.
- Fixed vLLM deterministic baseline: 4.137 seconds, 4 accepted / 0 downgraded / 0 rejected; first screen only identifies two changed files and broad areas.
- Fixed vLLM local-model v2: 47.275 seconds total, 43.375 seconds in model generation, 27,444 prompt tokens and 1,505 output tokens; 8 accepted / 1 downgraded / 1 rejected. It identifies the offline multimodal special-token default and duplicate-BOS risk, while preserving unknown runtime/user impact.
- The target repository's pre-existing status hash remained exactly `03392EBE75416C3ADD2E4D5F062FC0E3AF9D73E2AA1DC553F10DE839E71D4F39` before and after both model runs.

## Remaining limits

- The local 4B result is materially more specific than the rule baseline but still leads with file/class/tokenization terminology; it does not yet meet the non-coder language target.
- A successful structured response is not a scored accuracy result. Human comprehension, runtime behavior, and user impact remain unverified.
- Model generation currently improves change claims only. Generating or refining the complete owner-facing software-control document would need a second constrained contract and evaluation rather than letting the model author topology.
