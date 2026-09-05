# TASK-20260904-001: Phase 0 deterministic evidence spine

State: DONE
Tier: standard

## Source inputs and observed baseline

- User explicitly requested a new engineering project and asked work to start under the shared agent rules.
- Confirmed source PRD: `D:\Dev\Projects\DigitalSelf\design\ui-flows\ai-coding-session-review\01-prd\prd.md`.
- Source PRD SHA-256: `643F7A632523F831B0C90E5A9D6543A9CF4ADB456485DCBDB8B2A08C33199C7E`.
- PRD confirmation timestamp: `2026-09-03T07:32:53.478590Z`.
- Repository: new local Git repository at `D:\Dev\Projects\change-passport-spike`; no commits and no remote.
- Toolchain observed: Python `3.12.10`, Git `2.54.0.windows.1`, uv `0.11.21`; pytest is not globally installed.
- Business code, package metadata, virtual environment, fixtures, and tests do not yet exist.

## Goal and acceptance conditions

Implement one local end-to-end vertical slice:

```text
sample manifest
  -> immutable Git identity and read-only diff evidence
  -> authority/leakage validation
  -> generator-facing evidence packet
  -> constrained model JSON claims through a file bridge
  -> deterministic claim validation
  -> four-section Markdown + JSON brief
  -> annotation template
  -> computed score JSON
```

Acceptance requires:

1. A CLI can run the slice against a temporary test Git repository using an explicit base/head manifest.
2. Resolved base/head commit hashes, changed paths, line statistics, patch hash, and evidence references are deterministic.
3. Input evidence and hidden ground truth cannot refer to the same normalized source; overlap fails before collection.
4. The generator receives no hidden-ground-truth object, path, text, or identifier and cannot read the target repository directly.
5. Missing task/test/history evidence produces explicit unknown/attention claims, never inferred Why or pass status.
6. Raw model output is retained separately; unknown evidence IDs and authority mismatches cannot become verified rendered claims.
7. The collector invokes only allowlisted read-only Git commands and never executes commands found in a manifest or receipt.
8. Each verified fact carries at least one resolvable evidence reference of the required authority class.
9. Annotation scoring reports high-importance precision, critical recall, severe unsupported count, authority-error count, and leakage count without modifying the frozen raw output or validated brief.
10. Unit and end-to-end tests pass in the project-local environment.

## In scope / non-goals

In scope:

- Python 3.12 package with a project-local `.venv` managed through uv.
- `pyproject.toml` and a `change-passport` CLI.
- JSON manifest parsing and validation using the Python standard library.
- Read-only Git adapter using argument arrays, bounded output, explicit timeouts, and no shell execution.
- Provider-neutral JSON generator packet and raw model-response contract.
- A file bridge so Codex or Claude Code can consume the exact packet and return claims without receiving hidden ground truth.
- Deterministic evidence bundle, validated Markdown/JSON brief, annotation template, and score output under an explicit output directory.
- Synthetic test repositories created under pytest temporary directories.
- Small, non-private example manifests containing placeholders only.
- README/PROJECT updates and closeout Evolution record after verification.

Non-goals:

- Automatic model API calls, API-key handling, embeddings, semantic history retrieval, AST parsing, or unbounded architecture inference.
- Allowing a model to read the target repository, source ledgers, or hidden ground truth outside the generator packet.
- Reading complete DigitalSelf BUGLOG/Evolution files.
- Selecting or processing the 12 real DigitalSelf evaluation samples.
- Mutable working-tree review.
- UI, Desktop integration, IDE extension, MCP server, PR bot, CI, packaging, deployment, telemetry, remote, commit, or push.
- Automatic execution of repository tests or any command described inside evidence receipts.

## Affected domains, ADRs, and source records read

- Domain: evidence authority, immutable Git collection, evaluation scoring.
- Proposed ADR: `ADR-0001-deterministic-evidence-spine.md`.
- No raw BugLog or Evolution entry was required for planning this new repository.

## Plan, risks, and rollback/stop conditions

### Planned files

- `pyproject.toml`
- `src/change_passport/__init__.py`
- `src/change_passport/cli.py`
- `src/change_passport/models.py`
- `src/change_passport/git_evidence.py`
- `src/change_passport/generator_contract.py`
- `src/change_passport/validator.py`
- `src/change_passport/pipeline.py`
- `src/change_passport/scoring.py`
- `tests/test_models.py`
- `tests/test_git_evidence.py`
- `tests/test_generator_contract.py`
- `tests/test_validator.py`
- `tests/test_pipeline.py`
- `tests/test_scoring.py`
- `examples/sample-manifest.json`
- `docs/project-governance/domains/evidence-contract.md`

### Ordered implementation

1. Create package metadata and local environment; add only pytest as a development dependency.
2. Define typed manifest/evidence/claim/annotation objects and canonical JSON serialization.
3. Implement manifest validation, including normalized-source overlap and output-path safety checks.
4. Implement the read-only Git adapter for commit resolution, diff/name/numstat collection, and bounded evidence hashing.
5. Emit a generator packet that contains only allowlisted evidence IDs and content, plus a strict raw-claim JSON contract.
6. Implement the file bridge and deterministic claim validator; render only validated or explicitly downgraded claims.
7. Implement scoring over frozen raw claims, validated claims, hidden ground truth, and human annotations.
8. Add unit tests plus one temporary-repository end-to-end test and CLI smoke test. Use a scripted fake generator in automated tests; use the current Codex task only for a later explicitly selected real sample.
9. Update verified commands and boundaries; append an Evolution source record only if the implementation passes.

### Risks

- Path aliasing could bypass leakage checks.
- Git output can be unexpectedly large or contain binary data.
- A manifest field could accidentally become an executable command surface.
- Scoring definitions could reward omission or generated unknowns.
- Windows path normalization can differ by case and separator.
- A model could cite nonexistent evidence, use the wrong authority class, or smuggle unsupported certainty into prose.

### Required mitigations

- Resolve paths with `Path.resolve(strict=True)` where an input must exist; compare case-folded Windows identities.
- Enforce patch/file/output byte limits and mark truncation explicitly.
- Invoke Git with fixed executable and argument lists, `shell=False`, a timeout, and no manifest-provided subcommand.
- Keep hidden-ground-truth objects out of the generator-facing evidence bundle by type and API boundary, not prompt wording.
- Require strict JSON claims with section, scope, type, confidence, evidence IDs, limitations, and requested next check.
- Treat raw model output as untrusted input; reject unknown IDs and downgrade claims that lack the authority required by their scope.
- Test unsupported, missing, binary, timeout, invalid-ref, overlap, and path-escape cases.

### Stop conditions

Stop implementation and return to analysis if:

- the slice requires executing target-project commands;
- hidden ground truth cannot be isolated by construction;
- the change identity cannot be reproduced from immutable Git objects;
- the model cannot be constrained to the generator packet and strict claim contract;
- implementation requires a remote API, secret, or automatic source upload;
- implementation would write into the target repository;
- the new project contains unrelated user/agent changes.

### Rollback

No remote, commit, or external state will be created. All implementation files will remain uncommitted. Do not delete or reset them automatically; if rollback is requested, enumerate the exact new-project paths first.

## Approval

Status: approved on 2026-09-04.

Evidence: after the three-layer design was explained in Chinese, the user replied “嗯，对的”. Approval covers the deterministic evidence spine, constrained model file bridge, deterministic validator, renderer, annotation, scoring, and automated tests listed here. It does not authorize the 12-sample experiment, an automatic model API, source upload, commit, remote creation, push, CI, or deployment.

## Implementation and changes made

Implemented the approved three-layer vertical slice:

- Python package and `change-passport prepare|finalize|score` CLI.
- Strict manifest, source-authority, path/content-overlap, size, and output-path contracts.
- Read-only immutable Git collector with commit resolution, file/line statistics, patch hash, bounded patch excerpt, timeout, and no shell execution.
- Generator packet that omits manifest/repository paths and all hidden-ground-truth identifiers/content.
- Provider-neutral file bridge and strict raw-claim JSON contract.
- Deterministic evidence-ID, authority, section/scope, claim-count, and safe-unknown validation.
- Chinese Markdown renderer, separate raw/validated artifacts, annotation template, and score calculation.
- Project-local uv environment, pytest suite, placeholder manifest, and curated evidence-contract domain page.

No automatic model API, real DigitalSelf sample, commit, remote, push, CI, package release, or deployment was created.

## Verification actually run

- `python --version` -> `Python 3.12.10`.
- `git --version` -> `git version 2.54.0.windows.1`.
- `uv --version` -> `uv 0.11.21`.
- `git status --short --branch` -> new repository on `main`, all baseline files untracked.
- `git remote -v` -> no output; no remote configured.
- `uv sync --extra dev` -> project-local `.venv`; package and pytest installed.
- First `uv run pytest -q` -> `21 passed`.
- Boundary-hardening `uv run pytest -q` -> `24 passed`.
- `uv run python -m compileall -q src` -> exit 0.
- `uv run change-passport --help` -> exit 0; `prepare`, `finalize`, and `score` displayed.
- `rg` safety scan -> no `shell=True`, HTTP client, API key, or network integration in `src/`; Git subprocess calls use `shell=False`.
- `git status --short --branch` -> all work remains local and uncommitted on a repository with no commits.
- `git remote -v` -> no output; no remote configured.

## Closeout records

Bug IDs: BUG-20260904-001.

Evolution IDs: EVO-20260904-002, EVO-20260904-003, EVO-20260904-004.

## Handoff / next decision

Approved Phase 0-M1 is complete. The next decision is whether to select one bounded real DigitalSelf change, generate a packet, let the current Codex task produce the first real raw brief, and have the owner annotate it. Do not start the 12-sample set or remote-model integration automatically.
