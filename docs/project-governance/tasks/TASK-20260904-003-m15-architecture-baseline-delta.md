# TASK-20260904-003: M1.5 bounded architecture baseline and delta

State: IMPLEMENTED — EXPERIENCE FOLLOW-UP MOVED TO TASK-20260904-004; BASELINE APPROVAL PENDING
Tier: standard

## Trigger and authority

The owner concluded after the first DigitalSelf run that a prose-only brief is insufficient and explicitly requested a PRD revision. PRD v1.1 and ADR-0002 were confirmed on 2026-09-04, and the later explicit instruction “开始实现 M1.5” authorized the bounded implementation in this task.

## Goal

Add a graph-first, evidence-backed local architecture review that lets a person see changed topology and direct impact at a glance, while letting later runs reuse an approved module-level baseline instead of re-understanding the whole project.

## In scope after approval

1. Add schema models for `ArchitectureBaseline`, nodes, edges, `ArchitectureDelta`, impact paths, and `BaselineProposal`.
2. Build a deterministic Python/JavaScript minimum extractor for the selected DigitalSelf sample at module/component/responsibility/interface level.
3. Verify baseline repository/base identity, path/structure hashes, schema version, source refs, and per-node `last_verified_commit`; fail closed on stale/invalid input.
4. Compute added/removed/modified nodes and edges plus verified one-hop impact from changed nodes.
5. Render Mermaid and the existing four-section Markdown from one validated delta JSON.
6. Store proposal and decision artifacts separately; do not update approved baseline without an attributable human decision.
7. Re-run the first immutable DigitalSelf sample, then a minimum three-change consecutive sequence to test baseline reuse and invalidation.

## Non-goals

- Full symbol-level call graph, full repository knowledge graph, multi-language generalization, or a five-layer whole-project diagram.
- Desktop/Web/IDE UI, interactive graph navigation, cloud service, team roles, remote source upload, automatic code changes, or release packaging.
- Letting an LLM establish verified nodes/edges, approve a baseline, or override Git/code evidence.
- Replacing the evidence, history, annotation, or hidden-ground-truth contracts already implemented in M1.

## Planned implementation order

1. Freeze JSON schemas and fixtures, including stale/invalid/baseline-unapproved cases.
2. Add deterministic baseline identity and invalidation tests before extraction behavior.
3. Implement bounded node/edge extraction and delta calculation for the selected sample.
4. Add impact-path limits and explicit unknowns for dynamic/unsupported relations.
5. Add validator cross-checks for graph, claims, evidence refs, and proposal authority.
6. Add deterministic Mermaid/Markdown rendering from validated JSON.
7. Run the first sample and owner review before attempting the consecutive-change reuse evaluation.

## Acceptance conditions

- The first DigitalSelf sample produces one validated delta JSON, one Mermaid before/after map, one four-section explanation, and one separate baseline proposal.
- Every changed node/edge and displayed impact path has direct evidence refs; unsupported dynamic behavior is unknown, not a verified edge.
- Mermaid and prose contain no verified topology absent from the validated JSON.
- A mismatched commit/schema/path hash produces `baseline_invalid` or `baseline_stale` and never silently reuses the baseline.
- A pending/rejected proposal does not alter the next approved baseline.
- In a minimum three-change sequence, the run reports reused, invalidated, and reparsed scope; unchanged approved nodes need not be rebuilt, while changed-neighborhood nodes are reverified.
- The owner can identify changed responsibility/interface, direct affected nodes, and unknown impact without rereading every changed file. If not, M1.5 fails rather than expanding to a full graph platform.
- Existing M1 fidelity and target-repository read-only tests remain green.

## Verification plan

- Unit/property tests for schema identity, baseline invalidation, deterministic delta, bounded traversal, proposal separation, and graph/JSON parity.
- Existing `uv run pytest -q` suite plus new M1.5 tests.
- Reproduce immutable sample `d78f78b..430c342` without writing to DigitalSelf and compare target worktree status before/after.
- Owner review of the rendered graph and impact explanation; no self-score substitutes for this acceptance.

## Stop conditions

- Revised PRD is not confirmed.
- Useful output requires a full multi-language AST/symbol graph or unbounded traversal.
- The extractor cannot make direct node/edge evidence inspectable.
- Baseline drift cannot be detected deterministically.
- The graph makes comprehension worse or still forces a full file-by-file review.

## Approval evidence

PRD v1.1 and ADR-0002 were confirmed by the owner's explicit 2026-09-04 reply “确定”. The owner then explicitly instructed “开始实现 M1.5”, satisfying the standard-task `PLANNED → APPROVED → IMPLEMENTING` gate for the bounded scope in this task. This approval does not authorize a full knowledge graph, product UI, commit, push, packaging, or deployment.

## Implementation progress

- Added versioned baseline/node/edge/delta/proposal/decision contracts in `src/change_passport/architecture.py`.
- Added deterministic Python AST and JavaScript/TypeScript import extraction over immutable Git blobs, including batched reads for the initial bootstrap.
- Added approved-baseline repository/commit/schema/tracked-blob validation, stale/invalid fail-closed behavior, and incremental reparse/reuse accounting.
- Added changed node/edge comparison, unique one-hop importer impact paths, production-first display budgeting, explicit folded IDs, and one-JSON Mermaid/Markdown rendering.
- Added `approve-baseline`, which requires a separate attributable `approved` decision bound to the exact proposal SHA-256 and writes only beside the proposal.
- Added six architecture tests and one batched-Git regression; the full suite is 31 passed.

## First DigitalSelf M1.5 result

- Immutable range: `d78f78bab15802f7062bfd6794061c7208432fbe..430c34288e9565340e05e4235091335daac17c7c`.
- Output: `artifacts/digitalself-430c342-m15/`.
- Deterministic result: 3 added modules, 4 modified modules, 36 one-hop static consumers, 50 unique import-based impact paths.
- Main map: all 7 changed modules plus 7 production consumers; 32 additional one-hop/context nodes are explicitly folded and retained by ID in JSON.
- Owner review feedback required Chinese human-visible diagram annotations. The Mermaid renderer now localizes before/after, change/impact, static-import, interface-change, and folding labels while preserving code identifiers and machine-readable JSON semantics.
- Four-section finalize: 8 accepted, 0 downgraded, 0 rejected.
- DigitalSelf worktree status SHA-256 before/after: `CD460DD86EF3E92B3AB8DA22CA71ADDC416721A22A83CD6D8F6CFDF87BF3FDC5`; unchanged.
- Baseline proposal state: `pending`; no approved baseline was created.

## Handoff and remaining gate

ClaudeMap remains a preliminary offline comparison in `docs/experiments/claudemap-digitals-self-product-experience-20260904.md`; the authoritative CodeAtlas.live isolated and authenticated comparison is recorded in `docs/experiments/codeatlas-digitalself-product-experience-20260904.md`. CodeAtlas validated persistent selection and file-to-function drill-down while its forced replay, cross-layer over-reporting, path-dependent navigation, and unstable diff overlay confirmed that M1.5 validated JSON must remain the fact authority.

The owner then authorized optimization toward a non-coder-readable interactive experience. That work moved to `TASK-20260904-004-beginner-first-interactive-review.md` and is blocked on exact PRD v1.2 confirmation. This task's baseline proposal remains pending, and the consecutive-change reuse sequence has not started; neither is implicitly authorized by the experience handoff.
