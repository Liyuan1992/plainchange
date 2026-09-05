# Change Passport Spike

Status: Local baseline committed; UI work frozen; factual-fidelity evaluation, independent retelling, and the architecture-baseline decision remain pending

## Purpose

Test whether a local, evidence-bound architecture delta and change brief can explain an AI-assisted code change, preserve approved project understanding between runs, and avoid treating an agent summary as proof or leaking the after-the-fact answer into generation.

This repository is an experiment, not a product MVP. Its first gate is factual fidelity on historical Git changes.

## 快速开始

```powershell
uv sync --extra dev
uv run change-passport --help
```

第一阶段采用三步文件桥：

```powershell
# 1. 只读采集 Git 和显式输入证据；同时生成架构 delta、Mermaid 图和基线候选
uv run change-passport prepare examples\sample-manifest.json --output artifacts\sample

# 2. 让受约束模型只读取 artifacts\sample\generator-packet.json，
#    按合同写出 artifacts\sample\raw-brief.input.json

# 3. 校验模型引用与权威类型，再渲染 brief.json / brief.md / beginner-review.json / review.html
uv run change-passport finalize artifacts\sample\generator-packet.json artifacts\sample\raw-brief.input.json --output artifacts\sample

# 4. 人工填写 annotation.template.json 后计算指标
uv run change-passport score artifacts\sample\brief.json artifacts\sample\annotation.json --output artifacts\sample\score.json
```

`prepare` 新增的 M1.5 artifact：

- `architecture-delta.json`：唯一的结构化 before/after 拓扑和一跳影响事实。
- `architecture-map.mmd`：只从同一份 delta JSON 渲染的主图。
- `architecture-baseline.proposal.json`：`pending` 候选，不能直接作为下一轮 approved baseline。
- `baseline-decision.template.json`：人工决定模板。
- `system-architecture.json`：冻结 Head 的完整受支持静态模块/依赖快照、中文系统分区、底层边映射、变化 overlay、coverage 与限制；它是候选派生视图，不是已批准 baseline，也不等于完整运行时架构。

`finalize` 在同一已校验事实基础上额外生成：

- `beginner-review.json`：确定性的“小白四问 + 中文职责节点 + 技术引用”展示模型；它不是事实权威，也不能写回 baseline。
- `review.html`：可以直接双击打开的单文件只读页面；包含 `变化解读 / 整体架构` 一级 Tab、分区与模块下钻；不启动服务、不加载远程资源、不访问网络。

只有人工补全并明确批准 decision 后，才可生成 approved baseline：

```powershell
uv run change-passport approve-baseline artifacts\sample\architecture-baseline.proposal.json artifacts\sample\baseline-decision.json --output artifacts\sample\architecture-baseline.approved.json
```

下一次 manifest 可选引用它：

```json
{
  "architecture_baseline": {
    "path": "artifacts/sample/architecture-baseline.approved.json"
  }
}
```

示例 manifest 只含占位路径，不能直接运行。当前实现不会调用模型 API；Codex 或 Claude Code 只能通过 `generator-packet.json → raw-brief.input.json` 文件桥参与。

运行测试：

```powershell
uv run pytest -q
```

第一阶段合同记录在 [`TASK-20260904-001`](docs/project-governance/tasks/TASK-20260904-001-phase0-evidence-spine.md)。第一份真实 DigitalSelf prose 样本记录在 [`TASK-20260904-002`](docs/project-governance/tasks/TASK-20260904-002-first-digitals-self-sample.md)。M1.5 实现在 [`TASK-20260904-003`](docs/project-governance/tasks/TASK-20260904-003-m15-architecture-baseline-delta.md) 下进行；小白优先的本地交互产物记录在 [`TASK-20260904-004`](docs/project-governance/tasks/TASK-20260904-004-beginner-first-interactive-review.md)；完整受支持代码架构 Tab 记录在 [`TASK-20260904-005`](docs/project-governance/tasks/TASK-20260904-005-system-architecture-tab.md)。首份正式生成样本位于忽略提交的 `artifacts/digitalself-430c342-m15/`，其 baseline proposal 仍等待项目所有者另行决定。

## 来源合同

源 PRD 位于 DigitalSelf。v1.0 的确认只覆盖已完成的证据主干；v1.2 明确确认小白变化解读，v1.3 由用户开启 fast mode 后完成整体架构增量：

```text
D:\Dev\Projects\DigitalSelf\design\ui-flows\ai-coding-session-review\01-prd\prd.md
v1.0 SHA-256: 643F7A632523F831B0C90E5A9D6543A9CF4ADB456485DCBDB8B2A08C33199C7E
v1.0 Confirmed: 2026-09-03T07:32:53.478590Z
v1.1 SHA-256: 995E5701B2438A08ED9E32FBE68E54E197DB7F126BCDCECE0B6F3D953D3C1B9C
v1.1 Confirmed: 2026-09-04T04:47:49.462723Z
v1.2 SHA-256: 1787776EE1A415D00CF804C41CF6349108675CEF7637ED6454F1AEEB57A276A6
v1.2 Confirmed: 2026-09-04T10:01:22.671559Z
v1.3 amendment path: D:\Dev\Projects\DigitalSelf\design\ui-flows\ai-coding-session-review\01-prd\prd-v1.3-architecture-tab-draft.md
v1.3 SHA-256: B4B97D38C0BEF959D7D0EA19E4F82CA36BF7F20D9753BE8B7804A1D1177676DF
v1.3 Fast mode authority: 用户明确表示“直到完成之前不需要我确认”
```

修订实验仍只做本地 CLI/JSON/Markdown/Mermaid 与单文件 HTML 评测产物，不包含产品化 Desktop/Web UI、IDE 扩展、SaaS、PR Bot、自动修改代码或产品发布。

## Project governance

The cross-agent workflow, source logs, curated domain learning, ADRs, and task records live in [docs/project-governance/](docs/project-governance/README.md).
