# Round 2

- Focus: colors, spacing, icons, and illustrations
- Review items this round is allowed to fix: relation convergence, label collision, bidirectional-edge overlap, and unclear scan order found in round 1.
- Changes made: replaced the selected nine-card grid with a three-column focus map; duplicated bidirectional peers by direction; moved counts into named relation cards; gave every relation a dedicated routing lane; kept all facts and IDs unchanged.
- Verification result: 1440 px capture shows no line/card collision and no crossing; DigitalSelf user-entry sample renders 9 relation cards and 9 SVG lines; 390 px reports `scrollWidth === innerWidth`, hides SVG, and keeps all textual relations; console has zero warnings/errors.
- Remaining deviations: the six-item outgoing column continues below a 900 px viewport, intentionally using vertical scroll rather than shrinking text or reintroducing crossings.
