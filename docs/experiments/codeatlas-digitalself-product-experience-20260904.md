# CodeAtlas × DigitalSelf 产品体验对比

日期：2026-09-04  
状态：已完成隔离实测与账号登录后的交互点击验收  
对象：[CodeAtlas.live](https://www.codeatlas.live/)，不是同名 `Memnoc/CodeAtlas`，也不是 ClaudeMap

## 结论先行

CodeAtlas 是当前更合适的产品体验标杆。它最值得借鉴的不是“大而全的知识图谱”，而是三个产品原则：

1. **地图是常驻画布，Diff、影响、覆盖率和发现只是叠加层。** 用户不需要在多个互不相干的报告之间重新定位。
2. **点击逐层下钻，并保持空间上下文。** 从系统到功能、文件、函数逐步展开，而不是一次显示几千个节点。
3. **人和系统共用同一结构化底座。** 人看交互图，Agent 通过 MCP/JSON 查询同一份结构、路径和影响。

这与产品负责人提出的方向一致：输出应升级为本地 HTML 交互界面；默认先看本次变化，点击节点展开直接依赖与被依赖，点击分支再展开一层，证据与未知项在侧栏解释。

但 CodeAtlas 的分析事实不能直接照搬。对同一 DigitalSelf 变更，它的结构抽取很深，却出现了路径分隔符不一致、Feature 退化为文件名、Git Diff 在跨层回放中扩大成大量无关“修改”、新增文件没有稳定显示为新增、影响结果过载等问题。我们的优势仍应是“变更优先、证据可核验、未知不伪装成事实”。

## 为什么这次对象是对的

DigitalSelf 已确认 PRD 引用的是 [CodeAtlas.live](https://www.codeatlas.live/)。其官方产品定位直接覆盖：

- 五层架构图：系统、功能、序列、文件、函数流；
- commit、branch、PR Diff overlay；
- blast radius、路径查找、搜索、Health、Timeline Replay；
- 本地浏览器界面与结构化 MCP 工具。

此前 ClaudeMap 对比仍可作为“单文件离线总览”的旁证，但不能代表最佳交互体验。

## 版本、许可与隔离边界

| 项目 | 实测事实 |
| --- | --- |
| 最新 OpenVSX 扩展 | `codeatlaslive.codeatlas-live 9.3.0`，build `158` |
| 实际运行包 | `@codeatlas/mcp 5.3.0`，运行头显示 `5.3.0.158` |
| 版本一致性 | MCP server 文件和主 UI JavaScript 与 9.3.0 VSIX 内对应文件 SHA-256 完全一致 |
| VSIX SHA-256 | `02025480FF4B971FED395BE890084F84917CF7BD932DD494AFA5DE880BB3D7DA`，与 OpenVSX 发布值一致 |
| 许可 | 自定义 EULA，`All rights reserved`，明确禁止反编译和衍生作品；不是开源许可证 |
| 官网状态 | 页面仍显示“是否应开源 visual engine”的意向登记 |
| 公开热度 | OpenVSX 实测下载数为 18,016；官网宣称全渠道 22,800+。这不是 GitHub Star 数 |
| 网络/遥测 | 实测设置 `CODEATLAS_TELEMETRY=0` 和 `DO_NOT_TRACK=1`；运行日志明确确认不发送遥测 |
| 安装隔离 | 未执行推荐的 `npm install`，避免 postinstall 自动改写多个 Agent 配置并注册 Windows 后台任务 |
| DigitalSelf 边界 | 只在 `D:\Dev\Labs\change-passport-codeatlas-20260904\workspace` 的精确提交副本运行；原仓库未作为工具工作区 |

固定 Git 范围：

- base：`d78f78bab15802f7062bfd6794061c7208432fbe`
- head：`430c34288e9565340e05e4235091335daac17c7c`

## 实际上手体验

### 1. 安装体验

官方推荐安装会自动探测并改写 Claude Desktop、Cursor、Claude Code、Codex、Gemini、VS Code Copilot 和 Continue 的配置，还会注册常驻 daemon。这对“零配置”用户很顺，但对已有复杂 Agent 环境的用户过于侵入。

隔离下载后，固定版包首次启动还缺少运行时依赖 `chokidar`，浏览界面启动失败；在隔离包目录补齐后才成功。这个失败发生在 CodeAtlas 自身启动阶段，不是 DigitalSelf 解析失败。

### 2. 首屏体验

初次索引约 36 秒，日志报告 1,068 个文件、555 个 API 和 20,964 个图。首页随后显示：

- 1,068 Files
- 555 APIs
- 1 Service
- 505 Features
- 1,068 File diagrams
- 18,741 Function diagrams
- 499 Sequence diagrams

视觉层级、暗色主题、数字卡片和功能入口明显比当前 Mermaid 输出更像成熟产品。首页还提供 Junior / PM / Power 三种信息密度入口，其思想值得借鉴。

但所有图、Git Diff、搜索、Health、Impact 和 Timeline Replay 都在未登录状态被禁用。负责人随后自行注册账号并明确要求继续，本轮因此完成了登录后的 DigitalSelf 点击测试；没有启用 AI Review、LLM domain refinement、API testing、PR watcher 或账号配置变更。

### 3. 结构化接口实测

本地 MCP 接口无需登录，可以验证底层抽取质量：

| 检查 | 结果 |
| --- | --- |
| Workspace status | `ready`；1,068 files、555 APIs、20,830 graphs |
| 固定 base..head | 正确识别 7 个变更文件 |
| Review context | 返回完整 unified diff，但 `entryPacks=[]`、`dependents=[]` |
| Diff summary | 当前 snapshot 的 baseline 与 working 相同，因此返回 0 个变化；任意 base..head review context 没有自动投影为当前图 overlay |
| Forward-slash impact | 将 review context 原样输出的 `/` 路径传给 `get_impact_analysis`，得到 0 direct、0 transitive |
| Backslash impact | 改为 Windows `\` 路径后，得到 69 direct symbols、6 transitive functions、5 clusters、1 service |
| `base.py` impact-of-change | 0 entry points、0 affected sequences；它只回答可达 entry point，不等于模块导入消费者 |
| 新增 argument validation 搜索 | 第一结果被标成 Feature，但 label 是文件路径；该 cluster 只有生产文件和对应测试，0 entry points、0 subsystems |

这里有两个重要判断：

1. CodeAtlas 的 505 个 “Features” 不能直接理解为 505 个业务功能。至少在当前样本中，关键新模块的 Feature 只是以文件路径命名的结构聚类。
2. 69 个 direct impacts 主要是变更文件内所有符号，并不是 69 个外部消费者。与 M1.5 的 36 个一跳静态导入消费者不是同一口径，不能直接比较数字大小。

### 4. 登录后交互点击实测

固定选择 `d78f78b → 430c342` 后，CodeAtlas 正确提示正在构建 base/head snapshot，服务日志确认是 7 个变更文件；但完成约需一分钟，并自动进入 12 步跨层 Replay，而不是先停在本次变更总览。

真实点击链暴露了以下产品事实：

| 交互 | 实测结果 |
| --- | --- |
| Compare Commits | 基线与目标提交选择清楚，完成后自动回放 L5→L1；用户不能先看 7 文件总览再主动下钻 |
| L5 函数流 | `call_skill_with_policy` 的新增/删除分支能用绿/红标出，视觉反馈直观 |
| Replay 中间层 | 回放出现不在 7 个 Git 变更文件中的 `benchmarks/memory_dsl/comparison_evaluation.py`、`chat_ws` API 等“修改” |
| L1 系统层 | 回放末尾把唯一服务标成修改，并显示 470 HTTP routes；实时索引原本是 531，且该 Git 变更没有修改 Web 路由文件，无法建立证据归因 |
| Diff 状态保持 | 直接导航/重连后顶部仍显示提交范围，但 L1 回到 `No changes` 和 531 routes，说明范围徽标与实际 overlay 状态可能脱节 |
| 全局搜索 | Diff 模式打开搜索时，初始列表有 2,129 项并大量显示 `~`；查询后能准确找到新增源文件、测试和一个文件路径命名的 Feature |
| 搜索结果点击 | 点击 `argument_validation.py` 文件结果只关闭搜索框，没有进入文件图 |
| Windows 路由 | `/` 路径的文件路由显示 `Loading…` 并被服务判定为 not found；改用 `\` 后才能打开，与 MCP impact 的路径敏感问题一致 |
| L4 文件图 | 成功显示 32 个节点、3 imports、18 variables、11 functions；但真实新增文件没有 `ADDED` 标记 |
| 文件→函数下钻 | 点击 `validate_arguments` 可以进入 26 节点 L5 控制流，面包屑保留，证明“逐层下钻”交互成立 |
| 分支节点点击 | 点击判断节点没有出现持久侧栏、证据解释或按需展开下一跳；整图适配画布后文字很小、空白很大 |

因此，CodeAtlas 最成功的不是“替用户判断影响”，而是把图层、搜索、对比和下钻放在同一工作台；它最失败的地方恰好是本产品必须守住的边界：真实 Git 变化、派生结构变化和启发式变化没有被清楚区分。

## 产品体验对比

| 维度 | CodeAtlas | ClaudeMap | 当前 M1.5 |
| --- | --- | --- | --- |
| 首次进入 | 成熟首页、统计卡、分层入口 | 单 HTML，直接看图 | Markdown + Mermaid，工程感强 |
| 默认关注点 | 全项目地图 | 全项目地图 | 本次变化与直接影响 |
| 下钻 | 系统→功能→序列→文件→函数 | 搜索、节点邻居、详情 | 暂无交互下钻 |
| Diff | 跨层 overlay 与 12 步 Replay 已实测；局部红绿变化直观，但出现无关修改、路径错配和状态脱节 | 无 before/after overlay | 有确定性 before/after，但静态图 |
| 大仓库负担 | 分层和折叠设计明显更成熟 | 文件级图会变成星空 | 强制边界和折叠，信息少但可核验 |
| 语义可信度 | 结构深，但 Feature/impact 口径需要验证 | 风险/功能启发式噪声明显 | 只承认受支持静态关系，未知显式保留 |
| 机器消费 | 强：大量 MCP/SQL 工具 | JSON 可读但非 Agent 查询面 | JSON 是权威，但尚无查询/交互层 |
| 本地与账号 | 索引本地，但人类图需账号登录；本轮已由负责人账号完成点击测试 | 完全离线 | 完全本地 |
| 治理 | 评论、baseline、review 功能丰富，但不是我们的审批合同 | 无 | baseline proposal 与人工批准分离 |

## 应该借鉴的交互合同

建议后续 PRD 把下面内容作为 HTML 交互层，而不是扩大事实抽取范围：

1. **默认页面是“本次改变”，不是自动播放。** 首屏先稳定显示 7 个 changed nodes、最重要的一跳影响和折叠数量；Replay 只能由用户主动启动。
2. **画布不换，叠加层切换。** 同一空间位置切换“变更前 / 变更后 / 叠加”、“影响”、“证据”、“未知”。
3. **节点单击打开侧栏。** 侧栏固定显示：职责变化、接口变化、直接依赖、直接消费者、证据位置、未知/不支持关系。
4. **分支点击才展开。** 第一次点击只展开一跳；再次点击某条分支才展开下一跳，并显示“还折叠 N 个”。严禁默认倾倒全图。
5. **保持空间上下文。** 下钻后保留面包屑、返回、收起、适配画布、小地图和当前焦点，不让用户重新寻找节点。
6. **信息密度可切换。** 可借鉴 Junior / PM / Power 的思想，但先落成“简洁 / 详细”两档，不引入角色系统。
7. **人机同源。** HTML 只消费经过验证的 `architecture-delta.json`；Agent 也读取同一 JSON。画布状态不是事实权威，点击、布局和折叠只是视图状态。
8. **证据优先于动画。** 所有 changed edge、impact path 和责任/接口说明都必须能跳到 source ref；启发式标签必须标成“建议”或“未知”。
9. **本地即开即看。** 不复制登录门槛、账号依赖、后台 daemon 和全局 Agent 配置改写。
10. **路径在数据层统一。** Windows `\`、POSIX `/` 和 URL 编码都必须先归一到同一节点 ID；搜索、Diff、Impact 和路由不能各用一套路径合同。

## 不应该借鉴

- 不做五层全量图作为下一阶段目标；先验证一张 change-first 交互图能否明显提升理解速度。
- 不把结构聚类直接叫业务功能，除非有证据或人工确认。
- 不把“变更文件内符号数量”包装成外部影响范围。
- 不把跨层派生差异统一涂成 Git 修改；必须分别标识“代码直接变化 / 静态派生影响 / 启发式变化”。
- 不在提交对比完成后强制自动回放，也不让范围徽标与实际 overlay 状态脱节。
- 不让搜索、图布局或 LLM 命名结果进入 approved baseline。
- 不先做 AI Review、API Testing、Timeline Replay、Health 大盘或团队 SaaS。
- 不以下载量、官网数字或视觉精致度替代 DigitalSelf 样本上的正确性验收。

## 对 PRD 的影响

本报告只形成修订依据，不修改已确认 PRD，也不授权实现。

如果负责人下一步要求修订 PRD，建议把下一阶段限定为：**以现有 M1.5 validated delta JSON 为唯一事实源，增加一个无需登录的本地 HTML change canvas；验证点击下钻、overlay、证据侧栏和折叠分支能否让人一眼看出“改了什么、影响什么、哪里未知”。**

## 复现实验位置

- 运行隔离根：`D:\Dev\Labs\change-passport-codeatlas-20260904\`
- 精确 DigitalSelf 副本：`D:\Dev\Labs\change-passport-codeatlas-20260904\workspace`
- npm 包审计：`D:\Dev\Labs\change-passport-codeatlas-20260904\package-audit`
- OpenVSX 9.3.0 审计：`D:\Dev\Labs\change-passport-codeatlas-20260904\extension-9.3.0`

本轮未提交、推送、打包或部署本项目；未批准 M1.5 baseline；未开始连续三变更复用评估。
