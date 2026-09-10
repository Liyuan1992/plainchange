# TASK-20260910-036: Link change decisions to their system location

State: DONE
Tier: standard

## Trigger and authority

The owner explicitly requested a reusable link between the two owner-facing tabs: a mapped change on `这次改了什么` must open `这个软件怎么工作`, expand the containing overview stage, scroll to the changed detail step, and visibly distinguish the arrival target. The owner also clarified that the second tab is a system view rather than a repeated change report. This authorizes local implementation and verification only; it does not authorize a commit, push, deployment, model request, target-project write, or evidence/schema upgrade.

## Source facts

- `software-control.v1` already binds changed detail nodes to exactly one four-stage overview node when the evidence supports a unique mapping.
- The renderer already keeps all overview stages visible while one detail group expands inline.
- The current first-screen headline exposes the mapped change in text, but has no direct navigation to its source-bound workflow node.
- The current system inspector repeats change, affected-people, unknown, and owner-check content at nearly the same visual weight as the change tab.

## Goal

Turn the two tabs into one traceable owner journey: decision-oriented change summary on the first tab, and location/context-oriented system understanding on the second tab.

## Approved implementation plan

1. Derive the cross-tab target exclusively from the existing changed detail node and its declared `overview_map.detail_node_ids` membership; do not parse headline text or invent a fallback target.
2. Add a light `在软件流程中查看 →` action beside the first-screen conclusion only when one valid mapped target exists.
3. On activation, select the architecture tab, expand the containing overview stage, select the changed detail node, scroll it into view, move keyboard focus, and apply a temporary non-color-only arrival emphasis.
4. Reframe the system inspector around the selected step's responsibility, upstream/current-map input, produced result, downstream/next step, current-change location, and code-evidence boundary. Derive upstream/downstream labels from validated map edges.
5. Move duplicated affected-people, unknown, and owner-check material into a visually secondary collapsed disclosure; do not remove evidence or change its truth state.
6. Preserve existing manual tab switching, inline expand/collapse, Escape behavior, responsive layout, legacy fallback, and no-network single-file operation.

## Non-goals

- No new model call, workflow inference, runtime/data-flow claim, schema field, backend route, persistent URL router, or user action tracking.
- No repository-specific label or VideoFactory-only selector.
- No claim that a project-declared sequence proves runtime execution or payload transfer.
- No redesign of the accepted tab names or the first-screen decision hierarchy.

## Risks and fail-closed rules

- If the changed detail node cannot be mapped to exactly one overview node, omit the cross-tab action instead of linking to a guessed stage.
- Map edges may express declared sequence rather than runtime data flow. Use `按当前工作图` language and retain the evidence boundary.
- Programmatic scrolling must not overwrite normal saved scroll positions when users switch tabs manually.
- Arrival emphasis must remain understandable without color and respect reduced-motion preferences.

## Verification plan

- Unit/HTML assertions for conditional action rendering, source-derived mapping, semantic inspector headings, and absence in unmapped/fallback reports.
- Browser interaction on the current VideoFactory report: activate the first-tab action, confirm architecture tab selection, four-stage persistence, containing-stage expansion, changed-detail focus, visible arrival emphasis, and correct inspector content.
- Repeat browser checks at desktop and 390 px for overflow and scroll visibility.
- Full Python tests, compileall, JavaScript syntax, diff checks, and source repository-name scan.

## Rollback

The renderer-only addition can be removed without changing `software-control.v1` artifacts. Existing manual tab navigation and owner maps remain valid.

## Handoff condition

Complete when a uniquely mapped change can travel from the change summary to its exact system node, the second-tab inspector is system-context first, unmapped reports fail closed, and browser plus automated verification pass.

## Result

- Added a light `在软件流程中查看 →` action beside the first-screen conclusion. It appears only when exactly one changed detail node belongs to exactly one overview stage.
- Activating the action switches to `这个软件怎么工作`, preserves all four overview stages, expands the containing stage, selects and focuses the changed detail node, scrolls it into view, and briefly shows the textual marker `从变化页定位到这里`.
- Reframed the system inspector around six system questions: responsibility, upstream/previous step, produced result, downstream/next step, current-change location, and code-evidence boundary.
- Moved repeated change-impact, affected-people, unknown, and owner-check content into a collapsed `查看变化影响与检查建议` disclosure.
- Upstream/downstream copy is derived from validated map edges and says `按当前工作图`; it does not promote declared order to runtime data flow.
- Reports with zero or ambiguous changed workflow nodes keep the normal two tabs but do not render the cross-tab action.

## Verification result

- 78 automated tests pass. Python compilation, JavaScript syntax, diff checks, and the source repository-name scan pass.
- Headless Edge at 1440×1000 starts on the change tab with exactly one link. Clicking it selects the architecture tab, keeps four overview nodes, expands `overview.stage-3`, selects/focuses `declared-render`, shows the explicit arrival label, keeps the target in view, and renders all six system-context headings with the secondary disclosure closed.
- At 390×844, the same action keeps four overview nodes, one expanded group, target focus/visibility, and no document or canvas horizontal overflow.
- The unmapped FastAPI report renders zero cross-tab links. Desktop and narrow VideoFactory checks produced zero console problems.
- The browser integration surface was unavailable through the active Computer Use provider, so the existing local headless-Edge/CDP acceptance path was used instead.
- VideoFactory's working-tree fingerprint changed from the previous task's receipt because unrelated files were already being actively modified in that target before and during this run. This task read the fixed `d6594e3` commit and wrote no VideoFactory path; it does not claim an exclusive before/after worktree hash. The vLLM target fingerprint remained unchanged.
- Independent owner comprehension remains untested; the current owner review is the next product-quality gate.
