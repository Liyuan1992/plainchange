# TASK-20260911-052: Real-model owner-language regression

State: DONE
Tier: high-risk

## Trigger and authorization

After TASK-051 changed the model prompt, semantic schema and deterministic
owner projection, the owner requested: "嗯试一下". This authorizes one bounded
real-provider rerun of the same fixed ChestnutDogAiThink range already approved
in TASK-050, solely to compare the revised owner-language contract against the
previous successful result.

It does not authorize target writes, dirty-worktree reads, new target ranges,
credential storage, provider/model selection changes, commits, pushes,
publication or deployment.

## Fixed inputs and comparison criteria

- Target range: `f76838f1133f0d5fbfbdb9c3d0fc13356912263b..0883fe0676f0148139afc82e92101d732d75ed3b`.
- Provider configuration: existing Git-ignored, environment-only compatible
  provider configuration. The credential must not be read into output, logs or
  task records.
- Success criteria: a short result-first headline, a two-to-six item business
  map, and either a source-bound specific role marked only as possible impact or
  an honest no-role unknown. The result must retain explicit runtime boundaries.
- Comparison baseline: `artifacts/chestnutdogaithink-model-first-spark-v3`.

## Stop conditions

Stop and retain a secret-free receipt if the provider fails, model output fails
validation, the target identity changes, or generated content relies on a
target-specific branch. Do not silently reuse the prior artifact as a success.

## Verification plan

1. Recheck target HEAD/status before and after the run.
2. Run the configured full-model analysis into a new PlainChange artifact
   directory.
3. Inspect model receipts, validated project understanding, semantic output and
   software-control document against the three comparison criteria.
4. Re-run focused model/pipeline contract tests; report real-provider quality
   separately from those automated checks.

## Observed result

The first real rerun completed in 29.064 seconds (project understanding
15.408 seconds; change interpretation 11.211 seconds). It produced a six-step
business workflow and concrete, source-bound role candidates, but exposed a
generic report projection defect: the short result-first headline was
concatenated with its detailed explanation on the first screen. TASK-053 fixed
that renderer defect and performed a new fixed-input rerun.

The final rerun completed in 18.653 seconds, reusing immutable project
understanding and spending 14.479 seconds in change interpretation. The report
now renders the 23-character headline `商品推荐总览与替换方案已新增并补充同店分组支撑`
without its detailed explanation, preserves that explanation in the five
questions, shows six business workflow steps, and marks `店员` only as
`可能受影响`. Four claims were accepted, two were downgraded, and none were
rejected. Runtime/user-impact boundaries remain explicit. Target HEAD and the
pre-existing dirty-worktree count were unchanged before and after both runs;
receipts/artifacts contain no credential.
