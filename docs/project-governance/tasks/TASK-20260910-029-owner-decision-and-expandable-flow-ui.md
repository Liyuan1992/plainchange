# TASK-20260910-029: Owner decision and expandable flow UI

State: DONE
Tier: standard

## Trigger and authority

The owner supplied two visual references, accepted the assessment that they are materially friendlier, and explicitly authorized an implementation attempt. The accepted direction combines a result-first owner decision page with one clickable top-to-bottom software workflow. This approval is bounded to presentation and interaction; it does not authorize new product modules, fake navigation, external services, commits, pushes, deployment, or runtime claims.

## Source facts

- The current source-bound report already has two owner screens, a collapsed five-question explanation, a four-step overview covering every detailed workflow step exactly once, and lazy technical evidence.
- The first reference makes the change conclusion, likely impact, residual risk, and next action independently scannable.
- The second reference makes a selected workflow step and its explanation visible together, but its sample copy contains a dangerous contradiction: the selected node is styled as changed while its explanation says no change was found.
- Existing `change_state`, owner-view text, evidence basis, and overview/detail bindings are the authority. Visual state must be projected from the same node object rather than reconstructed independently.

## Approved plan

1. Integrate the two real report tabs into a compact product header and hide the redundant generic hero only in owner-control mode.
2. Restyle the first screen into one conclusion card plus three decision cards; keep the five-question explanation collapsed and technical evidence lower priority.
3. Keep the four-step overview as the default software mental model. Clicking a step expands its mapped detailed steps in the same top-to-bottom canvas and keeps a synchronized right inspector.
4. Derive changed badge, selected state, inspector question, and explanation from the same workflow node; add regression checks that prevent style/text state from drifting apart.
5. Collapse the duplicate relation list, preserve no-network/lazy evidence behavior, regenerate the fixed vLLM report, and validate desktop plus narrow layouts.

## Non-goals

- No left project sidebar, project list, model comparison, search, account menu, help center, release/version metadata, or other reference-only entry point.
- No new software-control fact, owner approval, completed check state, runtime execution, model call, or target-repository mutation.
- No repository-name, framework-name, path, or fixed-node special case in the renderer.
- No schema-breaking change, technical-evidence deletion, commit, push, deployment, or baseline approval.

## Risks and stop conditions

- Stop if a changed visual state can disagree with the selected node's `change_state` or evidence-bound owner text.
- Stop if the detailed workflow replaces the four-step default instead of being an explicit drill-down.
- Stop if reference-only navigation or fake metadata would need to be invented.
- Preserve all unrelated dirty-worktree content and retain the fallback report without software-control data.

## Verification plan

- Add focused HTML/JavaScript assertions for the integrated tabs, decision-card hierarchy, collapsed relations, four-step default, detail expansion, and single-source change presentation.
- Run the complete Python test suite, compileall, JavaScript syntax, HTML/offline scans, and `git diff --check`.
- Regenerate the fixed vLLM artifact and verify source/control identities, lazy technical payload hashes, and report size.
- Capture desktop and narrow screenshots if the available browser surface permits it; otherwise record the exact limitation and do not claim visual acceptance.

## Rollback

The change is limited to report templates/styles, their focused tests, and generated ignored artifacts. Reverting those template edits restores the previous UI without touching evidence, source repositories, or approved baselines.

## Handoff condition

Complete when both owner screens implement the approved hierarchy, change/selection semantics remain coherent, automated checks pass, and visual validation is either recorded or explicitly left pending with evidence.

## Observed result

- The real two-tab navigation now shares the compact report header. Owner-control mode no longer spends the first viewport on a redundant generic hero.
- The change screen now renders one dominant source-bound conclusion and three independently scannable decision cards for likely impact, residual risk, and the next action. The five questions and technical evidence remain closed by default.
- The software screen still starts from exactly four source-declared overview steps. Clicking one now expands only that overview node's mapped detail steps, in the same top-to-bottom canvas, with a synchronized right inspector and an explicit route back.
- `ownerChangePresentation(node)` is the single presentation path for changed badge, inspector eyebrow, and change question. The selected node, changed styling, inspector state, and copy all use the same node object and `change_state`.
- The duplicate relation inventory is preserved behind a collapsed disclosure. Reference-only navigation, search, account, release metadata, and persistent check actions were not added.
- The fixed vLLM artifact was regenerated at `artifacts/vllm-a69e75b-to-a85d073/review.html`; its validated 4 accepted / 1 safely downgraded / 0 rejected claim result is unchanged.

## Verification evidence

- Full suite: 65 tests pass. Focused owner-renderer/software-control tests: 12 pass.
- `python -m compileall -q src tests`, `node --check src/change_passport/templates/review.js`, and `git diff --check` pass; diff check reports only existing LF-to-CRLF notices.
- Real headless Edge interaction at 1440×1000: four overview nodes, one changed node, collapsed relation disclosure, no document or map horizontal overflow, and zero console warnings/errors.
- Clicking the changed overview produces detail depth with one mapped node for this vLLM step. Selected node `change_state`, changed class, inspector `data-change-state`, `AI 这次改了这里`, and `这次改了什么` all agree.
- Real 390×844 captures show three stacked decision cards, a closed five-question disclosure, four owner-map nodes, hidden SVG connectors for the narrow fallback, and no horizontal overflow.
- The regenerated 3,171,755-byte report remains a no-network single file; it has no external script/style or `fetch`, and its compressed technical payload hash validates.
- Human comprehension remains untested. Screenshot review scores the implemented visual direction 8.8/10; that is a layout/interaction judgment, not owner acceptance or runtime proof.
