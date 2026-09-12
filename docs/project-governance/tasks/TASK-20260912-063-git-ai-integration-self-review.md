# TASK-20260912-063：用 PlainChange 分析自身 Git AI 接入改动

状态：DONE
风险等级：标准
日期：2026-09-12
领域：产品自验证

## 目标

纠正 `TASK-20260912-062` 的验收对象偏差：上一份报告分析的是最小归因测试
仓库，只能验证 Git AI 链路，不能回答 PlainChange 这次接入 Git AI 到底改了
什么。此次应以 PlainChange 接入前的固定提交为 Base、当前实现快照为 Head，
生成面向软件负责人的真实 Change Passport。

## 范围

- 不提交或改写真实 PlainChange 工作区。
- 在 `D:\Dev\Labs` 创建独立验证副本，从当前固定 HEAD 建立基线，再复制
  当前工作区已存在的 Git AI 接入代码、测试和文档，形成只用于分析的提交。
- 使用现有本地 OpenAI-compatible 模型配置，以中文负责人语言生成报告。
- 报告必须重点识别：可选 Git AI 来源读取、隐私脱敏、证据权限边界、
  Windows 命令发现修复以及报告新增的代码来源区。

## 验收

- 首屏结论描述 Git AI 接入，而不是最小测试仓库的示例函数。
- 影响对象、仍未验证事项和负责人下一步行动与代码证据一致。
- “代码来源”不能被写成正确性、运行时或用户影响证明。
- 真实工作区在准备和分析前后保持不变；不提交、不推送 PlainChange。

## 批准依据

项目负责人指出：“这次分析不应该分析接入 GIT AI 的分析检测吗？”该反馈
明确纠正验收对象，并批准按 PlainChange 自身 Git AI 接入改动重新验证。

## 实施结果

- 在 `D:\Dev\Labs\plainchange-git-ai-integration-review-20260912` 建立独立
  验证副本，以 `6b10f9e4cc90a49c1f189b6dd93d3a290405a668` 为 Base，
  把真实工作区的 Git AI 接入改动固定为仅用于分析的 Head
  `b1eff9886794c8ae005ae71ae6b29e33aac743f0`；没有提交或改写真实仓库。
- 前三次模型调用分别暴露出工作流边不连续、引用未知来源/路径、来源引用超过
  本地上限的问题。没有为 PlainChange 写项目特例，而是统一收紧项目理解 JSON
  Schema、提示约束，并增加只删除非法/冗余值的契约归一化。兼容接口不支持的
  `uniqueItems` 没有留在正式 Schema 中。
- 为避免机械复制生成的验证提交把 1503 行错误记成人工历史，已从验证副本的
  活跃 `refs/notes/ai` 移除该合成记录，并保存在
  `refs/plainchange-validation/synthetic-snapshot-note` 供审计。最终报告如实显示
  1503 行“未追踪来源”、0% 历史来源覆盖，不把合成过程冒充真实作者历史。
- 正确报告生成在
  `artifacts/plainchange-git-ai-integration-review-v6/review.html`。首屏结论为
  “变更说明新增代码来源覆盖信息”，正文识别出可选 Git AI 来源记录、报告来源
  覆盖、Windows 命令兼容修复，以及运行、兼容性和实际覆盖仍未验证的边界。

## 验证

- `uv run pytest -q`：148 项全部通过，退出码 0。
- `uv build`：wheel 与 sdist 生成成功。
- `scripts/build-windows-portable.ps1`：便携包生成成功；ZIP SHA-256 为
  `4E79321FE0FB07AABB0F0E86847A8CEE3CE25A9B670AD0059476BC248F8C130D`。
- `git diff --check`：退出码 0；仅有 Git 的 LF/CRLF 提示，没有空白错误。
- 分析前后真实仓库 HEAD、活跃 Git notes 和工作区状态未被报告流程改变。
- 最终 `agent-provenance.json` 为 `no_record`，1503 行未追踪来源，且原始密钥
  命中数为 0。来源缺失只影响归因覆盖，不影响静态改动事实，也不证明正确性。

## 关联记录

- `BUG-20260912-055`
- `BUG-20260912-056`
- `EVO-20260912-049`
- `EVO-20260912-050`
