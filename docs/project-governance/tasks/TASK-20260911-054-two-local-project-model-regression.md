# TASK-20260911-054: Two local-project model regression

State: DONE
Tier: high-risk

## Trigger and authorization

The owner requested two more locally owned projects and explicitly delegated
selection. This bounded regression applies the already-approved model-first
owner-language path to two structurally different fixed Git ranges: the public
memory-language/runtime project `memdsl` and the configuration-driven local
video-production CLI `VideoFactory`.

This authorizes analysis and new artifacts only. It does not authorize writes
to either target, reading uncommitted target content, credential storage,
provider/model changes, committing, pushing, publishing, deployment, or any
change to either target project.

## Fixed inputs

| Target | Fixed range | Why selected |
| --- | --- | --- |
| `memdsl` | `f49bc0f9a398d25c39043aba8d77647b34e3243a..a061bc4efb9a0dacab04c2fa847bcf4b236146b4` | Public package/protocol and MCP Registry distribution change; clean worktree. |
| `VideoFactory` | `58d214911574c4e00629c1463f0a3b35f649560f..d6594e3e51e5b3449445c31200575a1741d7ba52` | Content-production pipeline change covering render freshness and QA behavior; existing dirty worktree is out of scope. |

## Success criteria

1. Each report has a short result-first title, a two-to-six-item business map,
   and explicit runtime/user-impact boundaries.
2. Descriptions fit each project's source role rather than treating both as a
   generic web application or framework.
3. Any failure, downgrade, or semantic ambiguity remains visible; no
   target-specific vocabulary/routing rule is introduced.
4. Target HEAD and dirty-state count remain unchanged before and after runs.

## Verification and stop conditions

1. Record each target identity and dirty-state count before running.
2. Run the existing environment-only compatible model configuration into two
   new PlainChange artifact directories.
3. Inspect validated semantic output, first-screen control document, model
   receipts, source-bound workflow/capability map, and target preservation.
4. Run focused model/pipeline tests if a generic defect is exposed; stop before
   any unapproved model/provider retry or target mutation.

## Observed result

Both runs completed against their fixed ranges without target writes or
credential-shaped output. `memdsl` completed in 26.122 seconds: project
understanding 10.410 seconds / 32,400 reported tokens and change
interpretation 12.848 seconds / 13,562 reported tokens. It produced a
six-item non-sequential capability map and the result-first headline
`补充 MCP Registry 发布配置并更新发行文档`; two claims were accepted and four
were safely downgraded. Its source-bound role candidates identify release
administrators and callers only as possible impact.

`VideoFactory` completed in 20.705 seconds: project understanding 8.269
seconds / 16,199 reported tokens and change interpretation 10.060 seconds /
14,984 reported tokens. It produced a six-step production workflow and the
headline `过期渲染会触发失败并阻断质检构建`; five claims were accepted and one
was downgraded. It correctly preserves uncertainty about real triggers,
retries and external automation.

The memdsl artifact also exposes BUG-20260911-049: a first-screen card can
retain an `已确认` state label while validation has replaced its body with a
safe unknown explanation. This is recorded rather than hidden or repaired
for a target. Both target HEADs and their pre-run dirty-state counts remained
unchanged (`memdsl`: 0; `VideoFactory`: 46).
