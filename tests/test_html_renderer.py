from __future__ import annotations

import json
import re

from change_passport.html_renderer import (
    EXPECTED_THEME_PROPERTIES,
    render_review_html,
)
from change_passport.review_model import build_beginner_review_model

from test_review_model import validated_brief


def _embedded_model(html: str) -> dict:
    match = re.search(
        r'<script id="review-data" type="application/json">(.*?)</script>',
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
    assert html.startswith("<!doctype html>")
    assert "<script src=" not in html
    assert "<link " not in html
    assert "fetch(" not in html
    assert "XMLHttpRequest" not in html
    assert "WebSocket" not in html
    assert "localStorage" not in html
    assert "innerHTML" not in html
    assert "prefers-reduced-motion" in html
    assert "aria-selected" in html
    assert 'data-page="architecture"' in html
    assert "系统全景" in html
    assert "静态结构快照" in html
    assert "直接关系 · 点击可单独追踪" in html
    assert "蓝色：它依赖谁 →" in html
    assert "architecture-arrow-outgoing" in html
    assert "谁依赖它 ·" in html
    assert "architecture-focus-map" in html
    assert "先选一个中文子区域" in html
    assert "技术模块（可选）" in html
    assert "按源码位置自动整理" in html
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
