# TASK-20260911-047: Change-tab technical localization

State: DONE
Tier: standard

## Trigger and authorization

The owner opened the English FastAPI report and showed that the first tab's
expanded `Why this conclusion? View technical details` section still contains
substantial Chinese text. The previously authorized localization completion
scope applies; this task corrects the generic reader and validation gap without
adding FastAPI-specific wording or rules.

## Facts and root-cause hypothesis

- The prior browser harness scanned the change tab before opening its technical
  disclosure, then opened only the system tab's implementation disclosure.
- The screenshot contains mixed-language PlainChange-generated summary cards,
  relationship nodes and inspector explanations. FastAPI source and the test task
  are English, so these visible Chinese strings are not project-source content.
- Existing generated review presentation covers only a bounded architecture
  subset; the legacy change-summary and relationship projection require complete
  identity-bound coverage.

## Plan

1. Make the real-browser test open the change-tab technical disclosure before
   scanning visible English text and preserve the failing result.
2. Inventory every PlainChange-owned dynamic text path used by that section and
   extend the generic identity-bound review presentation; do not translate IDs,
   evidence, paths, quotations or canonical truth state.
3. Add unit regressions for coverage, source-data preservation and wording
   mutation, regenerate the same FastAPI artifact, and require zero visible Han
   text in both English tabs (except the native language-selector label).
4. Run the full suite, syntax/compile/diff checks, and verify the external bare
   repository's fixed objects remain unchanged.

## Non-goals

- No FastAPI-specific phrase table, target profile, repository mutation, model
  call, runtime execution, commit, push or release.
- No translation of genuine project-authored or quoted source text.

## Observed result

- The strengthened browser harness reproduced the defect before the fix. After
  opening the first tab's technical disclosure it found PlainChange-owned
  Chinese summary headings, status labels, impact text, relationship labels and
  node-inspector explanations that the previous default-state scan never saw.
- Automatic review presentation now covers the change summary, task-context
  state, relationship views, node details, branch explanations and known
  deterministic claims using stable IDs, counts and states. Project-authored
  text, quoted task content, paths, evidence and canonical truth state remain
  unchanged.
- Node details now carry explicit `before_state` and `after_state` values so
  missing responsibility text is localized from semantic state instead of
  matching a Chinese fallback sentence.
- The real-browser acceptance path now opens technical details, expands task
  context, cycles Before/After/Changes only, clicks every unique visible node,
  opens the system technical view and merges visible-language findings across
  those states.
- The regenerated FastAPI report completed in 1.301 seconds with 2,242 cache
  hits. The enhanced Edge scan returns zero visible Han-bearing lines in both
  English tabs, excluding only the intentional native selector label `中文`.
- All 115 tests pass. Python compilation, JavaScript syntax checks for the two
  report scripts and browser harness, and `git diff --check` pass; only existing
  line-ending conversion warnings were emitted.
- The read-only FastAPI bare repository still points to
  `https://github.com/fastapi/fastapi.git`; both fixed commits remain commit
  objects with tree IDs `90fc2eb8836de44e75fd4a24c83f4cd07c000070`
  and `7ae7f0210a0468dbefcc8fb1889f1b634c940aff`. Its object store contains
  48,346 packed objects and no loose or garbage objects.

## Stop and handoff

The mixed-language disclosure and validation blind spot are fixed generically.
The separate automatic project-name defect remains BUG-20260911-037; no
FastAPI-specific profile, translation or name override was introduced.
