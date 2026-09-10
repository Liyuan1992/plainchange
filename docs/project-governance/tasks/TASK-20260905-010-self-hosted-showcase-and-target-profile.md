# TASK-20260905-010: Self-hosted showcase and portable target profiles

State: DONE
Tier: standard

## Trigger and approval

The owner clarified that Change Passport's rapid real iterations are its best high-confidence proving ground: every change has known task context and an inspectable outcome. The owner also set a non-negotiable constraint: fixes must not special-case this repository merely to make its own report look good. The owner explicitly approved this bounded task with `确认，开始吧` on 2026-09-05.

## Goal

Make Change Passport explain one of its own immutable changes as the public primary example, while moving repository-specific sections, beginner labels, terminology, branding, and theme provenance out of core logic into auditable target-profile assets.

## Scope

1. Add a versioned `target_profile` manifest reference and strict profile parser.
2. Move the existing DigitalSelf section map and presentation vocabulary into a DigitalSelf profile asset; add a Change Passport profile and a generic fallback profile.
3. Bind profile ID and SHA-256 into each system-snapshot group source and validate that binding.
4. Make the beginner review and HTML brand consume profile information carried by the validated snapshot rather than static DigitalSelf strings.
5. Freeze the immutable self sample `a4576ec..688fc5f` through an isolated read-only target clone, using the Change Passport profile; retain its generated artifacts only under ignored local artifacts.
6. Rewrite the public root README around the self sample and local evidence-bound workflow. DigitalSelf may remain in internal governance/provenance documents, but not in the root README's reader path.
7. Add generic fixture coverage proving profiles, profile hashes, grouping, display labels, and the absence of target-specific production-code branches.

## Non-goals

- No new model provider, live task-window integration, external deployment, remote, push, package release, or architecture-baseline approval.
- No claim that a self-known sample is blind or independently representative. It is a high-confidence correctness sample; cross-repository samples remain necessary for generalization.
- No special condition on `change-passport`, its commit hashes, its sample ID, or its source paths in production analysis code.
- No rewrite of the existing interactive UI behavior beyond consuming dynamic profile branding.

## Risks and stop conditions

- Stop if a profile can alter Git facts, nodes, edges, claims, or baseline authority rather than only grouping and presentation.
- Stop if the profile SHA cannot be carried and validated from manifest through snapshot to view.
- Stop if the self sample needs the mutable working tree or writes to the source repository.
- Stop if the public README would present self-known results as independent evaluation.

## Verification plan

- Unit tests for strict profile validation, configured grouping, SHA binding, dynamic presentation, and generic fixture behavior.
- Regression asserting no `DigitalSelf`, `digital_self`, Change Passport path, commit, or sample-ID branch remains in production profile consumers.
- Full pytest, compileall, JavaScript syntax, HTML no-network checks, and Git diff check.
- Formal self sample over an isolated clone of `a4576ec..688fc5f`, with source worktree status fingerprint unchanged before/after.

## Commit boundary

This approval authorizes implementation and local verification. It does not authorize a new local commit, remote, push, pull request, publication, or release.

## Completion evidence

- Added strict `change-passport.target-profile.v1` parsing, a generic packaged fallback, and auditable Change Passport and DigitalSelf profile assets. The profile records sections, labels, terminology, brand, and module areas only; architecture extraction remains profile-neutral.
- The system snapshot stores `target_profile` ID and raw SHA-256. Every group source binds the same identity, and validation fails closed if the binding is inconsistent.
- The beginner projection and HTML now read brand, labels, terminology, and module areas from the validated snapshot. Production profile consumers contain no DigitalSelf identifier, Change Passport commit, sample-ID, or path conditional.
- A generic temporary-repository regression proves that applying a profile changes grouping/presentation metadata without changing the Git or architecture facts. The initial optional-`module_areas` parser failure was fixed and recorded as `BUG-20260905-014`.
- Formal self sample: an isolated detached clone at `688fc5f094ca96703d5013da474cef6a5091bd5d` was clean before and after `prepare` and `finalize` for `a4576ec..688fc5f`. It produced 2 modified nodes, 0 added/removed/modified edges, 23 nodes, 48 static edges, 2 groups, 0 unclassified paths, Change Passport brand data, and validation summary 3 accepted / 1 downgraded / 0 rejected. The pending baseline was not approved.
- Final local verification: `uv run pytest -q` reported `48 passed`; `uv run python -m compileall -q src tests`, `node --check src/change_passport/templates/review.js`, and `git diff --check` exited successfully. The profile file SHA-256 equals the snapshot SHA-256, all group bindings matched, and the root README has no DigitalSelf reader-path reference.
- Public-facing material now starts from `docs/showcase/change-passport-self-688fc5f.md` and a portable manifest template. It explicitly says that this known-context self sample is not a blind holdout or a generalization claim.

## Stop / handoff

Stop after this local implementation and verification phase. No local commit, remote, push, release, provider integration, baseline approval, or next evaluation phase is authorized. The next substantive gate is independent human retelling plus scored cross-repository samples.
