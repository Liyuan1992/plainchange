# Asset Checklist

## Existing Usable Assets

| Path | Purpose | warm / agent mapping | Status |
| --- | --- | --- | --- |
| `src/change_passport/assets/review-theme.json` | Established colors, radii, and shadow | agent | reuse |
| `src/change_passport/templates/review.js` | Inline SVG arrows and obstacle-aware routing | agent | reuse |
| `src/change_passport/templates/review.css` | Grid canvas, cards, status chips | agent | reuse |

## Missing Assets

| Missing asset | Why existing resources are insufficient | Generation prompt | Target save path | Status |
| --- | --- | --- | --- | --- |
| None | Existing code-native assets cover the interface | — | — | not needed |

## Assets That Should Not Be Generated

| Visual element | Preferred implementation | Reason |
| --- | --- | --- |
| Common icons | lucide / existing SVG / CSS | Scalable, accessible, themeable |
| Real text | Framework-rendered text | Sharp, accessible, localizable |
| Business buttons | Component code | Must preserve behavior and state |
| Simple shapes | CSS / tokens | Lighter and easier to theme |

## Generation Rules

- Generate only missing reusable bitmap assets.
- Do not generate a complete UI mockup as the implementation target.
- Keep generated assets mostly text-free.
- Save metadata beside generated files when the generator provides it.
- Never store API keys in prompts, metadata, commands, or files.

Decision: no bitmap generation. It would add no functional clarity and would weaken the local single-file artifact.
