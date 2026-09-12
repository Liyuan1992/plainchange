# Asset Checklist

## Existing Usable Assets

| Path | Purpose | warm / agent mapping | Status |
| --- | --- | --- | --- |
| `00-inputs/reference.png` | English change-view frame supplied by the owner | agent frame 1 | accepted |
| `00-inputs/current-before.png` | English software-workflow frame supplied by the owner | agent frame 2 | accepted |
| `docs/images/plainchange-self-demo-en.gif` | Existing README animation to replace | agent output | replace |

## Missing Assets

| Missing asset | Why existing resources are insufficient | Generation prompt | Target save path | Status |
| --- | --- | --- | --- | --- |
| None | The owner supplied both required real states | Not applicable | Not applicable | complete |

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
