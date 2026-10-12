# Archify 接入试验 / Archify pilot

这次接入提供一个独立的 Python 适配脚本：把 PlainChange 的 `system-flow.json` 中一条流程转换为 Archify 交互图，同时保留完整条件、源码引用、疑点和未知项。尚未接入默认 GUI，也不是任意项目的自动布局器。

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

- 这是源码仓库内的脚本入口，不是 wheel 中新增的命令，也不是 Windows 便携包的新版本。
- 图和证据页分开，通过定位链接连接；点击图中节点尚不会自动打开对应源码面板。
- 图形校验不代表业务正确、测试执行或运行时验证。
- 保持 Archify 固定提交且已跟踪文件干净；不要直接用最新上游替代本版本。
- Archify 使用 MIT 许可，输出目录保留其版权与许可声明。

## English quick reference

Run the commands above from the repository root with Git, Python 3.12+ and Node.js 18+. The bundled input is synthetic, not a real DigitalSelf analysis. Open the generated `index.html`, or copy the complete output directory for offline reading. Custom reports need a matching, explicitly authored profile; this pilot is not a generic automatic converter. Existing private reports are not included in Git.
