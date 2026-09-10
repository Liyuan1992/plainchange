# TASK-20260910-031: Owner audience card responsive layout

State: DONE
Tier: standard

## Trigger and authority

The owner supplied a current generated-report screenshot and identified a layout-adaptation defect in the expanded `查看完整说明` area. The screenshot shows the audience explanation compressed into a near one-character-wide column, which stretches the card and the entire grid row. The owner requests correction; this authorizes a bounded responsive-layout fix without changing content, evidence, schema, or product scope.

## Source facts

- The affected-people question occupies the narrow right column of the desktop explanation grid.
- Each audience row currently forces three columns with minimum widths of 160 px and 110 px before allocating the remaining width to the explanation.
- At the captured content width, the explanation receives too little space and wraps almost character by character.
- The excessive height also determines the shared CSS grid-row height and leaves a large false blank area under the left question card.

## Approved plan

1. Keep the outer wide-screen two-column explanation hierarchy.
2. Reflow audience rows inside the affected-people card into a two-column heading row (`audience + status`) with the explanation spanning the full row below.
3. Add minimum-width and wrapping guards so long localized text cannot collapse into a vertical strip.
4. Validate wide, intermediate, and narrow viewports against real generated content.

## Non-goals

- No wording, source fact, question order, state label, schema, or data change.
- No vLLM-specific selector, string, card width, or breakpoint.
- No redesign of the first screen, owner map, technical evidence, or navigation.
- No new asset, dependency, commit, push, or deployment.

## Risks and stop conditions

- Stop if fixing the audience row changes the five-question reading hierarchy.
- Stop if any label or explanation becomes truncated, clipped, or horizontally scrollable.
- Stop if a target-specific conditional is required.

## Verification plan

- Add a focused CSS regression assertion for the affected-audience two-row layout.
- Regenerate the fixed vLLM artifact and capture the open explanation at 1440 px, the reported intermediate width, and 390 px.
- Check text dimensions, document overflow, console output, full tests, syntax, compileall, and diff checks.

## Rollback

Revert the scoped CSS/test/documentation edits to restore the previous three-column audience row. No evidence or generated source artifact is mutated.

## Handoff condition

Complete when every audience explanation has a usable horizontal measure at all three viewport classes, the shared grid row no longer stretches abnormally, and automated/browser checks pass.

## Observed result

- Audience items now use a two-row content-safe layout: audience plus status on the first row and the explanation across the full second row.
- The five questions now render into two independent semantic columns on wide screens: questions 1–2 on the left and 3–5 on the right. A tall right card no longer determines the next left-card position.
- At the existing responsive breakpoint, both columns merge in semantic order into questions 1–5.
- No question text, state, source data, evidence meaning, or interaction changed.

## Verification evidence

- Real Edge at 1560×1165 gives all four audience explanations 289 px of width and 21–42 px of height; no vertical-strip condition or horizontal overflow occurs.
- At the risky 1100×900 width, explanations retain 188 px and 42–62 px of height; no strip or overflow occurs.
- At 390×844, explanations retain 256 px, questions remain in 1→5 order, and no horizontal overflow occurs.
- Primary and secondary column gaps remain 14 px at all three widths, proving the false shared-grid-row whitespace is gone.
- Edge reports zero console problems. Screenshot review scores the corrected region 9.3/10.
- Full suite: 65 tests pass. `compileall`, JavaScript syntax, and `git diff --check` pass; diff check reports only existing LF-to-CRLF notices.
- The regenerated vLLM artifact retains 4 accepted / 1 safely downgraded / 0 rejected claims. Human comprehension and target runtime behavior remain untested.
