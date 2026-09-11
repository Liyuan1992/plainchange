# Model-first understanding implementation specification

## Stages

### 1. Local evidence preparation

Read immutable Git objects, exclude standard dependency/generated trees, collect
bounded root declarations, relative source paths, implementation groups and the
fixed change packet. Do not include absolute repository paths, dirty-worktree
content, hidden ground truth or secrets in model payloads.

### 2. Project understanding

Input schema: `plainchange.project-context.v1`.

Output schema: `plainchange.project-understanding.v2` with purpose, structure
kind, a shallow owner-facing map of two-to-six components (normally four to
six), a consecutive workflow chain or an unordered capability map, citations,
code paths and unknowns. Labels describe business actions, responsibilities or
outcomes; implementation vocabulary belongs in the existing technical
evidence drill-down. Local validation rejects unknown citations and paths.

Cache key includes the fixed head commit, context-packet SHA-256, provider-config
SHA-256, model name and understanding schema. A cache hit revalidates the output
against the current packet before use.

### 3. Change interpretation

Input contains the validated project understanding and existing frozen
`change-passport.generator-packet.v1`.

Output schema: `plainchange.change-interpretation.v2`. It wraps the existing raw
brief, adds one short result-first owner-language change summary, at most one
changed project component, cited evidence IDs, explicit limitations, up to
three source-bound audience candidates and one-to-three owner checks. An
audience candidate says who may need to pay attention; it cannot establish
actual user impact. The existing raw-brief validator remains authoritative.

### 4. Owner projection

The validated project understanding creates a candidate target profile before
architecture preparation. The validated change interpretation supplies the
headline, candidate change overlay and checks. `analysis_mode` is either
`full_model` or `basic_evidence`; basic evidence reports render a prominent
limitation banner.

## Provider boundary

Both stages use the existing strict `change-passport.model-provider.v1`
OpenAI-compatible contract and `json_schema`, `json_object` or `prompt_only`
capability modes. Separate receipts record stage, provider/model identity,
sanitized hashes, timings and token counters. They never record keys, headers or
response bodies.

## Failure behavior

- Invalid config or missing named credential: fail before network transmission.
- Invalid model JSON, unknown source/path/evidence or broken chain: fail visibly.
- Configured model failure: no silent basic-mode fallback.
- No config with CLI `auto`: finish in visibly limited basic evidence mode.
