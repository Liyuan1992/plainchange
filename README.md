# Change Passport

[MIT License](LICENSE)

把一次固定的 Git 变化，变成一份可核对的说明：改了什么、为什么改、影响到哪里，以及哪些事尚不能确定。

状态：`0.1.0a1` 本地 Alpha 已具备候选报告与首次使用入口；尚未完成独立人工复述、三份评分样本或 baseline 批准。因此自动分区和负责人语言仍是待确认初稿，不是运行事实或独立效果评估。

## 三步开始

```powershell
uv sync
uv run change-passport start
```

浏览器打开后，只需选择项目、确认前后两个版本并点击“生成变化说明”。默认全程本地运行，不调用模型、不上传源码，也不修改目标项目。Windows 用户还可以双击 `start-change-passport.cmd`。完整安装与 Alpha 限制见 [安装与首次使用](docs/INSTALL.md)。

## 从这里看起

这份项目自身的展示使用隔离、只读的目标克隆，分析范围为 `a4576ec..688fc5f`：它修复了“仅因重新验证而更换提交号的静态导入边被误判为变化”的问题。生成结果确认 2 个模块变更、0 条新增/删除/修改的结构边，并保留“运行时影响尚未知”的边界。完整的可复核记录在 [自举展示记录](docs/showcase/change-passport-self-688fc5f.md)。

这个样本很适合检查工具是否把已知任务和真实代码变化对上；它不适合证明陌生项目上的泛化能力。后者仍需要独立样本、人工标注和评分。

## 它做什么

1. 只读固定的 Git base/head 与明确提供的任务、测试等证据。
2. 生成受约束的证据包、静态架构变化和候选 baseline；模型若参与，只能读取证据包。
3. 校验每个陈述引用的证据类型，不能支持的说法会降级，而不是伪装成事实。
4. 输出 Markdown、结构化 JSON、Mermaid 图，以及可直接打开、无网络请求的单文件 HTML。

它不会把静态 import 当成运行时执行，不会把 AI 的解释当成用户意图，也不会把候选 baseline 自动升级为已批准的项目理解。

## 快速开始

```powershell
uv sync --extra dev
uv run change-passport --help
uv run pytest -q
```

新项目优先使用一条命令生成可打开的候选报告：

```powershell
uv run change-passport analyze path\to\sample-manifest.json --output artifacts\sample
```

这条命令会先检查固定 Git 版本所需对象；对象不完整时只在 Change Passport 受管缓存中补齐，不写目标仓库。随后读取固定版本中有限的根目录项目说明，把它当作“项目自述”而不是事实，并分别核对工作步骤是否有代码位置支持、声明的先后顺序是否有编排代码支持。找不到、对不上或存在歧义时会保留“仅项目说明”“自动候选”或“顺序未验证”，不会为了补齐流程而伪造结论。最后生成项目分区初稿、四步总览、可展开的详细工作图、负责人候选说明和 `review.html`。阶段进度会同时输出到终端并持续写入 `run-receipt.json`。重复分析按不可变 blob 内容复用解析缓存；可用 `CHANGE_PASSPORT_CACHE_DIR` 指定缓存位置，否则优先使用 `E:\DevCache\change-passport`。

默认的自动说明不调用模型，也不上传源码。它会把自动业务语义标成“候选说明”，把 README 自述、代码位置支持、静态顺序支持、真实运行和负责人确认分开。即使某一步显示“代码支持”，也只表示固定版本中找到了对应实现位置，不表示软件已经真实运行或 README 一定正确。

需要模型增强时，复制通用配置模板并填写自己的兼容提供商地址和模型名：

```powershell
Copy-Item examples\model-provider.template.json model-provider.local.json
$env:CHANGE_PASSPORT_MODEL_API_KEY = "你的密钥"
uv run change-passport analyze path\to\sample-manifest.json --output artifacts\sample-model --generator model --model-config model-provider.local.json
```

接口使用通用的 OpenAI-compatible Chat Completions 协议，不绑定具体国内、国外或本地厂商。配置中的 `base_url` 可以填写 `/v1` 根地址或完整的 `/chat/completions` 地址；`model` 完全由用户决定。密钥只从 `api_key_env` 指定的环境变量读取，不能写入配置文件。

不同兼容服务的结构化输出能力并不一致，可选择：

- `json_schema`：优先选择，服务端按严格 Schema 约束输出。
- `json_object`：提供商只支持 JSON 模式时使用。
- `prompt_only`：提供商不支持 `response_format` 时使用，输出仍必须通过本地 JSON 与证据校验。

只有显式选择 `--generator model` 才会把已校验的 `generator-packet.json` 发送到配置地址。模型、耗时、输入/输出 Token（服务返回时）、配置哈希和内容哈希会写入 `model-run-receipt.json`；密钥、请求头和响应正文不会进入收据。超时、无效 JSON、未知证据或缺少密钥会明确失败，不会静默伪装成规则版成功。项目仍保留下面的人工文件桥。

标准的本地文件桥仍可用于人工或模型增强：

```powershell
# 1. 只读采集 Git 与显式输入证据，并建立结构变化事实
uv run change-passport prepare examples\sample-manifest.json --output artifacts\sample

# 2. 让人工或外部流程只读取 generator-packet.json，写出严格 JSON
#    （不使用上面的配置接口时，文件桥本身不会发送任何内容）

# 3. 校验引用和权威类型，再生成说明与可交互 HTML
uv run change-passport finalize artifacts\sample\generator-packet.json artifacts\sample\raw-brief.input.json --output artifacts\sample
```

如已准备符合 `change-passport.software-control.v1` 的负责人解释层，可用同一条通用入口生成两屏报告；渲染器不按项目名分支：

```powershell
uv run change-passport finalize artifacts\sample\generator-packet.json artifacts\sample\raw-brief.input.json --output artifacts\sample --software-control path\to\software-control.json
```

要让同一套工具适配另一仓库，可在 manifest 中显式引用目标配置：

```json
{
  "target_profile": {
    "path": "examples/target-profiles/change-passport.v1.json"
  }
}
```

配置可定义阅读分区、中文职责标签、术语、品牌，以及明确标注来源的产品/流程架构；它不能改变 Git、模块、静态边、影响路径或 baseline 的事实。每份结构快照都会记录配置 ID 和 SHA-256，并把该指纹绑定到每个分区来源。可参考 [项目自身展示 manifest 模板](examples/showcase/change-passport-self-688fc5f.manifest.json)、[本项目配置](examples/target-profiles/change-passport.v1.json) 与 [通用默认配置](src/change_passport/assets/default-target-profile.json)。

## 产物与边界

- `architecture-delta.json`：唯一的 before/after 静态拓扑与一跳影响事实。
- `system-architecture.json`：固定 Head 的完整受支持静态代码快照；不是运行时、部署、数据库或网络架构的证明。
- `conceptual_architecture`：由目标配置声明并显式标注的产品/流程架构，用来解释输入、处理、输出与人工决定；不是静态 import 事实。
- `architecture-baseline.proposal.json`：待人工决定的候选，不能直接复用为 approved baseline。
- `brief.json` / `brief.md`：经证据校验后的变化说明。
- `beginner-review.json` / `review.html`：从同一事实派生的小白阅读视图；不能反写事实或批准状态。
- `software-control.json`：可选、单独校验和绑定来源的负责人解释层；存在时 `review.html` 默认展示“这次改了什么 / 这个软件怎么工作”，技术证据仍可下钻。
- `target-profile.draft.json` / `software-control.auto.json`：`analyze` 生成的候选项目语义；负责人确认前不能升级为项目事实。
- `run-receipt.json`：阶段、完成比例、耗时、Git 对象状态、缓存命中与失败位置。
- `model-run-receipt.json`：仅在显式选择模型生成器时产生；记录非秘密的提供商/模型身份、配置哈希、耗时、Token 计数、包与输出哈希和失败状态。

大仓库的 `review.html` 不再把完整静态快照放进首屏 JSON。技术快照以确定性 gzip 形式保存于同一离线 HTML，并绑定压缩前后 SHA-256；只有用户展开“查看技术实现结构”时才解压和建立模块/关系索引。浏览器不支持解压或校验失败时，技术层会保持不可用，而不会伪装成已有证据。

“这个软件怎么工作”始终保留四步全局图。点击任一步会在该节点下方展开来源合同映射的详细步骤，再点同一步即可收起；切换步骤不会进入另一张详情图，也不需要返回总览。当本次变化能够唯一对应一个流程步骤时，“这次改了什么”会显示 `在软件流程中查看 →`，一键展开并定位到该节点；无法唯一映射时不显示这个入口。第二个 Tab 的右栏以步骤职责、前后关系、产出、修改位置和代码依据为主，变化影响与检查建议降为按需展开内容。

目标仓库必须保持只读。分析产物写入分析项目自己的 `artifacts/`，而非目标仓库；`artifacts/` 默认不入版本控制。真正的 baseline 只有在有人填写并明确批准 decision 后才会生成：

```powershell
uv run change-passport approve-baseline artifacts\sample\architecture-baseline.proposal.json artifacts\sample\baseline-decision.json --output artifacts\sample\architecture-baseline.approved.json
```

## 项目治理

跨代理流程、任务记录、原始问题/演进账本和架构决定位于 [docs/project-governance](docs/project-governance/README.md)。当前实现仍是本地证据实验，不包含服务端、IDE 插件、账号系统、远程集成、自动改代码或发布。
