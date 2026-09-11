# TASK-040: Complete report-body localization

State: DONE
Tier: standard

The owner approved the correction with “嗯，你来补代码” after identifying that
English mode still showed Chinese headings, workflow nodes, and inspector prose.

Plan: add a generic source-identity-bound translation pack for owner-facing text;
validate complete coverage and permit only presentation text changes; render a
translated projection before building nodes and relationships; provide a reusable
CLI export/import route; translate the current vLLM sample through that route.
Preserve IDs, references, states, topology, and canonical source data. Verify both
tabs, every expanded step, switching, original evidence, and narrow layouts.
No provider call, commit, release, or target repository change is required.

## Observed verification

- Full suite: `102 passed in 53.77s`; Python compilation and JS syntax pass.
- Real Edge: 28 visible owner-body states across 1280/390 px, including both
  tabs, four overview expansions and eight details. No Chinese body remnants;
  language defaults/fallback/switch/persistence and console checks pass.
- Generic CLI roundtrip tests preserve canonical source bytes and graph/state
  fields. Missing/empty/unknown/stale/non-English packs fail without replacing HTML.
- Current vLLM report regenerated using its 158-string reviewed English pack.
  Screenshot: `artifacts/vllm-a69e75b-to-a85d073/english-body-check.png`.
- No new provider call, commit, tag change or external target write. The `ds`
  completion CLI was not available on PATH, so no completion receipt was submitted.

## Handoff and limits

The user can reload the current report and switch languages. New projects need
a source-bound translation pack; this change does not automatically call a model.
Coverage and identity checks cannot prove translation semantics. Original code
and quotations retain source language; visual checks are not comprehension tests.

## Reopened: technical disclosure coverage

The owner found Chinese inside System workflow and Why this conclusion / technical
details. This is a continuation of the approved localization correction, not a new
product feature. The previous browser check explicitly excluded both legacy hosts;
its 28 states did not cover these disclosures and must not be read as full-report QA.

Correction: bind an additional review-text translation set to review_identity;
translate only presentation fields in the compact review and the lazily verified
snapshot. Keep canonical JSON, IDs, topology, evidence references, task quotations
and original claim text unchanged. Show translated claims with an optional original.
Add both disclosures to the browser regression and a script/DOM regression.

Observed: script/DOM regression checks 11 states, including 8 workflow nodes and
technical conclusions/limitations. Canonical JSON remains unchanged. Real browser
launch was denied by the environment and the browser connector was unavailable;
this follow-up has no new real-browser layout acceptance. No provider call or commit.
Full follow-up suite: `103 passed in 46.37s`; JS syntax, Python compilation and
diff checks pass. The vLLM report was regenerated. `ds` is still unavailable.

Second recurrence: the user found untranslated change-view instructions and
direct-relationship arrow labels. Added all three view instructions to the UI
dictionary and translate the relation label before composing arrow decoration.
Expanded DOM coverage to before/after/diff and every displayed node selection:
48 states pass without unprotected Chinese. Sixteen focused Python tests and JS
syntax checks pass. Report regenerated; this remains script/DOM, not browser QA.

CSS badge recurrence: moved “实现已展开” out of pseudo-element content into a
localized DOM span. English is “Implementation expanded”. Badge assertion and
48 DOM states pass; 17 focused tests include a CSS-generated Chinese text guard.
See BUG-20260910-028. Report regenerated; no commit or unrelated cleanup.
