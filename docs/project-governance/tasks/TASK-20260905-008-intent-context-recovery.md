# TASK-20260905-008: Recover the reason from available task context

State: DONE
Tier: standard

## Trigger and approval

The owner challenged the `为什么这样改` card: an absent validated `task_intent` claim does not prove that the task conversation is absent. When a task window exists, the product should use the user's requests and the AI's replies to help summarize the reason, while keeping an on-demand model call behind an explicit button because it consumes tokens.

The owner's earlier `直到完成之前不需要我确认` fast-mode instruction remains active, and this message explicitly supplies the desired behavior. It approves this bounded local-spike implementation and the corresponding v1.4 product-contract amendment. It does not authorize reading an unrelated task, transmitting a transcript, adding a remote model provider, production DigitalSelf integration, baseline approval, commit, push, package, or deployment.

## Evidence and diagnosis

- The frozen DigitalSelf packet already contains one `original_task` item and one `retrospective_claim` item.
- The constrained raw brief contains no `task_intent` claim, so the current beginner projection collapses the card to `现有证据没有说明为什么这样改。`
- The app can list and read existing Codex tasks, but a static no-network HTML report cannot invoke that task API or an LLM by itself.
- User-authored text and AI-authored explanations have different authority. An AI reply is useful context but cannot silently become verified user intent.

## Plan

1. Pass the already validated generator-packet task evidence into the beginner projection.
2. Distinguish `reason ready`, `task clues available`, and `task context unavailable` instead of treating all missing `task_intent` claims as the same unknown.
3. In the current offline report, add a `查看已有任务线索` button that reveals bounded user and AI excerpts with explicit source labels and no model call.
4. Amend the product contract so a connected product may show `从任务窗口提炼` only when the matching transcript is available; the button must state that it consumes tokens and must preserve user/AI/confirmation roles.
5. Keep the current artifact offline and deterministic. Do not add a fake live button or network capability.

## Non-goals

- No automatic transcript discovery, broad task-history scan, remote request, model API, account, source upload, or token billing implementation.
- No inference of implementation intent from Git diff, file names, architecture paths, or an AI reply alone.
- No change to the validated claim authority rules, architecture snapshot, topology, baseline, target repository, or design tokens.

## Files

- `src/change_passport/pipeline.py`
- `src/change_passport/review_model.py`
- `src/change_passport/generator_contract.py`
- `src/change_passport/templates/review.js`
- `src/change_passport/templates/review.css`
- `tests/test_review_model.py`
- `tests/test_html_renderer.py`
- `tests/test_pipeline.py`
- `design/ui-flows/intent-context-recovery-agent-20260905/`
- DigitalSelf `design/ui-flows/ai-coding-session-review/` v1.4 contract files

## Verification plan

- Unit tests for all three context states, stable identity, source-role separation, bounded excerpts, and safe script escaping.
- Pipeline test proving prepared task evidence reaches `beginner-review.json` and `review.html` without changing validated claims.
- Formal frozen DigitalSelf regeneration: existing task/AI clues become inspectable while the architecture snapshot identity and hash stay unchanged.
- Browser desktop and 390 px: default card, expand/collapse, source labels, no horizontal overflow, zero console warnings/errors.
- JavaScript syntax, compileall, full pytest regression, and screenshot review.

## Stop conditions

- The implementation would have to pretend the offline HTML can call the task window or model.
- AI-authored text would be labelled as user-confirmed intent.
- Full transcript text would be embedded without a bounded, local, user-authorized contract.
- A remote provider or DigitalSelf production mutation becomes necessary.

## Completion evidence

- Root cause corrected: missing validated `task_intent` no longer collapses existing packet task evidence into an unknown state.
- Formal frozen sample now exposes one bounded `用户原话` item and one bounded `AI 回复` item behind `查看已有任务线索`, with explicit source labels, zero-Token copy, and an AI non-confirmation warning.
- The v1.4 DigitalSelf contract defines `reason_ready`, `task_context_available`, and `task_context_unavailable`, plus a future connected `从任务窗口提炼（需要 Token）` action that is click-only and transcript-bound.
- Validation: 44 tests passed; compileall passed; JavaScript syntax passed; formal validation remained 8 accepted / 0 downgraded / 0 rejected.
- Browser: desktop default/expand/`Escape` focus return passed; 390 px reported `innerWidth=390` and `scrollWidth=390`; console warning/error count was zero.
- Architecture evidence stayed unchanged: snapshot identity `23400d64e98911ba3093d3a46471883a791f75212cbf67fa1b348134de8aa1cc`, SHA-256 `7484AFEE355CE286336044327C7DC9D0FE06AEF05980E55C8A7215D4CDED459C`, 1,057 modules, 1,768 static edges, 9 sections, 39 section-edge bundles, 0 unclassified.
- Formal artifacts: review model SHA-256 `7649CAC95053A2FE2CE1283B3D573EE2C14EC99951114591D3A9EE30C6C36439`; HTML SHA-256 `EFD06BD522683019BD688DC2329A1EDB1CCB48BFB31DE3FC749DBAD72C746DD5`; accepted capture SHA-256 `73B1C3DA777B4F4B6F1927490389072C2E9626DDD963FDC4B9E787B4B6391FCE`.
- Boundaries preserved: no task-history auto-scan, model/provider integration, transcript transmission, baseline approval, commit, push, package, deploy, or DigitalSelf product mutation.
