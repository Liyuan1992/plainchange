# TASK-20260910-039: Add a bilingual public README and offline report reader

State: DONE
Tier: standard

## Trigger and authority

The owner requested separate Chinese and English README editions and asked that
`review.html` support Chinese/English switching, defaulting to the user's system
language. The owner explicitly limited the product surface to those two languages.
This authorizes local documentation, report-renderer, interaction, test, generated
sample, and governance changes. It does not authorize a remote, push, deployment,
registry publication, real model call, target-repository write, or translation of
source evidence into a stronger claim.

## Source facts

- `README.md` currently starts in English but is otherwise predominantly Chinese;
  there is no separate Chinese README.
- The offline report hard-codes Chinese UI labels and generated owner explanations.
- Project declarations, task quotations, model output, and code evidence can arrive
  in any language and remain source material rather than interface copy.
- The report is a single offline file and currently makes no network request.

## Goal

Make the public entry and report reader usable in Chinese or English without adding
network translation, changing evidence identities, or implying that untranslated
source material has been independently verified.

## Approved implementation plan

1. Make `README.md` the complete English edition and add `README.zh-CN.md` as the
   complete Simplified Chinese edition, with reciprocal language links and matching
   scope, safety, model-provider, artifact, and limitation statements.
2. Add a two-language report locale layer. Initial locale follows the browser/system
   preference (`zh*` -> Simplified Chinese; every other locale -> English).
3. Add an explicit `中文 / English` switch. Save an explicit choice locally and use
   it on later openings; provide a safe fallback when local storage is unavailable.
4. Translate the report shell, state labels, owner-facing deterministic templates,
   architecture controls, accessibility names, and failure messages. Keep project
   declarations, task quotations, code paths, identifiers, and technical evidence in
   their original language; mark that boundary in the reader.
5. Preserve the single-file, offline, no-fetch report contract and keep locale state
   outside the evidence/baseline identities.
6. Add focused unit and real-browser checks for English default, Chinese default,
   explicit switching, persistence, narrow layout, and zero console errors.

## Non-goals

- No machine-translation service, automatic model request, third language, locale
  negotiation server, translated schema identifier, or translated source evidence.
- No redesign of the owner workflow, evidence hierarchy, architecture topology, or
  report facts.
- No remote publication or movement of the accepted `v0.1.0-alpha.1` tag.

## Risks and fail-closed rules

- A broad text replacement could alter evidence. Translation applies only at the
  derived presentation layer; embedded canonical JSON remains unchanged.
- Browser storage can fail for local files. Locale detection and switching must still
  work for the current page and must never block report rendering.
- English text can expand controls and cards. Desktop and 390 px checks must show no
  horizontal overflow or clipped language controls.
- Unsupported locales deterministically fall back to English.

## Verification plan

- Unit assertions for packaged bilingual README files, reciprocal links, locale
  bootstrap, only two supported locales, source-data preservation, and offline HTML.
- JavaScript syntax, Python compilation, full pytest, and `git diff --check`.
- Real Edge checks with Chinese and English browser locale plus an explicit switch,
  reload persistence, desktop and 390 px layout, and console/network error capture.

## Stop and handoff condition

Complete when both README editions are accurate, the offline report chooses and
switches between the two languages without changing embedded evidence, browser and
automated checks pass, and the result is documented. Stop before any remote release.

## Result

- `README.md` is now the complete English entry and `README.zh-CN.md` is the
  complete Simplified Chinese entry. Both link to one another and state the same
  local-first, model-optional, read-only-target, evidence, and Alpha limitations.
- The report now packages a dedicated presentation-only locale layer with exactly
  `zh-CN` and `en`. It resolves `zh*` to Chinese and all other browser languages to
  English, exposes a visible `中文 / English` switch, and stores an explicit choice
  locally. A same-file hash keeps the current choice usable if browser storage is
  unavailable.
- PlainChange-owned navigation, status, accessibility, owner-control, architecture,
  evidence-disclosure, error, and known deterministic-template language is available
  in both languages. Translation happens only in rendered DOM text; embedded review,
  software-control, and technical-payload JSON remain byte-for-byte source data.
- Project declarations, task/AI quotations, paths, identifiers, technical evidence,
  and an explanation supplied in only one language remain in that language. The
  report says so explicitly instead of presenting a generated translation as new
  evidence.
- The locale file is included in wheel/sdist resources. The source archive includes
  both README editions. The accepted `v0.1.0-alpha.1` tag was not moved and no release
  output under `dist/` was replaced.

## Verification result

- Full suite: 93 tests pass. Focused renderer/public-doc/profile tests pass, including
  exact embedded-data equality and target-name neutrality across the locale layer.
- Python compilation, report/i18n/browser-check JavaScript syntax, and
  `git diff --check` pass; Git reports only existing line-ending normalization
  notices.
- Real headless Edge passed an English system preference, a Chinese system
  preference, unsupported `fr-FR` fallback to English, explicit switching in both
  directions, stored-choice reload, exactly two controls, 1280×900 and 390×844
  layouts, zero horizontal overflow, and zero browser console/log problems.
- A temporary package build under ignored `artifacts/bilingual-dist/` includes
  `review-i18n.js` in the wheel and both README files plus the locale resource in the
  source archive. No registry, remote, model, or target-repository action occurred.
