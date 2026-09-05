# Project facts

Status: Phase 0-M1 and the M1.5 implementation are locally preserved in Git. UI work is frozen after TASK-20260905-008. TASK-20260905-009 corrected the retained-edge delta fact from 95 false modified edges to the one real source-line move. Independent human retelling, three scored samples, and a separate architecture-baseline decision remain pending. The baseline proposal is still unapproved and the consecutive-change reuse evaluation has not started. No remote change, push, packaging, deployment, or DigitalSelf product integration is authorized.

## Purpose

Determine whether a deterministic evidence package, bounded architecture before/after delta, and constrained four-section explanation can improve post-session comprehension and reusable project understanding without inventing intent, confusing self-report with verification, or reading hidden after-the-fact ground truth.

## Entrypoints and main components

- Project governance entrypoint: `docs/project-governance/AGENT_ENTRYPOINT.md`
- Current completed correctness task: `docs/project-governance/tasks/TASK-20260905-009-preserve-and-fix-edge-delta.md` (DONE; formal DigitalSelf artifact and regression verified)
- Frozen final UI refinement: `docs/project-governance/tasks/TASK-20260905-008-intent-context-recovery.md` (DONE; browser verified at 1440 px and 390 px)
- Prior completed refinement: `docs/project-governance/tasks/TASK-20260905-007-progressive-module-layer.md` (DONE; browser verified)
- Prior completed refinement: `docs/project-governance/tasks/TASK-20260905-006-architecture-line-clarity.md` (DONE; browser verified at 1440 px and 390 px)
- Prior completed extension: `docs/project-governance/tasks/TASK-20260904-005-system-architecture-tab.md` (DONE; browser verified)
- Prior implementation task: `docs/project-governance/tasks/TASK-20260904-004-beginner-first-interactive-review.md` (IMPLEMENTING; automated and browser acceptance passed, independent human retelling pending)
- Accepted architecture decision: `docs/project-governance/decisions/ADR-0001-deterministic-evidence-spine.md`
- Accepted architecture decision: `docs/project-governance/decisions/ADR-0002-persistent-architecture-baseline-and-delta.md`
- Business/source PRD: current fast-mode v1.4 amendment in `D:\Dev\Projects\DigitalSelf\design\ui-flows\ai-coding-session-review\01-prd\prd-v1.4-intent-context-draft.md`, SHA-256 `6F51421778859B57E456199C3F699D79877145EC80565BEA8CFBF26B5231D6C8`; it inherits the explicitly confirmed v1.2 contract.
- CLI entrypoint: `src/change_passport/cli.py`
- Manifest and authority contract: `src/change_passport/models.py`
- Read-only Git collector: `src/change_passport/git_evidence.py`
- Generator packet contract: `src/change_passport/generator_contract.py`
- Deterministic validator/renderer: `src/change_passport/validator.py`
- Pipeline and scoring: `src/change_passport/pipeline.py`, `src/change_passport/scoring.py`
- Architecture schemas, extraction, baseline validation, delta, impact, proposal approval, and Mermaid rendering: `src/change_passport/architecture.py`
- Beginner-facing deterministic projection: `src/change_passport/review_model.py`
- No-network single-file renderer and packaged templates/theme: `src/change_passport/html_renderer.py`, `src/change_passport/templates/`, `src/change_passport/assets/`
- Tests: `tests/`

## Commands

| Purpose | Command | Last verified |
| --- | --- | --- |
| Environment inventory | `python --version` | 2026-09-04: Python 3.12.10 |
| Git inventory | `git status --short --branch` | 2026-09-05: local `main` initialized at `a4576ec`; no remote configured |
| Run/help | `uv run change-passport --help` | 2026-09-04: exit 0, three commands listed |
| Test | `uv run pytest -q` | 2026-09-05: 45 passed |
| Compile | `uv run python -m compileall -q src tests` | 2026-09-05: exit 0 |
| JavaScript syntax | `node --check src/change_passport/templates/review.js` | 2026-09-05: exit 0 |
| Formal DigitalSelf prepare + finalize | `uv run change-passport prepare ...` then `finalize ...` | 2026-09-05: exit 0; target status unchanged; 8/0/0 claims; 14 added / 1 removed / 1 modified edge; 1057 system modules / 1768 static edges / 9 groups / 0 unclassified |
| Build/package | Not in approved spike scope | — |

## Hard boundaries

- Phase 0 accepts immutable commit or explicit base/head ranges, not a mutable working tree.
- Target repositories are read-only. The tool must never commit, checkout, reset, clean, run project commands, or write into them.
- Agent summaries and retrospective user claims are claims, not verification evidence.
- Hidden ground truth must be structurally unreachable from the generator input path.
- Missing intent claims, task conversation, test, history, or architecture evidence must remain explicit and source-labelled. An absent intent claim does not imply an absent task conversation; user text, AI interpretation, and user confirmation must remain separate and cannot upgrade one another.
- Architecture baselines are revalidatable projections, not code authority. Only an attributable approved decision may promote a pending proposal; commit, repository, schema, and tracked-path mismatches fail closed.
- Human maps are bounded: all changed nodes remain visible, production consumers precede test/script consumers, and every folded node ID remains explicit in JSON.
- Beginner review JSON and HTML are derived views over the validated brief and the same architecture delta. They cannot create topology, upgrade truth state, or write presentation state back to baseline/evidence.
- Runtime operation is local-only. No source, diff, receipt, or history content is uploaded.
- Generated artifacts live under this project's ignored `artifacts/` directory.
- No UI, plugin, server, account system, remote integration, product packaging, or release is in Phase 0.

## Known unknowns

- The final 12-sample DigitalSelf evaluation set and stratification are not selected.
- Availability and timestamp quality of historical task/test receipts are not inventoried.
- One LLM-assisted real-sample brief has been generated through the provider-neutral file bridge. Its qualitative hidden comparison found no observed contradictions and several useful omissions, but one sample is not evidence of general quality.
- M1 detects identical source paths and copied content, but it does not yet prove that every history/receipt existed before the target change; temporal provenance remains a later contract.
- No owner annotation or numeric score exists yet. The first real sample also exposed that generic safe-unknown rendering can erase a useful evidence-gap explanation (`BUG-20260904-002`).
- The first M1.5 sample identifies 7 changed modules, 36 one-hop static consumers, and 50 unique import-based impact paths; the main map displays 14 prioritized nodes and explicitly folds 32. This still needs owner comprehension review and is not proof of behavioral impact.
- The formal retained-edge field is corrected: commit-only reverification no longer marks an edge modified; the immutable sample has exactly one retained edge whose source location moved (`registry.py` line 8 to line 10). This is a static source-location fact, not proof of runtime behavioral impact.
- The first baseline proposal remains pending. The minimum three-change DigitalSelf sequence cannot start until the owner approves or rejects that candidate.
- External adoption and willingness to pay remain untested and are outside the first implementation phase.
- The formal local HTML has automated identity, parity, safety, size and syntax evidence. Desktop interaction and 390 px responsive browser acceptance passed through a temporary read-only localhost preview. Independent human 30-second retelling is still pending.
- The Why card can now reuse bounded task evidence already included in the prepared packet and distinguish user text from AI explanations. The static report still cannot read a live task window or call a model; the v1.4 connected extraction button remains a product contract, not implemented integration.
- The overall-system architecture tab is implemented as a separate candidate static snapshot, not by relabeling the 46-node/109-edge bounded baseline. It covers 1,057 supported modules and 1,768 static imports across 9 Chinese sections with 0 unclassified paths; this still does not prove runtime, deployment, database, network, dynamic-call, or cross-repository architecture.
- CodeAtlas demonstrated the strongest interaction shell among the tested references. After the owner supplied a registered account, authenticated DigitalSelf click-through confirmed useful persistent navigation and file-to-function drill-down, but also exposed forced auto-replay, unrelated cross-layer "modified" items, Windows path/routing inconsistency, a newly added file without an `ADDED` overlay, and a diff badge that could outlive the actual overlay state. Its interaction model is a PRD input, not architecture authority.
