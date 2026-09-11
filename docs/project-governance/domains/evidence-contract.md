# Evidence contract

## Active source-backed constraints

- Target repositories are read-only. Git collection uses fixed argument arrays, `shell=False`, explicit timeouts, and `GIT_OPTIONAL_LOCKS=0`. Source: ADR-0001, EVO-20260904-003.
- The generator can see only `generator-packet.json`. The packet omits repository paths, manifest paths, hidden-ground-truth IDs, paths, and content. Source: ADR-0001, EVO-20260904-003.
- Full-experience model generation is explicit and split into fixed-revision project understanding followed by change interpretation. The active adapter reads a user-selected OpenAI-compatible provider config, keeps credentials environment-only, records sanitized input/output identities, timing and token use, and fails without silent deterministic fallback. Project context uses declarations plus bounded code outlines; change context uses a bounded evidence subset while the complete local packet still performs final validation. The model's default owner map has at most six business-level items, while technical implementation remains in the evidence drill-down. A source-bound role candidate can identify who may need to pay attention, but it remains an unverified user-impact candidate. Model completion is not evidence correctness or human approval. Source: ADR-0004, ADR-0005, EVO-20260910-016, EVO-20260911-035, EVO-20260911-036, EVO-20260911-037. ADR-0003 and EVO-20260910-015 remain historical evidence of the earlier local experiment.
- Input evidence and hidden ground truth cannot share the same resolved file path or exact content hash. Source: EVO-20260904-003.
- Raw model claims are untrusted. Unknown evidence IDs are rejected; missing authority classes and invalid section/scope combinations are downgraded to safe `unknown` text. Source: ADR-0001, EVO-20260904-003.
- A verified user-behavior claim requires both `original_task` and `git_fact`; test status requires `actual_test_receipt`; a history relation requires both `approved_history` and `git_fact`. Source: ADR-0001, EVO-20260904-003.
- `finalize` and `score` may write only inside the prepared artifact directory. Source: EVO-20260904-003.
- M1.5 architecture facts come from immutable Git tree/blob identities and supported Python/JavaScript static imports. The model may explain them but cannot add a verified node, edge, or impact path. Source: ADR-0002, EVO-20260904-008.
- `modified_edge_ids` compares retained-edge evidence locations after masking only the Git commit component. A new verification commit alone is not a topology change; source-path or line movement still is. Source: BUG-20260905-013, TASK-20260905-009.
- An approved baseline requires matching repository/base commit/schema/tracked blob identities plus an attributable approval decision bound to the exact proposal SHA-256. Candidate, tampered, or stale baselines fail closed. Source: ADR-0002, BUG-20260904-006, EVO-20260904-008.
- Mermaid and the graph-first Markdown section render from the same validated delta JSON. Display folding is explicit and retains omitted IDs in JSON. Source: ADR-0002, BUG-20260904-004, EVO-20260904-008.
- `beginner-review.json` and `review.html` are deterministic derived views over the validated brief and the same `ArchitectureDelta`. They preserve claim/node/evidence identity, may only maintain or lower truth state, retain every folded ID, and cannot write view state back into evidence or baseline authority. Source: TASK-20260904-004, BUG-20260904-009.
- `system-architecture.json` is a candidate full supported-code static snapshot for the frozen Head. Every parsed module belongs to exactly one confirmed display section, every cross-section relationship retains its source edge IDs exactly once, and the change overlay reuses `ArchitectureDelta` IDs. It is not an approved baseline or proof of runtime/deployment/database/network architecture. Source: TASK-20260904-005, EVO-20260904-014.
- A `target_profile` is a strict, versioned display/grouping asset. Its raw file SHA-256 and ID are embedded in the snapshot, and every group source is bound to that same identity. Profiles may classify paths and control reader-facing labels, terminology, brand, module areas, and an explicitly profile-sourced product/process architecture; they cannot change Git facts, topology, impacts, claims, or baseline authority. Configured process arrows must not be labelled as static imports or runtime order. Source: TASK-20260905-010, TASK-20260905-011, EVO-20260905-019, EVO-20260905-021.
- An optional `software-control.v1` document supplies the owner-language projection; the renderer cannot invent its software story. An ordered workflow has exactly four overview nodes covering every detailed step once. A non-sequential capability map may expose one to ten overview capabilities, must have no directional flows, and uses `not_applicable` rather than an unverified order. A changed overview node must still contain the directly evidenced changed detail node. Evidence-state explanations, unchecked owner actions, and same-canvas detail expansion are presentation data only and cannot upgrade a claim or record an approval/test result. Source: TASK-20260909-024, TASK-20260909-025, TASK-20260910-042, EVO-20260909-006, EVO-20260909-007, EVO-20260910-027.
- The fixed vLLM cross-project sample preserves the same source-binding and renderer contract at 4,501 supported modules and 21,091 static relationships: 9 profile-declared groups, 0 unclassified modules, four owner steps covering eight detail steps once, and one changed owner step bound to the prepared patch/node evidence. This is portability evidence for the contract, not runtime or automatic-generation evidence. Source: TASK-20260909-026, EVO-20260909-008.
- Owner workflow projections must distinguish request-entry types from startup/configuration actions, describe scheduling without implying unsupported model selection, and preserve complete versus optional streaming delivery where the target sources support both. Interactive selection and the current-change overlay remain separate states and require a nearby textual legend, not color alone. Source: TASK-20260910-027, BUG-20260910-008, EVO-20260910-009.
- Operational cache entries contain only parser-version/path/immutable-blob parse facts. Repository, commit, profile, snapshot, delta, packet, and claim identities remain validated outside the cache; cache hits cannot become evidence or upgrade semantic truth. Missing Git objects may be hydrated only in a managed bare copy outside the target worktree. Source: TASK-20260910-028, BUG-20260910-009.
- Automatic profiles and owner language are explicit candidate projections. They may classify conventional project shapes and translate verified change locations into owner language, but they remain `project_declared` or `supported_interpretation`, preserve runtime/user-impact unknowns, and require owner confirmation. Generator metadata is self-report, not Git or runtime evidence. Source: TASK-20260910-028, EVO-20260910-010.
- Root README purpose and workflow material is a versioned project declaration, never repository truth. Accepted material must retain fixed commit, path, and SHA-256 identity. Per-step code support, declared-order support, and runtime confirmation are independent states; an ambiguous change-to-workflow match must produce no changed-step overlay. Automatic area rules must be mutually discriminating rather than relying on broad first-match prefixes. Source: TASK-20260910-035, BUG-20260910-017, EVO-20260910-018.
- When a fixed README describes parallel capabilities rather than an ordered process, bounded bold-list groups and summary tables may become a source-bound capability candidate. Code-anchor matching is separate per capability; a declaration with no code anchor remains `declared_only`. An overview may expose internal candidate responsibilities only inside its explicit path or exact-identifier code scope, only when at least two distinct responsibility families are supported, and without implying order. These children are `code_discovered`, not project declarations or runtime facts. Weak generic tokens, prefix resemblance and a single repeated child cannot create an expansion. If no usable declaration exists, code-derived areas are orientation only and cannot receive a business change-location overlay. Repository, product and path names must not select this behavior. Source: TASK-20260910-042, TASK-20260910-043, BUG-20260910-030, BUG-20260910-031, EVO-20260910-027, EVO-20260910-028.
- The generator packet binds the complete system snapshot identity. The offline HTML initial model excludes the full snapshot and carries a deterministic gzip technical payload with pre/post-compression hashes; the browser must verify and decode it only on technical disclosure, and failure must stay visibly unavailable. Source: TASK-20260910-028, BUG-20260910-010.
- The owner overview is a persistent context layer: opening one workflow node may reveal only its source-declared `detail_node_ids`; opening one capability may reveal only its evidence-bound `code_discovered` children. Expansion cannot replace the overview, invent membership or order, duplicate a one-to-one parent, or change claim strength. Inspector text and changed/selected presentation still project from the same source node. Source: TASK-20260910-030, TASK-20260910-043, BUG-20260910-013, BUG-20260910-031, EVO-20260910-013, EVO-20260910-028.
- Cross-tab navigation from a change conclusion to the system map is allowed only when exactly one changed detail node belongs to exactly one validated overview node. The renderer may select, expand, focus, scroll, and transiently mark that existing node; it cannot parse prose to guess a target or create a new change-to-system fact. System-view upstream/downstream text derives only from validated map edges and must preserve the declared/static-versus-runtime boundary. Source: TASK-20260910-036, BUG-20260910-020, EVO-20260910-019.
- Added exception raises, explicit non-zero returns, and callable-signature changes may be retained as syntactic Git behavior signals with path, symbol, condition, and patch identity. They can prioritize a conditional stop/failure explanation and a two-case owner check, but cannot prove reachability, runtime execution, breaking impact, or user impact. When the deterministic generator reports `model=none`, unperformed behavior/user-impact interpretation is `还没判断`, never `目前没发现`. Source: TASK-20260910-037, BUG-20260910-021, EVO-20260910-020.
- Owner-facing evidence labels must distinguish `来自项目说明` from `找到对应代码`. A matching source location means only that the declared step has a fixed-version code anchor; it does not mean the declaration is correct, the code passed, the order ran, or the behavior was verified. Source: BUG-20260910-022.
- Report localization is presentation state, not evidence. The offline reader may
  choose or remember `zh-CN`/`en` and translate PlainChange-owned interface and known
  deterministic-template text, but embedded review/control/technical JSON identities
  remain unchanged. Project declarations, task quotations, technical evidence, and
  single-language authored explanation stay in their source language. Source:
  TASK-20260910-039, EVO-20260910-023.
- Automatically drafted owner messages use identity-bound presentation descriptors:
  stable message keys plus bounded arguments may target only approved text fields.
  They cannot target identity, truth state, basis, evidence, source references or
  topology. English deterministic projections therefore do not require a target-
  specific phrase table; project-authored wording remains explicitly source-language,
  and a complete reviewed pack may override the derived projection. Source:
  TASK-20260911-044, BUG-20260911-033, EVO-20260911-029.
- PlainChange-owned architecture wording in the compact review and lazy technical
  payload must project from stable map kind, snapshot status, automatic-profile
  origin and category/responsibility IDs. The path patches are bound to the
  review identity and may change presentation text only; project declarations,
  technical evidence, source references, topology and truth states remain
  canonical. Source: TASK-20260911-045, BUG-20260911-035,
  EVO-20260911-031.
- English-mode localization acceptance is measured on text that is actually
  visible in each owner tab, including lazy technical disclosure, rather than by
  searching the offline HTML source that intentionally contains both locale
  resources. PlainChange-owned decorative marks must be language-neutral; the
  native `中文` language-choice label is an intentional selector value, not
  untranslated report prose. Source: TASK-20260911-046, BUG-20260911-036,
  EVO-20260911-032.
- Browser-language acceptance must enumerate disclosure and interaction states,
  not only the initial viewport. For the change view this includes opened
  technical details, task context, Before/After/Changes-only modes and node
  inspectors; findings are accumulated across states. PlainChange-owned dynamic
  prose is projected from stable semantic fields, while project quotations,
  paths and evidence retain source language. Source: TASK-20260911-047,
  BUG-20260911-038, EVO-20260911-033.

## Regression checks

- Manifest and copied-content leakage: `tests/test_models.py`.
- Immutable read-only Git collection and truncation: `tests/test_git_evidence.py`.
- Generator-packet exclusion and tamper detection: `tests/test_generator_contract.py`.
- Evidence-ID, authority, section/scope, and safe-unknown validation: `tests/test_validator.py`.
- File-bridge end to end and artifact-path containment: `tests/test_pipeline.py`.
- Precision, recall, unsupported, authority, and leakage metrics: `tests/test_scoring.py`.
- Baseline approval/hash binding/staleness, incremental reuse, Python/JavaScript import impact, retained-edge reverification versus source-line movement, graph parity, display folding, and target-repository preservation: `tests/test_architecture.py`.
- Batched immutable Git blob reads: `tests/test_git_evidence.py`.
- Beginner-summary truth/identity/omission checks: `tests/test_review_model.py`.
- Single-file HTML escaping, no-network, theme, and embedded-identity checks: `tests/test_html_renderer.py`.
- Full-system snapshot identity, complete assignment, source-edge aggregation, review embedding, top-level architecture tab, and formal DigitalSelf browser smoke: `tests/test_architecture.py`, `tests/test_pipeline.py`, `tests/test_html_renderer.py`, TASK-20260904-005.
- Strict target-profile parsing, profile SHA/group-source binding, profile-neutral architecture facts, profile-sourced conceptual architecture, dynamic reader branding, and absence of repository-specific consumer branches: `tests/test_target_profile.py`.
- Software-control canonical identity, source binding, ordered four-step coverage, non-sequential capability coverage, changed-node binding, optional pipeline input, collapsed explanation, progressive graph controls, fallback, and no-network HTML: `tests/test_software_control.py`, `tests/test_pipeline.py`, `tests/test_html_renderer.py`.
- Managed shallow-history hydration, progress/failure receipts, cold/warm cache reuse, automatic cross-name project-class detection, packet/snapshot binding, and compressed technical-payload recovery: `tests/test_git_evidence.py`, `tests/test_pipeline.py`, `tests/test_auto_draft.py`, `tests/test_html_renderer.py`.
- Fixed-commit declaration extraction, source hashing, workflow/capability/code reconciliation, order support/conflict handling, disjoint automatic areas, fail-closed change mapping, and evidence-state rendering: `tests/test_auto_draft.py`, `tests/test_software_control.py`, `tests/test_pipeline.py`.
- Conditional raise/non-zero-return/signature signals, hunk-context isolation, truncation limits, packet inclusion, no-model state language, and two-case owner checks: `tests/test_behavior_signals.py`, `tests/test_generator_contract.py`, `tests/test_pipeline.py`.
- Two-language locale selection, source-data preservation, public README parity,
  target-name neutrality, and real browser switching: `tests/test_html_renderer.py`,
  `tests/test_public_docs.py`, `tests/test_target_profile.py`,
  `scripts/verify-review-i18n.cjs`.

## Known gaps

- A real compatible-provider model-first run now succeeds on the fixed ChestnutDogAiThink sample and corrects its dominant product story, but one sample does not establish a long-term default model, stable gateway behavior, acceptable token cost or independent beginner comprehension. Model output still cannot upgrade declaration or runtime truth.
- Historical evidence has no cryptographically enforced “existed before base/head” provenance yet.
- Exact copied content is blocked, but paraphrased answer leakage requires human evaluation.
- No real DigitalSelf sample or real model output has been scored.
- Static `imports` proves a dependency edge, not runtime execution or behavioral impact; dynamic imports, reflection, configuration injection, and runtime routing remain unknown.
- The first M1.5 DigitalSelf baseline proposal is not approved, so the required real consecutive-change reuse sequence remains pending owner review.
- Browser layout/interaction acceptance passed for the formal generated HTML on desktop and 390 px responsive layout. An independent human 30-second retelling remains pending; passing automated and browser rendering tests is not equivalent to that human outcome.
- The first Change Passport self-hosted result is intentionally a known-context sample; it needs external repository samples before it can support a generalization claim.
- The ten-second/four-step owner UI, inline detail interaction, and automatic candidate path are structurally verified. Real Edge screenshot/click validation passes for the fixed vLLM report, but independent comprehension and owner acceptance of automatically drafted language remain untested.
- The silent partial-clone and 12.9 MB eager-report defects now have generic implementations and vLLM measurements. Remaining scale work is narrower: full relationship indexes are still rebuilt in memory, and a single offline file still physically carries compressed technical evidence. Source: BUG-20260910-009, BUG-20260910-010, TASK-20260910-028.
- README extraction remains intentionally bounded to explicit Markdown workflow/pipeline headings plus structured capability lists and summary tables. Free-form prose, RST capability parsing, cross-document reconciliation, runtime tracing, and independent owner comprehension remain unimplemented. Capability maps describe parallel areas, not call order.
- The fixed ChestnutDogAiThink full-stack sample exposes four additional open
  boundaries: a syntactic stop signal can eclipse the dominant product change;
  a multi-column capability table can select a numeric count as description;
  Vue single-file components and MJS tests are outside current structure
  coverage; and tracked dependency trees can pollute project architecture.
  Honest unknown states do not make that owner explanation acceptable. Source:
  TASK-20260911-048, BUG-20260911-039, BUG-20260911-040,
  BUG-20260911-041, BUG-20260911-042.

## Source index

- ADR-0001: three-layer evidence/generator/validator architecture.
- EVO-20260904-002: owner-approved correction from model-free to constrained-model generation.
- EVO-20260904-003: locally verified Phase 0-M1 implementation.
- ADR-0002: approved bounded architecture baseline/delta authority contract.
- EVO-20260904-008: M1.5 core implementation and first real graph-first sample.
- EVO-20260904-014: complete supported-code system snapshot and browser-verified overall architecture tab.
- EVO-20260905-019: target-profile portability and self-hosted showcase decision.
- EVO-20260905-021: product-architecture-first map and static implementation-layer separation.
# Report-body translation boundary (TASK-040)

`report-translations.json` binds a complete set of allowed owner presentation
strings to `control_identity`. A translated projection must never replace the
canonical software-control data or change IDs, references, states or graph edges.
Coverage/identity validation does not validate translation meaning. Quoted source
evidence stays original. Missing packs are disclosed; stale packs fail closed.
New projects require reviewed translations; no hidden network translation occurs.
