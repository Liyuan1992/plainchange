# TASK-20260923-049：Archify 本地接入试验

## 授权与范围

2026-09-23 用户确认四步方案：固定 Archify 版本；转换已有 DigitalSelf 报告的一条完整流程；保留条件、源码、疑点和未知；检查成品。
风险 standard，方案已获批。此为既有 PlainChange 的限定适配试验，不新建产品，不替换默认入口，不发布或推送。
原有 PROJECT、EVOLUTION、TASK-047、TASK-048 未提交变更保留。

## 实现

- 上游：`D:/Dev/Repos/archify`，提交 `9e35d2b0b39b155553ba9fcfe0b4f2a5198dd993`；没有修改上游源码或全局安装。
- 适配入口：`scripts/archify_pilot.py`；展示配置：`examples/archify-online-index.profile.json`。
- 输入：`D:/Dev/Projects/plainchange-reports/iteration-20260921-digitalself-memory/digitalself-understand/system-flow.json`。
- 输入固定 DigitalSelf `dc7114606ae8052d92c317d3e5203fac372f3231`；SHA-256 `1fb7e704de75287b0912378bd138c115c92e720f51c62f5f6f9deaf9805d0815`。
- 输出：`artifacts/archify-pilot-20260923/delivery/index.html`、`diagram.html`、`evidence.html/json` 和校验回执。
- 图包含 online_index 的全部 7 个节点和 10 条原有连线。两个跨流程调用/返回保存在证据页，不伪造重试回边。
- 图用人工编写的条件摘要；完整原条件、测试候选、状态和引用保存在配套证据页与 JSON。整份报告的疑点/反证/未知明确标为历史报告范围。
- 入口通过 Archify 已有 `#focus` / `#relation` 链接定位。尚未实现点击图中节点自动联动源码面板。
- 适配拒绝漏掉节点/分支、改写拓扑、越界引用及不匹配/脏的上游提交。上游 MIT 声明随成品复制。

## 验证与边界

初版长条件和默认布局未通过排线校验；改为明确的展示配置，并保留原条件后通过。
初版横向图通过 9/9 showcase 校验、四种桌面分辨率的自动浏览器检查，但实际图片显示图过于横长、留白偏多，因此没有接受为最终视觉效果。
后续将同一拓扑调整为准备判断、写入返回、异常退避三层，并将默认 Agent 图例改为索引处理步骤；最终交付再次通过 9/9 showcase、0 errors、0 warnings。

手动浏览器打开本地 index.html 被 Browser Use URL 安全策略拒绝。未改用其他浏览器/服务器绕过。最终版的手动点击及视觉复核未完成；初版自动浏览器回执不能作为最终版证据。
最终图 SHA-256：`d6138711bdbcee8bf681a6323361d0367853c457021a2d9678eae6f600544030`。

适配器专项测试 `tests/test_archify_pilot.py`：5 passed（0.02 秒）。覆盖完整条件和状态保留、禁止漏分支、禁止改拓扑、越界引用拒绝、源码转义及行号。
真实输入静态核对：完整 flow、product_review、unknowns 与原报告相等；7 个节点和 10 条边在最终 SVG 存在；所有详情锚点及图定位目标存在。回执 `delivery/integration-check.json`。这不代替浏览器点击验证。
`git diff --check` 通过；`ds` 在当前 PATH 不可用。没有提交或推送。旧版浏览器截图和回执归档到 `initial-browser-evidence/`，不作为最终版验证。

此试验未重新调用分析模型、未执行 DigitalSelf、未把候选测试改为通过、未导入外层复现实验结果。本人是否更容易理解仍待实际阅读。

## 复现

```powershell
.venv/Scripts/python.exe scripts/archify_pilot.py --report D:/Dev/Projects/plainchange-reports/iteration-20260921-digitalself-memory/digitalself-understand/system-flow.json --profile examples/archify-online-index.profile.json --archify D:/Dev/Repos/archify --output D:/Dev/Projects/PlainChange/artifacts/archify-pilot-20260923/delivery
```

本阶段结论：无需 fork 或改上游就可以复用渲染、路径交互与导出；目前仍依赖一条流程的人工布局配置和分开的证据页，不能称为通用全自动集成。

## 2026-10-12：按用户授权提交与推送

用户明确要求将本次功能提交推送到 GitHub，以便在其他电脑拉取使用。本轮加入 `docs/ARCHIFY.md`、双语 README 导航和不含真实源码的合成演示输入；脚本路径统一解析为绝对路径，页面采用输入报告标题及实际节点/分支数，避免换报告后仍显示 DigitalSelf 固定文案。

合成示例已通过真实 Archify CLI 生成，9/9 showcase、0 errors、0 warnings；适配专项 5 passed。未重新访问被浏览器策略拒绝的页面，不新增视觉验收声明。未上传本机报告、源代码片段、截图或模型调用记录。此前无关的 PROJECT 改写和 TASK-047/048 保留在本地。

GitHub 目标已实时核对为 `https://github.com/Liyuan1992/plainchange.git` 的 `main`，推送前为 `21952b9f355851bd5eeeb59f827724fe89cb5d9d`。本地 origin 仍指向旧本地仓库，因此使用明确 GitHub URL 推送，不改 origin 设置。运行说明使用相对路径；其他操作系统实际运行尚未验证。

本轮全量回归：`python -m pytest`，219 passed in 197.11s；`git diff --cached --check` 通过。提交限定为本次接入相关的 9 个文件，EVOLUTION 只暂存本次接入与发布记录，旧任务记录保留在工作区。
