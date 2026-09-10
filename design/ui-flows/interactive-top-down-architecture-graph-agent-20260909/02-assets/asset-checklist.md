# Asset Checklist

## Existing Usable Assets

| Path | Purpose | warm / agent mapping | Status |
| --- | --- | --- | --- |
| `src/change_passport/templates/review.css` | Existing semantic node, focus, panel, and connector styling | agent | reuse |
| `src/change_passport/templates/review.js` | Existing topology ranking, SVG marker/path creation, obstacle checks, and click state | agent | reuse |
| `src/change_passport/assets/review-theme.json` | Existing product palette and geometry tokens | agent | reuse |

## Missing Assets

| Missing asset | Why existing resources are insufficient | Generation prompt | Target save path | Status |
| --- | --- | --- | --- | --- |
| None | The requested graph is a code-native interactive surface. | — | — | not needed |

## Assets That Should Not Be Generated

| Visual element | Preferred implementation | Reason |
| --- | --- | --- |
| Common icons | lucide / existing SVG / CSS | Scalable, accessible, themeable |
| Real text | Framework-rendered text | Sharp, accessible, localizable |
| Business buttons | Component code | Must preserve behavior and state |
| Simple shapes | CSS / tokens | Lighter and easier to theme |
| Architecture diagram | HTML buttons + CSS Grid + inline SVG | Must remain interactive and derive from real profile data |

## Generation Rules

- Generate only missing reusable bitmap assets.
- Do not generate a complete UI mockup as the implementation target.
- Keep generated assets mostly text-free.
- Save metadata beside generated files when the generator provides it.
- Never store API keys in prompts, metadata, commands, or files.
