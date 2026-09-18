# TASK-20260912-062：原生 Codex Git AI 自动归因验证

状态：DONE
风险等级：标准
日期：2026-09-12
领域：AI 代码来源

## 目标

在 Git AI hooks 安装后启动一个全新的 Codex 任务，只使用独立临时仓库验证：

1. Codex 的真实文件编辑是否被 Git AI 自动记录；
2. 普通 Git commit 后是否生成 `refs/notes/ai`；
3. 固定 `base..head` 的 Git AI JSON 是否包含 Codex 工具和模型归因；
4. PlainChange 是否能读取同一范围，同时不保存提示词、会话正文或人员标识。

## 范围

- 仅创建 `D:\Dev\Labs\plainchange-git-ai-codex-native-20260912`。
- 允许在该临时仓库内初始化 Git、创建基线提交、由新 Codex 任务编辑一个
  小型源码文件并创建验证提交。
- 不手动运行 `git ai checkpoint`；否则不能证明 Codex hooks 自动生效。
- 可读取 notes 对象、脱敏后的 Git AI 范围摘要和 PlainChange 输出状态。

## 明确不做

- 不修改、提交或推送 PlainChange。
- 不调用 `git ai ask`，不输出提示词、完整会话或原始转录。
- 不使用真实业务仓库，不发布任何验证仓库。

## 判定

- 通过：新任务的真实编辑在普通提交后形成 notes，且工具被识别为 Codex；
  PlainChange 得到可用的脱敏来源摘要并保持目标仓库只读。
- 部分通过：notes 存在但工具/模型缺失，或 Git AI 自身能读但 PlainChange
  降级；必须记录具体边界。
- 失败：没有自动 notes、需要手工 checkpoint，或任何私密会话内容进入
  PlainChange 默认产物。

## 批准依据

项目负责人已被明确告知“原生 Codex 真实归因验证需要一个新 Codex 任务”，
并于 2026-09-12 回复“好，先测试一下”，批准本任务所述隔离验证范围。

## 实际结果

- 在 hooks 安装后新建了独立 Codex 任务
  `Git AI 原生 Codex 归因验证`，只操作
  `D:\Dev\Labs\plainchange-git-ai-codex-native-20260912`。
- 新任务先创建人工基线，再通过 Codex 的正常补丁编辑能力为 `app.py`
  增加 5 行可运行代码，并使用普通 `git add` / `git commit` 创建验证提交。
  全程没有手动调用 `git ai checkpoint`。
- 固定范围为
  `3b9d10b6ff8de7b4b61d5b2032379351265e5748..e1608fb3cbfdfd12bd6cf94efa6d0c08c097993e`；
  自动生成的 `refs/notes/ai` 对象为
  `ca46d7c68f856f472b4f3bbd01db52e7cbcbd10d`。
- Git AI 归因汇总为：AI 新增 5 行、人工 0 行、未追踪 0 行，工具
  `codex`，模型 `gpt-5.6-sol`，会话数 1。验证仓库无远端，提交后
  工作树干净，没有推送或发布。
- 新 Codex 任务继承的进程 `PATH` 尚未包含安装后新增目录，但 Codex hooks
  使用绝对路径并正常工作。只读核验改用已校验安装路径，没有修改 PATH、
  hooks 或全局配置。
- 当前 PlainChange 对同一范围运行成功，`agent-provenance.json` 状态为
  `available`，保留相同的 5 行 AI、100% 覆盖率、`codex` 和
  `gpt-5.6-sol` 摘要。运行耗时 1.763 秒。
- PlainChange 分析前后验证仓库的 HEAD、notes 对象和工作区状态全部一致。
  产物对原始会话标识与提交测试邮箱均为 0 命中，禁止的原始私密字段键也为
  0 命中。

## 结论

原生 Codex hooks 自动归因、Git notes 持久化和 PlainChange 只读脱敏消费三段
链路均已验证通过。该结论只证明代码来源记录链路有效，不证明代码正确、运行
行为或用户影响。
