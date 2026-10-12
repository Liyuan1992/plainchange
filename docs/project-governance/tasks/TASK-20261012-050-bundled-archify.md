# TASK-20261012-050：默认系统报告内置 Archify

用户明确授权“直接把这个加进去。然后推送到main”。范围 standard：把 Archify 查看器接入现有理解系统报告，并提交推送 GitHub main。

## 实现与边界

- 使用固定上游 9e35d2b0b39b155553ba9fcfe0b4f2a5198dd993 的真实查看器模板，压缩资源、MIT 声明及摘要随 Python 包分发。维护者脚本校验上游版本和干净状态；运行时校验资源摘要。
- GUI 与 CLI 的正常理解系统入口均通过 render_flow 默认内置查看器；总览及各流程可用，节点和分支联动现有源码面板，保留基础视图切换。
- 用户无需 Node.js、独立 Archify checkout 或人工布局配置。生成的 HTML 离线自包含，旧 HTML 不自动更新。
- SVG 布局仍由 PlainChange 生成；没有接入上游 CLI 自动布局编译器，不宣称默认报告通过 Archify showcase。
- iframe 使用脚本沙箱，不授予同源权限；消息校验窗口、每次挂载标识和当前合法 ID。报告保持禁止网络连接。
- 原有条件、未知和未执行测试状态保持不变；没有新增模型分析或运行目标项目。

## 验证

- 全量 Python 测试：221 passed in 198.73s。
- JavaScript 语法检查通过。
- 六条历史流程的 DOM 模拟检查通过：42 节点、53 分支，逐项联动详情，拒绝伪造窗口、过期标识及未知 ID；源数据不变。脚本 scripts/test_archify_dom.cjs 可复现。
- uv build 生成 wheel/sdist；核对 wheel 资源，并在隔离 Python 导入 wheel 后成功生成内置查看器报告，不依赖源码目录或 Node。
- 先前浏览器 URL 安全策略拒绝仍有效，没有绕过；本轮 DOM 模拟不是实际浏览器点击或视觉验收，导出效果及最终人读体验尚未确认。
- 本机真实报告仅在 ignored artifacts 中；无关 PROJECT、TASK-047/048 和旧 EVOLUTION 工作区修改保留。

发布目标为 https://github.com/Liyuan1992/plainchange.git 的 main；本地 origin 指向旧本地仓库，因此使用明确 GitHub URL 推送。
