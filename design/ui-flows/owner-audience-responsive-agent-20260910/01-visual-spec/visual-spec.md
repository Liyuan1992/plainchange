# Visual specification

## Target region

One region only: audience-impact rows inside the right-column `谁会感觉到变化？` card in the expanded five-question explanation.

## Required result

- Keep the outer desktop explanation grid and existing card hierarchy.
- Within each audience item, place the audience name and status label on the first row.
- Place the explanation on a second row spanning the full card width.
- Give the explanation a normal Chinese reading measure; it must not collapse into a one-character column.
- Let long audience names wrap naturally while the status chip keeps its intrinsic width.
- Preserve existing borders, colors, radii, typography, and source-driven state tones.
- At narrow width, retain the same stacked semantic order without horizontal overflow.

## Existing features to preserve

- Five-question order and text.
- Collapsed-by-default behavior.
- State labels and explanations.
- Before/after comparison, unknown list, checks, and technical disclosure.

## Forbidden changes

- No content rewrite or truncation.
- No vLLM-specific CSS or data.
- No new control, icon, asset, or business state.
