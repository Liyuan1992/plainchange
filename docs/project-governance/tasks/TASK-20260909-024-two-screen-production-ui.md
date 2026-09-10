# TASK-20260909-024: Two-screen production UI

State: IMPLEMENTED — VISUAL ACCEPTANCE PENDING
Tier: standard

## Trigger and authority

The owner confirmed that the beginner-first direction is correct and asked to continue. The bounded next step from TASK-20260909-023 is production HTML integration of the two-screen semantic contract. This authorizes local source, test, generated-artifact, and design-evidence changes only; it does not authorize model/provider calls, commit, push, deployment, or target-repository mutation.

## Goal

When a validated `change-passport.software-control.v1` document is supplied, render a local single-file report whose default surfaces answer “这次改了什么” and “这个软件怎么工作”. Keep technical evidence available on demand and preserve the existing report as the fallback when the new input is absent.

## Approved plan

1. Add a generic software-control validator with canonical identity, source binding, node/flow, owner-view, and changed-node checks.
2. Add an optional `--software-control` finalize input, copy the validated document into the artifact, and embed it safely beside the existing review model.
3. Render an owner summary and five-question first screen, plus one clickable top-to-bottom working map with a right-side owner-language inspector.
4. Keep the existing change graph, static implementation map, claims, paths, and runtime limitations behind technical-detail controls.
5. Verify fallback compatibility, malformed-input rejection, single-file/no-network behavior, keyboard interaction, responsive layout, and a real generated self-hosted artifact.

## Non-goals

- No project-name branches, target-specific path rules, or renderer-owned business copy.
- No automatic model call or conversation extraction.
- No claim that the declared working map is runtime tracing.
- No removal of the existing evidence or static implementation views.
- No commit, push, deployment, baseline approval, or external asset generation.

## Risks and stop conditions

- Stop if the new owner layer changes a validated fact or weakens an unknown into a claim.
- Stop if a working-map flow references a missing node or the changed highlight lacks direct source IDs.
- Stop if the fallback path changes when no software-control input is supplied.
- Stop if the report introduces network, storage, or executable-data capabilities.

## Verification plan

- Unit-test valid, tampered, mismatched, and malformed software-control documents.
- Unit-test optional finalize CLI integration and the unchanged fallback.
- Run the complete pytest suite, Python compile check, JavaScript syntax check, and `git diff --check`.
- Generate the self-hosted artifact and inspect the two screens at desktop and narrow widths when the local browser security policy permits it.

## Handoff condition

Complete when the generic input path, two owner-facing screens, fallback behavior, generated self artifact, and recorded verification all pass. Human comprehension and runtime-behavior claims remain explicitly pending.

## Result and observed verification

The production path is implemented without repository- or framework-specific renderer branches:

- `finalize` accepts an optional `--software-control` document, validates its canonical identity, brief/review/change/profile bindings, five-question order, node/flow integrity, implementation-group references, owner-view completeness, and direct basis for a changed node.
- The local report defaults to “这次改了什么” and “这个软件怎么工作” only when that document is present; the original report remains the fallback when it is absent.
- The first screen renders the conclusion before three compact state statements, then the five questions, before/after example, owner checks, and detailed actions behind disclosure.
- The second screen renders one top-to-bottom clickable graph, highlights only the declared changed node, and updates a right-side owner-language inspector. The existing implementation explorer remains below an explicit technical disclosure.
- The self-hosted artifact was regenerated at `artifacts/change-passport-self-688fc5f/review.html` and contains `software-control.json` with identity `9608afd53e26cdd07a52ac23f2f6e9f9ed5ae96dcef229725798089337658967`.

Observed automated verification: 57 pytest tests passed; Python compile, JavaScript syntax, generated-HTML parsing, canonical binding, optional-pipeline, fallback, and `git diff --check` passed (line-ending warnings only).

Visual acceptance is not claimed. The configured in-app browser rejects interaction and navigation for the local `file://` report URL, including its already-open FastAPI report tab. The security barrier was not bypassed, so no after screenshot, overlap verdict, or visual score exists yet. A final screenshot-only correction round remains required after the owner opens the new self-hosted artifact in a browser surface that permits inspection.
