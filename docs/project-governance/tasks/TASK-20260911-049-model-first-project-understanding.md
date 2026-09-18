# TASK-20260911-049: Model-first project understanding

State: DONE
Tier: high-risk

## Trigger and authorization

The ChestnutDogAiThink validation showed that deterministic rules can preserve
code facts while still choosing the wrong business story. The owner concluded
that PlainChange should involve a configured model from the beginning and then
explicitly authorized execution. This authorizes the bounded product,
documentation, implementation and local verification work below. It does not
authorize transmitting any repository to a real external provider, storing a
secret, modifying analyzed projects, committing, pushing, publishing or
deploying.

## Baseline facts

- The current `model` generator is optional and only rewrites a prepared claim
  packet. Project purpose, workflow/capability structure and change location are
  already chosen by deterministic heuristics before that call.
- The guided browser entry always runs the deterministic generator and has no
  model settings surface.
- Deterministic analysis is currently presented as the normal product path even
  when semantic interpretation was not run.
- ADR-0001 requires Git facts, evidence scope, unknowns and human approval to
  remain deterministic boundaries. ADR-0004 provides a provider-neutral,
  OpenAI-compatible configuration contract and environment-only credentials.
- BUG-20260911-039 through BUG-20260911-042 are generic failures exposed by the
  business application sample; no project-specific exception is permitted.

## Goal

Make model-assisted understanding the normal full-experience path: first build
and cache a source-bound understanding of the fixed project revision, then
interpret the selected change against that understanding, and finally validate
every owner-facing claim against local evidence. When no model is configured,
produce a clearly labelled basic evidence report rather than implying that the
software's business meaning was understood.

## Approved implementation

1. Revise the product and architecture decision so that the model owns semantic
   interpretation while deterministic code owns collection, sanitization,
   identities, evidence validation, downgrade rules and unknowns.
2. Add a strict project-understanding contract and a content-addressed cache
   bound to the fixed head commit, sanitized input identity, provider config and
   model. Cached model prose must never become runtime evidence.
3. Run two constrained model stages for the full experience: project
   understanding followed by change interpretation. The second stage receives
   the first stage's validated output plus the frozen change packet.
4. Let the project-understanding result drive a candidate target profile and
   owner workflow/capability map before final report generation. Every semantic
   item retains source references and a non-authoritative state.
5. Make `auto` the default analysis mode. It uses the configured compatible
   provider when one is supplied; otherwise it completes locally in explicit
   `basic_evidence` mode with no network request. Keep explicit `model` and
   `deterministic` choices for automation and diagnosis.
6. Add guided local model settings for provider ID, compatible endpoint, model,
   credential environment-variable name and response mode. Do not accept or
   persist an API key value in the browser or repository.
7. Correct the generic input-quality defects needed by the semantic stage:
   exclude vendored dependency trees, avoid treating Markdown table counts as
   capability descriptions, and surface unsupported changed-language coverage
   honestly. Parser expansion may be added only where it is generic and tested.
8. Add mocked-provider and cross-project regression coverage. No real provider
   call is required or permitted for this task.

## Non-goals

- No model-selected provider, bundled credential, provider account setup,
  billing integration, background upload, embeddings service or model download.
- No claim that model text proves runtime order, user impact, correctness or
  human acceptance.
- No ChestnutDogAiThink-, FastAPI-, vLLM-, VideoFactory- or DigitalSelf-specific
  path, repository-name, vocabulary or workflow branch.
- No target application execution or mutation.

## Affected domains

- Product positioning and onboarding
- Model-provider and semantic-analysis contracts
- Evidence and privacy boundaries
- Target-profile/owner-report generation
- Analysis caching and run receipts
- Cross-project regression tests and public documentation

## Risks and stop conditions

- Fail before transmission when configuration, credentials or sanitized input
  constraints are invalid.
- Never send repository paths, hidden ground truth, secrets, dirty-worktree
  content or unrestricted source trees.
- Do not silently fall back after a configured model request fails; a user who
  selected the full path must see the failure.
- Stop if model output can upgrade an unsupported statement to observed fact, or
  if cached output is not bound to immutable input/provider identities.
- Preserve the dirty worktree and all unrelated existing changes.

## Verification plan

- Contract tests for project-understanding validation, evidence/source
  allowlists, cache hit/miss/invalidation and tamper rejection.
- Mocked compatible-provider tests proving two ordered stages, bounded payloads,
  secret redaction, failure receipts and no silent fallback.
- CLI and guided-server tests for default `auto`, explicit basic evidence mode,
  browser settings validation and environment-only credentials.
- Regression tests for vendored-dependency exclusion, Markdown capability-table
  extraction and honest unsupported-language reporting.
- Full pytest, compileall, JavaScript syntax, package-data/build smoke and
  `git diff --check`.

## Stop and handoff

Complete when the configured path performs and records both model stages, the
unconfigured path is visibly degraded without network access, the settings UI
uses the same provider contract, generic regressions pass, and remaining real
model quality and human-comprehension validation are reported separately.

## Observed result

- The configured full path now performs two ordered, schema-constrained calls:
  fixed-revision project understanding followed by change interpretation. Both
  stages validate source/evidence allowlists before their output reaches the
  owner report, and each completed network stage writes a secret-free receipt.
- Project understanding is cached by fixed head commit, sanitized context
  identity, provider configuration identity, model and schema. The mocked
  provider regression proves that a repeated analysis reuses stage one while
  still running stage two for the selected change.
- The guided local UI now defaults to `完整理解（推荐）`, accepts an
  OpenAI-compatible endpoint/model plus an environment-variable name, and never
  accepts an API-key value. The unconfigured CLI path remains local and labels
  its result `basic_evidence` instead of implying semantic understanding.
- Generic input corrections are active for every target: semantic Markdown
  table columns are selected by header role, Vue/MJS/CJS source extensions are
  admitted by the bounded static parser, and standard dependency/build trees
  are excluded before architecture construction.
- The fixed ChestnutDogAiThink rerun produces eight owner-readable capability
  descriptions, 518 first-party nodes including 79 Vue and 3 MJS files, excludes
  480 vendored/generated source files, and contains zero dependency/build-tree
  nodes. It still reports the low-level exception headline in basic evidence
  mode by design; BUG-20260911-039 remains open until the model-assisted result
  is exercised and accepted on a real provider.
- Verification: 121 tests pass; focused two-stage/cache/source-scope tests pass;
  Python compilation, both JavaScript syntax checks, `git diff --check`, wheel
  and source-archive builds pass. The target repository HEAD remains
  `0883fe0676f0148139afc82e92101d732d75ed3b`; all target access was read-only.
- No real provider request, secret storage, target mutation, commit, push,
  publication or deployment occurred. Real-model semantic quality and beginner
  comprehension are the next validation gate, not a completed claim here.
