# TASK-20260911-051: Owner-language contract and bounded business map

State: DONE
Tier: standard

## Trigger and authorization

The first real model-assisted ChestnutDogAiThink report corrected the dominant
business story, but its headline still used engineering abstractions, its
ten-area capability map was too deep for a non-technical owner, and the
generic "ordinary user" impact wording did not identify the product's actual
audience. The owner reviewed these limits, asked whether a prompt alone could
solve them, then explicitly instructed: "好的，改吧".

This authorizes a generic PlainChange-side contract, presentation and test
change. It does not authorize a new external provider request, transmitting a
repository, changing an analyzed target, saving credentials, committing,
pushing, publishing or deployment.

## Approved plan

1. Make the model's project-understanding prompt and schema distinguish a
   short owner-facing business label/description from technical implementation
   terminology, and limit the default business map to four through six items.
2. Add a bounded, source-supported audience candidate to model change
   interpretation, so the impact card can name a role when the fixed evidence
   supports it and otherwise remain explicitly unknown.
3. Constrain the change summary to a short result-first headline and a concise
   explanation; preserve full technical detail only in the existing evidence
   drill-down.
4. Keep all evidence IDs, truth states, source paths, claim validation,
   runtime/user-impact unknowns and rendering identity deterministic. Model
   output may be rejected or downgraded; it cannot turn a role or an effect into
   a verified runtime fact.
5. Add mocked-provider and report-projection regressions, including business
   projects and framework-like projects. Do not use target-name, path-name or
   repository-vocabulary special cases.

## Non-goals

- No universal natural-language quality guarantee, user testing claim, or
  automatic translation of project-authored text.
- No model retry, provider selection, pricing change, live provider request or
  token-budget redesign in this task.
- No removal of the technical architecture/evidence view.

## Verification plan

- Schema and validator tests for bounded map sizes, concise summaries,
  source-bound audience candidates and invalid values.
- Pipeline/report tests proving the default impact text uses the specific role
  only when supplied by the validated semantic candidate.
- Existing semantic, pipeline, HTML and localization regressions plus full
  pytest, compileall, JavaScript syntax and `git diff --check`.

## Stop condition

Stop if a candidate audience is presented as verified user impact, a model can
bypass existing evidence validation, or the change requires a target-specific
phrase/path rule.

## Observed result

- The model-first project-understanding and change-interpretation contracts now
  use v2 schema identities. A business map is bounded to two through six items
  (the prompt requests four through six except for genuinely small evidence
  sets), instead of accepting a ten-item implementation inventory.
- Component labels/descriptions and change summary fields have short,
  owner-facing length constraints. The system prompts explicitly require a
  result-first title and prohibit engineering abstractions from becoming its
  main subject.
- Change interpretation can return up to three source-bound audience
  candidates. The deterministic projection accepts only a concrete role with
  evidence IDs, renders it as `可能受影响`, and retains `unknown` truth state plus
  the runtime boundary. Generic labels such as `普通用户` and `最终用户` are not
  promoted over the normal unknown fallback.
- Mocked-provider integration confirms that a concrete caller role reaches the
  impact card while preserving unverified status. Contract tests reject a
  seven-item owner map and exercise generic/missing-evidence audience fallback.

## Verification

- `tests/test_semantic_analysis.py`, `tests/test_owner_language_contract.py`,
  `tests/test_pipeline.py`, `tests/test_model_adapter.py`,
  `tests/test_html_renderer.py`, and `tests/test_software_control.py`: pass.
- Remaining suite groups also pass: architecture/automatic drafting/behavior/
  generator/Git/HTML/model/model tests (49), onboarding tests (8), and owner/
  pipeline/localization/review/scoring/source-scope/target-profile/validator
  tests (67): 124 tests total.
- `python -m compileall -q src`, both review JavaScript syntax checks, and
  `git diff --check` pass. The optional Python build module is not installed in
  the existing project virtual environment, so package rebuild was not run.
- This task made no real provider request and did not read or modify any target
  repository.
