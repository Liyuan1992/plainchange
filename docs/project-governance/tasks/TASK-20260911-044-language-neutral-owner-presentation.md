# TASK-044: Language-neutral owner presentation

State: DONE
Risk: standard
Owner approval: On 2026-09-11 the owner confirmed the proposed architectural
correction after tracing the remaining Chinese text to PlainChange's own
deterministic draft generator rather than only to the target project.

## Problem

The bilingual reader currently treats a complete authored translation pack as
the only way to translate report-body text. As a result, an English reader can
still receive Chinese conclusions that PlainChange itself generated, even
though their meaning already comes from structured states such as no model
assessment, runtime not verified, a detected stop/failure branch, or an
unmapped change. Exact-string substitutions also fail when counts, filenames
or project labels are composed into a sentence.

This is a generic presentation-architecture defect. It must not be corrected
with DigitalSelf-specific vocabulary or a larger collection of sample-specific
translations.

## Approved scope

1. Record PlainChange-owned owner messages as stable message keys plus bounded
   arguments alongside the canonical Chinese projection.
2. Build the English owner projection from those structured messages without a
   model, network request or exact matching against the Chinese sentence.
3. Keep project declarations, project-provided labels, task quotations and
   technical evidence in their source language unless an identity-bound
   reviewed translation pack supplies an explicit translation.
4. Preserve the canonical control document, claim/evidence IDs, truth states,
   topology and source references. Localization remains a derived view.
5. Let a complete reviewed translation pack override the deterministic English
   projection, preserving the existing export/import route.
6. Make the language boundary state whether owner explanations were translated
   automatically while project/source text remains original.

## Non-goals

- No automatic translation of README content, project-authored capability names,
  task quotations, source code, file paths or technical evidence.
- No model/provider call, hidden machine translation or claim that a translated
  sentence has been semantically reviewed.
- No repository-name branch, target-specific glossary, target-repository write,
  commit, tag, push, package publication or deployment.
- No change to evidence authority or to whether a behavior/user impact has been
  verified.

## Risks and stop conditions

- A localization descriptor must not point into evidence, identity, state or
  topology fields. Stop if the projection can alter anything except approved
  presentation text.
- Source-language project wording may remain inside an otherwise English page.
  It must be disclosed rather than silently translated or presented as
  PlainChange-authored English.
- Existing complete reviewed packs must continue to validate against their
  frozen identity and must remain authoritative over the automatic projection.
- Stop if the generic fix requires a project or repository name.

## Verification plan

- Unit tests for descriptor validation, dynamic count/filename composition,
  canonical immutability, blocked evidence paths and reviewed-pack precedence.
- Generate a fresh DigitalSelf report without a translation pack and assert that
  PlainChange-owned first-screen conclusions, states and actions have an English
  projection while project-origin text remains unchanged.
- Run the localization, renderer, pipeline and auto-draft regressions, then the
  full test suite, Python compilation, JavaScript syntax checks and a target-name
  source scan.
- Regenerate the current report and inspect English/Chinese switching in a real
  browser when available. Browser rendering is not a comprehension test.

## Stop and handoff

Close only after observed evidence is recorded below. Do not start automatic
project-text translation, model-assisted rewriting, release work or Git
publication as an implied next phase.

## Observed result

Implemented without a repository-name branch, model call or target-repository
write.

- `software-control.json` now carries `plainchange.owner-presentation.v1`:
  each PlainChange-owned sentence is represented by a stable message key,
  bounded semantic arguments and an approved target text path. The validator
  rejects paths into identity, truth state, basis, evidence, source references,
  validation data or topology.
- The HTML renderer creates an English owner projection automatically when the
  descriptor exists. A complete identity-bound reviewed translation pack is
  applied afterwards and therefore remains the explicit override.
- Dynamic change, risk and action language uses behavior/map/assessment states,
  counts and filenames instead of matching the composed Chinese sentence.
  Code-discovered responsibility labels and evidence notes use the same path.
- Project purpose, project-declared capability labels/descriptions, quotations,
  paths and technical evidence remain original. The English boundary now says
  which class of text remains source-language.

Observed verification:

- Full suite: 113 tests passed. Focused regressions cover dynamic `14` plus
  `settings.json` composition, canonical immutability, blocked non-presentation
  paths, generated responsibility labels and reviewed-pack precedence.
- Python compilation, `review.js`, `review-i18n.js` and browser-harness syntax,
  `git diff --check` and a production target-name scan pass. Diff check reports
  only the repository's existing LF-to-CRLF notices.
- Fresh fixed DigitalSelf `4da99fc..a662719` generation completed in 2.154 s
  with 1,140 supported Head modules and 2,261 cache hits. The control contains
  317 PlainChange-owned messages and 49 explicit source-language paths.
- Structured inspection finds English owner conclusions, states, actions,
  dynamic risk text, code-discovered internal responsibilities and evidence
  labels. Remaining displayed Chinese is limited to the fixed README purpose
  and project-declared capability wording, introduced in English as source
  language.
- Real Edge at 1280 and 390 px passes both tabs, every capability expansion,
  console and document-overflow checks. The technical canvas remains horizontally
  scrollable and moved from 0 to 280. A later attempt to open the local file via
  the interactive browser connector was blocked by its file-URL policy; no
  workaround was attempted.

Artifact:
`artifacts/digitalself-language-neutral-owner-v2/review.html`

Remaining boundary: technical evidence and model/project-authored prose are not
silently translated. They require a complete, identity-bound reviewed pack when
an alternate-language presentation is needed. Human comprehension remains not
run, and this task does not authorize release or publication.

## Follow-up correction

Owner screenshots after closeout disproved the broader implication that every
PlainChange-generated architecture phrase was covered. This task covered the
owner `software-control.json` projection, but not generated fields coming from
the separate compact review and lazy architecture payload. TASK-20260911-045 /
BUG-20260911-035 closes that gap; the canonical verification recorded above is
retained as evidence of what TASK-044 actually checked.
