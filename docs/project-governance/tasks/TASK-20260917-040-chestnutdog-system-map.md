# TASK-20260917-040: Try system understanding on ChestnutDogAiThink

State: DONE (generated and inspected; owner acceptance pending)
Tier: micro validation and bounded correctness fix

## Request and scope

Owner: “用chestnutdogaithink这个项目看看”. Reuse the authorized local Codex
provider to produce a real map from an existing project. Target remains read-only;
no project execution, business API calls, commits, deployment or release freeze.
Existing PlainChange modifications from TASK-039 were preserved.

Target: `D:\Dev\Archive\OldLaptop-20260622\work\E-myProject\ChestnutDogAiThink`.
Analyzed commit: `0883fe0676f0148139afc82e92101d732d75ed3b`, dated 2026-06-18.
The working tree had 22 modified, 824 deleted and 7 untracked status entries; these
are excluded. Binary porcelain status captured before and after matched exactly.

## Result

- Four actual Codex requests succeeded, 535.53 seconds total provider time.
- 13 of 517 eligible files read, 24 excerpts, 146,703 source-text bytes.
- 6 flows / 42 nodes / 45 edges and pending test scenarios: request/session entry;
  intent/validation/decision; Task/Skill/output; confirmation/recovery;
  Agent/query orchestration; failure/SSE return.
- Every excerpt's path/blob/line content and SHA-256 checked against the exact Git
  commit, not merely the supplied packet. References and graph consistency pass.
- Model-authored busy-request and dependency-ready branches were spot-checked
  against code. Whole-map semantic entailment and branch completeness are not proven.
- Browser: all six flows render at 1440/390 px; node/edge selection, code disclosure,
  test navigation, and entry switching pass; no page overflow, JS exceptions,
  label/label or label/node collisions. Desktop screenshot inspected.

Artifacts: `D:\Dev\Projects\plainchange-reports\ChestnutDogAiThink-system-20260917`.
Local validation: `artifacts/chestnutdog-validation/checks.json` and nested
`artifacts/system-flow-browser/`. These artifacts contain source excerpts and are
not committed. Target source files and unrelated local changes were untouched.

## Exposed defect and bounded fix

Initial flow validation rejected five references to decision.py ending at line 162
under the excerpt ID for lines 1–160. Lines 161–162 were already in the next supplied
excerpt of the same file/blob. No missing code needed acquisition.

`system_flow.py` now splits only fully covered ranges across same-path, same-blob,
same-kind excerpts, preserves the untrusted raw object, and records the original and
normalized references. Gaps, unknown IDs and other-version substitutions still fail.
Added a regression covering contiguous references, gaps, blob mismatch and input
preservation. Focused flow/provider suite: 19 passed. `git diff --check` passes.

Re-finalized saved raw output locally without another model request. Original
`run-receipt.json` remains failed; `finalization-receipt.json` records successful
normalization, five corrections, output hash and zero additional model calls.

## Material limits

The map describes the June 18 commit, not the current uncommitted worktree. parse.py
and ChatView.vue exceed the current whole-file size gate and were excluded, leaving
intent-recognition and UI internals incomplete. Other unread orchestration/verification
implementations are listed as unknown. This is a bounded core-flow sample, not a
complete project map. No generated branch tests or target application were executed.
`ds` was not available on PATH; no DigitalSelf receipt CLI submission was possible.
