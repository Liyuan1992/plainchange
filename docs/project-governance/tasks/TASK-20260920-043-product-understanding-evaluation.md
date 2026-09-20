# TASK-20260920-043: Understand projects and identify actionable limitations

State: DONE (implemented and verified locally; independent reader acceptance pending)
Tier: standard

## Authorization

Owner approved the bounded plan on 2026-09-20: “好 批准”. Evaluate memdsl,
VideoFactory and DigitalSelf at fixed commits, improve ordinary-reader explanations
and evidence-linked issue diagnosis, compare actual reports, and retain old features.
Target repositories remain read-only. Use the signed-in local Codex text provider.
No commit, push, publication, paid API substitution or target business execution.

## Baseline and implementation plan

- PlainChange starts at addb7bac with a clean worktree. Full baseline tests started.
- Existing flow v2 validates graph and citation ranges but has no structured reader
  brief or findings contract. Prior participant comprehension is not established.
- Record target HEAD/worktree fingerprints, run current maps, independently inspect
  selected claims against fixed source and retain all failed attempts.
- Add a cited reader brief (audience, purpose, usage, result and limits), actionable
  suspected risks / verification gaps, and plain-language presentation with source
  disclosure. Model output cannot label a defect as independently confirmed.
- Keep legacy maps and change reports usable. Reject invalid evidence. Protect
  common credential patterns before source excerpts enter model packets.
- Compare the same source context before/after the additional assessment; disclose
  that this controls source variability rather than proving exhaustive coverage.
- Verify contract failures, old report compatibility, full suite, actual model runs,
  browser interactions at desktop/narrow widths and an independent source audit.
- Deliver three reports plus a product evaluation and a five-question reader test.
  Agent review is not a substitute for a nontechnical participant's acceptance.

## Observed verification

- Baseline 185 tests passed; final suite: 207 passed in 181.23 seconds. Wheel and
  sdist built with `uv build`; JS syntax and Git whitespace checks passed.
- Three fixed-source baseline maps generated with local Codex; assessed and
  counter-reviewed with at most two additional selection rounds sharing the
  400 KB source-text budget. 11 initial candidates became 6 retained findings.
- Four candidates were withdrawn as unsupported/normal behavior; one duplicate
  merged. DigitalSelf counter-reading found task-local ContextVar properties and
  failure-aware UI handling, invalidating two initial allegations.
- VideoFactory first assessment failed a reversed citation range; preserved the
  raw attempt and failed comparison receipt. The counter-reviewed report corrected
  the reference and passed validation without relaxing citation rules.
- Final real `plainchange understand` CLI run on memdsl succeeded: 11 provider
  requests, 17 files / 48 excerpts, 291,889 bytes; three different retained risks.
  Provider receipt elapsed times sum to 498.13 seconds; this is not an instant
  workflow. Findings still require independent runtime verification.
- Delivery uses VideoFactory-reviewed (4 risks), DigitalSelf-reviewed (1 risk,
  1 evidence gap) and memdsl-end-to-end (3 risks), with baseline/comparison records
  retained separately. No accuracy/recall claim is made across different excerpts.
- Four reports passed real Edge at 1440/390, including guide, citations, journey,
  findings, challenge history, graph, scenario and backtracking. Final guided
  entry also passed switching between system and existing change modes.
- All 181 excerpt occurrences across those four reports match fixed Git blob,
  path, line content and SHA-256. Overlapping excerpts are not unique coverage.
  All three target HEAD/status/tracked-diff fingerprints unchanged.
- Independent static review corroborated the relevant cache/manifest/query budget
  code and the DigitalSelf counterevidence; no target project business execution.
  Human five-question test is prepared, not completed.
- Outputs: `D:/Dev/Projects/plainchange-reports/product-evaluation-20260920/`.
  Local tests/screenshots/builds: `artifacts/product-evaluation-20260920/`.
- `ds` unavailable. No unrelated PlainChange changes existed at baseline; target
  projects' pre-existing dirty changes preserved. No commit, push or publication.

See `TASK-043-product-evaluation.md` for qualitative findings, sampling limitations,
remaining semantic-citation limits and why a zero-finding sample is not certification.
