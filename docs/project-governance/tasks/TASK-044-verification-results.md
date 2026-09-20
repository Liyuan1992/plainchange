# PlainChange 自动验证结果 · 2026-09-20

本轮选取的 3 个疑点均在报告对应的固定版本中复现。它证明系统能提出可验证的真实问题，但不能据此计算整体准确率，也不能代替普通人的理解测试。

| 报告问题 | 实际观察 | 对照结果 |
|---|---|---|
| memdsl / R3：查询字节预算 | 真实 MCP stdio 调用：report 模式要求 2,048 字节，却成功返回 19,096 字节；预算改到 65,536 时结果大小不变 | quarantine 模式小预算返回 820 字节、budget_limited；大预算返回 11,261 字节、ok |
| VideoFactory / F1：复用旧声音 | 同一路径音频从 220 Hz 替换为 440 Hz，普通 synthesize 仍显示 reuse，输出哈希与旧音频完全一致 | 未变输入能复用；--force 重新生成，输出哈希改变 |
| VideoFactory / F4：渲染与质检衔接 | 真实 render 成功生成可解码 MP4，但缺少 3 个签名字段；随后的 qa 抛出 StaleRenderError | 同一配置使用新版本目录运行 build，质检通过 10/10、acceptance=pass |

## 对产品的判断

“发现项目不足”已有运行证据支持；报告还能提供触发条件、源码和复现方向，具备辅助审查价值。3 份报告分别在 1440 和 390 像素宽度通过真实浏览器交互：5 张说明卡、源码展开、问题卡、流程导航和跨流程跳转；没有脚本错误或横向溢出。

“普通人是否理解”仍未验证，用户已选择暂不安排真人。本次浏览器检查只能证明内容可访问、操作可完成，不能证明读者读懂。没有完成全项目覆盖，另外 6 项待核查内容本轮未复现；不能把挑选的 3 项全部复现解释成系统准确率 100%。

## 证据与边界

- memdsl 版本 a061bc4efb9a0dacab04c2fa847bcf4b236146b4；VideoFactory 版本 d6594e3e51e5b3449445c31200575a1741d7ba52。源码导出副本逐文件与 Git archive 字节相符。
- 原项目 HEAD、Git 状态和跟踪文件差异指纹前后一致；未修改目标项目。此指纹不覆盖所有忽略文件和未跟踪文件的内容。
- 使用合成记忆、合成音频和 1.2 秒/12 帧小视频；未调用付费模型。音频结果限定为 locked_audio 同路径替换；不推广为所有语音后端参数均已实测。
- 保留两次测试脚本准备失败：MCP SDK 属性命名兼容问题、视频样例缺少 factual 声明；修正样例后重跑。它们不计入目标项目缺陷。
- 运行证据是本轮另外执行的验证，不是 PlainChange 原报告自动完成的验证；原报告的模型判断保持原样。
- ds 命令不可用，未执行该收尾集成。

完整 JSON：D:/Dev/Projects/plainchange-reports/product-evaluation-20260920/runtime-verification.json

复现脚本、原始输出、截图、MP4、源码副本：D:/Dev/Projects/PlainChange/artifacts/issue-verification-20260920/

复现命令（最后参数必须是未存在的新目录名）：

```powershell
& D:/Dev/Projects/memdsl/.venv/Scripts/python.exe -B -X utf8 D:/Dev/Projects/PlainChange/artifacts/issue-verification-20260920/reproduce_memdsl.py memdsl-budget-repeat
& D:/Dev/Projects/VideoFactory/.venv/Scripts/python.exe -B -X utf8 D:/Dev/Projects/PlainChange/artifacts/issue-verification-20260920/reproduce_video.py video-runtime-repeat
```

本轮完成验证与记录，未修复目标项目、未提交或发布。下一步优先修复这 3 项并沿用这些用例做回归。
