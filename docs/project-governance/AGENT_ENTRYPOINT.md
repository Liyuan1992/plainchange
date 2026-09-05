# Shared agent entrypoint

These instructions apply to both Codex and Claude Code. `AGENTS.md` and `CLAUDE.md` should point here instead of duplicating this process.

1. Before work, inspect `WORKFLOW.md`, `PROJECT.md`, current task material, and the actual Git/worktree state.
2. Classify the request as micro, standard, or high-risk. Do not implement standard/high-risk work until its plan is explicitly approved.
3. Retrieve only the affected domain pages and relevant ADRs. Do not load the full raw `BUGLOG.md` or `EVOLUTION.md` by default.
4. Perform only the approved phase. Completion never authorizes a commit, push, deploy, external write, or the next phase.
5. Report observed verification separately from plans and claims. At closeout, append any required raw BugLog/Evolution record.
6. Treat idle curation as a separate documentation task. It may distill source records into domains but must preserve source IDs and must not delete the raw logs.
