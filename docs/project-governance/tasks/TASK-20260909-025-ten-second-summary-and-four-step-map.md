# TASK-20260909-025: Ten-second summary and four-step map

State: IMPLEMENTED — VISUAL ACCEPTANCE PENDING
Tier: standard

## Trigger and authority

The owner reviewed the first production two-screen report and supplied prioritized P0/P1 corrections. The feedback explicitly defines the next accepted direction: result-first language, a ten-second four-part summary, explainable evidence states, a four-step default mental model with the existing eight-step map behind interaction, a stronger change overlay, a scannable audience table, and an owner checklist. The ongoing instruction authorizes this bounded correction without another approval round.

## Goal

Make the default report understandable in about ten seconds and make the default software map a four-step mental model, while preserving the source-bound five-question explanation, eight-step detailed model, technical evidence, and generic cross-repository renderer.

## Approved plan

1. Extend the generic contract with a result-first internal concept label, per-state explanation, and a source-declared four-step overview map bound to detailed node IDs.
2. Replace the default first-screen stack with the result sentence, one plain-language explanation, and three compact answers for user impact, residual risk, and immediate owner action.
3. Collapse the five questions under “查看完整说明”; shorten question wording without changing IDs or evidence.
4. Render the four-step map by default. Clicking one overview step switches the same canvas to the eight detailed steps, focuses the mapped detail, and keeps a one-click route back to the overview.
5. Render audience impact as a scan-friendly table and owner checks as a non-mutating checklist.
6. Recompute contract/evaluation identities, regenerate the self-hosted artifact, and verify the generic/fallback paths.

## Non-goals

- No interactive “mark checked” persistence, approval mutation, or completed-test claim.
- No project-name, framework-name, path, or node-ID renderer branch.
- No automatic generation/model/provider work.
- No deletion of the five-question, eight-step, evidence, or implementation layers.
- No commit, push, deployment, baseline decision, or target-repository mutation.

## Risks and stop conditions

- Stop if the four-step map is inferred in the renderer rather than supplied and source-bound by the target contract.
- Stop if “目前没发现” is visually presented as “已证明不存在”.
- Stop if clicking the overview loses the current-change location or creates a separate architecture page.
- Stop if checklist styling implies that a recommended check has already run.

## Verification plan

- Validate Schema, canonical identity, overview/detail mappings, unique flow endpoints, and exactly one changed overview node containing the changed detail node.
- Test the collapsed five-question layer, explainable state controls, four-step default, detail expansion/back action, audience table, checklist, fallback, and no-network constraints.
- Run the complete test suite, compile check, JavaScript syntax check, HTML parse, and diff check.
- Attempt real browser screenshot review on the already-open artifact; record the browser policy limitation rather than bypass it if local-file access remains blocked.

## Handoff condition

Complete when the contract, renderer, self-hosted artifact, and automated checks pass. Visual acceptance remains separate unless a real screenshot can be captured from the allowed browser surface.

## Observed result

- The default conclusion starts with the concrete repaired outcome. “变化识别规则” appears only as the secondary `涉及内部` label.
- The first screen now contains one plain-language explanation and three compact owner answers: current software impact, residual risk, and the next action. Each state label opens its meaning, including the explicit rule that “目前没发现” is not proof of absence.
- The complete five questions remain source-bound but are collapsed under “查看完整说明”. Audience impacts use a scan-friendly three-column layout and owner checks render as unchecked items; no completion state is stored or implied.
- The default software map contains exactly four source-declared owner steps. Those four steps cover all eight detailed nodes exactly once. Clicking one switches the same graph to its mapped detail and preserves the current-change focus; “返回四步总览” reverses the interaction.
- The self-hosted artifact regenerated at `artifacts/change-passport-self-688fc5f/review.html` with control identity `979031ea971f7dc2dab79cd2d2f60b443eba455170cd2d6e4be4dbfee4bfaf22`.

## Verification

- `uv run pytest -q`: 60 passed.
- `uv run python -m compileall -q src tests`: exit 0.
- `node --check src/change_passport/templates/review.js`: exit 0.
- PowerShell `Test-Json` validates the source control document against `software-control.v1.schema.json`; the optional Python `jsonschema` package is not installed and was not added for this task.
- Generated HTML parses successfully, contains the result-first headline, overview/detail controls, collapsed complete explanation, and state explanations. It has no external script, stylesheet, `fetch`, or XHR dependency.
- Canonical control identity, evaluation-manifest file hashes, and generated `software-control.json` identity match.
- `git diff --check`: exit 0 with existing LF-to-CRLF notices only.
- Real screenshot review remains pending because the selected in-app browser blocks interaction with the local `file://` report. The restriction was not bypassed, and no visual score or human comprehension pass is claimed.
