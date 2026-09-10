# TASK-20260905-012: Architecture story-map readability correction

State: DONE
Tier: standard

## Trigger and approval

After reviewing the generated self-hosted report, the owner found that the first concept map still obscures several workflow arrows and labels under cards. The owner asked to research alternatives, reviewed the recommendation for a responsibility-banded, numbered main path, and explicitly authorized a local experiment with “嗯，试试” on 2026-09-05.

## Goal

Replace the occluded free-form concept-map connectors with a beginner-readable architecture story: responsibility bands, one numbered left-to-right main path, short orthogonal input/approval branches, and a separate accessible relationship explanation.

## Scope

1. Keep the profile-sourced conceptual architecture data and its evidence boundary unchanged.
2. Render a desktop-only responsibility-banded workflow whose lines occupy dedicated gutters and never pass beneath cards.
3. Express the primary route with numbered stages and concise, plain-language labels; keep secondary relationships visible in a compact legend/list rather than on top of connectors.
4. Retain existing mapped-code drill-down and the complete static implementation layer.
5. Add targeted renderer/browser assertions and regenerate the isolated self-hosted artifact for desktop and narrow screenshots.

## Non-goals

- Do not change target-profile facts, Git/import extraction, baseline authority, or target-repository access.
- Do not imply that profile flow arrows prove runtime order, static imports, deployment, or user impact.
- Do not add a model provider, live integration, commit, remote, push, release, or baseline approval.

## Risks and stop conditions

- Stop if the new presentation needs repository-specific rendering branches or changes the profile contract only to accommodate the Change Passport sample.
- Stop if any connector overlays card content or if narrow mode gains horizontal overflow.
- Stop if a visual simplification hides a configured relationship without an explicit textual fallback.

## Verification plan

- Existing full tests plus JavaScript syntax, compileall, and diff check.
- Regenerate the clean isolated self-hosted sample and inspect the embedded conceptual metadata.
- Browser screenshot and DOM checks at 1440 px and 390 px: main path and human boundary are readable; desktop connectors use explicit gutters; mobile keeps a linear story without decorative arrows; console remains clean.

## Commit boundary

This approval authorizes local implementation and verification only. It does not authorize a commit, remote, push, publication, release, provider integration, or baseline approval.

## Completion evidence

- Replaced free-form Bézier arrows and floating SVG labels with three responsibility bands, six numbered story stages, and orthogonal connector routes. All cards are derived from configured component types and topology; no Change Passport path, component ID, or flow is hard-coded in the renderer.
- The primary route now reads left-to-right through evidence, static extraction, constrained explanation/validation, reader report, human approval, and candidate baseline. Inputs retain short entry branches. The configured evidence-spine-to-validation shortcut is retained, but it uses a dedicated lower gutter to avoid crossing the intermediate static-extraction card.
- Relationship labels now live in two DOM-readable groups: `主路径（按编号阅读）` and `输入如何进入主干`; the canvas has zero floating edge labels. Existing implementation mapping buttons and the static implementation layer remain unchanged.
- Regenerated the isolated self-hosted `a4576ec..688fc5f` artifact. The browser review at 1440×1050 found 8 components, 8 flows, 3 bands, 8 textual relationships, zero SVG labels, zero card-intersecting connector paths, and no horizontal canvas overflow. At 390×844, the cards preserve source-to-baseline order, decorative links/bands are intentionally hidden, and document width equals the viewport width. Console warnings/errors: 0.
- Final local verification: `uv run pytest -q` reported `49 passed`; `uv run python -m compileall -q src tests`, `node --check src/change_passport/templates/review.js`, and `git diff --check` succeeded. The targeted screenshot harness is `design/ui-flows/architecture-story-map-agent-20260905/04-validation/capture.py`.

## Stop / handoff

Stop after this approved local correction. No commit, remote, push, release, provider integration, or baseline approval is authorized. The next product gate remains an independent non-coder retelling of this architecture story.

## Post-completion micro correction

Owner viewport review found that the fixed tab-switch toast could cover the human-decision card and that band subtitles could meet the first card edge. The scoped correction suppresses the redundant tab toast and increases the top story inset from 46 px to 62 px. Browser capture confirms `pageSwitchToastHidden=true` and `bandHeadersClearCards=true`; no product facts, relationships, mappings, or static implementation behavior changed. See `BUG-20260905-018` and `EVO-20260905-023`.
