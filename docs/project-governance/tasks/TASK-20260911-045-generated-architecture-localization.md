# TASK-045: Generated architecture localization

State: DONE
Risk: standard
Owner approval: The owner approved completing the language-neutral correction,
then supplied English-mode screenshots showing untranslated architecture text.
This is a continuation of the approved TASK-044 scope and does not authorize
translation of project-authored source text.

## Problem

TASK-044 localized PlainChange-owned text in `software-control.json`, but the
technical architecture view also renders PlainChange-owned presentation from
`beginner-review.json` and the lazy `system-architecture.json` payload. English
mode therefore still shows generated Chinese titles, baseline status and
implementation-category labels. Browser phrase replacement translates some
outer wrappers but leaves nested generated labels untouched.

The same screenshots also contain DigitalSelf capability names and descriptions
copied from the fixed project declaration. Those are source text, not this bug.

## Approved scope

1. Build an identity-bound automatic English projection for PlainChange-owned
   review and architecture fields from stable status, map kind, profile origin
   and implementation-category IDs.
2. Apply that projection to both the compact review data and the lazy technical
   payload without changing their embedded canonical JSON or hashes.
3. Translate generated conceptual titles, boundary/source labels, candidate
   snapshot state and automatic implementation categories.
4. Preserve project-declared capability labels/descriptions, quotations,
   identifiers, paths, source references, topology and truth states.
5. Let a complete reviewed translation pack continue to override the automatic
   projection.

## Non-goals

- No DigitalSelf-specific vocabulary or repository-name branch.
- No automatic translation of README/project capability wording.
- No model call, network translation, target-repository write, commit, push,
  release or publication.
- No change to evidence authority, graph membership, order or runtime claims.

## Verification plan

- Unit-test projection from mutated source wording to prove it depends on stable
  IDs/states rather than matching Chinese strings.
- Assert source capability text and canonical inputs remain byte-for-byte
  unchanged while generated review/architecture paths receive English values.
- Regenerate the fixed DigitalSelf report and inspect the two screenshot areas
  in English mode with real Edge at desktop and narrow widths.
- Run focused and full tests, Python/JavaScript syntax, diff checks and a
  production target-name scan.

## Stop and handoff

Stop after the generated-text leak is fixed and verified. Project-source
translation remains a separately reviewed/model-assisted capability.

## Observed result

Implemented without repository-name rules, model calls or target-repository
writes.

- Added `plainchange.generated-review-presentation.v1`: an identity-bound list
  of review/architecture text paths, stable message keys, bounded arguments and
  rendered English values. The renderer applies review patches to the compact
  model and architecture patches only after the hash-checked lazy snapshot is
  decoded.
- Automatic-profile conceptual titles and boundaries use map kind and product
  name; snapshot status uses its stable status value; implementation labels and
  responsibilities use category IDs. Project capability labels/descriptions are
  intentionally untouched.
- A complete reviewed translation pack still replaces the automatic review
  projection and may provide reviewed English for project-authored text.

Observed verification:

- Full suite: 114 tests passed. A new regression mutates every source-language
  generated phrase and still receives the correct English projection from
  stable IDs/status, while project capability text and canonical inputs remain
  unchanged.
- Focused owner/localization/renderer/pipeline suite: 33 tests passed. Python
  compilation and JavaScript syntax checks pass. A production scan finds no
  DigitalSelf, VideoFactory, memdsl, vLLM or FastAPI names in the correction.
- Fresh fixed DigitalSelf `4da99fc..a662719` analysis completed in 2.192 s with
  1,140 supported Head modules and 2,261 cache hits.
- Real Edge at 1280 and 390 px passes both tabs, capability expansion, console,
  document overflow and technical horizontal-scroll checks. In English mode the
  conceptual title, boundary, candidate-snapshot status and implementation
  mapping contain no Chinese generated text. The mapping reads
  `Implementation: Core functions, Documentation and engineering support, Calls
  and user entry points`.

Artifact:
`artifacts/digitalself-language-neutral-owner-v3/review.html`

Remaining boundary: DigitalSelf capability names/descriptions in the screenshots
are fixed-revision project declarations. A fully English presentation of that
source requires a complete identity-bound reviewed translation pack or a future
explicit model-assisted translation workflow; this task does not silently
translate or overwrite it.
