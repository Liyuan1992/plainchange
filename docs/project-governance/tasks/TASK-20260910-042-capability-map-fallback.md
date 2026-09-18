# TASK-042: Capability-map fallback for projects without a proven workflow

State: DONE
Risk: standard
Owner approval: Explicitly approved on 2026-09-10 when the owner classified the
multi-project result as a real bug and required a generic fix before rerunning
the affected projects.

## Problem

When a repository explains its product as a set of capabilities rather than a
short ordered pipeline, PlainChange currently discards that useful material and
renders a generic four-step input/process/output story. The result looks like a
workflow fact even though no source proves the order, and it fails to explain
libraries, runtimes and multi-surface applications.

This is BUG-20260910-029. The fix must not recognize repository names or add
project-specific labels, paths or branches.

## Approved scope

1. Extract bounded capability structures from common README bullet groups and
   summary tables when an explicit ordered workflow is absent.
2. Reconcile each declared capability with fixed-commit code paths using the
   same source-reference and evidence-state boundary as workflow steps.
3. Represent the result as a non-sequential `capability_map`; if documentation
   has no usable structure, fall back to code-derived implementation areas, not
   a fabricated ordered process.
4. Teach the target-profile, software-control and offline UI contracts to
   distinguish an ordered workflow from an unordered capability map.
5. Rerun memdsl and DigitalSelf as bug-reproduction cases, and VideoFactory as
   an ordered-workflow regression control. Preserve all target worktrees.

## Non-goals

- No memdsl, DigitalSelf, VideoFactory or other repository-name exceptions.
- No model call, remote source upload, runtime/deployment inference or claim
  that README text is automatically true.
- No commit, tag, push, package publication or target-repository modification.
- No attempt to infer business sequence from import order or directory order.

## Risks and stop conditions

- README lists may describe installation, release notes or non-goals rather
  than product capabilities. Extraction therefore stays bounded, scores
  product/capability sections, and keeps the source state visible.
- A capability may not map uniquely to code. It remains `declared_only`; this
  must not be upgraded to code-supported or changed-location evidence.
- If the new representation weakens source/identity validation or makes
  VideoFactory lose its source-declared order, stop and return to design.

## Verification plan

- Unit tests for an unrelated capability-list fixture, an unrelated capability
  table fixture, an undocumented code-only fixture and the existing ordered
  workflow fixture.
- Schema/contract tests proving capability maps have no directional flows and
  workflow maps retain their ordered four-step overview behavior.
- Full test suite and source scan proving production code contains no target
  repository names.
- Fresh reports for fixed revisions of memdsl, DigitalSelf and VideoFactory,
  followed by DOM/browser checks of map type, labels, expansion and overflow.
- Record timings, report sizes and target HEAD/status fingerprints before and
  after analysis.

## Observed result

- `uv run pytest -q` completed successfully; `pytest --collect-only` reports
  107 tests. New fixtures cover a capability list, a capability summary table,
  a code-only fallback and the unordered software-control contract.
- Production source contains no case-insensitive `memdsl`, `DigitalSelf` or
  `VideoFactory` branch. Python and JavaScript syntax checks pass; `git diff
  --check` reports only existing line-ending warnings.
- memdsl `7fc1d0b..a061bc4` now renders 5 source-declared, code-anchored memory
  capabilities with zero directional connectors. Measured analysis: 1.11 s;
  report size: 372,643 bytes.
- DigitalSelf `4da99fc..a662719` now renders 10 source-declared, code-anchored
  product areas with zero directional connectors. Measured analysis: 2.52 s;
  report size: 1,048,437 bytes.
- VideoFactory `58d2149..d6594e3` remains an ordered `workflow`: 7 detailed
  steps, 4 overview stages, 6 detail flows and the change still mapped to
  `检查视频质量`. Measured analysis: 1.15 s; report size: 384,474 bytes.
- Headless Edge expanded and collapsed every capability/stage on both tabs at
  1280 and 390 px. All three reports have zero console errors and no horizontal
  overflow. Capability reports draw zero arrows; VideoFactory draws three
  overview connectors.
- Target proof after analysis matches the preflight exactly: memdsl remains
  clean at `a061bc4` (`e3b0c442...b855`); DigitalSelf remains at `a662719`
  with 82 status lines (`a8e16c88...655a4`); VideoFactory remains at `d6594e3`
  with 39 status lines (`27fbaaa0...b4d33`).

## Remaining limits

- This fixes false workflow structure and restores useful owner orientation; it
  does not prove that README declarations are current, that code paths run, or
  that a non-technical reader understands every capability description.
- Free-form prose and broader documents are not yet reconciled. Fresh reports
  still need reviewed English body packs for complete English content.
- No model call, target write, commit, tag, remote operation or release occurred.
- `uv run ruff check ...` could not run because `ruff` is not installed in the
  project environment; Python compilation, JavaScript syntax, the 107-test suite,
  diff checks and real-browser checks are the observed validation instead.
- The `ds` CLI was not available, so no DigitalSelf completion receipt was
  submitted.
