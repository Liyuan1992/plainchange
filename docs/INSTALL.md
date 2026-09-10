# 安装与首次使用

当前版本：`0.1.0a1`（Alpha）。它适合受邀用户在自己的电脑上试用，还不是面向所有人的正式版。

## 需要准备什么

- Windows 10/11、macOS 或 Linux。
- Git。
- Python 3.12 或更高版本。
- 一个至少有两次提交的本地 Git 项目。

分析在本机完成，目标项目保持只读。报告默认写到目标项目旁边的 `change-passport-reports` 文件夹。

## 方法一：从源码启动（推荐给当前 Alpha 试用者）

先安装 [uv](https://docs.astral.sh/uv/)，然后在项目目录运行：

```powershell
uv sync
uv run change-passport start
```

Windows 用户也可以双击仓库根目录的 `start-change-passport.cmd`。

浏览器会自动打开首次使用页面。接下来只需要：

1. 选择要理解的软件项目。
2. 确认要比较的较早版本和较新版本；默认就是最近一次改动。
3. 可选填写“这次原本想让 AI 做什么”，然后点击“生成变化说明”。

## 方法二：安装 Alpha wheel

收到 `change_passport_spike-0.1.0a1-py3-none-any.whl` 后，在它所在的目录执行：

```powershell
py -m pip install .\change_passport_spike-0.1.0a1-py3-none-any.whl
change-passport start
```

如果命令不在 PATH 中，可以使用：

```powershell
py -m change_passport start
```

## 本地页面没有自动打开

运行：

```powershell
change-passport start --no-open
```

终端会打印一个 `http://127.0.0.1:8765/` 开头的本机地址。复制到浏览器即可。页面只监听本机，不能作为公开网站使用。

## 端口被占用

换一个端口：

```powershell
change-passport start --port 8877
```

## 模型增强是可选项

首次使用页不调用模型，也不上传源码。高级用户需要模型增强时，可以使用 `analyze --generator model`，并按 README 配置任意 OpenAI-compatible 提供商。

## 当前限制

- 只分析已经提交到 Git 的两个固定版本，未提交的工作区变化不在范围内。
- 静态代码关系不等于真实运行、部署、数据库或网络行为。
- 自动生成的项目流程和负责人说明仍是候选，需要人核对。
- Alpha 尚未完成足够的非技术用户理解测试，也没有原生 Windows 安装程序。
