# TASK-20260911-055: Open-source README and release preparation

State: DONE
Tier: high-risk

## Trigger and authorization

The owner requested that PlainChange be prepared for GitHub submission and
explicitly asked for serious English and Simplified Chinese README files. This
authorizes public-documentation preparation, package/release audits and local
verification on the existing release branch.

It does not authorize selecting or creating a remote repository, pushing,
creating a GitHub Release, publishing a package, changing credentials,
rewriting history, or mixing unrelated local changes into an unreviewed commit.

## Scope

- Rewrite `README.md` and `README.zh-CN.md` as equivalent public entry points.
- Explain the user problem, full model-assisted path, basic-evidence fallback,
  privacy boundaries, local-only operation, outputs, supported languages and
  honest Alpha limitations.
- Retain installation detail in `docs/INSTALL.md`, security policy in
  `SECURITY.md`, and release evidence in `docs/RELEASE_CHECKLIST.md`.
- Verify public-documentation contracts and packaging/readme inclusion without
  exposing a provider credential or generated private artifacts.

## Risks and stop conditions

- Do not claim model explanations prove runtime behavior or user impact.
- Do not show an endpoint, token, target source content or private artifact.
- Stop before commit/push if the public tree scope or remote destination is
  still ambiguous. A local commit and a GitHub push are separate decisions.

## Verification plan

1. Run public README contract tests and inspect rendered Markdown structure.
2. Run the relevant full test/build checks required by the current release
   checklist, with actual pass/failure recorded separately.
3. Scan intended public source files for ignored local provider configuration
   and token-shaped secrets.
4. Record the release-preparation result and the absence/presence of a remote.

## Observed result

Both public READMEs now lead with the owner problem, result shape, local
quick-start, model-provider boundary, explicit non-claims, bilingual report
behavior, generated artifacts, Alpha limits and security/feedback guidance.
The two documents retain the same source-language and evidence boundaries. Each
README now also embeds a language-matched, looping GIF from a real, locally
generated self-analysis report: the change view remains visible for four
seconds before switching to the system view for four seconds. The final public
demonstration uses the configured model for bounded project understanding and
change interpretation, then validates the output locally against fixed Git
evidence; it retains the report's runtime and verification boundaries.

The later generic language-contract repair in `TASK-20260911-057` regenerated
the English frames from a real English model report and makes model-authored
mixed Chinese output fail visibly. The two public GIFs remain language-matched
two-frame demonstrations, with each view held for four seconds.

`tests/test_public_docs.py` passes (2 tests). A fresh full pytest run passes
at 100%; its stderr is empty. Python compilation, both review JavaScript syntax checks and
`git diff --check` pass. `uv build` produced
`plainchange-0.1.0a1.tar.gz` and `plainchange-0.1.0a1-py3-none-any.whl`; the
source distribution contains both READMEs and the package build listing
contains neither artifacts nor local provider configuration. A non-ignored
worktree token scan found no token-shaped strings; `model-provider.local.json`
and test logs are ignored.

No Git remote is configured on `release/plainchange-0.1.0a1`. No commit,
remote configuration, push, release or package publication was made. The next
operation needs an owner-selected GitHub destination and an explicit decision
on the exact staged release scope.
