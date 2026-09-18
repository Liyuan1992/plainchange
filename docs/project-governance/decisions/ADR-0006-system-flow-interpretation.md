# ADR-0006: Add source-linked system interpretation alongside change reports

- Status: Accepted for implementation by owner, 2026-09-16
- Task: TASK-20260916-039

## Decision

The owner approved a new capability rather than replacing or freezing the current
product. `understand` analyzes one existing commit, independent of change ranges.
The owner explicitly selected local Codex as the default generation capability.
This authorizes the bounded real text integration test, not arbitrary provider
spending, release or repository mutations.

The host controls read-only Git source access. A model may request excerpts only
from a filtered inventory, within bounded rounds and byte limits. Exact source
identities and actual read coverage are retained. The Codex process has a fresh
working directory and no shell or web tools; credentials remain managed by Codex.
Compatible API configuration is available only by explicit selection, with no
silent fallback between providers.

The new artifact `plainchange.system-flow.v1` contains semantic nodes, conditional
edges, source references and pending test scenarios. These are model interpretations,
never additions to `architecture-delta.json` or an approved architecture baseline.
Validation proves citation bounds and graph consistency only. It cannot prove that
a cited line entails a claim, that all runtime branches were found, or that tests
passed. Design rationale without independent records remains unknown.

## Consequences

Users can follow implementation decisions and derive tests without selecting change
pairs or manually matching files. The first version deliberately bounds exploration
and excludes uncommitted edits; the report states these limits and lists unread
files. Each run preserves separate artifacts, including sensitive source excerpts
and provider request records. The generated HTML itself is offline and has no remote
assets. Existing change reports and their stricter deterministic authority remain
unchanged.

## 2026-09-17 approved incremental extension
TASK-041 extends the artifact to v2 with explicit cited cross-flow node connections and call/return/next-request kinds. Legacy v1 maps remain readable without invented links. Function indexes guide bounded reads of larger files; indexes are navigation hints, not call evidence. Scenario traversal follows user-selected conditions on the validated graph and does not execute business code or prove path feasibility. A single reference-only model repair may follow an invalid citation; original raw output is retained, semantic claims cannot be changed by the repair contract, and full validation still applies.
