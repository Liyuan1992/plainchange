# TASK-20260904-002: First real DigitalSelf sample

State: DONE
Tier: standard

## Approval and scope

The owner explicitly requested `DigitalSelf 你跑一次` on 2026-09-04. This approves one bounded real-sample run through the existing Phase 0-M1 file bridge. It does not approve modifying DigitalSelf, executing DigitalSelf project commands, uploading source to another model/provider, starting the 12-sample evaluation, committing, pushing, packaging, or deployment.

## Selected immutable change

- Target repository: `D:\Dev\Projects\DigitalSelf` (read-only).
- Base: `d78f78bab15802f7062bfd6794061c7208432fbe`.
- Head: `430c34288e9565340e05e4235091335daac17c7c`.
- Head subject: `feat(skills): validate arguments from input_schema and classify failures`.
- Changed surface: seven files, 767 additions, 37 deletions.
- Selection reason: bounded runtime/tool-contract change with code and test changes, a pre-existing approved tool-boundary rule, and a separate immediately following after-the-fact documentation commit (`44cf378`) suitable for a hidden comparison.

## Evidence and authority plan

- `original_task`: exact historical user direction from the originating Codex task: pursue one clear mainline and improve both safety and efficiency. This is broad and does not by itself prove every implementation detail was requested.
- `retrospective_claim`: the later local provider completion receipt's normalized goal and implementation summary. It may inform attention/inference but is not original intent.
- `self_report`: test counts and quality-gate claims from that completion receipt. No raw command output or independently verified receipt is available in the selected inputs, so the generator and validator must not report test success as verified.
- `approved_history`: the AgentRuntime/tool boundary text that already existed in the base commit and assigns deterministic parameter validation and structured failure handling to tool code.
- Git facts: immutable base/head diff collected by the tool.
- Hidden comparison: a patch generated from the later documentation-only commit `44cf378`; it must not be read until after raw model JSON is frozen.

## Execution plan

1. Preserve the existing dirty DigitalSelf worktree and use only immutable read-only Git object commands.
2. Materialize the hidden comparison patch under this project's ignored `artifacts/` directory without printing its contents.
3. Prepare the generator packet and verify that it contains no hidden path, ID, or content.
4. Read only `generator-packet.json` for the semantic generation step and write strict raw brief JSON.
5. Finalize through the deterministic validator and render the four-section Markdown brief.
6. Only after raw output is frozen, inspect the hidden comparison and perform a qualitative blind-review note. Do not fabricate owner annotations or a numeric score.
7. Re-run the project test suite, record artifacts and limitations, append a material Evolution entry, and stop.

## Risks and stop conditions

- Historical Codex context may contaminate the model step. The chosen sample was not described in the loaded memory summary, and the later documentation content remains unread before generation. Stop and mark the run non-blind if that content is exposed.
- The original user direction is broad; specific task intent must remain cautious.
- Test evidence is a provider self-report. It cannot support verified test-status claims.
- The hidden comparison is after-the-fact documentation, not infallible truth; it is a review aid only.
- Stop if any command would write inside DigitalSelf or depend on its mutable working-tree contents.

## Acceptance conditions

- DigitalSelf status is unchanged before/after the run.
- Prepared packet uses the exact base/head identities and omits all hidden-ground-truth identifiers/content.
- Raw model JSON satisfies the strict schema and cites only packet evidence.
- Unsupported test certainty is downgraded or represented as unknown/attention.
- Four-section Markdown and annotation template are produced under ignored artifacts.
- No score is claimed without owner annotations.

## Execution result

- Prepared sample: `digitalself-430c342-argument-validation`.
- Generator packet SHA-256: `dc84e3f167f05f099bc54fb79c433dce87a80b6868a322187b23401a9470df58`.
- Git patch SHA-256: `b06730f8c2971f82b96051a4351022f3db8277e376074dad8c10d679f937e98b`.
- Validated brief identity: `bbadd0a6093ba1b669c113fb0f740ff94baae2b9313dccaf88b41747bad204bd`.
- Validator result: 8 accepted, 0 downgraded, 0 rejected.
- Hidden comparison was opened only after the raw model JSON was frozen.
- Qualitative comparison found no observed contradiction in the eight claims. It found useful omissions around the 67-schema inventory, traceback logging, named residual hand-written checks, and the direct-call fallback detail.
- The validator safely refused to present provider self-reported tests as verified, but its generic unknown sentence erased the precise abstention reason. Recorded as `BUG-20260904-002`.
- Artifacts: `artifacts/digitalself-430c342/prepared/final/brief.md`, `brief.json`, `annotation.template.json`, and `artifacts/digitalself-430c342/blind-review.md`.
- Numeric scoring was not run because the owner has not filled the annotation template.

## Verification actually run

- `uv run change-passport prepare ...` -> exit 0; immutable base/head and packet hash emitted.
- Packet forbidden-string scan -> no hidden ID, path, commit, or filename match.
- `uv run change-passport finalize ...` -> exit 0; 8 accepted, 0 downgraded, 0 rejected.
- DigitalSelf worktree status hash before the run: `EAAE23A18E89C10D4CABEA32754563EA8C2F2470C233575D23F98B40B55A8EDE`.
- After-run DigitalSelf worktree status hash: `EAAE23A18E89C10D4CABEA32754563EA8C2F2470C233575D23F98B40B55A8EDE`; the pre-existing dirty state was unchanged.
- `uv run pytest -q` after closeout documentation -> 24 passed.
- Markdown trailing-whitespace scan -> no matches.
- `git remote -v` in the spike repository -> no output; no remote was created.

## Closeout records

- Bug: `BUG-20260904-002`.
- Evolution: `EVO-20260904-005`.
