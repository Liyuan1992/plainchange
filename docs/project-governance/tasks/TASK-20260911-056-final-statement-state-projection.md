# TASK-20260911-056: Final statement-state projection

State: DONE
Tier: standard

## Trigger and authorization

Release preparation exposed BUG-20260911-049: a validator-downgraded,
architecture-only model claim could occupy the first screen's green confirmed
card. The owner authorized GitHub preparation without further confirmation
rounds; this is the directly exposed, generic release-blocking correction.

## Scope and verification

- When no accepted function-level change claim exists, show only the fixed-Git
  file-change fact in the confirmed card and explicitly leave semantic meaning
  unknown.
- Do not select a downgraded claim as a confirmed first-screen statement.
- Preserve accepted model title/detail language and all runtime boundaries.
- Add a regression fixture for an architecture-only unknown claim; run focused
  and full verification. No target-specific wording or source rule.

## Observed result

The first-screen confirmed card now selects a deterministic file-change fact
when no accepted function-level claim exists: it confirms the fixed Git file
count and explicitly says that the functional/architectural meaning is still
unknown. It no longer reuses the validator's unknown fallback text with a
confirmed label. The model contract also forbids blank `limitations` items in
both its raw-brief and change-summary schemas and prompt.

Focused semantic/model/pipeline tests pass (20 tests), and the fresh complete
pytest run passes at 100%. The original memdsl
rerun first failed visibly at local validation because the compatible provider
returned empty limitation strings; after the generic contract correction, the
same fixed range completed in 15.624 seconds using cached project
understanding. Its first card says `固定 Git 差异确认这次修改了 21 个文件；具体功能或架构含义还不能确定。`, with only `git.change_identity` and
`git.diff_summary` as its basis. Target HEAD remains
`a061bc4efb9a0dacab04c2fa847bcf4b236146b4` and its worktree remains clean.
