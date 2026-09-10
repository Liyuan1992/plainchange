# Change Passport 自举展示：保留导入边误判修复

## 这个展示证明什么

这是 Change Passport 用自己的历史提交做的一次本地、可复核的正确性样本。它检查工具能否把一项已知的 bug 修复正确地映射成静态结构变化，而不会把重新验证的提交号变化误报为架构变化。

它不证明陌生仓库上的效果，不替代人工复述或评分，也没有批准任何 baseline。

## 固定输入

| 项目 | 值 |
| --- | --- |
| 目标范围 | `a4576ec..688fc5f` |
| 目标读取方式 | 临时隔离、detached HEAD 的只读克隆 |
| 目标状态 | prepare 与 finalize 前后均为 clean |
| 配置 | `change-passport` |
| 配置 SHA-256 | `928fcffe396d74ecfd73b49e6e8b968fdf0a8d90e1b10e17df80d8102ab30e26` |
| 显式证据 | 原始任务说明、已记录的测试收据 |

配置参与分区、呈现和明确标注来源的产品/流程架构说明；它不改变静态 Git/模块/边事实。快照中的每个分区来源均写入 `target-profile:change-passport:sha256:...`，因此任何人都可以核对这份展示使用了哪个配置文件。

## 观察到的结果

| 项目 | 结果 |
| --- | --- |
| 变更模块 | 2 个 modified，0 个 added/removed |
| 静态导入边 | 0 个 added，0 个 removed，0 个 modified |
| 静态系统快照 | 23 个模块、48 条 import 边、2 个分区、0 个未分类路径 |
| 产品/流程架构 | 8 个配置声明组件、8 条流程关系；输入、自动处理、输出和人工批准闸门在静态代码层之前展示 |
| 验证后的陈述 | 3 accepted，1 downgraded，0 rejected |
| 降级内容 | 没有证据确认这次变化与已批准历史记录的关系 |
| 候选 baseline | `pending`；没有批准或复用 |

“0 个 modified 边”是本展示最重要的回归事实：提交号本身只是重新验证的来源信息，不是拓扑变化；若 import 的文件位置或行号发生变化，仍会被识别为 modified。

## 读者可复查的边界

- 报告确认的是 Python/JavaScript 的受支持静态 import 关系，不是运行时调用、用户影响或性能结果。
- 测试陈述引用的是明确提供的测试收据；它不等价于本次运行了所有环境或外部 CI。
- HTML 页面是 `beginner-review.json` 的派生视图；它不能创造事实或把候选状态升级。
- 产品/流程架构来自带 SHA 指纹的目标配置，页面会明确说明它不是静态 import 图或运行时顺序。
- 本地生成的完整 JSON、Markdown 和 HTML 位于忽略提交的 `artifacts/change-passport-self-688fc5f/`。在获得单独的提交授权前，这份记录不是已发布版本。

## 复现方式

先创建一个与分析工作区分离的只读目标克隆，在其中 checkout 上述 Head，再把其绝对路径填入 [展示 manifest 模板](../../examples/showcase/change-passport-self-688fc5f.manifest.json) 的 `repository.path`。从分析工作区运行：

```powershell
uv run change-passport prepare examples\showcase\change-passport-self-688fc5f.manifest.json --output artifacts\change-passport-self-688fc5f
# 再由受约束生成者仅根据 generator-packet.json 写入 raw-brief.input.json
uv run change-passport finalize artifacts\change-passport-self-688fc5f\generator-packet.json artifacts\change-passport-self-688fc5f\raw-brief.input.json --output artifacts\change-passport-self-688fc5f
```

该模板的路径故意不是可直接执行的默认值：避免示例误把当前分析工作区当作允许写入的目标仓库。
