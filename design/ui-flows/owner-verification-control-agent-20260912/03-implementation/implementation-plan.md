# Implementation Plan

## Round

- Round number: 1
- Allowed focus: structure/layout and evidence-backed content projection.

## Regions To Change This Round

- 变化结果区、已验证区、未验证区、负责人决策区。
- 代码来源无记录状态的原因解释。

## Files To Change

- `src/plainchange/verification.py`
- `src/plainchange/generator_contract.py`
- `src/plainchange/validator.py`
- `src/plainchange/review_model.py`
- `src/plainchange/templates/review.html`
- `src/plainchange/templates/review.js`
- `src/plainchange/templates/review.css`
- 对应测试、项目任务与证据合同文档。

## Things Not To Change

- Git/架构事实、Git AI 原始读取合同、第二 Tab 语义、语言切换与技术下钻。
- 不自动运行目标代码，不增加项目名称规则。

## Expected Screenshot Changes

- 首屏不再是三个抽象问题；用户先看到具体能力变化与真实通过项。
- “还没验证”旁直接出现原因和验证方法。
- 页面明确说明负责人是否需要亲自运行命令。

## Verification Commands

- `uv run pytest -q`
- `uv build`
- 重新生成 Git AI 接入报告。
- Edge 桌面与 390px 截图、控制台和水平溢出检查。
