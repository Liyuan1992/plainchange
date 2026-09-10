# TASK-20260910-038: Freeze the first Alpha and add a guided local start

State: DONE
Tier: high-risk

## Trigger and authority

After reviewing current readiness, the owner explicitly authorized items 1, 2,
and 3 through “好的，你先把123做好”: freeze a reproducible Alpha baseline,
complete the distribution/install surface, and add a minimal project/version/report
onboarding path. This authorizes local branches, commits, an annotated local Alpha
tag, local package builds, documentation, and the guided local UI. It does not
authorize a remote, push, deployment, account/cloud service, telemetry, automatic
model request, target-repository write, or public release.

The owner subsequently chose direct open source distribution and the OSI-approved
MIT license. The owner then selected `PlainChange` as the product/package/CLI identity
and retained `Change Passport` as the core generated artifact and protocol family.
This authorizes the coordinated local rename but still does not authorize a remote,
registry publication, deployment, or public account action.

## Baseline facts

- Branch `main` points to `688fc5f` with only two historical commits.
- The complete working implementation has 25 modified tracked files and 185
  untracked files; 20 package Python modules exist while only 12 are currently
  tracked. There is no Git remote.
- `uv run pytest -q` currently passes 82 tests; compileall, JavaScript syntax, and
  diff checks pass.
- The package declares Python 3.12+, has no runtime dependency, and exposes the
  `change-passport` console script, but still describes itself as an experiment and
  has no install guide, license decision, changelog, release checksum, or built
  distribution.
- Starting a new report still requires manually writing a manifest with a repository
  path and Git base/head identifiers.
- The Figma/prototype preflight found no callable `figmaPrototypeDirector` or Figma
  surface. The guided entry will reuse the accepted local report language, tokens,
  and interaction patterns rather than introduce a new visual direction.

## Goal

Produce a reproducible, locally installable `0.1.0a1` Alpha whose first-time user can
select a local Git project, choose an earlier and newer version in plain language,
add optional task context, generate the existing evidence-bound report, follow real
progress, and open the result without authoring JSON.

## Approved implementation plan

1. Create a named local release branch and make a focused baseline commit containing
   the already-approved working implementation, governance records, tests, and small
   design evidence. Keep generated reports, caches, environments, secrets, and build
   outputs ignored. Record the baseline commit identity.
2. Add a loopback-only guided web entrypoint, served by the installed package with no
   runtime dependency. It will:
   - accept or browse for a local Git directory;
   - show recent commits as dated, human-readable version choices;
   - default to the newest commit and its predecessor while allowing explicit change;
   - collect optional original task text;
   - choose an output directory outside the target repository;
   - create the manifest internally and invoke the existing deterministic pipeline;
   - show stage progress/failure from `run-receipt.json` and open the completed report.
3. Bind every state-changing local API call to a per-process token, accept only
   loopback hosts, validate Git/revision/output paths with fixed subprocess arguments,
   never serve arbitrary files, and never enable model generation from the beginner
   screen in this Alpha.
4. Add CLI `plainchange serve`, direct `plainchange analyze .`, shorthand
   `plainchange .`, packaged onboarding HTML/CSS/JS, a Windows source launcher,
   focused unit/HTTP tests, and concise user-facing failure language.
5. Update package metadata to `0.1.0a1`, replace the experiment description, add an
   installation/first-run guide, changelog, security/privacy boundary, and release
   checklist. Add the owner-selected license only after the explicit choice arrives.
6. Build wheel and source distribution locally, create SHA-256 checksums, install the
   wheel into a clean temporary virtual environment, and verify CLI/help/onboarding
   resources plus one real guided analysis against an isolated tiny Git fixture.
7. After all verification passes, commit the release surface and create an annotated
   local tag `v0.1.0-alpha.1`. Do not create or contact a remote.

## Non-goals

- No cloud hosting, login, collaboration, automatic repository upload, telemetry,
  IDE integration, auto-update, signed installer, or OS-level installation.
- No public marketing claim, independent comprehension result, baseline approval,
  or model-provider correctness claim.
- No rewrite of the evidence engine, report visual design, or target-specific rule.
- No inclusion of generated `artifacts/`, caches, `.env`, API keys, virtual
  environments, or target-repository content in Git or packages.

## Risks and fail-closed rules

- A local web server can expose filesystem actions. It must bind to loopback only,
  require a random per-process request token, reject unknown origins/content types,
  and serve only bundled assets plus reports registered by the current process.
- A user can choose the same or invalid revisions. Validate both commits and reject
  invalid/equal selections before writing a manifest.
- The output directory must not be the target or any child of it. Default to a sibling
  report directory and retain the existing pipeline containment validation.
- A package install can omit templates. Clean-install verification must start the
  guided entry and load all three bundled assets before tagging.
- A product identity cannot be guessed into a public release. Stop before the final
  release commit/tag until the replacement name is explicitly selected.
- Existing working-tree content belongs to the owner. Review the staged file list and
  secret/path scan before committing; do not clean or discard anything.

## Verification plan

- Existing full pytest suite plus new repository-inspection, revision-validation,
  manifest-generation, loopback/token, API-state, resource, and guided-analysis tests.
- `compileall`, JavaScript syntax checks for report and onboarding scripts, JSON
  validation, `git diff --check`, secret-pattern scan, ignored-artifact check, and
  package-content inspection.
- Build wheel/sdist; install wheel in a fresh temporary virtual environment; assert
  version, CLI help, `plainchange serve --help`, bundled resources, and a
  loopback HTTP smoke test.
- Run the guided path on an isolated two-commit fixture, assert target Git status is
  unchanged, report exists, progress succeeds, and the report opens through the
  registered report route.
- Attempt actual browser inspection when the active provider is available; otherwise
  record the exact blocker and retain human visual acceptance as unverified.

## Rollback and stop condition

The release branch and commits preserve the pre-task state and can be abandoned
without resetting or deleting owner files. Stop before tagging if tests, clean-wheel
installation, source privacy review, license choice, or guided end-to-end analysis
fails. Stop after the local Alpha tag; remote publication remains a separate owner
decision.

## Implementation evidence so far

- Created local release branch `release/alpha-0.1.0a1` and froze the previously
  approved implementation at commit `c09652efb34f` after 82 tests, compileall,
  report JavaScript syntax, credential-signature, and staged-diff checks passed.
- Added `plainchange serve`, a dependency-free loopback onboarding server and
  packaged Chinese HTML/CSS/JS. The page selects a Git directory, defaults to the
  newest commit and its predecessor, accepts optional task context, writes a managed
  manifest outside the target, follows `run-receipt.json`, and serves only the
  report registered by that process.
- Added session-token, origin, content-type, request-size, revision, output ownership,
  and loopback-bind validation. The beginner entry deliberately uses deterministic
  local generation and exposes no model request control.
- Added six focused tests. The complete suite now passes 88 tests, including an HTTP
  journey that generates and opens a report from a two-commit fixture while the
  target Git status remains unchanged.
- Real browser inspection passes at 1280 px and emulated 390 px with no horizontal
  overflow or console warnings/errors. After repository selection, the page shows
  dated commit messages, short identities, the external output path, and an enabled
  generation action.
- Built wheel and sdist, verified all four onboarding resources in the wheel, and
  installed it into a new Python 3.12 virtual environment. The installed console
  script reports `0.1.0a1`, starts on an ephemeral loopback port, and returns the
  protected Chinese page over HTTP 200.
- Added installation, changelog, security, release-checklist, Windows source launcher,
  and reproducible SHA-256 build script. The sdist manifest was narrowed to public
  runtime/documentation material rather than internal governance and design evidence.

The owner selected PlainChange and approved the brand/artifact split recorded in
ADR-0005. The distribution/import namespace, CLI, cache, guided UI, launcher, current
self-profile, installation copy, and README now use PlainChange; existing
`change-passport.*` schema identifiers remain the stable Change Passport artifact
contracts. Direct project analysis works through `plainchange analyze .` and the
equivalent `plainchange .`, while the browser UI is `plainchange serve`.

During the rename, a clean editable rebuild exposed a current-setuptools PEP 639
conflict between the SPDX MIT expression and its redundant legacy classifier. The
classifier was removed and BUG-20260910-023 records the confirmed release defect.
Final package hashes, the release commit, `DONE` state, and annotated tag still wait
for the complete renamed-package, clean-install, browser, and privacy gates.

## Final acceptance evidence

- Full suite: 90 tests passed. Python compilation, report/onboarding/verification
  JavaScript syntax, and `git diff --check` passed; Git emitted only line-ending
  normalization notices.
- The final wheel installs into a clean Python 3.12 environment as `plainchange
  0.1.0a1`. Both `plainchange --help` and `python -m plainchange --help` expose
  `serve`, `analyze`, and the retained advanced commands.
- The clean-installed shorthand analyzed this repository's fixed last two commits in
  0.612 seconds, generated `review.html`, printed readable Chinese UTF-8 progress,
  and left the target worktree byte-for-byte unchanged according to before/after Git
  status output.
- The final wheel contains 35 entries and all six packaged HTML/CSS/JS report and
  onboarding assets. The 56-entry sdist excludes tests, design files, generated
  artifacts, internal product/governance documents, target profiles, and showcase
  fixtures. Package scans found no old `change_passport` import package, local
  `C:\Users\Administrator` / `D:\Dev\Projects` paths, or old secret variable.
- Headless real Edge checks against the clean-installed loopback server pass at
  1280×900 and 390×844: PlainChange title/brand and required controls are present,
  horizontal overflow is false, and console/network problems are zero. A missing
  favicon 404 found in the first pass was fixed before the final build.
- Final package SHA-256 values are
  `7143117072aa0358849aae1323452dddfed673e2a5116ea384bcfb9047e21177`
  for the wheel and
  `3c92cfe292cb5220b0b4d977b3cd0862131fb0f42deebca54f3fac9996f74c49`
  for the sdist. `dist/SHA256SUMS.txt` contains only these PlainChange artifacts.
- The release is committed on `release/plainchange-0.1.0a1` and the annotated local
  tag is `v0.1.0-alpha.1`. No Git remote, push, deployment, registry publication,
  telemetry, target write, or model request occurred.
