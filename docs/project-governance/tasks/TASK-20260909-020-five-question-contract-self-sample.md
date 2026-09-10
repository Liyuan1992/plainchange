# TASK-20260909-020: Five-question contract and self-hosted text sample

State: DONE — CONTRACT AND SELF-HOSTED TEXT SAMPLE VERIFIED
Tier: standard

## Trigger and authority

PRD v2.0 requires Change Passport to answer five owner questions before adding more UI. The owner confirmed the exact PRD and the stated next action with “确定” on 2026-09-09. The immediately preceding handoff explicitly said that confirmation would authorize freezing the five-question data contract and creating a Change Passport self-hosted text sample.

This is the approved implementation boundary for this task. It does not authorize the later UI stage or any remote integration.

## Facts and assumptions

- The retained self-hosted sample is fixed to `a4576ec082d88ca935496919992fcc3837b79ac7..688fc5f094ca96703d5013da474cef6a5091bd5d`.
- Its validated brief contains a verified change claim, a verified architecture claim, a verified test-receipt claim, and an unknown history claim.
- Its target profile declares how Change Passport works and is bound by SHA-256.
- Static impact paths do not identify a user role or prove runtime behavior.
- A text sample may use plain-language editorial wording, but every conclusion must retain state and source pointers. It is a product-validation candidate, not an automatically generated production artifact.

## Approved plan

1. Define a versioned, machine-readable `software-control.v1` contract for the five questions, software working map, evidence depths, answer states, source identities, audience impact, unknowns, and recommended-but-not-run actions.
2. Write a human-readable contract guide that explains authority and downgrade rules without requiring JSON knowledge.
3. Create a self-hosted JSON sample using only the retained Change Passport brief, beginner review, target profile, and their fixed identities.
4. Render the same sample as a first-screen text document whose five answers do not require code reading.
5. Validate JSON syntax, schema conformance, source IDs, exact source hashes, question order, action status, plain-language restrictions, and Markdown/JSON parity.
6. Record observed limitations and stop before UI implementation or a simulated “independent user” result.

## Planned files

- `docs/product/software-control-v1-contract.md`
- `docs/product/schemas/software-control.v1.schema.json`
- `docs/product/samples/change-passport-self-688fc5f.software-control.json`
- `docs/product/samples/change-passport-self-688fc5f.software-control.md`
- Governance status and append-only evolution record at closeout.

## Non-goals

- No change to `src/`, templates, target-profile schema, CLI, pipeline, HTML, CSS, or JavaScript.
- No remote model, task-window/account read, source upload, or Token use.
- No claim that this manually grounded sample proves automatic generation quality.
- No self-authored independent-human score or invented user-test result.
- No second/third sample, UI implementation, commit, push, package, deploy, or baseline decision.

## Risks and stop conditions

- Stop if a plain-language sentence cannot be tied to a retained claim, limitation, task excerpt, or versioned project declaration.
- Stop if “not observed” becomes “confirmed unchanged”.
- Stop if a proposed verification action is presented as already completed.
- Stop if the sample requires adding Change Passport-specific branches to production code.
- Stop after contract and sample verification; human retelling is a real external acceptance step.

## Verification plan

- Validate the sample against the checked-in JSON Schema.
- Recompute and compare the four source artifact SHA-256 values.
- Assert exactly five ordered question IDs and four permitted statement states.
- Assert all recommended actions use `recommended_not_run`.
- Assert source claim/evidence/component IDs are subsets of the retained artifacts.
- Assert Markdown contains the same five answer texts and action titles as JSON.
- Scan the first-screen section for banned implementation vocabulary.
- Run `git diff --check` and report existing line-ending warnings separately.

## Handoff condition

Complete when the contract and one self-hosted text sample are reproducible and source-bound. Stop before UI design. The owner or a genuinely independent participant must perform the comprehension test; automated checks do not substitute for it.

## Result and observed verification

The first semantic slice is complete without changing production code or UI:

- Human-readable contract: `docs/product/software-control-v1-contract.md`.
- JSON Schema: `docs/product/schemas/software-control.v1.schema.json`, SHA-256 `6CFEB19B4767EA34AEEA37F2FDA9F39B3460B926B2E9011ADE4D06E76F43B1BD`.
- Source-bound JSON sample: `docs/product/samples/change-passport-self-688fc5f.software-control.json`, file SHA-256 `286BFB0B12DAB23A5106B84BF9F5B710F859220843D191129A313D0884D1E216`, canonical `control_identity` `21dcff469d5b0faf297dbe890eecd1e68b8eca939e18bf8b28f905c0561dd9cc`.
- First-screen Markdown sample: `docs/product/samples/change-passport-self-688fc5f.software-control.md`, SHA-256 `3CD92D24F50ACF0AFCAB88EA10DD314DF52BFA58798126537C4A1D3B7BC1BA2F`.

Observed checks:

- PowerShell `Test-Json` accepted the sample against the checked-in Draft 7 schema.
- Exactly five ordered questions and three recommended actions were present; all actions remained `recommended_not_run`.
- Every claim, evidence, and software-map component ID used by a five-question answer was a subset of the retained source artifacts.
- The four recorded artifact SHA-256 values matched the current retained files, and brief/review identities matched their source objects.
- Canonical identity recomputation matched `control_identity`.
- Markdown contained the exact five answer texts and all action titles from JSON.
- The marked first-screen region contained zero occurrences of the banned implementation vocabulary scan (`Git`, `Diff`, `AST`, `OpenAPI`, `API`, `import`, `module`, controller/service/repository/baseline, 模块, 依赖, 函数, 提交号, 静态).
- `git diff --check` passed with only pre-existing LF/CRLF normalization warnings.

Owner review then found that the first answer summarized the product but did not visibly show how the software works. The correction now exposes the same five ordered software steps from JSON directly in the first-screen Markdown as a plain-language input-to-human-decision flow. Verification requires all five steps and four visible down connectors; see `BUG-20260909-002`.

## Honest limitation

This is a manually edited, source-constrained product sample. It proves that the contract can preserve authority while producing a shallower explanation; it does not prove automatic generation quality or real user comprehension. `human_comprehension_status` remains `pending_independent_participant`. No UI, provider, account access, commit, push, deploy, or baseline decision was performed.

Subsequent owner review found the corrected workflow visible but rejected the overall language depth and equal-weight first-screen hierarchy. `TASK-20260909-022` supersedes this task's current sample identity and hashes; the values above remain the observed historical result of this task.
