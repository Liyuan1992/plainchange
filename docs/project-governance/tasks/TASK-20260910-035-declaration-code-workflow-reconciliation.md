# TASK-20260910-035: Reconcile project-declared workflows with code evidence

State: DONE
Tier: high-risk

## Trigger and authority

After reviewing the automatic VideoFactory result, the owner identified that project documentation may itself be wrong and explicitly authorized a general correction plus multi-project validation. This authorizes implementation and local verification only; it does not authorize a commit, push, deployment, remote model request, target-project write, or runtime execution of analyzed projects.

## Source facts

- PRD v2.0 already separates immutable technical facts from project-declared product context and requires file identity, version, and hash for README-derived material.
- `BUG-20260910-017` shows two independent failures: broad overlapping generated section rules collapse classification, and a documented VideoFactory pipeline is replaced by a generic callability template.
- A README is a versioned declaration, not runtime truth. Static imports and text matches also cannot prove runtime order.
- Existing `software-control.v1` supports `project_declared`, `supported_interpretation`, and `unknown` states, but the automatic workflow currently gives every step only the undifferentiated `project_declared` state.

## Goal

Generate an auditable candidate software workflow from bounded project documentation, reconcile each declared step with deterministic code anchors, expose the resulting evidence state to the owner, and keep unsupported order or behavior explicitly unverified.

## Approved implementation plan

1. Read only small, versioned root declaration files from the fixed Git commit. Extract a bounded project-purpose candidate and explicit workflow candidates from clearly labelled workflow/pipeline sections.
2. Bind every extracted declaration to commit/path/blob hash. Match workflow steps only against deterministic source-path and bounded orchestrator/entrypoint text anchors.
3. Track declaration support and order support separately. A documentation-only step remains `仅项目说明`; matching code becomes `代码支持`; order becomes supported only when one orchestrator contains the declared step anchors in sequence. No automatic result becomes runtime-confirmed.
4. Generate mutually discriminating section rules from classified files instead of reusing one package prefix across multiple categories. Ambiguous directory prefixes must fall back to exact paths or `unclassified`, not first-match success.
5. Propagate the evidence label, note, and source references into `software-control.v1` and render them on the working map and inspector without changing Git/architecture authority.
6. Add repository-name-neutral fixtures for correct documentation, stale/unsupported documentation, missing documentation, overlapping source trees, and ordered versus unverified orchestration.
7. Re-run the unchanged automatic path on Change Passport, VideoFactory, and an available external framework sample. Compare semantic output, coverage, timing, and exact target status preservation separately.

## Non-goals

- No claim that README text, static text matches, imports, or orchestration source prove actual runtime behavior.
- No automatic approval of a workflow, no mutation of target repositories, no VideoFactory/FastAPI/vLLM name branch, and no user-specific wording exception.
- No broad documentation crawler, embeddings, model call, runtime tracing, package execution, or replacement of the existing evidence validator.
- No requirement that every repository expose a workflow; absence or ambiguity must remain visible.

## Risks and fail-closed rules

- Natural-language workflow extraction can over-match examples. Restrict extraction to explicit workflow/pipeline headings and bounded list/fence forms.
- Token matching can produce false support. Require stable identifier-like step keys and bounded source anchors; otherwise retain `仅项目说明`.
- Declared ordering can disagree with code. Do not silently choose one; expose `顺序未验证` or a conflict note.
- Exact-path classification may make profiles larger. Keep the generated profile below its existing size limit and measure the real samples.
- Stop if correctness would require a target-specific branch or if the output promotes a declaration to observed fact.

## Verification plan

- Focused unit tests for extraction, hashing, support classification, ordered orchestration, stale documentation, and disjoint section assignment.
- Contract tests for optional workflow evidence fields, canonical identity, HTML escaping, and owner-map rendering.
- Full Python test suite, compileall, JavaScript syntax, `git diff --check`, and repository-name scan.
- Fixed-range analyses for at least three unrelated projects, with source/target status hashes captured before and after.
- Manual semantic inspection must report useful conclusions, mismatches, and remaining unknowns separately; structural pass counts do not establish human comprehension.

## Rollback

The new declaration evidence fields are optional and existing manual profiles retain their current defaults. If automatic extraction fails, the generator returns the existing generic candidate with an explicit no-declaration/unknown boundary rather than emitting partial asserted workflow facts.

## Handoff condition

Complete when generic code, tests, three-project evidence, UI labels, and governance records agree on the distinction among project declaration, code support, order support, and runtime unknown.

## Result

- Added a fixed-commit declaration reader for bounded root README material. Every accepted purpose/workflow source keeps its commit, path, and SHA-256 identity.
- Reconciled declared steps and declared order separately. A step can be `代码支持` while the overall order remains `顺序部分支持` or `顺序未验证`; none of these states claim runtime execution.
- Replaced overlapping automatic area rules with mutually discriminating prefixes plus exact-path fallbacks. No repository-name branch was added.
- Made current-change mapping fail closed. A workflow step is highlighted only when changed files map to that step uniquely; ambiguous vLLM and FastAPI changes no longer receive a fabricated business-step overlay.
- Propagated evidence labels and notes into the owner map and inspector. The current four-stage context remains visible while a declared detail group expands and collapses inline.
- Re-ran the same implementation on VideoFactory, vLLM, and FastAPI. VideoFactory exposes seven README-declared steps with code support and partially supported order; vLLM and FastAPI retain generic candidate workflows with unverified order.

## Verification result

- 78 automated tests pass; Python compilation, JavaScript syntax, diff checks, and the source repository-name scan pass.
- Real Edge DOM interaction at desktop width shows four overview nodes, one unambiguous changed overview group, two inline detail nodes, visible `代码支持` badges, successful collapse, and no document/canvas horizontal overflow.
- The same report at 390 px has `scrollWidth == viewport == 390`, four overview nodes, one-column layout, and no document/canvas horizontal overflow.
- VideoFactory target status remains `C1B1230B1902F3220E463F7AC0EDED95D867EF9B5D0FB061D9D21E8963A3B4BA`; vLLM remains `03392EBE75416C3ADD2E4D5F062FC0E3AF9D73E2AA1DC553F10DE839E71D4F39`. Both match their pre-run receipts. FastAPI is a bare repository and both fixed revisions still resolve exactly.
- This is structural and semantic regression evidence, not independent human comprehension, runtime correctness, or owner approval of the generated workflow.
