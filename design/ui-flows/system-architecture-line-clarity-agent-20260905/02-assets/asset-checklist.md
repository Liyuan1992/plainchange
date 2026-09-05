# Asset Checklist

## Metadata

- Target page: system-architecture-review
- Target mode: agent
- Design pack: `design/ui-flows/system-architecture-line-clarity-agent-20260905`
- Date: 20260905
- Image generation workflow: not used

## Existing Usable Assets

| Path | Purpose | warm / agent mapping | Status |
| --- | --- | --- | --- |
| `src/change_passport/assets/review-theme.json` | Existing colors, borders, radii and focus treatment | agent | reuse |
| `src/change_passport/templates/review.js` inline SVG | Paths, arrowheads and count labels | agent | refine in code |
| `00-inputs/reference.png` | User-reported before/problem reference | agent | analysis only |

## Missing Assets

| Missing asset | Why existing resources are insufficient | Generation prompt | Target save path | Status |
| --- | --- | --- | --- | --- |
| None | CSS and SVG can express all required clarity changes | — | — | not needed |

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
