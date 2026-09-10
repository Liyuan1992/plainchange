# TASK-20260910-033: Configurable model provider interface

State: DONE
Tier: high-risk

## Trigger and authority

The owner corrected the local-model direction: Change Passport should expose one configurable interface instead of running or privileging Ollama. Users must choose their own domestic, international, hosted, or local OpenAI-compatible provider after the product starts. The owner explicitly authorized this implementation and asked not to run a local model.

## Source facts

- TASK-032 proved the evidence/model/validator boundary but exposed Ollama-specific CLI flags and defaults.
- Domestic and international providers commonly expose OpenAI-compatible Chat Completions, while structured-output support varies between JSON Schema, JSON Object, and prompt-only JSON.
- Provider credentials must not be stored in repository configuration, receipts, generated reports, or command output.
- Default analysis must remain deterministic and make no network request.

## Goal

Replace the Ollama-specific entrypoint with a provider-neutral, runtime-configurable OpenAI-compatible Chat Completions interface that preserves privacy disclosure, evidence validation, receipts, and deterministic defaults.

## Approved implementation

1. Add a strict `change-passport.model-provider.v1` JSON configuration contract for provider ID, base URL, model name, API-key environment variable name, timeout, and structured-output mode.
2. Support `json_schema`, `json_object`, and `prompt_only` request modes without vendor-specific code branches.
3. Add `analyze --generator model --model-config <path>`; remove public Ollama-specific model/base-URL/timeout flags and hard-coded model defaults.
4. Read secrets only from the configured environment variable at request time. Reject embedded key fields and never persist authorization headers or key values.
5. Keep explicit model invocation, frozen-packet-only transmission, deterministic validation, failure receipts, and no silent fallback.
6. Provide a safe template config and documentation for user-owned runtime setup.

## Non-goals

- No provider account setup, bundled key, provider discovery, billing integration, remote or local model execution, automatic provider selection, settings UI, model download, commit, push, or deployment.
- No promise that every nominally compatible provider implements identical structured-output behavior.
- No model-authored topology, runtime fact, user-impact proof, or baseline approval.

## Risks and stop conditions

- Fail before transmission when configuration is invalid or a required credential environment variable is missing.
- Do not permit credentials inside the JSON config or receipt.
- Preserve exact packet/output hashes and identify the endpoint origin without recording query parameters, headers, or response bodies in receipts.
- Preserve unrelated dirty-worktree changes and the read-only target-repository boundary.

## Verification plan

- Unit tests for all three response-format modes, URL composition, environment-backed bearer auth, missing credentials, unknown config/key rejection, response parsing, receipt redaction, and no fallback.
- Pipeline/CLI tests with a mocked compatible endpoint; no real model request.
- Full pytest, compileall, JavaScript syntax, CLI help, and `git diff --check`.

## Rollback

Deterministic generation remains the default. Reverting the provider-config module and CLI option restores the file bridge and deterministic path without touching evidence or target repositories.

## Handoff condition

Complete when a user can copy the template, select any compatible endpoint/model through configuration, keep the secret in an environment variable, and run the same validated analysis path without provider-specific code.

## Implementation result

- Replaced the public Ollama-specific generator with `--generator model --model-config <path>` and removed all built-in model names, model endpoints, and provider-specific runtime flags from source, tests, README, and current project status.
- Added the strict `change-passport.model-provider.v1` config loader. It rejects unknown fields, embedded credential fields, URL credentials/query/fragment, invalid timeout, and unsupported response modes.
- Added one OpenAI-compatible Chat Completions adapter with `json_schema`, `json_object`, and `prompt_only` capability modes. All modes send the same frozen packet and feed the same validator.
- Credentials are resolved only from the named environment variable when a request is about to be sent. Missing credentials fail before `_post_json`; receipts never contain the key or authorization header.
- Added `examples/model-provider.template.json`, `.env.example`, and an ignored `model-provider.local.json` convention.
- Retained TASK-032/ADR-0003 as historical experiment evidence; ADR-0004 is now the active provider-interface decision.

## Verification evidence

- 73 tests pass, including three output modes, strict configuration, environment-backed bearer authentication, secret redaction, request isolation, missing-key fail-closed behavior, pipeline routing, and missing-config CLI failure.
- `change-passport analyze --help` lists only `--generator {deterministic,model}` and `--model-config`; no provider or model is selected by default.
- Python compileall, JavaScript syntax, and `git diff --check` pass.
- A source/test/README/example scan finds no Ollama name, local model name, or removed model/base-URL/timeout flags.
- No real local or remote model request was made in TASK-033.

## Remaining limits

- Compatibility means OpenAI-style Chat Completions request/response shape, not guaranteed provider fidelity. Users must select the response-format mode their provider actually supports.
- Azure-specific query strings and non-Bearer authentication are outside this first contract.
- This is a runtime configuration/CLI interface, not yet a visual settings screen. A future settings UI should bind to the same schema rather than introduce provider-specific fields.
