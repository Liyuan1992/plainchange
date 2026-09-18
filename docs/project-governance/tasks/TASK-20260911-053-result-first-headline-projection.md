# TASK-20260911-053: Result-first headline projection

State: DONE
Tier: micro

## Trigger and authorization

TASK-052's real-model rerun produced a valid short model headline, but the
rendered first-screen headline concatenated that headline with its explanation
and runtime boundary. The result violated the just-approved ten-second reading
contract despite valid model output. The owner previously authorized the
owner-language correction and its real rerun; this is the directly exposed,
repository-neutral display defect within that scope.

## Scope and verification

- Preserve the full explanation in the change question and technical detail.
- Render only the validated model headline in the first-screen headline field.
- Keep deterministic/no-model headline behavior unchanged.
- Add regression coverage, rerun the fixed model sample once, and retain all
  runtime/user-impact boundaries. No target-specific text or path rule.

## Observed result

The renderer now stores the validated model headline separately and uses it
only for the ten-second first screen; the fuller headline-plus-explanation text
continues to appear in the detailed change answer. The regression verifies this
separation without changing deterministic/no-model output. A second real
ChestnutDogAiThink run used the same commits and model configuration, rendered
the 23-character headline as intended, and retained all uncertainty language.
Focused tests, then the full 124-test suite, Python compilation, JavaScript
syntax checks and `git diff --check` pass. The correction is generic: it acts
on a validated semantic-summary field, not on target names, paths or phrases.
