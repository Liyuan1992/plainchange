# Scope Lock

## Reference Exists And Current Business Exists: Must Implement

- 保留真实代码变化结论、代码来源、状态边界和两个主 Tab。
- 把截图中难懂的三张卡改成验证控制面，并解释无来源代码的时间原因。
- 使用已有 `actual_test_receipt` 权威类型，不另造不受约束的“AI 已验证”状态。

## Reference Exists But Current Business Does Not Exist: Do Not Fake, Pending User Confirmation

- 生产环境运行、长期兼容、外部用户理解测试均无现成收据，不得显示通过。
- 自动执行任意仓库测试会改变安全边界，本任务不添加。

## Current Page Exists But Reference Does Not Show It: Hide Or Downplay This Task

- 完整五问和技术关联图继续保留，但默认折叠。
- 静态关系数量、文件名和校验器术语不得占据首屏。

## Current Page Exists And Is A Key Business Flow: Restyle Only, Keep Behavior

- 语言切换、跨 Tab 定位、来源详情、完整说明和技术详情保持原行为。

## Hard Behavior Locks

- Do not change API, SSE, SkillResult, permissions, write-operation status, authentication, or other business contracts.
- Do not add fake data, fake entry points, or decorative business buttons.
- Verification receipts may confirm only their exact scope and fixed change identity.
- The UI must not infer that an absent receipt means a failed check.
