# Implementation Plan

## Round

- Round number: 1
- Allowed focus: asset normalization and animation packaging.

## Regions To Change This Round

- Normalize the two screenshots to their common visible rectangle.
- Resize both to 1440 pixels wide with preserved aspect ratio.
- Encode a two-frame looping GIF with 4000 ms per state.

## Files To Change

- `docs/images/plainchange-self-demo-en.gif`
- `docs/images/plainchange-self-change-en.png`
- `docs/images/plainchange-self-software-en.png`
- `docs/images/plainchange-self-demo-en.png`
- `04-validation/current-after.png`
- `04-validation/software-after.png`
- This design pack's validation records.

## Things Not To Change

- Report code, report content, README prose, Chinese screenshot/GIF, and evidence states.

## Expected Screenshot Changes

- The English README animation will show the accepted v12 bilingual report instead of the previous mixed-language report.

## Verification Commands

- Inspect source/output dimensions and frame durations with Pillow.
- Extract every GIF frame and compare it with the normalized PNG source.
- Run public documentation tests and `git diff --check`.
