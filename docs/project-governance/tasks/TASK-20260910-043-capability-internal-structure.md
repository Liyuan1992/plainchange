# TASK-043: Evidence-bound capability internal structure

State: DONE
Risk: standard
Owner approval: The owner approved the bounded implementation plan on
2026-09-10 and explicitly requested execution after reviewing the proposed
evidence-first, in-place expandable capability design.

## Problem

The capability-map correction prevents PlainChange from inventing a workflow,
but each overview capability currently contains exactly one identically named
detail node. Expanding a capability therefore repeats the same statement rather
than explaining how that capability works. The loose single-token path matcher
can also label unrelated benchmark, design or packaging files as corresponding
code.

This is a general analysis and contract defect, not a DigitalSelf-specific UI
problem.

## Approved scope

1. Replace loose single-token/prefix code-anchor matching with an auditable,
   precision-first matcher that prefers explicit paths and exact code
   identifiers and fails closed when evidence is weak.
2. Derive a bounded internal structure for a declared capability only when two
   or more distinct, source-bound responsibilities can be recovered from its
   declaration and corresponding code scope.
3. Represent each top-level capability as one overview node whose detail-node
   membership contains its distinct internal responsibilities; capability
   internals remain unordered unless source evidence supports a sequence.
4. Do not render an expansion affordance for a one-to-one capability. Explain
   that finer structure is not yet supported instead of duplicating the parent.
5. Preserve source labels, unknowns, change-overlay fail-closed behavior and
   the existing ordered-workflow contract.
6. Verify the generic behavior with synthetic fixtures plus fresh DigitalSelf,
   memdsl and VideoFactory reports. Do not add target-name branches.

## Non-goals

- No project-name, product-name or repository-specific extraction rules.
- No claim that source declarations are current, code paths execute, or runtime
  behavior has been verified.
- No unlimited recursive code graph, whole-repository model prompt or inferred
  sequence from import/directory order.
- No target-repository write, commit, tag, push, package publication or remote
  provider call.

## Risks and stop conditions

- Over-splitting names, prose or arbitrary files can create a more detailed but
  false story. Stop rather than expose children without distinct evidence.
- A precise matcher may downgrade existing weak `找到对应代码` labels. This is
  expected and must not be patched with broader fallback matching.
- Ordered workflow behavior must remain unchanged. If VideoFactory loses its
  source-declared sequence or change mapping, return to analysis.
- The offline report must remain usable at desktop and 390 px without hidden
  controls or horizontal overflow.

## Verification plan

- Unit tests for weak-token false positives, explicit-path/exact-identifier
  positives, distinct capability children and one-to-one no-expansion behavior.
- Contract tests for overview/detail coverage and unordered capability internals.
- Full test suite, Python/JavaScript syntax checks and production-source scan
  for target names.
- Fresh fixed-revision reports for DigitalSelf, memdsl and VideoFactory; inspect
  node membership, source refs, change mapping, report size and timing.
- Real Edge desktop and 390 px checks for expand/collapse, readable inspector,
  no horizontal overflow and zero console errors.

## Result

Implemented without target-name rules or target-repository writes.

- Capability declarations retain explicit backtick references. Reconciliation
  first resolves exact files/directories, then unique exact code identifiers;
  weak generic tokens and prefix resemblance cannot establish support.
- Internal responsibilities are derived only inside that explicit fixed-revision
  code scope. An expansion requires at least two responsibility families and
  three supporting source files; output is bounded to six unordered children.
- Children are labelled `从代码结构发现` / `code_discovered`. Their evidence
  note says they are filename/identifier-based candidates, not project
  declarations or runtime verification.
- One-to-one capabilities render as leaves with no expansion affordance. A
  supported expansion remains inside the complete map and uses a two-column
  desktop / one-column narrow layout with the existing inspector.
- The target-profile contract accepts optional 2–6 capability details, rejects
  a fake single child, and keeps ordered workflow behavior unchanged.

Fresh fixed-range results:

- DigitalSelf `4da99fc..a662719`: 10 capability overviews, 19 detail candidates,
  and 3 expandable capabilities. `主聊天运行时` exposes 6 responsibilities;
  every child code ref stays inside `src/digital_self/core/chat_engine/`.
- memdsl `7fc1d0b..a061bc4`: 5 capability overviews and 0 expansions. The tool
  does not manufacture a hierarchy when distinct internal evidence is absent.
- VideoFactory `58d2149..d6594e3`: preserved 7 declared workflow steps, 4
  overview stages, 6 flows and the changed `检查视频质量` node.

Verification passed:

- 110 Python tests.
- Python compileall and JavaScript syntax checks for the report, i18n and
  multi-project browser harness.
- Production-source scan: zero DigitalSelf, memdsl, VideoFactory, vLLM or
  FastAPI name branches.
- Headless real Edge at 1280 and 390 px: every overview/detail click passed,
  no duplicate leaf details, no console errors and no horizontal overflow.
- Target fingerprints remained DigitalSelf `a662719` / 82 existing status
  lines, memdsl `a061bc4` / clean, and VideoFactory `d6594e3` / 39 existing
  status lines.
- `git diff --check` passed with only existing LF-to-CRLF notices. `ds` is not
  installed on this host, so no optional governance receipt was submitted.

Artifacts:

- `artifacts/digitalself-capability-depth-evidence-final/review.html`
- `artifacts/memdsl-capability-depth-evidence-final/review.html`
- `artifacts/videofactory-capability-depth-regression-evidence-final/review.html`

Remaining boundary: the new internal responsibilities are deterministic static
code-structure candidates. They do not establish call order, runtime behavior,
business correctness or owner comprehension. A future configured-model path may
propose richer wording only through the same evidence and review boundary.
