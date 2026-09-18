# Visual Spec

## Metadata

- Target page: Change Passport 变化首页
- Target mode: agent
- Reference: `00-inputs/reference.png`
- Current before: `00-inputs/current-before.png`
- Date: 20260912

## Project Context Summary

- Current framework: Python 生成单文件离线 HTML；原生 CSS 与 JavaScript 渲染。
- Current theme entry: `src/plainchange/assets/digitalself.tokens.css` 与 `templates/review.css`。
- Current page component structure: 顶栏、变化结论、三张状态卡、代码来源、完整说明、技术详情。
- Current usable resource paths: 现有状态色、chip、卡片、details、CSS 图标和双语字典。
- Business flows that must not change: 两个 Tab、跨 Tab 定位、完整说明、技术下钻、离线与语言切换。

## 1. Overall Page Layout

- 保留顶栏和双 Tab。变化页第一屏改成从结论到决策的垂直阅读链：具体变化 → 已替你验证 → 尚未验证 → 只剩你的决定。
- 桌面宽度内首先看到变化和验证，不要求进入技术详情才能知道结论。
- 代码来源是证据的一部分，放在验证控制面之后，不抢占“现在怎么办”的阅读顺序。

## 2. Left Sidebar Specs

- 无左侧栏；不得为这次改造新增导航。

## 3. Main Content Specs

- 结论标题必须说明新增能力，不使用“覆盖信息”等实现名词作为主语。
- 变化区用“以前 / 现在”对照；描述使用者能获得的新能力及无 Git AI 时的兼容行为。
- 验证区逐条显示真实收据，包含验证范围与边界；通过状态不等于生产验证。
- 未验证区逐条回答缺什么、为什么缺、怎么验证、由谁处理。
- 决策区只保留负责人真正需要选择或接受的事项；若无需运行命令，明确写出。

## 4. Right Sidebar Specs

- 无固定右侧栏。桌面可将“尚未验证”和“你的决定”并排，窄屏自然堆叠。

## 5. Card Specs

- 通过项使用绿色细边和勾号；未知项使用琥珀色但必须附原因。
- 每张卡最多一个主结论，避免三张抽象问句重复同一信息。
- 技术命令、文件数和实现术语进入折叠证据，不占负责人首屏。

## 6. Typography Hierarchy

- H1 先陈述使用结果；正文 16px 左右，行高不少于 1.6。
- 区块标题直接使用“已经替你验证”“还没验证”“你现在只需要决定”。

## 7. Colors, Backgrounds, Shadows, And Radii

- 复用现有蓝、绿、琥珀 token；不增加品牌色。
- 通过与未知依靠图标、标题和文字共同表达，不能只靠颜色。

## 8. Icon And Illustration Placement

- 使用现有 CSS 文本图标；本轮不需要位图或新插画。

## 9. Existing Features To Hide Or Downplay

- 下调“涉及内部”“文件数量”“未追踪行数”等技术指标权重。
- 原三张抽象问句卡不再作为首屏主结构；其事实进入新的控制面。

## 10. Fake Or New Features That Must Not Be Added

- 不增加会运行任意项目命令的假按钮。
- 不把任务文档中的自报直接显示为已验证；只有受合同校验的收据可进入通过区。
- 不声称生产运行、长期兼容、用户影响或 Git AI 历史来源已经验证。
