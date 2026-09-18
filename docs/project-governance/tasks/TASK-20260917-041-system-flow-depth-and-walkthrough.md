# TASK-20260917-041: Connected system maps and scenario walkthrough

State: DONE (implemented and verified locally; owner acceptance pending)
Tier: standard

## Approval and scope
Owner accepted the preceding review and requested implementation: “好，你把这个功能补上”. Implement the three proposed priorities: function-guided source exploration, evidence-backed connections between subflows, and interactive scenario walkthrough. Preserve Change Passport and prior reports. Target project remains read-only; no target execution or external business API calls.

## Baseline and plan
Existing flow/provider suite: 19 passed. Prior changes are uncommitted and preserved.
- Raise bounded file gate to 2 MB; return function location indexes with excerpts; increase exploration to six rounds within a 400 KB source budget.
- Add explicit cross-flow node connections with citations and current-call/return/next-request types. Validate IDs and citation ranges. Keep legacy reports readable.
- Render a navigable overview and let readers select conditions, traverse branches, backtrack, and enter linked subflows. Walkthrough remains unexecuted reasoning, not runtime proof.
- Validate large-file retrieval, cross-flow validation, legacy behavior, and UI journey; regenerate the ChestnutDogAiThink sample with local Codex.

## Remaining scope boundaries
Commit-only analysis remains explicit. Automatic test execution, worktree snapshots, arbitrary chat follow-ups and persistent generation resume are outside this increment.

## Observed verification and real sample
- Initial full suite: 111 passed. After adding bounded reference-repair regression: 22 focused flow/provider tests passed; final full-suite result recorded below.
- Real ChestnutDogAiThink Codex run: 8 successful provider requests including one bounded reference-only repair, 461.57 seconds provider time. Six exploration requests (last returned no further reads), one map, one repair.
- 10 files / 40 excerpts / 253,376 source-text bytes; parse.py and ChatView.vue now included and their deep functions actually read. Function indexes are de-duplicated for subsequent generation requests.
- Final map: 4 flows, 28 nodes, 41 edges, 8 cross-flow connections, including three next-request boundaries. Target commit remains 0883fe0676f0148139afc82e92101d732d75ed3b (June 18).
- Every excerpt rechecked against Git path/blob/line/hash. Target porcelain status exactly matches prior preserved baseline. No target execution or business API calls.
- Real Edge checks at 1440/390: all maps, code disclosure, overview navigation, cross-flow destination, scenario advance/backtrack and visited path highlighting pass; zero page overflow, label collisions or browser exceptions. Final desktop screenshot inspected.
- The raw model map contained one reversed reference range (2949..101). One model correction changed only that item's references; original raw output and failed run receipt retained with separate successful finalization receipt. The product now performs this bounded repair automatically, once, and rejects missing evidence or further errors. Two contiguous ranges were normalized from already-supplied code.
- Report: D:/Dev/Projects/plainchange-reports/ChestnutDogAiThink-system-v2-20260917. Checks: artifacts/flow-v2-validation/checks.json and artifacts/system-flow-browser/checks.json under the same validation folder.
- Browser connector unavailable; repository-owned isolated Edge regression harness used. Local report endpoint verified HTTP 200. App open request returned queued, not confirmed-visible.
- `ds` unavailable. Prior uncommitted changes preserved; no commit/push/release.

Whole-map semantic entailment, complete branch coverage, target runtime tests and owner comprehension remain unverified. The sample reports unread lock-release/query-scheduler/card handling paths rather than inventing them.

## Regression discovered during final validation
The final pre-closeout suite returned 111 passed / 1 failed in the existing guided-report test. Its persisted receipt shows WinError 5 replacing run-receipt.json during HTTP polling; the isolated test immediately passed. Added a bounded Windows sharing/access-denied replacement retry used by both old progress and new model receipts, with three fault-injection cases. Persistent/non-Windows failures remain errors. This preserves the requested old-function compatibility rather than suppressing the test.

Final verification: `.venv/Scripts/python -m pytest` passed all 115 tests in 127.78 s after the Windows retry fix. Real-report browser checks additionally confirm next-request traversal and backtracking at 1440/390 px. JavaScript syntax, compileall, and git diff --check pass.
