# TASK-20260909-021: Independent five-question comprehension test kit

State: DONE — BLIND TEST KIT VERIFIED; HUMAN RUN PENDING
Tier: standard

## Trigger and authority

TASK-20260909-020 completed the first source-bound five-question sample and stopped honestly at the independent-human gate. The owner then replied “好的 你继续”. This authorizes preparing the blind evaluation materials needed to run that gate. It does not authorize inventing a participant, filling answers on their behalf, or treating an AI review as independent human evidence.

## Goal

Make the required 60-second comprehension test executable by separating participant-visible content from evaluator-only scoring material and by providing a structured observation record that cannot silently convert “not run” into “passed”.

## Scope

1. Create a participant-only reading card containing the five-question first screen and no evidence links, hashes, rubric, answer key, or technical drawer.
2. Create an evaluator guide with eligibility, timing, no-hint protocol, exact prompts, scoring anchors, critical-misunderstanding overrides, and pass rule.
3. Define a machine-readable observation schema and an untouched `not_run` template.
4. Bind all materials to the current `software-control` identity with a checksum manifest.
5. Verify separation, JSON validity, schema conformance, question order, untouched result state, and file hashes.

## Non-goals

- No simulated participant, fabricated answer, self-score, or pass claim.
- No UI, production code, model/provider call, live account read, or Token use.
- No collection of participant name, email, account, or other personal information.
- No commit, push, package, deploy, baseline approval, or next product phase.

## Risks and stop conditions

- Stop if evaluator guidance appears in participant-visible material.
- Stop if a participant with prior project knowledge is treated as independent.
- Stop if prompts are reworded in a leading way or hints are omitted from the record.
- Stop if a score of 4/5 can pass while the participant confidently mistakes “unknown impact” for “confirmed no impact”.
- Stop after the kit is verified; only a real participant can produce the outcome.

## Verification plan

- Validate observation template against its JSON Schema.
- Assert the five answer IDs are present in fixed order and unscored.
- Assert `status=not_run`, points/pass are null, and hints are false before use.
- Assert participant material contains no rubric, score threshold, hashes, paths, evidence IDs, or technical terms from the first-screen banned list.
- Assert evaluator material contains all five prompts, the 4/5 threshold, and the critical-unknown-impact override.
- Recompute every checksum in the manifest and match the source control identity.
- Run `git diff --check`.

## Handoff condition

Complete with a ready-to-share participant card and evaluator record. Human comprehension remains pending until a qualified participant completes the protocol and the evaluator saves a separate observation result.

## Result and observed verification

The blind evaluation kit is ready at `docs/product/evaluations/change-passport-self-688fc5f/`:

- `participant-card.md` is the only participant-visible file.
- `evaluator-guide.md` defines eligibility, timing, exact prompts, scoring anchors, the 4/5 threshold, and critical misunderstanding overrides.
- `observation.template.json` starts with no participant, answers, scores, result, or timestamp and is validated by `docs/product/schemas/human-comprehension-observation.v1.schema.json`.
- `evaluation-manifest.json`, SHA-256 `C3E62DA5119E40A3868B177ACEDAC4E31D504166ADA318574B93B144AD2AA960`, binds the kit to control identity `21dcff469d5b0faf297dbe890eecd1e68b8eca939e18bf8b28f905c0561dd9cc` and records each file hash.

Observed checks:

- Observation template schema validation passed.
- Five answer slots are in fixed order and contain no fabricated response or score.
- Evaluation status remains `not_run`; points and pass are null; hints default to false.
- Participant material contains the exact five source answer texts and zero rubric, threshold, hash, path, evidence-ID, or banned implementation-term matches.
- Evaluator-only material contains all five prompts, the 4/5 rule, and the “unknown is not confirmed no impact” critical override.
- All manifest hashes and the source control identity match.
- `git diff --check` passed with only existing LF/CRLF normalization warnings.

Owner review invalidated the first kit because its participant card exposed only a purpose summary for Q1. The corrected participant card now visibly includes all five ordered software-work steps with four down connectors. The evaluator rubric explicitly gives zero for a purpose-only answer such as “it explains what AI changed”. Manifest hashes, observation source identity, and source-sample identity were regenerated; see `BUG-20260909-002`.

No comprehension outcome is claimed. A qualified real participant remains required.

The owner then rejected the participant-facing language as still too engineering-oriented before any test was run. `TASK-20260909-022` revises the kit and supersedes this task's current control identity and hashes; this task's original result remains historical and `not_run`.
