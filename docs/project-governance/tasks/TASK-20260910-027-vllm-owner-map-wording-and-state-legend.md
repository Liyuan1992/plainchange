# TASK-20260910-027: vLLM owner-map wording and state legend

State: VERIFIED — OWNER VISUAL REVIEW PENDING
Tier: standard

## Trigger and authority

The owner reviewed the generated vLLM report, explicitly requested a bounded correction, and supplied four concrete acceptance points: treat entry methods as ways a request enters rather than a chronological CLI step; describe scheduling without implying dynamic model selection; make streaming output visible; and explain selected versus changed visual states. This authorizes the scoped implementation without another approval round.

## Facts and source basis

- The fixed vLLM quickstart separates Offline Batched Inference through the `LLM` class from Online Serving through an OpenAI-compatible server; `vllm serve` starts the server and is not itself an end-user request.
- The fixed vLLM V1 guide describes the scheduler, KV cache manager, worker, and token-budget scheduling policies. The owner-language map must not imply that the scheduler dynamically chooses a model.
- The fixed snapshot exposes `stream_interval` in scheduler/output configuration and output processing. Owner wording may say results can be returned while generation continues, without claiming every entry or call always streams.
- Current generic UI already distinguishes selection with a deep-blue/ink focus border and change with amber styling, but provides no nearby explanation.

## Goal

Make the vLLM owner map technically safer and easier for a beginner to interpret, while adding one lightweight generic legend for interactive owner maps.

## Approved plan

1. Revise only the vLLM target profile and source-bound software-control wording for entry, scheduling, and streaming output.
2. Add a generic two-item legend next to the owner map: deep-blue border means the currently viewed node; amber means the location changed in this AI change.
3. Recompute profile/control identities, rerun the fixed snapshot preparation because the profile hash is evidence-bound, and regenerate the report.
4. Add focused renderer assertions, run the full test/compile/JavaScript/diff suite, and confirm the target repository fingerprint remains unchanged.

## Non-goals

- No new workflow step, topology, architecture inference, vLLM-specific renderer branch, runtime tracing, model execution, or automatic profile generation.
- No performance/progress/compact-report implementation from `BUG-20260909-006` or `BUG-20260909-007` in this wording/legend task.
- No commit, push, deployment, baseline decision, or human-comprehension-pass claim.

## Risks and stop conditions

- Stop if the entry correction duplicates one entry type as a false chronological stage instead of clarifying the boundary.
- Stop if scheduling wording implies model choice, or if streaming wording implies that every result always streams.
- Stop if the legend relies on color alone or changes existing selected/changed semantics.
- Preserve the dirty worktree and all unrelated prior changes.

## Verification plan

- Validate fixed-snapshot source references, target profile parsing/hash binding, software-control Schema/canonical/source identity, four-to-eight exact coverage, and one changed-node binding.
- Assert both legend labels and non-color swatches are present in generic HTML/CSS; verify the fallback remains valid.
- Regenerate the vLLM artifact, run `uv run pytest -q`, compileall, JavaScript syntax, HTML/offline checks, renderer special-case scan, and `git diff --check`.
- Record browser visual/human acceptance separately from automated checks.

## Handoff condition

Complete when the bounded wording and generic legend appear in the regenerated source-bound report and automated checks pass. Stop before performance work or another product expansion.

## Observed result

- Replaced “接收调用方式” with “请求进入 vLLM” and removed the misleading command-line-as-request wording. Both overview and detail now say that requests can enter through a direct program call or an OpenAI-compatible interface.
- Replaced “安排模型和计算资源” with “安排请求和计算资源”. The owner explanation now describes request ordering, batching/cache management, and execution coordination, and explicitly says this is not dynamic model choice.
- Reframed output as “整理生成结果，可边生成边返回”. Overview, detail, result boundary, and flow labels now preserve both complete and streaming-return possibilities without saying every request streams.
- Added a generic, lightweight legend above every owner map: `深蓝边框 = 当前查看` and `橙色 = 本次改动`. A selected changed node keeps the deep-blue outer border while retaining its amber change stripe/background/badge.
- Reprepared and regenerated `artifacts/vllm-a69e75b-to-a85d073/review.html`. The target profile is now bound as `22f935b64d107a0cda146b58f0304353272664a342dd396031c342196e10b41a`; the control identity is `1a484c052e9680487f36696f6a5abbf7bf07971df9005914dd7ecfbfc12f53c5`.

## Verification evidence

- Fixed snapshot source check: quickstart separates Offline Batched Inference from Online Serving, `vllm serve` starts the server, the V1 guide identifies scheduler/KV-cache/worker responsibilities, and the fixed tree contains `stream_interval` in scheduler and output processing.
- Target profile parser: pass; 8 conceptual components.
- PowerShell JSON Schema plus software-control canonical/source binding: pass; 4 overview nodes cover 8 detail nodes exactly once and retain one changed step.
- Regenerated architecture remains 4,501 modules, 21,091 static relationships, 9 groups, and 0 unclassified modules.
- Exact new copy/legend presence, stale-copy absence, offline-resource scan, and vLLM-specific renderer/test scan: pass.
- Target worktree/index fingerprint remains `2F1F2AE2F11E34AB47C59032B71BC57F667C77B820282A80D9F18A09F922C908`.
- `uv run pytest -q`: 60 tests passed. `compileall`, JavaScript syntax, and `git diff --check` pass; only existing line-ending warnings were emitted.
- The refreshed analysis completed in about 10.9 seconds and finalization in under one second because the immutable objects were already local.

## Remaining limits

- Computer Use could not obtain the current in-app browser surface after one retry and a kernel reset (`nodeRepl.fetch request failed`). The generated HTML was reopened through Codex, but no visual screenshot acceptance is claimed.
- This task does not fix progress reporting, first-time partial-clone hydration, manual profile/control authoring, or the 12.9 MB report. Those remain separate open scale/product gaps.
- No vLLM runtime, model, test, commit, push, deployment, or human-comprehension test was performed.
