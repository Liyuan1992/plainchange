# ADR-0005: Make model-assisted semantics the full PlainChange experience

- Status: Accepted
- Date: 2026-09-11
- Decision owner: Project owner
- Related task: `TASK-20260911-049`
- Revises: ADR-0004 item 4 (default product experience)

## Context

Deterministic rules reliably freeze Git facts and static relationships, but a
business-application regression showed that they can select an incidental code
signal as the main story and fail to form the product's real capability model.
Calling a model only after those semantic choices have already been made cannot
repair that product failure.

## Decision

1. The full experience uses a configured model before final project/workflow and
   change-salience choices are made.
2. Project understanding and per-change interpretation are separate constrained
   stages. Project understanding is cached only under immutable input and model
   identities.
3. The model proposes meaning; deterministic code owns evidence collection,
   sanitization, source/evidence allowlists, identities, downgrade rules,
   unknowns and rendering boundaries.
4. `auto` is the CLI default. With a provider config it selects the full model
   path; without one it produces an explicit `basic_evidence` report and sends no
   network request.
5. A configured model failure is visible and does not silently fall back.

## Consequences

- PlainChange can use business semantics that are not recoverable from import
  topology alone without treating model prose as truth.
- A first-time user must configure a provider for the intended full experience.
- The no-model path remains useful for private diagnostics but is no longer
  presented as equivalent product understanding.
- Real model quality, language quality, token cost and human comprehension need
  empirical validation beyond contract tests.

## Approval

Accepted through the owner's explicit conclusion that business projects expose
the wrong direction and that model access should happen from the beginning,
followed by “嗯，执行”. No real provider transmission is authorized by this
implementation task.
