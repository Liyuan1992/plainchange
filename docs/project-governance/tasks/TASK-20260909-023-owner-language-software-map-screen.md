# TASK-20260909-023: Owner-language software-map second screen

State: DONE — SECOND-SCREEN SEMANTIC CONTRACT VERIFIED
Tier: standard

## Trigger and authority

After the owner-language first-screen correction, the owner asked “第二屏的呢”. This identifies a real completeness gap: the “这次改了什么” candidate is now shallow, but “这个软件怎么工作” still exists only as structured map data and the older engineering-oriented architecture UI.

The ongoing instruction authorizes completion of the bounded product slice without repeated confirmation. This message approves a semantic second-screen candidate and its generic contract fields. It does not authorize production HTML/UI integration, model/provider calls, commit, push, deployment, or baseline approval.

## Goal

Define and demonstrate a second screen that lets a software owner understand the whole software as one top-to-bottom working picture, see where the current change belongs, and inspect one selected step in owner language without exposing source modules by default.

## Facts and assumptions

- The first screen answers “what changed”; the second answers “how this software works”. They share conclusions and source identities but have different reading goals.
- The target profile declares the conceptual process. It is explanatory project data, not runtime tracing.
- The current retained change is source-backed as a correction to the step that decides whether software relationships changed; this can highlight one working-map node when the mapping remains explicit and sourced.
- A Markdown candidate can verify information semantics and hierarchy, but it cannot prove final graph interaction or visual quality.

## Approved plan

1. Extend the generic working-map node contract with an owner-facing inspector: meaning, visible result, current-change explanation, affected people, unknowns, owner checks, and basis.
2. Rewrite all Change Passport working-map labels and descriptions in software-owner language; mark only the source-backed changed step.
3. Create a standalone second-screen Markdown candidate showing one top-to-bottom graph and the selected changed node's inspector.
4. Update the PRD and contract guide so the second screen has an explicit overview → graph → selected-step explanation → technical-evidence hierarchy.
5. Regenerate the control identity, dependent evaluation identities/checksums, and validate node/flow completeness, single-node change highlighting, source binding, and rejected-term absence from the owner layer.

## Non-goals

- No production HTML, CSS, JavaScript, layout engine, or browser acceptance.
- No change to the versioned target profile or any target repository.
- No claim that the project-declared flow is observed runtime order.
- No project-specific renderer condition, simulated click test, fabricated human score, commit, push, package, or deployment.

## Risks and stop conditions

- Stop if the second screen duplicates the first screen instead of explaining the complete software flow.
- Stop if change highlighting relies only on a broad implementation group shared by several steps.
- Stop if the owner inspector introduces a user-impact claim stronger than the first screen.
- Stop if technical evidence becomes necessary to understand the default graph.

## Verification plan

- Validate the revised sample against the revised Schema.
- Assert every working-map node has a complete owner inspector and every flow endpoint exists.
- Assert exactly one node is highlighted as changed and its basis includes the retained change claim.
- Assert the second-screen candidate contains every node and flow label, places the overview before the graph and inspector, and exposes technical evidence only after the owner explanation.
- Scan the owner layer for the previously rejected abstractions and implementation vocabulary.
- Recompute canonical identity and all dependent checksums.
- Run `git diff --check`.

## Handoff condition

Complete when the second-screen semantic candidate and generic contract are source-bound and internally consistent. Stop before production UI implementation; interactive and human comprehension evidence remain pending.

## Result and observed verification

The second-screen semantic candidate is complete at `docs/product/samples/change-passport-self-688fc5f.software-map.md`:

- It opens with one owner-language explanation of how inputs become a decision.
- One top-to-bottom graph contains all 8 working-map nodes and all 8 declared flows.
- Only `static_extraction` is highlighted as changed, using direct retained claim and evidence IDs rather than its shared implementation group.
- The selected-node inspector explains meaning, visible result, current change, affected people, unknowns, and owner checks before technical implementation.
- Every working-map node now carries the same generic `owner_view` contract so another repository can supply its own content without renderer branches.

Observed identities and checksums:

- Canonical `control_identity`: `9608afd53e26cdd07a52ac23f2f6e9f9ed5ae96dcef229725798089337658967`.
- Revised Schema SHA-256: `BB7B82EAA93F53C2F1B6A37AE224BCD891F1040CEFC331F2C59DD5FA8EE30C77`.
- JSON sample SHA-256: `C49D45CB6EE30F5A3817832E099927A6E40C5A7893C09A22720484B11E174E00`.
- First-screen Markdown SHA-256: `880FB2FFC01893FF6C21DF841693F3BD6BB619DA5A28842797CC32926D5AA34C`.
- Second-screen Markdown SHA-256: `C932EFB5656DE4FB85F71666B51B65C04F8C69596746027B9A90F81967C5529C`.
- Observation template SHA-256: `6233007DD914361BB58381F41729C90222AACF68AB3DC9B9A5DA7536AEB53883`.
- Evaluation manifest SHA-256: `3381BA7837530F3FCFEB25CBD8FE9C827A71F9826006E4974854C42161F77E37`.
- Current PRD SHA-256: `9B32A54FE77C7FC37B0AEDA07E2191EBFE26DDAE860EAF2AB5C41132F13839FE`.
- Current contract-guide SHA-256: `3103D093CDE89C2B3B3C4718813C482DFE5A9C8C22103CABD571E1709A713B83`.

Draft 7 schema validation passed. Custom checks found 8 unique nodes, 8 valid flows, complete owner inspectors for every node, exactly one changed node with direct claim/evidence binding, every node and flow label present in the candidate, correct overview → graph → inspector → technical-detail order, and zero owner-layer occurrences of the seven rejected abstraction phrases or prior implementation-term list. All dependent manifest hashes match and canonical identity recomputation passed.

This is still a Markdown semantic/interactivity-state candidate. No actual click behavior, browser layout, or human comprehension result is claimed, and production UI remains unchanged.
