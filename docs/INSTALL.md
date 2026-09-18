# PlainChange 安装与首次使用

当前版本：`0.1.0a1`（Alpha）。它适合受邀用户在自己的电脑上试用，还不是面向所有人的正式版。

## 需要准备什么

- 一个至少有两次提交的本地 Git 项目。
- Git。
- Windows 10/11（使用便携包时）；或 Python 3.12+ 与 `uv`（从源码运行时）。

分析在本机完成，目标项目保持只读。报告默认写到目标项目旁边的 `plainchange-reports` 文件夹。

普通使用不需要输入命令：使用便携版后直接双击 `PlainChange.exe`。CLI 只保留给
开发者和自动化。

## 方法一：Windows 便携包（推荐）

从 [GitHub Release](https://github.com/Liyuan1992/plainchange/releases) 下载
`PlainChange-windows-x64-portable.zip`，解压，然后双击
`PlainChange.exe`。首次页面直接选择项目、接口地址、模型名和 API Key；密钥只在当前进程
内存中使用。

当前仓库可以用 `scripts/build-windows-portable.ps1` 在本机构建该压缩包；公开附件
是否已发布以 Release 页面为准。

## 方法二：从源码启动（开发者）

先安装 [uv](https://docs.astral.sh/uv/)，然后在项目目录运行：

```powershell
uv sync
uv run plainchange serve
```

Windows 用户也可以双击仓库根目录的 `start-plainchange.cmd`。

浏览器会自动打开首次使用页面。接下来只需要：

1. 选择要理解的软件项目。
2. 确认要比较的较早版本和较新版本；默认就是最近一次改动。
3. 可选填写“这次原本想让 AI 做什么”，然后点击“生成变化说明”。

## 方法二：安装 Alpha wheel

收到 `plainchange-0.1.0a1-py3-none-any.whl` 后，在它所在的目录执行：

```powershell
py -m pip install .\plainchange-0.1.0a1-py3-none-any.whl
plainchange .
```

这会分析当前项目最近两个提交。需要选择其他项目或版本时，运行：

```powershell
plainchange serve
```

如果命令不在 PATH 中，可以使用：

```powershell
py -m plainchange .
```

## 本地页面没有自动打开

运行：

```powershell
plainchange serve --no-open
```

终端会打印一个 `http://127.0.0.1:8765/` 开头的本机地址。复制到浏览器即可。页面只监听本机，不能作为公开网站使用。

## 端口被占用

换一个端口：

```powershell
plainchange serve --port 8877
```

## 模型增强是可选项

首次使用页默认选择“完整理解”：用户填写自己的 OpenAI-compatible 接口、模型和 API Key 后，PlainChange 会先理解项目，再解释变化。密钥只在当前进程内存中使用，关闭 PlainChange 后清除，不会写入项目、报告、日志、配置文件或 Git。模型负责人说明会跟随浏览器语言（只支持英文、简体中文）；CLI 可用 `--human-language auto|en|zh-CN` 指定。选择“基础证据模式”或在没有配置时使用 CLI `auto`，不会调用模型，但报告会明确说明它没有完成业务语义理解。详见 README 的模型配置与隐私边界。

## 当前限制

- 只分析已经提交到 Git 的两个固定版本，未提交的工作区变化不在范围内。
- 静态代码关系不等于真实运行、部署、数据库或网络行为。
- 自动生成的项目流程和负责人说明仍是候选，需要人核对。
- Alpha 尚未完成足够的非技术用户理解测试；当前提供便携式 Windows EXE，但尚无安装程序、代码签名或自动更新。
