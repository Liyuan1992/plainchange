# ClaudeMap × M1.5：DigitalSelf 同范围产品体验对照

日期：2026-09-04
状态：第三方实测完成；M1.5 baseline 审核暂停，候选仍为 `pending`

## 目的

用一个开源、纯本地的第三方产品拆解与 M1.5 完全相同的 DigitalSelf 提交范围，重点比较人第一次进入产品时如何看全局、定位变化、理解影响、下钻细节和建立信任。

## 公平范围与工具边界

- DigitalSelf base：`d78f78bab15802f7062bfd6794061c7208432fbe`
- DigitalSelf head：`430c34288e9565340e05e4235091335daac17c7c`
- 第三方：ClaudeMap `0.1.0`，源码提交 `c2e1424f272aae22a6a14a8cde9cd6b44844d3c9`
- 上游：<https://github.com/ingridtoulotte/claudemap>
- 许可证：MIT；`pyproject.toml` 无运行时依赖。
- 本地审计：未发现 HTTP、socket、遥测、外部脚本加载或模型调用；内置自测 `28/28` 通过。
- 两个 DigitalSelf 快照通过独立的本地共享克隆检出，HEAD 精确匹配且工作区均为 0 条状态记录。Windows `tar.exe` 首次导出漏掉 4 个中文路径，因此那批快照被弃用。
- ClaudeMap 的交互 HTML 没有通过自动化浏览器实点：浏览器安全策略禁止打开本地 `file://`。本文对交互能力的描述来自实际生成产物和前端源码；静态五视图已经实际渲染检查。

## 同一范围的第三方结果

| 指标 | Base | Head | 差值 |
| --- | ---: | ---: | ---: |
| 扫描文件 | 2,915 | 2,918 | +3 |
| 非空行 | 928,905 | 929,522 | +617 |
| 导入连接 | 2,527 | 2,540 | +13 |
| 顶层模块 | 11 | 11 | 0 |
| 自动子系统 | 28 | 28 | 0 |

ClaudeMap 能识别三个新增路径，但产品本身没有 before/after 叠加，也没有把四个修改文件显式列为“本次修改”。如果只打开 Head 地图，本次参数校验变化几乎不可见。

M1.5 在相同范围中给出：3 个新增模块、4 个修改模块、36 个一跳静态依赖方、50 条去重影响路径，并把 7 个变化节点全部放在主图。

## 静态视图实测

### 架构视图

![ClaudeMap architecture](../../artifacts/third-party/claudemap/digitalself-head-architecture.png)

优点是首屏只有 11 个顶层模块，面积表示规模、颜色表示职责，用户几乎不需要学习。缺点是 `digital_self`、`tests`、`benchmarks` 粒度太粗，无法表达本次改动。

### 依赖与子系统视图

![ClaudeMap dependencies](../../artifacts/third-party/claudemap/digitalself-head-dependencies.png)

![ClaudeMap subsystems](../../artifacts/third-party/claudemap/digitalself-head-subsystems.png)

2,918 个文件同时出现后成为“星云”。搜索、缩放、邻居聚焦和缩略图对于探索有价值，但静态首屏本身没有可读的信息层级。

### 热力与功能视图

![ClaudeMap heatmap](../../artifacts/third-party/claudemap/digitalself-head-heatmap.png)

![ClaudeMap features](../../artifacts/third-party/claudemap/digitalself-head-features.png)

它们提供了很强的“可探索感”，但启发式标签容易被用户误认为事实：

- 一个只有 1 行的 `design/.../user-idea.md` 因自然语言中的分支词被算成风险最高的 45%。
- `messaging` 被标到 501 个文件，`user management` 被标到 349 个文件，信号过宽。
- 本次关键新增 `argument_validation.py` 的风险仅 3.01%，没有功能标签；被广泛依赖的 `skills/base.py` 为 12.47%。

因此这类热力/功能标签适合做探索提示，不适合作为已验证架构事实。

## 产品体验对照

| 体验维度 | ClaudeMap | 当前 M1.5 | 结论 |
| --- | --- | --- | --- |
| 首次进入 | 11 个大模块，极易建立全局轮廓 | 直接进入本次 14 节点 before/after | ClaudeMap 更适合 onboarding；M1.5 更适合审变更 |
| 变化感知 | 两张独立快照，无变化叠加 | 新增/删除/修改/影响明确着色 | M1.5 明显更强 |
| 导航 | 五视图、搜索、缩放、平移、缩略图、适配画布 | 静态 Mermaid | ClaudeMap 明显更顺手 |
| 下钻 | 点击节点看 LOC、风险、fan-in/out、导入与被导入邻居 | 需要转到 JSON/源码证据 | ClaudeMap 的详情抽屉更像产品 |
| 信息密度 | 架构层很轻；文件层过载 | 默认限制 14 节点，32 个显式折叠 | M1.5 的变更主视图更克制，但折叠不可交互展开 |
| 影响解释 | 通用 fan-in/out，无本次变化路径 | 变化节点到直接依赖方的证据化路径 | M1.5 更贴近代码审查任务 |
| 可信度 | 风险、功能、架构风格为启发式，局部有明显误判 | 图拓扑来自固定 Git blob/import 证据，未知项保持未知 | M1.5 更适合治理和审批 |
| 复用 | 单文件 HTML/JSON，可离线分享；没有审批基线 | 有内容哈希、失效检测、候选/审批分离 | 两者目标不同：一个复用浏览体验，一个复用受控认知 |
| 导出 | HTML、JSON、SVG、PNG | JSON、Mermaid、Markdown | ClaudeMap 的交付体验更完整 |

## 最重要的产品结论

不应把 M1.5 改成 ClaudeMap 式的全图产品，也不应忽略它的交互体验。更合理的方向是“变更优先、全局可切换”：

1. 默认仍打开“本次变更”，确保用户一眼看出改了什么、影响哪里。
2. 增加“全局架构”作为上下文视图，而不是把 2,918 个文件直接塞进首屏。
3. 借鉴搜索、邻居聚焦、点击详情抽屉、图例筛选、缩略图、适配画布和导出。
4. 折叠的 32 个节点应可按需展开，而不是只能去 JSON 查 ID。
5. 节点详情应同时显示职责、接口变化、证据位置和影响理由，而不只是 LOC/fan-in/risk。
6. 风险、功能、架构风格等启发式必须显式标注“推测/提示”，不能混入 verified topology。
7. Baseline 的价值仍然成立，但应服务于默认变更视图和可选全局视图，而不是把知识图谱本身做成目标。

## 可复核产物

- `artifacts/third-party/claudemap/digitalself-head.html`：离线交互成品，SHA-256 `79DE0FD9E6E963E97CBC192BAD3B26C2691301B3B467D72314F8766D39300AAA`
- `artifacts/third-party/claudemap/digitalself-head.json`：第三方 Head 模型，SHA-256 `74ABB229F3FB79A04FC27396C86BADBD0C5775980D1F72AB528453FFA9F69F0E`
- `artifacts/third-party/claudemap/digitalself-base.html` / `.json`：相同范围的 Base 快照
- `artifacts/third-party/claudemap/digitalself-head-{architecture,dependencies,subsystems,heatmap,features}.{svg,png}`：五种静态视图

本实验没有批准 M1.5 baseline，没有启动连续三次变更验证，也没有修改 DigitalSelf 的目标提交。
