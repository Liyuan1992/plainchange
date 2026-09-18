# Round 1

- Focus: structure and layout
- Review items this round is allowed to fix: clipped conceptual nodes and missing horizontal user scrolling inside the technical canvas.
- Changes made: replaced the unified inner canvas's hidden overflow with contained horizontal auto overflow and token-based scrollbar styling; added an actual browser-wheel regression.
- Verification result: fixed report moved from scrollLeft 0 to 280 in Edge, remained document-overflow-free, and passed the full automated suite.
- Remaining deviations: native scrollbar visibility can still follow operating-system overlay-scrollbar preferences; horizontal wheel, trackpad/touch movement and the scroll range are available.
