# TASK-20260909-022: Owner-language first-screen contract correction

State: DONE — OWNER-LANGUAGE CONTRACT AND SAMPLE VERIFIED
Tier: standard

## Trigger and authority

After reviewing the corrected five-question sample, the owner directly identified that its structure was understandable but its answers still used engineer-facing abstractions. The owner supplied the required hierarchy and examples: lead with one plain conclusion, show likely user impact and residual uncertainty, retain the five questions beneath it, explain abstract changes with a before/after example, separate affected people from unverified items, show owner-level verification goals first, and demote evidence state to compact labels.

The same conversation already authorized continuation without repeated confirmation until this bounded product slice is complete. This message is treated as approval for the correction below. It does not authorize production UI, model/provider calls, commit, push, deployment, or baseline approval.

## Facts and assumptions

- The existing five-question structure remains valid.
- Owner review is direct product feedback and can reject a candidate, but it is not an independent-human pass.
- The current sample accurately preserves evidence state, yet phrases such as “结构变化”, “同一条关系”, “来源位置”, and “真实运行时” raise the entry threshold.
- A generic contract must carry the presentation hierarchy; the sample must not gain Change Passport-specific rendering branches.
- Plain language may simplify an explanation but cannot upgrade an unknown impact into confirmed absence of impact.

## Approved plan

1. Add a generic first-screen summary object with a headline, confirmed-change statement, user-impact statement, and residual-risk statement; each conclusion retains its own state and basis.
2. Add a generic before/after comparison example for abstract changes and an owner-level verification checklist separate from detailed test instructions.
3. Rewrite the Change Passport sample in software-owner language while preserving source IDs, uncertainty, and technical evidence below the first screen.
4. Rebuild the participant card and evaluator rubric from the same semantics, keeping the result `not_run`.
5. Update the contract guide and confirmed PRD with the owner-language hierarchy and compact-state-label rule.
6. Regenerate the canonical control identity and every dependent checksum, then verify schema, parity, language depth, and source binding.

## Non-goals

- No changes to `src/`, templates, HTML, CSS, JavaScript, CLI, or the retained generated reports.
- No simulated participant, fabricated score, or comprehension-pass claim.
- No project-name conditional or content rule specific to Change Passport.
- No model/provider integration, task-window read, commit, push, package, deploy, or architecture-baseline decision.

## Risks and stop conditions

- Stop if simpler wording changes an observed fact into a behavior claim.
- Stop if “currently no evidence” becomes “confirmed no impact”.
- Stop if the first-screen summary and five questions can contradict each other.
- Stop if detailed test construction remains necessary to understand the owner-level next action.

## Verification plan

- Validate the revised sample against the revised JSON Schema.
- Recompute canonical `control_identity` and all evaluation checksums.
- Assert the summary appears before the five questions in both user-facing documents.
- Assert the before/after example contains the same “unchanged → rechecked” input but different old/new outcomes.
- Assert Q3 describes likely affected people while Q4 lists only remaining unverified items.
- Assert Q5 exposes owner checks while detailed construction remains outside the participant card.
- Scan the first screen for the owner-rejected abstraction vocabulary.
- Run `git diff --check`.

## Handoff condition

Complete when the generic contract and self-hosted candidate demonstrate the new information hierarchy without weakening evidence state. Stop before production UI implementation. Human comprehension remains unclaimed.

## Result and observed verification

The generic semantic contract and self-hosted candidate now implement the owner-directed information hierarchy without modifying production code:

- `first_screen_summary` carries a headline plus separately sourced confirmed-change, user-impact, and residual-risk statements.
- Abstract rule changes can carry a generic `comparison_example`; this sample shows the same unchanged input and recheck producing an old false alert versus the corrected non-change result.
- Q3 now describes likely affected people only; Q4 lists uncompleted verification only.
- `owner_checks` carries decision-level outcomes, while detailed test construction remains in `actions` and outside the participant card.
- State prose is reduced to short labels while the full statement state remains machine-readable.

Observed identities and checksums:

- Canonical `control_identity`: `99209ec836b4fccbfd65690d566eac7dd65040f72abe1c37769863de6e1e3172`.
- Revised Schema SHA-256: `0DD6F80FDFC9B7ED0F619864EB9F3EBF29EC4F6A69BEB512F85896DC351A280A`.
- JSON sample SHA-256: `7DD614EFAC15705F3F3D54BC6FEB5F179D0625B2FB8C960DBBCCFDB6EC2CF21F`.
- Markdown sample SHA-256: `EDC433B123502DC39A537B1BA13CFC03F7E947F3B8FC0CD67D00CB6B3BF2B642`.
- Participant card SHA-256: `26DB0AED5AEAD93E820E39A65CFBC5320686A8A4678D27EDE1FDCA870C1DECBA`.
- Evaluator guide SHA-256: `E07DCD20991278A587FE7E8C95B7BC6F03FDBF1896973CDB664BB5288878531E`.
- Observation template SHA-256: `411BC972495E776520D193E39B06AACC4E76E70C522D00E7A8C2F58A40FB9E39`.
- Evaluation manifest SHA-256: `EAF7671F4A78302B81F13217CC31F0CA0B40E692FEF79BC1A15B7890A4175844`.
- Owner-language PRD revision SHA-256: `CC2FB5CB06A60606BB23E61156D75A8FE08BBB6A31809F39CC2E5F028A532E4A`.

PowerShell Draft 7 validation accepted both schemas and samples. Custom assertions passed for summary-before-five-question order, exact JSON/user-document parity, before/after input equality with differing outcome, Q3/Q4 separation, owner-check visibility, detailed-action isolation, and zero first-screen occurrences of the seven owner-rejected abstraction phrases or the prior implementation-term list. Every manifest hash matched and canonical identity recomputation passed. Human comprehension remains `not_run`; this correction records owner rejection and semantic repair, not a participant pass.

The owner immediately identified that this task covered only the first screen. `TASK-20260909-023` adds the missing “这个软件怎么工作” second-screen contract and supersedes this task's current control identity and file hashes; the values above remain this task's historical closeout evidence.
