# TASK-20260904-004: Beginner-first interactive change review

State: IMPLEMENTING — AUTOMATED AND BROWSER VERIFICATION PASSED; INDEPENDENT HUMAN RETELLING PENDING
Tier: standard

## Trigger and authority

After reviewing the same DigitalSelf range in CodeAtlas.live, the owner concluded that a developer-first architecture browser has too high a threshold for non-coders. The owner explicitly approved optimizing toward a beginner-readable experience with an interactive HTML impact map. This authorizes the bounded PRD v1.2 revision and planning work, but the DigitalSelf UI Design Pipeline requires the revised PRD artifact to be confirmed before prototype or implementation work starts.

## Goal

Let a non-coder understand what changed, why it changed, who or what is directly affected, and what remains risky or unknown before exposing code concepts. Preserve deterministic evidence authority and allow developers or later systems to drill down into the same validated architecture delta instead of generating a second story.

## In scope after PRD confirmation

1. Add a deterministic `BeginnerChangeSummary` projection over existing validated claims and architecture delta data.
2. Render the default Chinese four-question explanation: what changed, why, direct impact, and attention/unknowns.
3. Generate one local single-file HTML artifact from the same validated JSON used by Mermaid and Markdown.
4. Show a stable Chinese change-impact path with changed nodes highlighted, unchanged context muted, and explicit folded counts.
5. Let a click select a node and open a persistent sidebar; let each branch action expand exactly one additional hop.
6. Keep files, functions, Git identity, tests, history refs, and evidence refs behind an explicit technical-details action.
7. Add deterministic parity checks and an independent beginner retelling acceptance fixture.

## Non-goals

- New fact extraction, broader language support, a full code/symbol graph, or an unbounded repository atlas.
- Production Desktop/Web/IDE integration, server, account, cloud upload, team collaboration, or release packaging.
- Automatic code edits, baseline approval, commit, push, merge, deployment, or CI blocking.
- Treating CodeAtlas output as project authority or copying its visual design wholesale.
- Starting the pending baseline approval or consecutive-change reuse evaluation under this task.

## Product and authority contract

- Default language is plain Chinese responsibility and process wording; code identifiers are secondary labels.
- The first screen must be understandable without API, function, module, dependency, Git, or internal enum vocabulary.
- `architecture-delta.json` and validated claims remain the only fact source for HTML, Mermaid, Markdown, and agent/system consumption.
- Layout, selection, expansion, and viewport state are view-only and cannot create or promote project facts.
- Unsupported business impact must say that static evidence did not prove it; a static import path is not automatically a real runtime or user impact.

## Planned implementation order

1. Confirm PRD v1.2 and record its exact SHA-256.
2. Freeze beginner-summary and HTML view-model fixtures before rendering code.
3. Add parity and unsupported-claim tests.
4. Implement the beginner projection and local HTML renderer.
5. Render the first immutable DigitalSelf sample and inspect it in a browser.
6. Run an evaluator-authored beginner retelling check and record the observed answer/time.
7. Return to baseline approval or consecutive-change evaluation only under a separate explicit decision.

## Acceptance conditions

- Within 30 seconds and without opening code, an independent non-coder correctly retells all four: what changed, why, one direct impact, and one risk or unknown.
- If the default page requires technical vocabulary to complete the retelling, the task fails.
- Clicking a changed node reveals prior responsibility, current change, impact, evidence boundary, and unknowns in Chinese without losing selection.
- A branch expands one hop per user action; no forced replay, cycling, or surprise reset occurs.
- HTML, Mermaid, Markdown, and validated JSON contain the same verified claims, nodes, edges, statuses, and evidence references.
- No HTML interaction mutates baseline, proposal, annotation, or target-repository state.
- Existing M1/M1.5 deterministic and read-only tests remain green.

## Verification plan

- Unit tests for beginner-summary projection, truth-state downgrade, escaping, and JSON/HTML/Mermaid/Markdown parity.
- Browser smoke test of the generated local HTML, including first load, node selection, sidebar persistence, and one-hop expansion.
- Evaluator-authored retelling input and timestamped observed answer; generator self-evaluation is not accepted.
- Target DigitalSelf Git status fingerprint before and after the run.

## Risks and stop conditions

- Plain-language transformation overstates business/runtime impact beyond static evidence.
- Simplification hides a material unknown or evidence limitation.
- The first screen becomes a decorative graph that still requires code knowledge.
- Useful behavior requires a server, external account, full symbol graph, or unbounded extraction.
- The revised PRD is not explicitly confirmed.

## Approval evidence

The owner's 2026-09-04 message “嗯，对的，按这个方向来优化” authorized this direction and the PRD v1.2 draft. The later explicit reply “确认 PRD v1.2” confirmed the exact PRD SHA-256 `1787776EE1A415D00CF804C41CF6349108675CEF7637ED6454F1AEEB57A276A6` and moved this standard task to approved/implementing within its bounded scope. The owner subsequently confirmed the prototype, visual direction, exact HTML SHA-256 `A8EB78D68141808502C864F97E0A184557812BECB2865C971E7D1EE656DD6CAF`, exact design-token SHA-256 `3C14725FC63A06CD32820F9B734E570B02075E72D60D8FEB96581BC3AC869D40`, and exact implementation-spec SHA-256 `ED36ED3567C32D1285AFFDB798BED91FE83998F6B13E250F56E78251B218B584`. This authorized the bounded local implementation and verification, not baseline approval, commit, push, packaging, deployment, or DigitalSelf product integration.

## Current progress

- PRD v1.2 is confirmed and bound to the exact SHA-256 above.
- DigitalSelf `prototype.plan` was attempted twice and both calls returned upstream 504 Gateway Timeout; the PRD confirmation remained valid.
- The required prototype artifacts were manually bridged from the confirmed PRD at `design/ui-flows/ai-coding-session-review/02-prototype/screens.md` and `state-matrix.md`.
- The owner explicitly confirmed the prototype information order and interaction contract.
- A built-in image-generation run produced the project-bound visual reference at `design/ui-flows/ai-coding-session-review/03-visual/png-reference.png`, SHA-256 `345EC977635B218BE56756C0C60DAE36FF25D08C8E644592C8D45EE312F912F3`.
- The owner explicitly confirmed the visual direction. A visual-mood contract and single-file HTML prototype were created from the confirmed visual hierarchy and frozen validated sample.
- Browser verification observed no horizontal overflow at 1440 px desktop or 390 px mobile, one-hop branch expansion, selected-node persistence across before/after, and all 8 claims in the technical drawer.
- The owner explicitly confirmed the exact browser-verified HTML SHA-256 `A8EB78D68141808502C864F97E0A184557812BECB2865C971E7D1EE656DD6CAF`.
- Design tokens were extracted from that HTML to `design/ui-flows/ai-coding-session-review/05-tokens/design-tokens.json`, SHA-256 `3C14725FC63A06CD32820F9B734E570B02075E72D60D8FEB96581BC3AC869D40`; JSON parsing passed and all 22 CSS custom properties were preserved with no missing or extra properties.
- The owner explicitly confirmed the design-token artifact SHA-256 `3C14725FC63A06CD32820F9B734E570B02075E72D60D8FEB96581BC3AC869D40`.
- The implementation specification was completed at `D:\Dev\Projects\DigitalSelf\design\ui-flows\ai-coding-session-review\06-implementation\implementation-spec.md`, SHA-256 `ED36ED3567C32D1285AFFDB798BED91FE83998F6B13E250F56E78251B218B584`.
- The owner explicitly confirmed the implementation specification SHA-256 `ED36ED3567C32D1285AFFDB798BED91FE83998F6B13E250F56E78251B218B584`.
- The formal generator now emits `beginner-review.json` and a no-network single-file `review.html` from the validated brief plus the same `ArchitectureDelta`; the presentation model records claim/node/evidence identity and never writes back to evidence or baseline state.
- The implementation adds shared architecture-evidence bindings, safe JSON script embedding, all 22 confirmed theme variables, Chinese responsibility labels with explicit presentation-source metadata, one-hop branch controls, before/after/diff state, and technical evidence drill-down.
- Automated verification passed: `39 passed`, Python compileall passed, JavaScript syntax passed, and the formal DigitalSelf sample retained all 8 claims, 14 displayed nodes, and 32 explicit folded IDs with matching brief/review/embedded identities. The DigitalSelf target status fingerprint was unchanged by finalize.
- A fresh evaluator-authored order-validation holdout produced 4 accepted, 1 correctly downgraded, and 0 rejected claims; the self-reported test result stayed `尚不清楚`, the internal authority enum did not leak to the default page, and the holdout target repo remained unchanged.
- Formal DigitalSelf outputs: `artifacts/digitalself-430c342-m15/beginner-review.json` SHA-256 `AFC0428D519DF593C681CDAA5CA390400ECDC5FB4A45F94957F983541D9E5C63`; `review.html` SHA-256 `2FEC3841C85EEF9887799FBAA4B82643676CACD4276130603149FDB81483FA1C`.
- A later formal regeneration was served through a temporary read-only `127.0.0.1` preview because direct `file://` takeover remained policy-blocked. Browser acceptance then passed: change/architecture Tab switching, selected-node persistence across before/after, first-level branch grouping (29 direct + 3 context), all 8 technical claims, architecture section/module drill-down, 390 px no-overflow, and zero console warnings/errors. The temporary service was used only for verification. Independent human 30-second retelling remains pending.
- No baseline approval, commit, push, packaging, deployment, or DigitalSelf product integration has started.
- A later owner request for a separate overall-system architecture tab is recorded as the unapproved v1.3 extension `TASK-20260904-005`; it does not retroactively expand this task's confirmed v1.2 scope.
