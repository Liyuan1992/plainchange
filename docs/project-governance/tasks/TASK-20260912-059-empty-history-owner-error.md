# TASK-20260912-059: Handle projects without comparable history

State: DONE
Tier: micro
Date: 2026-09-12
Domain: first-run-onboarding

## Problem

Selecting a newly created Git project with no commits exposed Git's raw
`fatal: ... does not have any commits yet` error in the guided interface. The
existing friendly two-version guard ran only after `git log`, so it was never
reached for an unborn branch.

## Approved scope

The owner reported the failure from the portable first-run flow and asked
whether it had been tested. Fix the product class generally; do not add a rule
for the reported project and do not modify that target repository.

## Implementation

- Treat no saved version and one saved version as distinct first-run states.
- Explain both states in owner language without exposing Git's raw error or
  requiring the user to understand `commit` terminology.
- Preserve the existing read-only repository inspection contract.
- Add regressions for both history boundaries.

## Verification

- Focused onboarding tests cover zero, one and two saved versions.
- The complete test suite passes.
- The rebuilt portable executable returns the owner-language error for the
  reported zero-version repository without changing that repository.
- `git diff --check` passes.

## Observed result

Repository inspection now checks whether the current branch has any saved
version before asking Git for its history. A zero-version project receives the
message “还没有保存过任何版本”; a one-version project receives “只有一个已保存版本”.
Neither path exposes `fatal` or `commit`, invents a baseline, or writes to the
target.

Verification completed:

- Focused onboarding suite: 11 passed.
- Full suite: 139 passed in 62.33 seconds.
- Rebuilt windowed portable executable returned the owner-language message
  through its real `/api/repository` endpoint for the reported project.
- The target's before/after `git status --porcelain` output remained identical.
- `git diff --check` passes.
