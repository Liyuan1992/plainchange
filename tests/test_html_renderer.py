from __future__ import annotations

import json
import re

from change_passport.html_renderer import (
    EXPECTED_THEME_PROPERTIES,
    render_review_html,
)
from change_passport.review_model import build_beginner_review_model
from test_software_control import resign, software_control_sample

from test_review_model import validated_brief


def _embedded_model(html: str) -> dict:
    match = re.search(
        r'<script id="review-data" type="application/json">(.*?)</script>',
        html,
        flags=re.DOTALL,
    )
    assert match is not None
    return json.loads(match.group(1))


def _embedded_software_control(html: str):
    match = re.search(
        r'<script id="software-control-data" type="application/json">(.*?)</script>',
        html,
        flags=re.DOTALL,
    )
    assert match is not None
    return json.loads(match.group(1))


def _embedded_technical_payload(html: str):
    match = re.search(
        r'<script id="technical-payload-data" type="application/json">(.*?)</script>',
        html,
        flags=re.DOTALL,
    )
    assert match is not None
    return json.loads(match.group(1))


def test_single_file_html_embeds_valid_review_without_network_capabilities():
    model = build_beginner_review_model(
        validated_brief(),
        task_evidence_value=[
            {
                "id": "task.user",
                "kind": "task",
                "authority": "original_task",
                "content": "用户原话：把分散检查收口到统一入口。",
            },
            {
                "id": "task.ai",
                "kind": "task",
                "authority": "retrospective_claim",
                "content": "AI 解释：统一校验可以减少重复行为。",
            },
        ],
    )
    html = render_review_html(model)

    embedded = _embedded_model(html)
    assert embedded["review_identity"] == model["review_identity"]
    assert "system_architecture" not in embedded
    payload = _embedded_technical_payload(html)
    assert payload is None
    assert html.startswith("<!doctype html>")
    assert "<script src=" not in html
    assert "<link " not in html
    assert "fetch(" not in html
    assert "ensureArchitectureLoaded" in html
    assert "DecompressionStream" in html
    assert "XMLHttpRequest" not in html
    assert "WebSocket" not in html
    assert "localStorage" not in html
    assert "innerHTML" not in html
    assert "prefers-reduced-motion" in html
    assert "aria-selected" in html
    assert 'data-page="architecture"' in html
    assert "系统全景" in html
    assert "可展开的整体架构图" in html
    assert "系统工作流" in html
    assert "展开的静态实现" in html
    assert "architecture-story-band" in html
    assert "主路径（按编号阅读）" in html
    assert "computeConceptualLayout" in html
    assert "findTopDownConceptRoute" in html
    assert "routeCrossesConceptCard" in html
    assert "findOrthogonalConceptRoute" in html
    assert "--concept-tracks" in html
    assert "aria-expanded" in html
    assert "path.dataset.from" in html
    assert "path.dataset.to" in html
    assert "关系包含循环，已切换为结构化阅读" in html
    assert "关系过于密集，已切换为结构化阅读" in html
    assert "architecture-concept-label" not in html
    assert "静态结构快照" in html
    assert "architecture-inline-expansion" in html
    assert "architecture-module-details" in html
    assert "architectureModuleAreaEdges" in html
    assert "点击展开：" in html
    assert "这不是运行时调用顺序" in html
    assert "查看已有任务线索" in html
    assert "不调用模型，不消耗额外 Token" in html
    assert "用户明确提出 → AI 给出解释 → 用户是否确认" in html
    assert "architecture-link-label-bg" in html
    assert "还有 ${total} 个静态关联位置" in html
    for property_name in EXPECTED_THEME_PROPERTIES:
        assert f"{property_name}:" in html


def test_model_text_cannot_escape_application_json_script():
    attack = "</script><script>globalThis.pwned=true</script>\u2028仍需确认"
    model = build_beginner_review_model(validated_brief(malicious_text=attack))
    html = render_review_html(model)

    assert attack not in html
    assert "\\u003c/script\\u003e\\u003cscript\\u003e" in html
    assert "\\u2028" in html
    embedded = _embedded_model(html)
    function_claim = next(
        item for item in embedded["claims"] if item["id"] == "function.change"
    )
    assert function_claim["text"] == attack


def test_task_context_cannot_escape_application_json_script():
    attack = "</script><script>globalThis.taskPwned=true</script>"
    model = build_beginner_review_model(
        validated_brief(),
        task_evidence_value=[
            {
                "id": "task.user",
                "kind": "task",
                "authority": "original_task",
                "content": attack,
            }
        ],
    )
    html = render_review_html(model)

    assert attack not in html
    assert "\\u003c/script\\u003e\\u003cscript\\u003e" in html
    embedded = _embedded_model(html)
    why = next(item for item in embedded["summary"] if item["id"] == "summary.why")
    assert why["task_context"]["entries"][0]["text"] == attack


def test_owner_control_renders_two_plain_language_screens_without_replacing_fallback():
    model = build_beginner_review_model(validated_brief())
    control = software_control_sample()
    control["source_identity"]["review_identity"] = model["review_identity"]
    control = resign(control)

    html = render_review_html(model, control)

    assert _embedded_software_control(html)["control_identity"] == control["control_identity"]
    assert "这次改了什么" in html
    assert "这个软件怎么工作" in html
    assert "owner-map-inspector" in html
    assert "ownerMapSelectedId" in html
    assert "查看详细验证步骤" in html
    assert "查看技术实现结构" in html
    assert "查看完整说明" in html
    assert "owner-state-details" in html
    assert "ownerExpandedOverviewId" in html
    assert "ownerMapDepth" not in html
    assert "overview_map" in html
    assert "收起当前步骤" in html
    assert "返回四步总览" not in html
    assert "目前没发现" in html
    assert "还没验证" in html
    assert "☐" in html
    assert "深蓝边框 = 当前查看" in html
    assert "橙色 = 本次改动" in html
    assert "来自项目说明</strong>：项目自己这样描述" in html
    assert "找到对应代码</strong>：代码里确实有相关位置" in html
    assert "hasDeclaredSource" in html
    assert "hasCodeLocation" in html
    assert "owner-map-legend-swatch is-selected" in html
    assert "owner-map-legend-swatch is-changed" in html
    assert '.owner-map-node.changed[aria-pressed="true"]' in html
    assert '<div class="topbar-main">' in html
    assert '<details class="owner-full-explanation">' in html
    assert "owner-question-column owner-question-column-primary" in html
    assert "owner-question-column owner-question-column-secondary" in html
    assert '<details class="owner-relation-disclosure">' in html
    assert "owner-status-icon" in html
    assert ".owner-status-list { display: grid; grid-template-columns: repeat(3" in html
    assert ".owner-audience-row { min-width: 0;" in html
    assert ".owner-audience-explanation { grid-column: 1 / -1;" in html
    assert ".owner-question-column { min-width: 0; display: grid;" in html
    assert ".software-control-mode .hero { display: none; }" in html
    assert "function ownerChangePresentation(node)" in html
    assert html.count("ownerChangePresentation(") >= 4
    assert "function ownerMappedDetails(overviewNode)" in html
    assert "owner-map-inline-details" in html
    assert 'button.setAttribute("aria-expanded", String(expanded));' in html
    assert "state.ownerExpandedOverviewId === node.id" in html
    assert "在软件流程中查看 →" in html
    assert "function ownerChangeLocation()" in html
    assert "changedDetails.length !== 1" in html
    assert "overviewMatches.length !== 1" in html
    assert "openOwnerChangeLocation" in html
    assert 'state.ownerExpandedOverviewId = location.overview.id;' in html
    assert "从变化页定位到这里" in html
    assert "function ownerRelationContext" in html
    assert "这个步骤负责什么" in html
    assert "它从哪里来 / 前一步" in html
    assert "它会产生什么" in html
    assert "它会交给哪里 / 后一步" in html
    assert "这次修改发生在哪里" in html
    assert "代码依据到哪里" in html
    assert "ownerSecondaryContext(node, presentation)" in html
    assert "查看变化影响与检查建议" in html
    assert "四步总览 · 已展开" in html
    assert "legacy-change-content" in html
    assert "legacy-architecture-content" in html
    assert "fetch(" not in html


def test_fallback_embeds_null_software_control():
    model = build_beginner_review_model(validated_brief())
    html = render_review_html(model)

    assert _embedded_software_control(html) is None
