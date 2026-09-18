# PlainChange PRD v2.1: Model-first understanding

Status: confirmed direction, implementation tracked by TASK-20260911-049
Date: 2026-09-11

## Product decision

PlainChange is not a deterministic code summarizer with optional polished
wording. Its full experience is a human-control layer in which a configured
model first understands the software, then explains one change, while local
deterministic code keeps evidence, privacy, identity and uncertainty boundaries.

The product promise remains:

> AI can write the code, but the person responsible for the software should
> still understand what changed, what it may affect, and what must be checked.

## Primary user

A person responsible for AI-built software who does not have complete code
review ability: a vibe-coding owner, product manager, founder, junior developer,
small-team lead or engineer delegating substantial work to an AI coding agent.

## Default experience

1. Fix the before/after Git revisions and collect bounded local facts.
2. Ask the user's configured model to form a source-bound project understanding:
   purpose, actors, main workflow or capabilities, and unresolved questions.
3. Cache that understanding by immutable revision, input and model identity.
4. Ask the model to interpret the selected change against that project model.
5. Validate every cited source/evidence ID locally and downgrade unsupported
   statements.
6. Show `这次改了什么` and `这个软件怎么工作` as linked event/system views.

## Experience without a configured model

The product still completes locally, but the result is explicitly named
`基础证据模式`. It may show fixed code facts, static relationships and unknowns;
it must not imply that PlainChange understood the project's business purpose,
main workflow, change salience or user impact.

## Trust contract

- Model output is a supported interpretation, never an observed fact.
- README and other documentation are project declarations, not truth.
- Git identity, patch facts, source scope, static relationships, citations,
  cache identity, downgrade rules and unknowns are deterministic.
- Static code cannot prove runtime order, deployed behavior or user impact.
- Human acceptance remains an explicit later decision.

## Configuration and privacy

The user chooses any domestic, international, hosted or local OpenAI-compatible
endpoint and model. PlainChange stores no API-key value: configuration names an
environment variable read only when a request is sent. The UI must show which
mode will transmit bounded material and provide an always-available no-network
basic evidence option.

## Success criteria

- A business application does not default to incidental syntax signals when a
  source-supported product change is more salient.
- A new user can tell whether semantic model interpretation ran.
- Repeated changes on the same revision reuse a correctly bound project model.
- Fabricated paths, evidence IDs or runtime claims are rejected locally.
- Framework, library, pipeline and business-application regressions use the same
  implementation without repository-specific rules.

## Open validation

Real-provider output quality, token/cost behavior, cross-language model prose,
and independent beginner comprehension remain separate empirical gates. Passing
mocked contracts proves orchestration and safety, not semantic quality.
