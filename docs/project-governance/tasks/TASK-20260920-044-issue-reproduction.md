# TASK-20260920-044: Reproduce selected product-review findings

State: DONE (authorized automated verification scope)
Tier: standard

## Authorization and bounded plan

Owner requested “你去验证一下” after the proposed next step: isolated reproduction
of memdsl query byte budget, VideoFactory stale audio reuse and standalone render
to QA handoff, plus ordinary-reader validation and retained evidence.

Use the exact analyzed commits (memdsl a061bc4e, VideoFactory d6594e3e) exported
under PlainChange ignored artifacts. Originals, real memories, production media
and credentials remain untouched. Synthetic fixtures only, no paid model calls,
no publication. Existing uncommitted TASK-043 changes are preserved.

For each finding retain inputs, commands, outputs and code identity; distinguish
reproduced behavior, disproved hypothesis and unresolved integration effects.
Try actual public services/CLI and actual local rendering when supported by the
installed dependencies; mocks cannot establish a real end-to-end result.
Publish the results as local verification artifacts linked to original findings;
do not silently edit prior model output or auto-fix the target projects.

Actual independent reader comprehension requires a participant. Requested their
availability asynchronously; continue technical verification without fabricating
participant responses. Agent/browser checks have a separate evidence label.

## Results

User deferred independent reader testing: “暂时没有，先完成可自动验证的部分”.

All three selected hypotheses reproduced against exact exported commits using
synthetic fixtures: memdsl R3 via actual MCP stdio (19,096 bytes under a 2,048
byte budget in report mode); VideoFactory F1 via actual synthesize CLI (same-path
locked audio replacement reused previous output); VideoFactory F4 via real
FFmpeg render followed by QA (missing signatures caused StaleRenderError).
Positive controls passed: quarantine budget response, forced audio regeneration,
and complete build with 10/10 QA acceptance.

Three existing reports passed real Edge interaction checks at 1440/390 widths,
including reader-guide evidence, issue cards and navigation. This does not prove
comprehension. Original Git HEAD/status/tracked diff fingerprints are unchanged;
snapshot file bytes still match archives. No target code changes or model calls.

See TASK-044-verification-results.md for results, commands, limitations and
retained harness failures. Machine-readable receipts and full runtime artifacts
are under artifacts/issue-verification-20260920; a results sidecar is linked from
the local product-evaluation index. Original model reports remain unchanged.
The ds closeout command is unavailable. No commit/push/publication performed.
