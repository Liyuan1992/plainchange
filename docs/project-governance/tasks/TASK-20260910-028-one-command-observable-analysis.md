# TASK-20260910-028: One-command observable analysis

State: DONE
Tier: high-risk

## Trigger and authority

The owner explicitly asked to implement the six unresolved generic product gaps after confirming that the forty-minute vLLM onboarding path was unacceptable. Earlier standing direction removes repeated confirmation until the bounded implementation is complete. This record narrows the work into three dependent capabilities rather than six repository-specific patches.

## Source facts

- A fixed vLLM analysis completes in about 11 seconds after required Git objects are local, but the first partial-clone attempt spent more than ten minutes in silent object hydration.
- The vLLM target profile and owner-language control document were manually authored; this is not an acceptable new-project onboarding path.
- The full vLLM static snapshot is about 12.7 MB and the single-file report about 12.9 MB because the renderer eagerly serializes and parses all technical detail.
- Existing architecture baseline/delta support is evidence governance, not an operational content cache for repeated parsing.

## Goal

Provide a generic, observable and reusable path that can prepare a new project, produce a source-labelled owner draft, and open a compact offline report without manually writing a complete target profile or parsing all technical evidence at first paint.

## Approved implementation

### A. Analysis job engine

1. Add structured progress events and a durable run receipt with stage start/end, elapsed duration, counts, cache status and failure state.
2. Add a read-only Git object preflight. Missing/promised objects must be reported explicitly; any automatic hydration occurs only in a Change Passport-managed mirror/cache, never by writing to the target repository.
3. Add a content-addressed analysis cache under the configured developer-cache location, with exact repository/commit/profile/parser identities and safe invalidation.
4. Reuse identical snapshots and, where the existing static parser contract permits, unchanged immutable blob results; never treat cache hits as runtime evidence.

### B. Automatic owner draft

1. Generate a deterministic target-profile draft from immutable paths, language mix and conventional repository roles; retain unmatched paths and mark every semantic label as a candidate.
2. Generate a deterministic four-step owner map and source-bound software-control draft from repository/project declarations plus validated change evidence.
3. Preserve an optional model/file-adapter boundary for improved language, with explicit token/cost notice at the UI boundary; no external provider or silent upload is added in this task.
4. Validate the automatic outputs through the existing profile, claim/evidence and software-control contracts. Generated text cannot become observed fact or human approval.

### C. Compact offline report

1. Separate the owner-first model from the full static snapshot before HTML serialization.
2. Gzip the full technical snapshot deterministically and embed it as a content-addressed payload that is decoded only when the user opens technical implementation.
3. Keep a no-network single-file artifact, verify payload integrity before use, and retain a safe unavailable state when browser decompression is unsupported or integrity fails.
4. Preserve the existing fallback report when no owner-control document is supplied.

## Non-goals

- No Git writes, checkout, clean, reset, commit, push, deployment, target runtime, model download, or GPU execution.
- No repository-name/path-specific renderer or analyzer branch.
- No automatic external model call, account integration, live task-window extraction, or claim of human comprehension.
- No approval of an architecture baseline and no deletion of full technical evidence.

## Risks and stop conditions

- Stop if automatic hydration requires mutating the source repository or hiding network activity.
- Stop if cached content is not bound to immutable Git/profile/parser identities or if stale cache can upgrade a claim.
- Stop if automatic owner text is presented as verified runtime behavior or approved project truth.
- Stop if compact delivery discards evidence IDs, weakens tamper detection, or makes technical data silently unavailable.
- Preserve all unrelated dirty-worktree changes.

## Verification plan

- Unit tests for progress/receipt ordering, failure receipts, preflight classification, cache hit/miss/invalidation and target preservation.
- Cross-project automatic-draft tests on synthetic repositories plus fixed Change Passport/FastAPI/vLLM inputs without renderer special cases.
- Compact report tests for deterministic gzip, initial-model exclusion, lazy-decode wiring, integrity metadata, no network, fallback and tamper/error state.
- Re-run the fixed vLLM sample twice and compare cold/warm stage receipts, target fingerprint, report bytes and initial embedded JSON bytes.
- Run the full pytest suite, compileall, JavaScript syntax, HTML parse/offline scans and `git diff --check`.

## Rollback

All new behavior remains additive or optional until verified. Existing `prepare`/`finalize` inputs and uncompressed fallback behavior remain callable. Reverting the new modules/flags restores the previous deterministic pipeline without touching target repositories or generated evidence sources.

## Handoff condition

Complete when the six gaps have implemented, tested generic mechanisms and the fixed vLLM benchmark demonstrates observable stages, cache reuse, automatic drafts and a substantially smaller lazy technical payload. Report remaining model-quality and human-understanding limits separately.

## Implementation result

- Added `change-passport analyze`, which creates a deterministic target-profile draft when none is supplied, validates an automatic raw brief, builds a source-bound four-step software-control draft, and emits the final owner report without a model call.
- Added a durable `run-receipt.json` and terminal JSON progress events for Git preflight, Git evidence, both immutable snapshots, packet generation, artifact writes, owner drafting, completion, and failure.
- Added read-only object preflight. Complete repositories are used directly; shallow/missing histories are hydrated only into a managed bare Git copy. A shallow-clone regression proves the source worktree remains unchanged.
- Added a SQLite content-addressed parse cache keyed by parser version, repository path within the tree, and immutable blob ID. Downstream snapshot/profile/change identities remain separately validated, so a cache hit cannot strengthen a claim.
- Bound the full system snapshot identity into the generator packet and evidence bundle; finalize fails closed if the prepared snapshot no longer matches.
- Removed the full system snapshot from the initial review model. The single-file report now embeds a deterministic gzip/base64 technical payload with compressed and uncompressed SHA-256 values, and decodes it only on technical disclosure (or on the fallback architecture screen).
- Added generator self-report metadata to the output contract and validated brief. The automatic path records `deterministic-local`, model `none`, and candidate-draft mode.

## Verification evidence

- Full suite: 65 tests pass, including failure receipts, cold/warm cache behavior, shallow-history hydration outside the target, automatic model-serving workflow detection under an unrelated repository name, owner-contract validation, technical-payload decode, and target status preservation.
- Fixed vLLM automatic run: 4,501 modules and 21,091 static relationships; 5 populated automatic groups plus the unused explicit fallback; 0 unclassified modules.
- First run after cache introduction: 9.406 seconds total, 6.485 seconds architecture, 4,503 cache misses and 4,499 same-range reuse hits.
- Warm run: 3.808 seconds total, 1.118 seconds architecture, 9,002 hits and 0 misses.
- Report size: prior report 12,926,806 bytes; automatic compact report 3,141,945 bytes, a 75.7% reduction. The 12,616,264-byte full technical snapshot remains separately preserved.
- Automatic vLLM owner draft identifies a model-serving class without a repository-name rule, explains the product as handing inputs to a model and receiving complete or streaming results, and uses the four steps “请求进入软件 → 整理模型输入 → 安排请求和计算资源 → 运行模型并返回结果”.
- Browser screenshot/click acceptance remains not run: two Computer Use connection attempts failed with `nodeRepl.fetch request failed`. No local-file or browser safety boundary was bypassed.

## Remaining limits

- Automatic project semantics are a deterministic candidate classifier, not a replacement for project declarations, a model-assisted refinement, or owner confirmation.
- Cache reuse reduces parsing but the full static relationship index is still rebuilt in memory; large-project warm time is improved, not constant-time.
- The compact offline report still physically contains compressed technical evidence. It reduces bytes and defers decompression/DOM indexing, but it is not a network-loaded sidecar.
- Independent non-coder comprehension, runtime behavior, user impact, the three-sample score gate, and architecture-baseline approval remain pending.
