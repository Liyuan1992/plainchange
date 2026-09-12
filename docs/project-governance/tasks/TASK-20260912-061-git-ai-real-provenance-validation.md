# TASK-20260912-061：Git AI 真实来源采集验证

状态：DONE
风险等级：标准
日期：2026-09-12
领域：AI 代码来源

## 目标

在不修改 PlainChange 真实仓库 hooks、不改全局 Codex 配置、不持久修改系统
`PATH` 的前提下，使用 Git AI 官方 Windows 可执行文件和独立临时仓库，验证：

1. Git AI 能产生真实的 `refs/notes/ai` 来源记录；
2. PlainChange 能读取同一固定版本范围并生成归一化来源摘要；
3. PlainChange 分析前后不会改变 Git AI notes；
4. 默认产物不泄露提示词、会话位置、会话/人员标识或邮箱。

## 范围

- 从 Git AI 官方 GitHub Release 下载固定版本 Windows x64 可执行文件；保存到
  `E:\Downloads\Software\git-ai\<version>`，校验官方发布的 SHA-256。
- 在 `D:\Dev\Labs` 创建一个本阶段专用验证仓库。
- 仅在该验证仓库内使用 Git AI 的公开 checkpoint/commit 能力产生可控来源记录。
- 仅对单个命令进程临时追加 `PATH`，不写用户或系统环境变量。
- 用当前 PlainChange 工作区对验证仓库运行固定 `base..head` 分析并检查产物。

## 明确不做

- 不运行官方安装脚本，因为它会修改用户安装目录、PATH 和 Agent hooks。
- 不给 PlainChange 或其他真实项目安装 Git hooks。
- 不修改全局 Codex、Claude Code 或 Git 配置。
- 不调用 `git ai ask`，不打开或读取完整会话。
- 不提交、不推送、不发布 PlainChange。

## 风险与停止条件

- 下载哈希与官方 Release 不一致时立即停止，不执行二进制。
- Git AI 若必须依赖全局 Agent hook 才能生成测试记录，则停止并报告，不扩大授权。
- PlainChange 若修改验证仓库除预期 Git AI notes 之外的状态，则判定失败并保留证据。
- 任何原始会话、提示词、邮箱或密钥进入默认报告或模型上下文时判定失败。

## 验证计划

- 记录 Git AI 版本、下载 URL、官方 SHA-256 与本地 SHA-256。
- 固定验证仓库 base/head，记录 `refs/notes/ai` 分析前后对象 ID。
- 运行 `git-ai diff <base>..<head> --json`，确认真实来源数据存在。
- 运行 `plainchange analyze`，检查 `agent-provenance.json` 与 `review.html`。
- 检查目标仓库工作树、HEAD 与 notes 在 PlainChange 分析前后不变。
- 运行来源适配器相关测试；如本阶段修代码，则再运行完整测试。

## 批准依据

第一阶段明确把“安装并配置 Git AI、进行真实来源采集”留作需再次确认的下一步。
项目负责人于 2026-09-12 回复“继续下一步”，批准本任务所述的可回退、临时仓库
真实验证范围。该回复不授权全局安装、真实项目 hooks、提交或推送。

## 实际执行结果

- 官方 GitHub Release 当前稳定版为 `v1.7.5`。Windows x64 EXE 下载到
  `E:\Downloads\Software\git-ai\v1.7.5\git-ai.exe`；本地 SHA-256 与
  GitHub Release 摘要的
  `52e61e2d0830f6f9c0ef23ba658b68410df170c027d0d418f101c6a66ba32c4a`
  一致。
- 已创建独立验证仓库
  `D:\Dev\Labs\plainchange-git-ai-validation-20260912`，固定范围为
  `5f784a3310c995ba44ff76a30ce344178706b264..efad265ac5189606326abee9861bb65ddc0e3cbb`。
- `checkpoint mock_ai` 接受了一个真实请求，但在未安装全局集成的情况下，
  后续普通 Git commit 没有生成 `refs/notes/ai`；`git-ai diff --json`
  只返回没有 annotation/prompt 的提交差异，不能声称来源采集成功。
- Git AI v1.7.5 的后台进程即使收到测试数据库路径和临时
  `USERPROFILE`，仍会在真实用户目录创建 `.git-ai` daemon 状态。因此当前
  Windows 正式二进制无法满足本任务“完全隔离且真实记录”的约束。
- 一次把 `install-hooks --help` 当作帮助命令的尝试实际执行了安装，临时加入
  Codex/Claude hooks、VS Code 扩展并启动后台扫描。发现后已立即停止；
  官方 `uninstall-hooks` 移除了 hooks，VS Code 扩展已注销，后台进程已停止，
  两次新建的 `.git-ai` 状态与扩展残留已移动到回收站。最终核对为：
  Git AI 进程 0、用户 `.git-ai` 目录不存在、Codex/Claude Git AI 引用 0、
  VS Code Git AI 扩展 0；两份配置均可解析。

## 当前停止点

要获得真实 Codex 来源记录，需要按 Git AI 官方集成方式进行用户级安装，允许
其配置 Agent hooks、后台服务和用户级状态，并重启相关 Agent/IDE。该动作超过
本任务批准的隔离验证范围，需项目负责人单独授权后才能继续。

## 用户级安装批准

项目负责人于 2026-09-12 明确回复“授权”，批准按 Git AI 官方方式进行
用户级安装，包括配置 Codex/Claude hooks、安装 VS Code 扩展、启动后台服务，
以及在用户目录保存 Git AI 本地状态。本授权仍不包含提交、推送、发布，或读取
完整会话与调用 `git ai ask`。

## 授权后实施结果

- 使用 Git AI 官方 `v1.7.5` 安装脚本完成用户级安装。安装脚本和 Windows
  x64 可执行文件均从固定版本 Release 下载；可执行文件的安装后 SHA-256 仍为
  `52e61e2d0830f6f9c0ef23ba658b68410df170c027d0d418f101c6a66ba32c4a`。
- 当前安装包含 Codex 3 个 hook、Claude Code 2 个 hook、VS Code 扩展
  `git-ai.git-ai-vscode@0.1.22` 和一个用户级后台进程。`git-ai config`
  报告 `telemetry_oss_disabled: true`。
- 安装后的 Git AI 在独立验证仓库为固定范围
  `efad265ac5189606326abee9861bb65ddc0e3cbb..d55f0268d8e2d205c68616260a5602836d7488fe`
  生成真实 `refs/notes/ai` 对象
  `2775979ff0384d554392969873c0f77ec9c6ed49`。该受控记录使用官方
  `mock_ai` checkpoint，覆盖 `app.py` 的 4 行新增代码；它验证 Git notes
  记录与 PlainChange 适配器，不冒充一次原生 Codex 会话。
- 首次真实读取暴露出一个通用 Windows 兼容问题：`shutil.which` 返回
  `git-ai.EXE` 时，Git AI v1.7.5 会按调用名称错误转发到普通 Git。
  PlainChange 现在只在 Windows 上把已发现路径的 `.EXE` 后缀规范为
  `.exe`，不更改路径、命令参数或任何目标仓库规则。
- 修复后 `agent-provenance.json` 状态为 `available`：4 行 AI 记录、0 行人工、
  0 行未追踪，记录覆盖率 100%，一个脱敏会话摘要，工具为 `mock_ai`、模型
  为 `unknown`。PlainChange 分析前后 HEAD、notes 对象和工作区状态一致；
  工作区中原有的 `state/` 是前一轮隔离验证留下的未追踪测试状态，不是
  PlainChange 创建的。
- 对完整产物执行敏感信息反查，原始会话 ID、提示 ID、线程 ID、测试邮箱、
  commit message、`base_content` 和 `authorship_note` 均为 0 个命中。
- 146 项自动化测试全部通过；Python 编译、JavaScript 语法、diff 检查、
  Python sdist/wheel 构建和 Windows 便携包重建均通过。便携包 SHA-256 为
  `450859f6d5e76df06461c9147dc89745e4ae985e14d01fa32e24597f6e2837a6`。

## 已知限制与后续验证

- 安装过程扫描既有 Agent 历史后，用户级 `.git-ai` 状态当前约为
  3.5 GB，且仍可能随后台扫描增长。这是 Git AI 的本地运行成本，需要继续
  观察增长和清理策略；
  PlainChange 不读取该会话数据库。
- 当前 Codex 任务在 hooks 安装前已经启动，因此本任务自身没有验证原生
  Codex 会话。后续 `TASK-20260912-062` 已在安装后新建独立 Codex 任务，
  对新的固定提交范围确认自动归因、notes 持久化和 PlainChange 只读消费均通过。
- 本任务没有调用 `git ai ask`，没有读取完整会话，也没有提交、推送或发布
  PlainChange。
