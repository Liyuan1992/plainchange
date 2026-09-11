# TASK-20260911-050: Real-provider model-first validation

State: DONE
Tier: high-risk

## Trigger and authorization

After TASK-049 implemented the configurable model-first path, the owner supplied
a specific OpenAI-compatible endpoint and API credential and instructed
PlainChange to fill it in. This authorizes using that endpoint and credential for
the current local configuration and the previously requested fixed
ChestnutDogAiThink analysis. It does not authorize storing the credential,
transmitting dirty-worktree content, modifying the target project, committing,
pushing, publishing or deploying.

## Plan and boundaries

1. Verify the endpoint credential and enumerate its available models without
   printing the credential.
2. Store only provider ID, `/v1` endpoint, selected model and credential
   environment-variable name in the Git-ignored local config.
3. Run the two-stage fixed-revision ChestnutDogAiThink analysis and retain
   secret-free success/failure receipts.
4. If real-provider behavior exposes a generic contract or payload defect, fix
   only that class of problem, add regression coverage and retry within bounded
   attempts.
5. Stop rather than silently use deterministic output if the configured provider
   remains unavailable or the model result fails evidence validation.

## Observed provider evidence

- `GET /v1/models` accepted the configured environment credential and listed the
  selected model family. The credential value was never written to the project,
  generated report or run receipts.
- `gpt-5.6-sol` reached the project-understanding stage but the upstream gateway
  returned HTTP 504 after about 65 seconds.
- `gpt-5.6-luna` returned one project result that exposed a redundant
  structure-kind/component-type contradiction, then a retry returned HTTP 504.
  The contradictory result was rejected before report generation.
- `gpt-5.3-codex-spark` completed project understanding in about 20 seconds. The
  first change-interpretation attempts returned HTTP 502 because the model input
  still carried the complete 622 KB generator packet.

## Generic corrections

- Capability-map component type is now derived from the parent map kind. The
  repeated model field cannot invalidate an otherwise source-bound capability
  model; workflow role mismatches still fail closed.
- Project-understanding path input now contains only paths introduced by bounded
  code outlines or implementation-group samples, while retaining the complete
  first-party source count separately.
- Change interpretation now receives a bounded semantic context: change facts,
  highest-churn file records, behavior/task evidence, a limited set of changed
  architecture nodes, counts, unknowns and limitations. The full packet remains
  local and still performs final evidence validation. Omitted evidence is
  explicitly unavailable, not negative evidence.
  On this sample the transmitted change context is 28,269 bytes with 87 evidence
  records; 167 local records and the full patch remain local for final validation.

## Successful result

- The final `gpt-5.3-codex-spark` run reused cached project understanding,
  completed change interpretation in 12.468 seconds and generated the full
  report in 17.827 seconds.
- The model identified the project as a pet-store operations AI assistant and
  produced a ten-area capability map rather than a fake sequential workflow.
- The owner headline now identifies the dominant change as a new product-
  recommendation overview spanning a backend task, frontend cards, replacement-
  plan presentation and peer-shop data support. Incidental exception branches no
  longer replace the product story.
- The local validator accepted four claims, downgraded two unsupported claims to
  unknown and rejected none. User impact and runtime behavior remain unverified.
- Stage receipts report 25,401 tokens for cached project understanding and
  19,796 tokens for change interpretation. Both receipts contain provider/model,
  timing, token counts and hashes, but no credential or response body.

## Verification

- Focused semantic/pipeline regressions pass, including a bounded change-context
  assertion below 150 KB and exclusion of the full patch from model input.
- All 122 tests pass. Python compilation, both JavaScript syntax checks,
  `git diff --check`, wheel/source-archive rebuild, clean wheel reinstall and
  packaged CLI startup pass.
- The target repository was read only and remained at fixed head
  `0883fe0676f0148139afc82e92101d732d75ed3b`.
- Browser-control recovery failed in this session, so the generated HTML was
  opened for owner review but not claimed as a new browser-layout acceptance.

## Remaining decision

The real run demonstrates that the model-first direction fixes the previously
wrong semantic focus on this sample. It does not yet prove that
`gpt-5.3-codex-spark` is the default quality/cost choice, that every compatible
gateway accepts the same payload, or that a non-technical owner accepts the
wording. Those require cross-project and human review rather than another hidden
fallback.
