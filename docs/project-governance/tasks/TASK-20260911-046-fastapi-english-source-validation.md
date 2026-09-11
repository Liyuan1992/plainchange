# TASK-20260911-046: FastAPI English-source validation

State: DONE
Tier: standard

## Trigger and authorization

The owner requested a new run against the public GitHub FastAPI repository to
check whether an English-only project produces an English reader without visible
Chinese remnants. This is an explicitly authorized cross-project validation of
the already approved generic localization work.

## Scope

- Reuse the fixed public `fastapi/fastapi` comparison from `0.136.2`
  (`22b02e2`) to `0.136.3` (`8206485`).
- Use the automatic candidate profile and an English task statement; do not use
  the earlier FastAPI-specific profile or add repository-name/path branches.
- Keep the target bare repository read-only and verify its fixed objects before
  and after the run.
- Generate an isolated report and inspect both owner-facing tabs in English in a
  real browser.
- Treat Chinese translation resources inside the offline HTML as acceptable;
  the acceptance boundary is visible English-mode text, not dormant locale data.

## Non-goals

- No FastAPI execution, dependency installation, runtime verification, commit,
  push, release, provider request, or target-repository mutation.
- No claim that one English public project proves universal localization.

## Verification plan

1. Verify both fixed Git objects and record the target repository fingerprint.
2. Run the current generic `plainchange analyze` path into a fresh artifact.
3. Run focused automated localization/rendering tests.
4. Open both report tabs in English and fail if visible text contains Han
   characters; also check console errors and horizontal overflow at desktop and
   narrow widths.
5. Recheck the target repository fingerprint and fixed objects.

## Observed result

- The generic deterministic run completed in 1.456 seconds with all 2,242
  supported parse lookups served from cache. It parsed 1,121 modules at each
  fixed revision and collected the four-file release change.
- The first browser pass found one visible Han character on the English system
  page: `能`, used by PlainChange as a capability-card icon. This was not FastAPI
  source text. The renderer now uses the language-neutral `◆` mark and has a
  direct regression assertion.
- A second real Edge pass scanned the default first-tab state and the opened
  system technical implementation disclosure. It returned zero Han-bearing
  lines after excluding the intentional native language-choice label `中文`, but
  it did **not** open the first tab's technical disclosure or exercise its view
  and node interactions. TASK-20260911-047 supersedes this incomplete acceptance
  claim and records the corrected full-state browser coverage.
- At 1280 and 390 px the document has no horizontal overflow or console errors.
  The wide technical canvas remains independently scrollable and moved from
  `scrollLeft=0` to `280` under horizontal input.
- The complete project suite passes: 114 tests. Python compilation, JavaScript
  syntax and `git diff --check` also pass; only existing line-ending warnings
  were emitted.
- The target remains the same bare repository at
  `https://github.com/fastapi/fastapi.git`; both fixed commits and tree IDs are
  unchanged, and the object-store counts match the pre-run fingerprint.

## Boundary and follow-up

This validates the current localization boundary for one English-source public
project; it does not validate FastAPI runtime behavior or universal language
coverage. The report still derives its displayed product name from the bare
clone directory (`change-passport-fastapi-0.136.3.git`) rather than the canonical
project/package name. That separate owner-comprehension defect is retained as
BUG-20260911-037 and was not hidden by this language check.
