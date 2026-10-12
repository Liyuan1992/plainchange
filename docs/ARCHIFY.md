# 内置 Archify / Bundled Archify

## 正常使用：无需单独安装

更新 PlainChange 并安装依赖后，启动 `uv run plainchange serve`，选择“理解系统”，按原流程选择项目和模型，生成后打开系统报告即可。CLI 的 `plainchange understand` 使用同一个生成入口。

- 总览和所有已分析流程默认使用内置 Archify 交互查看器；点击总览节点可进入流程，点击步骤或分支可在右侧查看完整条件、源码引用和候选测试。
- 可直接使用查看器的主题、搜索、路径探索、缩放和导出入口；需要时可切换基础视图。
- 查看器已打包在源码及 wheel 内，无需 Node.js、额外仓库或手工 profile，也不会联网安装第三方代码。生成报告是自包含 HTML，可以离线复制。
- 分析部分仍需按 PlainChange 原要求配置模型或本地 Codex。已有 HTML 不会自行更新，须用新版重新生成报告。

内置的是固定版本 Archify **查看器**。PlainChange 负责通用流程布局、原始拓扑与证据联动；此路径没有调用 Archify CLI 的布局编译器，不宣称通过其 showcase 校验，也不保证任意复杂图无交叉。原条件和连线不会因展示而删除。当前改动针对“理解系统”，不是旧变更报告入口的全面替换。

维护者可用 `node scripts/build_archify_viewer.mjs <固定版本 Archify 仓库>` 重建内置资源。资源绑定上游提交和 SHA-256，保留 MIT 声明；普通使用者不运行此命令。

## 保留的独立渲染试验

下面是上一阶段的可选 Python 脚本，用于调用 Archify CLI 渲染器和 showcase 校验。它与上面的默认内置查看器是两个入口；只有这个试验脚本需要 Node.js、Archify 检出和人工编写的 profile。

## 在另一台电脑运行

需要 Git、Python 3.12+、Node.js 18+（本次验证使用 Node.js 24）。适配脚本只用 Python 标准库；Archify 固定版本自带校验器，无需 npm install。

在检出的 PlainChange 根目录执行，Windows、macOS、Linux 均可使用这些命令（某些系统的 Python 命令是 `python3`）：

```sh
git clone https://github.com/tt-a1i/archify.git ../archify
git -C ../archify checkout --detach 9e35d2b0b39b155553ba9fcfe0b4f2a5198dd993
python scripts/archify_pilot.py --report examples/archify-demo.system-flow.json --profile examples/archify-online-index.profile.json --archify ../archify --output artifacts/archify-demo
```

用浏览器打开 `artifacts/archify-demo/index.html`。同目录的 `diagram.html` 是交互图，`evidence.html` 是完整条件与证据；`validate.json`、`deliver.json` 和 `receipt.json` 记录本次生成的校验与哈希。拷贝整个输出目录可在另一台机器离线查看。

仓库示例是**合成演示数据**，不包含本机 DigitalSelf 私人源码或真实报告，也不证明任何真实系统行为。此前的 DigitalSelf 报告和浏览器截图在忽略的 `artifacts/` 或项目外目录，不随 Git 推送。

## 使用自己的报告

保留现有 PlainChange 使用方式，先生成 `system-flow.json`，再替换 `--report` 参数。报告须为 `plainchange.system-flow.v2`。

展示配置的 `flow_id` 选择一条流程；`nodes` 和 `edges` 必须分别覆盖其全部 ID。配置仅控制布局、颜色和条件摘要，不可修改连线起止点。自有报告需要根据实际节点、分支编写自己的 profile；内置 profile 仅适用示例的 `online_index` 结构。Schema 与布局限制由固定版本 Archify 校验，失败会返回诊断，不会作为成功交付。

源码、完整条件和原有未验证状态保存在证据页；图上的短条件是展示摘要。整个报告的疑点/未知项会保留，并标明不一定属于当前单条流程。源码仍会存在于输出中，请按原项目资料管理。

## 限制与许可

- 以下限制仅适用于独立试验脚本：它是源码仓库内的入口，不是 wheel 中新增命令。
- 试验脚本的图和证据页分开；默认内置报告已实现节点/分支与源码面板联动。
- 图形校验不代表业务正确、测试执行或运行时验证。
- 保持 Archify 固定提交且已跟踪文件干净；不要直接用最新上游替代本版本。
- Archify 使用 MIT 许可，输出目录保留其版权与许可声明。

## English quick reference

For normal use, generate a new report through the System Understanding UI or `plainchange understand`. The bundled Archify viewer is the default for overview and flow diagrams; no Node.js, extra checkout or manual profile is needed. Evidence stays in the report's side panel. PlainChange supplies layout/topology; this path does not claim Archify CLI showcase validation. The older optional CLI-renderer pilot above still requires Node.js and a matching manual profile. Existing private reports are not included in Git.
