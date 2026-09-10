# Asset Checklist

## Existing Usable Assets

| Path | Purpose | warm / agent mapping | Status |
| --- | --- | --- | --- |
| `src/change_passport/assets/review-theme.json` | Semantic colors and spacing | agent | Reuse |
| Existing CSS cards and SVG arrows | Canvas nodes, focus, and unobscured relations | agent | Reuse |

## Missing Assets

| Missing asset | Why existing resources are insufficient | Generation prompt | Target save path | Status |
| --- | --- | --- | --- | --- |
| None | Existing tokens and CSS shapes cover the requested interaction | N/A | N/A | Not needed |

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
