# TASK-20260910-037: Restore behavior-semantic coverage in the owner report

State: DONE
Tier: standard

## Trigger and authority

The owner asked Codex to optimize the product after a source-level review of the
VideoFactory blind-spot list and explicitly delegated the implementation through
“我信你，你来优化一下”. This authorizes local implementation, regression
artifacts, and verification. It does not authorize a commit, push, deployment,
real model request, target-repository write, baseline approval, or automatic
execution of suggested checks.

## Source facts

- The fixed VideoFactory range `58d2149..d6594e3` added a stale-render exception
  branch in `run_qa()` and a non-zero early return in `build_all()`.
- The current generator packet already contains the full patch, ADR path/content,
  YAML change, architecture nodes, `video_factory.cli`, `cmd_qa`, `cmd_build`, and
  `StaleRenderError` evidence.
- The analyzed report used `provider=deterministic-local`, `model=none`. Its owner
  draft reduced the change to file counts and a workflow location, while labeling
  user impact as `目前没发现`.
- `video_factory.qa.report` is one of the 14 displayed changed nodes. The display
  budget already retains every changed node, so the confirmed failure is not a
  folded-node or missing-CLI defect.
- Static code can confirm that a new stop/failure branch exists, but cannot prove
  that a real user or deployed integration encountered it.

## Goal

Make the deterministic fallback honestly useful: surface conservative code-level
behavior risk signals, distinguish “semantic interpretation not run” from “searched
and found no impact”, and give an owner a bounded two-case check without inventing
runtime or user-impact claims.

## Approved implementation plan

1. Add a generic unified-diff behavior-signal extractor for newly added exception
   raises, explicit non-zero returns, and callable signature changes. Signals remain
   Git facts, include source path/symbol/condition when available, and never claim
   runtime execution or user impact.
2. Add the extracted signals to the frozen generator packet as separately identified
   evidence so both deterministic and configured-model generation see the same input.
3. Let the deterministic raw brief prefer a concise behavior-risk claim over file
   count when signals exist, while retaining the file summary as secondary evidence.
4. In the owner projection, expose generator coverage. When `model=none`, say that
   behavior/user-impact interpretation has not been completed; do not label it
   `目前没发现`.
5. Replace the generic “run one important path” with a source-bound two-case owner
   check: verify the mapped workflow step once normally and once under the new
   stop/failure condition. Keep the action as recommended and unexecuted.
6. Surface changed unsupported text/config paths as “collected but not structurally
   parsed”, prioritizing ADR/decision/migration/changelog paths without treating their
   prose as verified truth.
7. Add a known-answer regression for the VideoFactory-shaped case and generic
   negative/conditional fixtures. No target-name, repository-name, or VideoFactory-only
   code branch is allowed.

## Non-goals

- No general Python call graph, runtime tracing, framework-specific route parser,
  automatic model invocation, provider settings UI, or automatic test execution.
- No rule that every `raise` or non-zero return is a breaking change.
- No inference that an ADR, README, filename, or commit message is true without code
  reconciliation.
- No visual redesign beyond the copy/state needed to expose semantic coverage.

## Risks and fail-closed rules

- A syntactic signal can be intentional or unreachable. Present it as “代码中新增了
  停止/失败分支”, not “软件已经坏了”.
- Truncated patches provide incomplete coverage and must state that limitation.
- If no unique workflow step is source-mapped, give a generic two-case check and do
  not guess a location.
- Existing model-generated claims remain validator-controlled; deterministic signals
  cannot upgrade user behavior or runtime truth.

## Verification plan

- Unit tests for raise, non-zero return, signature change, deleted/context-line
  exclusion, condition capture, patch truncation, and evidence identity.
- Pipeline tests asserting deterministic `model=none` reports say “还没判断” rather
  than “目前没发现”, include a behavior-risk conclusion when present, and retain
  source-bound recommended-not-run checks.
- Re-run the fixed VideoFactory analysis and assert `qa/report.py` remains displayed,
  the report describes conditional stop/failure branches without claiming observed
  user impact, and the target repository is unchanged.
- Full pytest, compileall, JavaScript syntax, JSON validation, `git diff --check`, and
  repository-name scan over implementation files.

## Rollback

The extractor and deterministic wording are downstream of immutable Git collection.
They can be removed without changing target repositories, baseline authority, model
provider configuration, or existing evidence identities outside the new signal items.

## Handoff condition

Complete when the generic known-answer fixture and fixed VideoFactory report both
surface the conditional behavior risk, the no-model path no longer masquerades as an
impact finding, all evidence boundaries remain intact, and automated verification
passes.

## Result

- Added a repository-neutral Python unified-diff signal extractor for newly added
  exception raises, explicit non-zero integer returns, and changed callable
  signatures. Each signal retains path, symbol, nearest conditional expression, and
  patch identity while explicitly denying reachability, runtime, breaking-change,
  and user-impact proof.
- Added those signals to the same validated generator packet used by deterministic
  and configured-model paths. The deterministic brief now gives a conditional
  stop/failure signal higher priority than a file-count summary.
- The owner projection now receives the packet evidence directly, maps the primary
  signal path only when one workflow step is supported, says `还没判断` when
  `model=none`, and recommends separate normal-path and stop/failure-path checks.
- Changed unsupported documentation/configuration remains visible as collected but
  structurally uninterpreted material. Decision/ADR, migration, changelog, and
  breaking-change paths receive display priority but no truth upgrade.
- Fixed a regression discovered by the real sample: a diff hunk without an added
  function definition could inherit the previous hunk's symbol. Hunk headers now
  reset context and supply their own function/class name when Git provides one.
- Regenerated the fixed VideoFactory report. It now locates the primary behavior
  signal at `检查视频质量`, describes conditional stop/failure branches, labels
  ordinary-user impact `还没判断`, and presents `确认正常情况` plus `确认停止条件`.

## Verification result

- 82 automated tests pass, including generic known-answer fixtures for raise,
  non-zero return, signature change, condition capture, truncation boundaries, hunk
  symbol isolation, packet inclusion, and end-to-end no-model owner wording.
- Python compilation, JavaScript syntax, and `git diff --check` pass. The only diff
  output is the repository's existing LF-to-CRLF warning set.
- The fixed VideoFactory analysis completes in 0.784 seconds on the recorded run with
  complete Git objects and 172 cache hits / 0 misses. The regenerated packet binds
  `run_qa` to `StaleRenderError` under `not render_is_fresh(unit)` and `build_all` to
  return `1` under `existing.is_file()`.
- `video_factory.qa.report` remains in the displayed architecture set; the report
  does not claim that the branches were reached, run, breaking, or user-visible.
- No VideoFactory repository-name or target-specific rule was added to the behavior
  extractor, packet builder, deterministic draft, or pipeline.
- The regenerated HTML contains the validated headline/state/action data and passes
  renderer tests. A fresh interactive browser observation was attempted twice, but
  the active Computer Use browser provider returned `nodeRepl.fetch request failed`;
  no new human visual-acceptance claim is made for this copy-only change.
- The target repository was read through fixed Git commits only. This task wrote no
  VideoFactory path and does not claim an exclusive dirty-worktree fingerprint while
  unrelated target work is active.
