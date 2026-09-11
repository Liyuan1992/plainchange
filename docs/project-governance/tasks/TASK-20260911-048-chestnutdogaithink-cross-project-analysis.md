# TASK-20260911-048: ChestnutDogAiThink cross-project analysis

State: DONE
Tier: standard

## Trigger and authorization

After accepting the corrected FastAPI English report, the owner explicitly
asked PlainChange to analyze their `chestnutdogaithink` project. This authorizes
the bounded cross-project run and PlainChange-side artifact/governance writes;
it does not authorize modifying, promoting, running or repairing the archived
target project.

## Baseline facts

- The only main project found is the migration archive at
  `D:\Dev\Archive\OldLaptop-20260622\work\E-myProject\ChestnutDogAiThink`.
  Migration classification marks it `personal-candidate` and requires the
  archive to remain untouched until separately promoted.
- The archived checkout is on branch `test`, at
  `0883fe0676f0148139afc82e92101d732d75ed3b`, with 3,031 reported worktree
  entries and status SHA-256
  `de49131ded724bfe318935c0b49f699d354ffae60c6ed0d5f1ae41dca869e57d`.
  Many entries are missing tracked dependencies/caches after migration.
- The latest committed range is
  `f76838f1133f0d5fbfbdb9c3d0fc13356912263b..0883fe0676f0148139afc82e92101d732d75ed3b`
  (`feat: add product recommendation overview`): 120 files, 10,159 insertions
  and 1,434 deletions across Python backend, tests and Vue frontend.
- The project describes itself as a pet-store SaaS AI assistant using a Python
  FastAPI BFF/Agent, Vue UI, SSE, PostgreSQL, existing Java business APIs and
  model/tool routing. These are project declarations, not runtime proof.

## Plan

1. Create a PlainChange manifest bound to the two fixed commits and the owner's
   request; do not read dirty worktree content as change evidence.
2. Run the unchanged deterministic automatic analysis into an isolated artifact
   directory; no model provider or target profile.
3. Inspect the generated owner summary, system map, change mapping, omissions
   and evidence states for beginner-facing usefulness and generic failure modes.
4. Exercise both tabs and their disclosures in real Edge at desktop/narrow
   widths, recording console/overflow/interaction results.
5. Recheck target HEAD, status fingerprint and Git objects. Record results in
   this task; append a PlainChange bug/evolution entry only if the sample exposes
   a reusable product issue.

## Non-goals and safety boundary

- No target write, dependency installation, project execution, database/model/
  network request, deployment, environment repair, commit, push or promotion.
- No ChestnutDogAiThink-specific code, profile, phrase mapping or exception.
- Static/source analysis cannot prove APIs, permissions, database behavior,
  runtime order, model behavior or user impact.

## Stop and handoff

Stop after the fixed report, browser evidence, target-preservation check and
honest product assessment. Any exposed generic defect becomes a separate
follow-up rather than being silently patched for this sample.

## Observed result

- The unchanged deterministic run succeeded in 3.789 seconds without a model
  call or target profile. It analyzed 860 base and 868 head modules, with 791
  cache hits and 937 misses; the generated change graph displays all 77 changed
  or context nodes with zero display omissions.
- Delivery mechanics pass: real Edge opens both tabs and all eight capability
  cards at 1280/390 px with no console or document-overflow errors. The wide
  technical canvas remains independently scrollable and moves from 0 to 280.
- Product semantics fail this sample. The first-screen headline promotes four
  incidental syntax signals (three added `ValueError` branches and one callable
  signature change) as the main change, while the commit's dominant product
  addition—product recommendation overview across backend and frontend—is not
  identified or mapped to a software capability.
- README capability extraction finds the correct eight business areas, but uses
  the table's numeric `数量` column (`4`, `5`, `3`, etc.) as each area's visible
  description instead of the `覆盖功能` column. The resulting owner map is not
  acceptable for a beginner.
- Architecture coverage reports 43 unsupported changed files. These include the
  changed Vue product cards and `productReplacementPlan.test.mjs`, so the static
  graph omits the largest visible product surface of this change.
- The fixed revision contains tracked dependencies. PlainChange includes 432
  `frontend/node_modules` modules among 868 head modules and places all of them
  in the user-entry group, materially polluting the system map and counts.
- The report honestly keeps runtime and user impact unknown, preserves the
  source-backed project purpose, and does not fabricate a change-to-capability
  link. Those boundaries remain correct even though the explanation is weak.

## Target preservation

- Target HEAD remains `0883fe0676f0148139afc82e92101d732d75ed3b` and the
  3,031-entry worktree status retains SHA-256
  `de49131ded724bfe318935c0b49f699d354ffae60c6ed0d5f1ae41dca869e57d`.
- Base/head remain commit objects with tree IDs
  `c80b41b3f443e13407298caaf0d0ab0e68d9a964` and
  `1e04dafe59fd4bf51eb0bde3f194bf5437a006b3`.
- The archive contains pre-existing loose-object garbage reported by Git; it was
  observed but not cleaned or changed because archive repair is outside scope.

## Assessment

The report is mechanically usable but semantically **not accepted** as a good
PlainChange result. BUG-20260911-039 through BUG-20260911-042 retain the four
generic failures. No sample-specific fix was made; the report is kept as the
failing evidence for the next approved correction.
