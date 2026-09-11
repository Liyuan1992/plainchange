# TASK-20260911-057: Model-language contract hardening

State: DONE
Tier: standard

## Trigger and authorization

The owner reported that the English README demonstration still showed Chinese
report content and requested that it be solved. This authorizes a generic
language-contract repair, a real configured-provider rerun, refreshed public
demonstration media, and local verification. It does not authorize modifying
the analyzed target, storing a provider secret, committing, pushing, or
publishing a release.

## Scope

- Carry `auto`, `en`, and `zh-CN` through onboarding, CLI, model stages,
  deterministic owner projection, cached project understanding, and report UI.
- Reject mixed Chinese model-authored owner prose for an English report rather
  than silently presenting it as English.
- Keep original quotations, code paths, identifiers, and technical evidence in
  their source language; they are evidence, not model-owned prose.
- Make generated candidate-profile labels and owner-map composition language
  aware without adding project-specific rules.
- Bound every provider-returned evidence-id list loss-only before schema
  validation, because compatible providers can ignore nested item limits.
- Refresh the English two-frame README GIF from a real English model report.

## Non-goals and risks

- No automatic translation/retry call is added; a non-compliant English model
  output fails visibly rather than spending undisclosed tokens.
- Static code evidence remains incapable of proving runtime behavior or user
  impact.
- The language rule must not reject source-language code, paths, evidence IDs,
  or quoted project material.

## Observed result and verification

The root cause had three general parts: the provider language was a prompt
preference rather than a validated contract; some PlainChange-owned candidate
and deterministic strings were Chinese-only; and a split template literal left
a Chinese suffix after its heading was translated. A real provider also
returned an oversized nested evidence list, demonstrating that requested
structured-output limits cannot be trusted alone.

The repaired path rejects CJK in English model-authored owner prose while
allowing structural/source fields, validates cached project understanding,
projects PlainChange-owned text in the selected language, bounds all known
model evidence arrays before validation, and translates the split template
literal. A real model run against the unmodified PlainChange demo target
completed successfully in 18.6 seconds and produced an English report with
the language control as the only intentional Chinese UI label. The refreshed
English GIF has two frames, each held for 4000 ms.

Verification completed:

- Focused model/pipeline/semantic/owner tests: 40 passed.
- Full suite: 130 passed.
- `node --check` passed for both report scripts and the README capture script.
- `uv build` produced the wheel and source distribution without artifacts or
  local provider configuration.
- GIF inspection confirmed both language demos contain two 4000 ms frames.

## Stop / handoff

Language quality is now enforceable for model-authored English owner prose;
source-language evidence deliberately remains untranslated unless a reviewed
translation pack is supplied. The public release still awaits a separately
selected remote and explicit staged scope.
