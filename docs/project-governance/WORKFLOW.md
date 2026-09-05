# Workflow

## State machine

`NEW → BASELINED → ANALYZED → PLANNED → APPROVED → IMPLEMENTING → VERIFIED → DOCUMENTED → DONE`

`PLANNED → APPROVED` requires explicit user approval for standard and high-risk work. A failed validation returns the task to analysis or implementation; it does not permit ignoring the failure.

## Risk tiers

| Tier | Gate |
| --- | --- |
| Micro | State scope and validation before writing. |
| Standard | Record a bounded plan and wait for approval before implementation. |
| High-risk | Record plan, non-goals, risks, rollback/stop conditions, approval, and appropriate real verification. |

Use the higher tier when uncertain. Consequence, not line count, determines risk.

## Required preflight

- Read `PROJECT.md` and this workflow.
- Inspect applicable project instructions and current Git/worktree state.
- Identify affected domains and read their curated pages and ADRs.
- State facts, assumptions, scope, non-goals, risk, and verification plan.

## Retrieval rule

The normal task-time read path is `domains/` plus relevant ADRs and current task files. `BUGLOG.md` and `EVOLUTION.md` are source ledgers; open only targeted entries when investigating a recurrence, validating a domain claim, or doing curation.

## Closeout

- A bug fix always appends a structured record to `BUGLOG.md`, even if the bug appears minor or its root cause remains unknown.
- A completed material change or decision appends an `EVOLUTION.md` record.
- Record commands actually run and their observed results; do not call a plan, local test, commit, merged change, or production deployment the same thing.
- Update README, ADR, domain pages, or changelog only when their own ownership and trigger rules apply.
- Stop after the approved phase and request the next decision.
