# TASK-20260916-039: Model-assisted system flow map

State: DONE (local implementation and verification; owner acceptance pending)
Tier: standard

## Authorization and outcome

The owner requested a repeatable, detailed explanation of a system: real steps,
conditions, alternative outcomes, implementation references and missing tests,
for version review and interview preparation. The owner explicitly approved the
proposed model-assisted implementation with “好，直接在这个基础上做吧” and
specified an additive feature with existing features retained; no release freeze.
This is authorization for this local implementation and verification, not a new
release, push, target changes, or an unspecified paid provider run.

## Baseline and approved implementation scope

Clean worktree before changes. Existing `analyze`/guided comparison and compatible
model config are reusable. The model currently only writes change briefs. Dev
dependencies were missing; restored with `uv sync --extra dev` before baseline tests.

1. Add `understand` and a guided “理解系统” mode, using one immutable commit
   (default HEAD), without selecting or freezing a release or changing the target.
2. Build a bounded source inventory; let the model select and follow source
   excerpts across files. Preserve exact commit/blob/line identities, actual read
   coverage, omitted inputs and request receipts. No target commands are executed.
3. Validate model-authored flows, branches and citations; all semantic relations
   remain model interpretations, not deterministic runtime facts. No design intent
   or test completion may be invented. Produce branch-linked pending test cases.
4. Render a standalone offline interactive flow map with node details, branch
   conditions, source excerpts, coverage and a project explanation for interviews.
5. Verify with adversarial source/response fixtures, local mock HTTP end-to-end,
   existing tests and browser interaction. Real provider quality is a separate check
   pending the owner's provider choice; never label a mock run as real generation.

## Design and implementation basis

Read `E:\AI\Prompts\AI_PRODUCT_PHILOSOPHY.md` in full. System chooses source
matches; user supplies a project and optional focus, reviews results and corrects
them. Reuse the current local guided page and visual language. This is an existing
project feature, not a project bootstrap or a Figma redesign. Existing evidence
domains and model-provider boundaries remain in effect for old reports. New model
flow edges are in a separate artifact and never overwrite static architecture.

## Verification

Baseline: 90 existing tests pass. New tests cover cross-file exploration, one-commit
projects, dirty-worktree exclusion, output preservation, exact citation bounds,
unknown graph targets, disconnected graphs, decision alternatives, HTML escaping,
HTTP jobs, provider failure, completion events, and timeout uncertainty.

Owner subsequently selected “直接调用codex的能力”. Default provider is therefore
the signed-in local Codex CLI; compatible API remains an explicit alternative.
Read `codex-local-bridge/SKILL.md` and integration contract; verified ChatGPT login
without reading tokens. Text adapter is adapted into the distributable package,
using an isolated directory, read-only sandbox, shell/web/image tools disabled,
schema output, event completion validation and durable request/attempt receipts.
CLI implementation guidance checked against
https://learn.chatgpt.com/docs/non-interactive-mode on 2026-09-16.

## Observed result

- Full suite: 108 passed (90 baseline + 18 added). Focused provider/flow tests rerun
  after final schema/error-handling adjustments. Python compilation, JS syntax and
  `git diff --check` pass.
- Real Codex run on existing commit `c54fc7f2fcfccf987adb357dc1a917fa6caa981b`:
  4 completed CLI requests, 614.47 s total, 176,556 reported input+output tokens.
  These are subscription usage counters, not an estimated API invoice. No exact
  backend model identity is claimed beyond `codex-session-default`.
- 14 / 46 eligible files, 24 excerpts, 136,520 bytes read; 5 flows, 43 nodes,
  55 conditional/sequential edges and corresponding pending test scenarios.
- Artifacts: `D:\Dev\Projects\plainchange-reports\PlainChange-system-c54fc7f2-93d91ddc`.
  Original source packet, untrusted output and all Codex request/event/receipt files
  are preserved. HTML was re-rendered after layout refinement without another model
  request or altering the model document. The raw model output also passes the final
  current contract.
- Manual semantic spot-check: version strings and parsed commit equality, output
  directory ownership, and corresponding failure responses agree with cited excerpts.
  This is a spot-check, not independent verification of all 55 connections.
- Browser verification: all 5 flows render; node and branch selection, code expansion,
  test navigation and old/new entry switching pass at 1440 and 390 px. No JS errors,
  page overflow, label/label overlap or label/node overlap in either viewport.
  Screenshots inspected at `artifacts/system-flow-browser/`.
- Visual QA initially exposed overlapping long condition labels and BFS placing
  shared failure/join nodes before later callers. Changed ranking to longest paths
  after cycle-edge separation, used outside lanes for non-adjacent connections and
  collision-aware condition labels. References and graph topology are unchanged.

## Limits and handoff

This first real run takes about 10 minutes. Scope remains bounded; schema-valid
citations are not proof of semantic entailment or exhaustive branch coverage. The
diagram describes the existing commit, not uncommitted feature code. No branch test
cases were executed, no human acceptance recorded, no release freeze/commit/push.
The target's existing files were not rewritten by analysis. Implementation added
only this feature and its documentation/tests; no unrelated changes existed at start.
`ds` was not found on PATH, so no DigitalSelf completion CLI was available.
