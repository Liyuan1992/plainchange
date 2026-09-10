# TASK-20260909-026: vLLM complex-project validation

State: VERIFIED — OWNER VISUAL REVIEW PENDING
Tier: standard

## Trigger and authority

After accepting the ten-second/four-step self-hosted result as broadly usable, the owner asked to switch to a more complex project and inspect the effect. This explicitly authorizes one bounded public cross-project sample without another approval round.

## Facts and selected sample

- Target: public `vllm-project/vllm` from the existing local read-only bare mirror.
- Mirror snapshot: 2026-09-04; this task does not claim it is the live online latest revision.
- Repository scale at the selected Head: 6,929 tracked files and 290,868 commits reachable across the mirror.
- Immutable range: `a69e75b9b6d6a26d90b6790e2eb75b3419a47c16..a85d0738da311ce4ad5814787e61a12826e232df`.
- Selected change: `[Bugfix] Fix double BOS in LLM.chat() for multimodal models (#55288)`; two files changed in the commit.
- A local shared/no-checkout clone may be created under `D:\Dev\Repos` only to provide a normal non-bare Git target. After creation it remains read-only to Change Passport.

## Goal

Generate the same generic owner-facing report for a substantially larger open-source project, showing both a simple four-step software mental model and a source-bound location for one narrowly scoped change.

## Approved plan

1. Create a minimal local shared/no-checkout clone from the existing vLLM mirror; do not fetch, checkout, run, or modify vLLM.
2. Add a versioned vLLM target profile that groups supported source paths and declares an owner-language workflow without changing renderer logic.
3. Prepare the immutable range and inspect the generated Git/static evidence.
4. Write a source-bound software-control sample and constrained raw brief from the selected commit, README, prepared evidence IDs, and explicit unknowns.
5. Finalize the report, validate contract/identity/fallback boundaries, run the project test suite, and open the generated HTML for owner review.

## Non-goals

- No vLLM installation, model download, GPU execution, test execution, checkout, commit, push, or modification.
- No online-latest claim and no runtime/user-impact claim from static imports.
- No vLLM-, model-, path-, or node-specific branch in the Change Passport renderer.
- No automatic model/provider generation and no product release.

## Risks and stop conditions

- Stop if the prepared evidence cannot resolve the immutable range from the local mirror-backed clone.
- Stop if a changed workflow node cannot be bound to actual prepared claim/evidence IDs.
- Stop if the report hides unsupported files, upgrades static relations to runtime behavior, or requires a renderer special case.
- Record rather than bypass the existing local-file browser limitation.

## Verification plan

- Confirm target identity before and after analysis and prove no worktree/index mutation.
- Validate profile schema/group assignment, software-control schema/canonical identity, four-step exact coverage, and changed-node source binding.
- Run finalize, HTML parse/offline checks, project tests, Python compilation, JavaScript syntax, generic-renderer scan, and diff check.
- Open the generated report in the app when possible; visual acceptance remains the owner's decision.

## Handoff condition

Complete when a reproducible vLLM artifact exists and automated/source-bound checks pass. Do not claim runtime correctness or human comprehension.

## Observed result

- Used the fixed public range `a69e75b9b6d6a26d90b6790e2eb75b3419a47c16..a85d0738da311ce4ad5814787e61a12826e232df`; the selected commit changes two tracked files with 140 additions and 3 deletions.
- Added `examples/target-profiles/vllm.v1.json`. The generic profile produces 9 implementation groups over 4,501 supported modules and 21,091 static relationships, with 0 unclassified supported modules.
- Added the source-bound `docs/product/samples/vllm-a69e75b-to-a85d073.software-control.json`. Its four-step owner map covers all eight detailed workflow steps exactly once and highlights only “准备模型输入”.
- Generated `artifacts/vllm-a69e75b-to-a85d073/review.html`. The report embeds no remote script, stylesheet, fetch call, or XMLHttpRequest, and the renderer/test source contains no vLLM repository, revision, or sample-specific branch.
- The target no-checkout worktree/index fingerprint remained `2F1F2AE2F11E34AB47C59032B71BC57F667C77B820282A80D9F18A09F922C908` before and after analysis. Its 6,976 deleted-status entries are the unchanged consequence of creating a no-checkout clone, not analyzer writes.

## Verification evidence

- `prepare`: success after explicitly materializing the selected immutable tree; 4,501 parsed modules, 21,091 static edges, 9 groups, 52 cross-group edges, 0 unclassified.
- `finalize --software-control`: success; 4 claims accepted, 1 missing-runtime claim safely downgraded, 0 rejected.
- PowerShell JSON Schema validation: pass.
- Software-control canonical identity and source-binding validation: pass; identity `e8f05d53d106063b37463de16ba4864738fc8e659f097c9a879753240ab508e9`.
- HTML parse/embedded-identity/offline-resource assertions: pass; 4 overview nodes, 8 detail nodes, exactly 1 changed overview node.
- `uv run pytest -q`: 60 tests passed.
- `uv run python -m compileall -q src tests`, `node --check src/change_passport/templates/review.js`, and `git diff --check`: pass; only existing Git line-ending warnings were emitted.

## Remaining limits and discovered gaps

- No vLLM runtime, model, GPU, or test execution was performed. The report explains a source-supported change and an owner-declared software workflow; it does not prove runtime behavior or user impact.
- The first `prepare` attempt against a partial clone spent more than ten minutes fetching blobs without useful progress output. After an explicit immutable-tree prefetch, the same prepare completed in about 11.4 seconds. This generic large-repository experience gap is recorded as `BUG-20260909-006`.
- `review.html` is 12,924,883 bytes because `system-architecture.json` is 12,657,291 bytes and is embedded in full. This generic scale gap is recorded as `BUG-20260909-007`.
- The current in-app browser's local-file limitation prevents automated screenshot/interaction acceptance. Opening the generated report for owner review does not convert it into a human comprehension pass.
- An earlier incomplete clone remains at `D:\Dev\Repos\vllm-change-passport-a85d073`; safe recursive cleanup was blocked by the host policy and was not bypassed. The completed sample source is `D:\Dev\Repos\vllm-change-passport-a85d073-online`.
