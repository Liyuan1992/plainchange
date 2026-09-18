# TASK-20260912-058: Windows portable first-run

State: DONE
Tier: high-risk

## Trigger and authorization

The owner judged the current `uv`/Python/command-line/model-JSON path too
complicated and approved the proposed P0 direction: a Windows portable launch
path, a guided project picker, and direct first-run provider input. This
authorizes implementation and local packaging verification. It does not
authorize a new GitHub Release, package-registry upload, code signing,
installer distribution, automatic updates, or a new provider request beyond a
user-initiated analysis.

## Facts and scope

- The current guided page already selects a project and fixed commits, but its
  model panel requires an environment-variable name and exposes provider
  compatibility terminology.
- `start-plainchange.cmd` requires `uv`; public first use therefore still
  requires a Python development environment.
- The provider contract intentionally keeps persisted configuration credential
  free and receipts sanitized.

Implement the portable P0 path:

1. Add a reproducible Windows one-file executable build script that bundles
   PlainChange and its local web assets.
2. Simplify first-run full-model input to endpoint, model name, and a masked
   API-key field. Hide provider identifier and structured-output mode from the
   ordinary path.
3. Treat the pasted key as process-memory-only: do not write it to reports,
   JSON configuration, receipts, logs, browser storage, or Git.
4. Keep existing CLI/config/environment-variable support as an advanced,
   compatible path for automation.
5. Update bilingual public documentation to lead with download/unzip/double
   click, while retaining an honest current-release boundary until an artifact
   is attached to a GitHub Release.

## Non-goals and stop conditions

- No credential persistence in this P0. Windows Credential Manager, installers,
  code signing, macOS/Linux bundles and update delivery require separate scope.
- No bundled Git implementation: the portable app detects missing Git and
  explains it in the local UI.
- No automatic model selection, provider discovery, remote telemetry, or model
  call during packaging/build verification.
- Stop if direct key handling could enter an artifact, a receipt, an exception
  message, or an HTTP response.

## Verification plan

- Unit-test direct ephemeral credential use and prove it is absent from provider
  identity/config hashes and public job data.
- Run the complete suite, JavaScript syntax checks, `git diff --check`, and
  package build.
- Build the Windows executable and launch it against a local fixture or use its
  loopback start path; verify the first-run shell loads without a Python/uv
  dependency.
- Inspect generated artifacts for expected templates/assets and scan the
  portable output for the test credential literal.

## Approval

Approved by the owner on 2026-09-12: “好的。” in response to the P0 portable
double-click and simplified first-run proposal.

## Observed result

The first-run UI now asks only for a compatible endpoint, model name and masked
API key. An optional checkbox supports keyless compatible endpoints; response
format compatibility remains available behind an advanced disclosure. The key
is passed separately from the persisted provider configuration into the in-
memory provider object, so its value cannot enter the config hash, model-stage
receipt, guided manifest or public job status.

`scripts/build-windows-portable.ps1` produces a one-file, windowed
`PlainChange.exe` and `PlainChange-windows-x64-portable.zip`. A console build
switch exists only for packaging diagnosis. The formal windowed executable was
launched; it selected an ephemeral loopback port and served the simplified
first-run shell successfully. The ZIP contains only `PlainChange.exe`; a byte
scan found none of the injected test credentials or environment credential
names.

Verification completed:

- Full suite: 137 passed in 55.34 seconds.
- Onboarding JavaScript and browser-check script parse successfully.
- Wheel and source-distribution build succeeds.
- Portable EXE build and loopback smoke pass.
- `git diff --check` passes.

The available browser-control bridge failed before it exposed any browser, so
the existing desktop/narrow visual automation script could not be run in this
session. The executable smoke verified its actual served content, but a new
human/visual responsive acceptance remains outstanding.
