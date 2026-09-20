# TASK-045: PlainChange self-evaluation

State: DONE (diagnosis only)
Scope: User requested testing PlainChange itself. Read-only product diagnosis,
isolated fixtures and evidence documents; no product-code edits or real commits.

Evaluate the current dirty implementation using an isolated Git snapshot with
source hashes and explicit synthetic commit identity. Exercise real model-backed
understand, onboarding/API entry and error paths, report browser interactions,
and existing regression checks. Reproduce independent findings where possible.
Human comprehension remains deferred. No publication or provider switch.

Results: 207 tests passed; two real model runs, first failed at out-of-inventory
read, second succeeded with 44 Git-verified excerpts and 2 retained findings.
Real HTTP and browser entry/basic-report paths exercised. Self-generated
concurrent_output reproduced with real jobs: one failed, successful job's shared
evidence contained the other request's task. Additional access, UI state and
error-path issues documented in TASK-045-self-evaluation-results.md.
New local HTML browser test was policy-blocked; no circumvention. Product source,
tests and scripts unchanged. No real repository commits; synthetic fixture Git
commits only. ds unavailable. No fixes or publication.
