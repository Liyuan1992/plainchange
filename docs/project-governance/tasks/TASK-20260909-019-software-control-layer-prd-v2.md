# TASK-20260909-019: Software control layer PRD v2.0

State: DONE — EXACT PRD CONFIRMED; IMPLEMENTATION REMAINS SEPARATE
Tier: standard

## Trigger and authority

The owner identified a product-level discontinuity created by AI Coding: a person can now build software without being able to fully read or review its code. The owner reframed the target user as someone who lacks complete code control but remains responsible for the software, and proposed moving Change Passport from Code View to Software View. After the analysis confirmed that this changes the product definition rather than only its wording, the owner replied “嗯，好 继续”.

That reply authorizes writing and recording the PRD v2.0 proposal. It does not yet confirm the exact PRD, authorize implementation, or authorize model/provider connections, account/task-window reads, commit, push, packaging, deployment, or baseline approval.

## Evidence observed

- The current README defines Change Passport around a fixed Git change and four-section explanation.
- The existing beginner task already requires a 30-second independent retelling, but that human gate remains pending.
- Recent work improved system and implementation architecture layout without establishing non-coder comprehension.
- PRD v1.4 already distinguishes user text, AI replies, user confirmation, and an optional Token-consuming task-window extraction action.
- The accepted evidence spine requires unsupported user-behavior claims to remain unknown and forbids treating static dependencies as runtime behavior.
- The current FastAPI artifact is useful for technical portability and graph stress, but is not an appropriate primary proof that a non-technical software owner understands their own product.

## Product decision proposed

Reposition Change Passport as an AI-built software control layer. The default experience should let a responsible non-expert answer five questions about software operation, the current AI change, affected people or surfaces, unknowns, and the next verification action. Code structure becomes progressively disclosed evidence.

## Approved scope for this task

1. Produce a repository-owned PRD v2.0 draft.
2. Define target and non-target users, product promise, five core questions, three information depths, source/authority boundaries, task-window extraction behavior, software-map semantics, impact-by-audience, verification advice, MVP scope, metrics, risks, and stop conditions.
3. Preserve the accepted deterministic evidence contract and the v1.4 task-context distinctions.
4. Record the draft and return it for exact owner confirmation.

## Non-goals

- No production code, HTML, CSS, JavaScript, schema, profile, generator, or artifact changes.
- No Figma or visual-design stage; this task defines the product contract first.
- No model/provider call, live task-window access, source upload, account integration, or Token consumption.
- No commit, push, package, deploy, baseline approval, or mutation of a target repository.
- No claim that the pivot is validated before an independent non-technical user completes the five-question test.

## Affected domains

- Product positioning and target user.
- Evidence-constrained software-behavior explanation.
- Beginner comprehension and progressive disclosure.
- Task-context provenance and optional model use.
- Human validation and cross-project sample strategy.

## Risks and stop conditions

- Plain language may overstate behavior beyond available evidence.
- A business map may become an expensive per-project manual artifact.
- Continued diagram polish may distract from human comprehension validation.
- Test recommendations may be mistaken for executed verification.
- Multiple explanation levels may drift if they do not share claim identity and state.

Stop implementation if the exact PRD is not confirmed, if a behavior claim cannot retain its source and uncertainty, or if implementation would require an unapproved remote/provider contract.

## Verification for this planning task

- Confirm the PRD contains the five user questions and three information depths.
- Confirm it explicitly preserves v1.2 evidence authority and v1.4 task-context roles.
- Confirm it separates observed facts, supported interpretations, project declarations, and unknowns.
- Confirm it defines a Change Passport self sample, an application sample, and a framework/tool sample.
- Confirm implementation, model access, account access, commit, push, deploy, and baseline approval remain outside this task.
- Parse and inspect the Markdown files, check links/paths, compute the PRD SHA-256, and run `git diff --check`.

## Handoff condition

Stop after the PRD draft, its identity, and governance pointers are recorded. The next transition is exact owner confirmation of PRD v2.0. Implementation planning starts only after that confirmation.

## Result

The repository-owned draft is complete at `docs/product/PRD-v2.0-software-control-layer-draft.md`, SHA-256 `3AE6F91ECDC647B9A3934F976B8130C8FB006048D702B10AC6DCF513A853C98E`.

Observed planning verification:

- The five owner questions, three information depths, two plain-language top-level entries, behavior-first software map, impact-by-audience view, next-test guidance, task-window extraction contract, and progressive technical evidence are explicitly defined.
- The document preserves the deterministic evidence spine and separately labels observed facts, supported interpretations, project declarations, and unknowns.
- The sample strategy requires Change Passport self-hosting, a user-facing application, and a framework/tool project; FastAPI is retained as a technical portability sample rather than non-coder product proof.
- Production implementation, model/provider access, task-account reads, source upload, commit, push, packaging, deployment, and baseline approval remain outside this task.
- SHA-256 computation and `git diff --check` passed. The diff check emitted only existing LF/CRLF normalization warnings.

## Approval evidence

The owner replied “确定” on 2026-09-09 to the exact draft identified by SHA-256 `3AE6F91ECDC647B9A3934F976B8130C8FB006048D702B10AC6DCF513A853C98E`. This confirms the product direction, first-stage scope, evidence boundaries, and implementation order defined in that document.

After confirmation, the PRD's administrative status line was changed from pending to confirmed and linked back to this approval record; no product requirement section changed. The current file SHA-256 with that receipt metadata is `0932D5F1585F8DBA664B5600865B146A0AB68DA4A9C6615D7D66AE8DB3BDCD0B`.

The confirmation also authorizes the already-described first follow-up: freeze the five-question data contract and create a Change Passport self-hosted text sample before any new UI work. It does not authorize later UI implementation, provider/account integration, commit, push, packaging, deployment, or baseline approval.

No production implementation was performed in this PRD task. The next bounded phase is tracked separately.
