# TASK-20260905-009: Preserve the spike and correct retained-edge classification

State: DONE
Tier: micro

## Trigger and approval

The owner supplied a repository review identifying two immediate risks: the entire spike had no Git commit, and `modified_edge_ids` compared evidence refs containing commit hashes. After a read-only audit reproduced both findings, the owner replied `好的` to the proposed sequence of one local baseline commit followed by one local bug-fix commit. This authorizes those two local commits only. It does not authorize a remote, push, pull request, architecture-baseline approval, provider integration, packaging, deployment, or further UI work.

## Observed baseline

- Branch `main` had no commits; all 97 non-ignored project files were untracked.
- `.venv`, caches, package metadata and `artifacts/` were ignored.
- Eight design PNGs totalled about 1.4 MB and were retained as intentional design/validation evidence.
- The initial local preservation commit is `a4576ec` (`chore: establish local change passport baseline`).
- Before that commit, 44 tests, compileall and JavaScript syntax passed; staged credential-pattern and `.env` checks found zero candidates.
- The frozen DigitalSelf bounded delta reports 14 added, 1 removed and 95 modified edges.
- Full immutable base/head reconstruction found 1,755 base edges, 1,768 head edges and 1,754 retained edge identities. The current comparison marked all 1,754 retained edges modified; after removing only the commit component from evidence refs, exactly one retained edge differed (`registry.py` import moved from line 8 to line 10).

## Scope

1. Normalize the commit component of edge evidence refs only for retained-edge change comparison.
2. Preserve path, line, source, target and relation differences; a real source-location move must still count as modified.
3. Add a regression test covering commit-only reverification and a real line move.
4. Regenerate the frozen DigitalSelf artifact and verify `modified_edge_ids` changes from 95 to 1 while node/added/removed edge facts remain stable.
5. Append the bug fact, record the preservation/focus decision, update the active evidence contract and stale status pointers, then create the authorized local bug-fix commit.

## Non-goals

- No UI, target-profile, model metadata, provider adapter, system-snapshot packet binding, architecture file split, HTML size change, lint/type setup, curation, scoring, annotation, baseline approval or remote operation.
- No deletion of `modified_edge_ids`; its existing source-location semantics are corrected narrowly.

## Verification

- Focused and full pytest.
- Python compileall and JavaScript syntax.
- Immutable DigitalSelf base/head reconstruction with normalized comparison.
- Formal `finalize` remains 8 accepted / 0 downgraded / 0 rejected.
- Architecture added/removed edges remain 14/1; modified retained edges become 1.
- Git diff check, local commit identity and clean worktree.

## Stop conditions

- Normalization hides a path or line change.
- Node, added-edge, removed-edge or impact identities change unexpectedly.
- The target DigitalSelf worktree is modified.
- A remote operation or architecture-baseline decision becomes necessary.

## Completion evidence

- Added a retained-edge evidence-location signature that masks only the 40-character Git commit component. Source path and line remain part of the comparison.
- Added a two-step regression: commit-only reverification produces no modified edge; moving the same import to a new line produces exactly one modified edge.
- Focused architecture tests passed: 10.
- Full project tests passed: 45. Python compileall, JavaScript syntax, and Git diff checks passed.
- Rebuilt the immutable DigitalSelf range in 4.808 seconds. The formal delta now reports 14 added, 1 removed, and 1 modified edge; the sole modified ID is `edge.305a63dbc617414072cb` for the `registry.py` import moving from line 8 to line 10.
- The frozen raw brief SHA-256 remained `4D3A88DBE97EF570F331EC484DEE342B62772110B29F0D3E70713A4F209B6A2B`; finalize remained 8 accepted / 0 downgraded / 0 rejected.
- DigitalSelf status SHA-256 was `E915F087780653DCCD1BB63C6F545D26D96DD7A81EC09D32D2F63612B2A4F106` both before and after regeneration. The target worktree was not modified.
- The candidate architecture baseline remains unapproved. No remote was configured and nothing was pushed.
