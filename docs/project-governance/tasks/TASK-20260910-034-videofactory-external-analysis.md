# TASK-20260910-034: VideoFactory external analysis

State: DONE
Tier: standard

## Trigger and authority

The owner asked Change Passport to try parsing VideoFactory. This authorizes one read-only, deterministic external-project analysis and local report generation without a model call.

## Source facts

- Target repository: `D:\Dev\Projects\VideoFactory`.
- Fixed committed range: `58d214911574c4e00629c1463f0a3b35f649560f..d6594e3e51e5b3449445c31200575a1741d7ba52`.
- The target working tree already contains many modified and untracked files. They are outside the fixed range and must remain untouched.
- The target README describes a configuration-driven headless local video-production CLI, but no VideoFactory-specific Change Passport target profile exists.

## Goal

Generate a source-bound owner report and interactive architecture view for the latest committed VideoFactory change using the unchanged automatic profile and deterministic explanation path.

## Scope

1. Create an ignored sample manifest with the exact repository/base/head identities and the owner's request as task evidence.
2. Run deterministic `change-passport analyze`; allow only Change Passport artifacts/cache writes.
3. Inspect the generated project purpose, four-step working map, changed-area placement, static coverage, timings, and unknowns.
4. Verify the complete target Git status hash is unchanged.

## Non-goals

- No model call, custom target profile, VideoFactory source/config write, runtime execution, render, test execution, baseline approval, commit, push, or deployment.
- No claim that static imports describe render order or that the committed change is the current dirty working tree.

## Risks and stop conditions

- Stop if analysis needs to write inside VideoFactory or execute its pipeline.
- Keep auto-generated semantics labelled as candidates; report unclassified modules and rejected source files rather than hiding them.
- Preserve the target's pre-existing dirty state exactly.

## Verification plan

- Compare target status hashes before/after.
- Validate run receipt, packet/snapshot binding, report existence, generator metadata, module/group coverage, and owner-map structure.
- Run offline-resource and HTML parse checks on the generated report.

## Handoff condition

Complete when the deterministic report is generated and its useful conclusions, misleading abstractions, evidence limits, and target-preservation result are reported separately.

## Observed result

- `change-passport analyze` completed in 0.806 seconds with no model call. Git-object preflight found the fixed range complete; the static pass parsed 85 base and 87 head modules, produced 158 static relations, reused 78 cached parses, and reported no parse failure or unclassified node.
- The generated report is a self-contained 298,829-byte HTML artifact with no external script or stylesheet dependency. Its sole `http://` text is the SVG namespace used by `createElementNS`, not a network resource.
- The committed change added `video_factory.render.grade` and `tests.test_grade`, modified seven modules, and exposed 27 one-hop static impact paths. The evidence correctly preserves the fixed Git identity and does not claim runtime behavior.
- The owner-facing result fails the beginner comprehension goal. It describes VideoFactory only as software that other programs can call and reduces its work to the generic sequence `调用或输入进入软件 -> 检查并整理输入 -> 执行主要功能 -> 返回结果或状态`, despite the target README declaring a concrete video-production pipeline.
- The generated module areas all reuse `src/video_factory/` as a path prefix. First-match grouping therefore puts 72 of 87 modules into `调用与用户入口`, while `主要功能` receives one module. The report consequently cannot show where video planning, design, speech, timeline, rendering, QA, and delivery sit in the system.
- The target's complete `git status --porcelain=v1 -z` SHA-256 remains `C1B1230B1902F3220E463F7AC0EDED95D867EF9B5D0FB061D9D21E8963A3B4BA`, exactly matching the pre-analysis receipt. No VideoFactory file or working-tree state changed.

## Verification

- Run receipt: `succeeded`; all seven stages succeeded.
- Snapshot coverage: 87/87 supported files parsed, 87 nodes assigned once, 158 edges, 4 non-empty groups, 0 unclassified.
- Change set: 2 added nodes, 7 modified nodes, 0 removed nodes, 27 bounded static impact paths.
- Owner draft validation: 4 claims accepted, 0 downgraded, 0 rejected; this validates evidence conformance, not usefulness or human comprehension.
- Report parse/resource check: valid document shell, zero external script/link dependencies, 298,829 bytes.
- Target preservation: exact pre/post status hash match.

## Decision and follow-up

The parser is fast and source-bound, but this automatic result is not acceptable as a beginner-facing explanation. Record the cross-project failure as `BUG-20260910-017`: automatic profile generation must create mutually discriminating module areas and must use explicit project-declared workflow material before falling back to a generic four-step callability template. Do not fix it with a VideoFactory-specific profile or wording exception.
