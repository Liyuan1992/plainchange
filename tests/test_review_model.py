from __future__ import annotations

import copy

import pytest

from plainchange.models import ManifestError
from plainchange.review_model import (
    build_beginner_review_model,
    validate_beginner_review_model,
)


def validated_brief(*, malicious_text: str | None = None) -> dict:
    before_core = {
        "node_id": "module.core",
        "kind": "module",
        "label": "core",
        "owned_paths": ["src/core.py"],
        "responsibilities": ["统一检查输入参数"],
        "interfaces": ["function:validate"],
        "invariants": [],
        "evidence_refs": ["git:path:src/core.py"],
        "last_verified_commit": "base",
        "content_identity": "blob.base",
        "verification_status": "verified",
        "change_status": "modified",
        "change_detail": "module content changed",
    }
    after_core = {**before_core, "last_verified_commit": "head", "content_identity": "blob.head"}
    consumer = {
        "node_id": "module.consumer",
        "kind": "module",
        "label": "consumer",
        "owned_paths": ["src/consumer.py"],
        "responsibilities": ["调用统一入口"],
        "interfaces": [],
        "invariants": [],
        "evidence_refs": ["git:path:src/consumer.py"],
        "last_verified_commit": "head",
        "content_identity": "blob.consumer",
        "verification_status": "verified",
        "change_status": "impacted",
        "change_detail": "direct consumer of a changed module",
    }
    edge = {
        "edge_id": "edge.consumer-core",
        "source_node_id": "module.consumer",
        "target_node_id": "module.core",
        "relation": "imports",
        "evidence_refs": ["git:path:src/consumer.py"],
        "last_verified_commit": "head",
        "verification_status": "verified",
    }
    delta = {
        "schema_version": "change-passport.architecture-delta.v1",
        "baseline_validation": {
            "status": "bootstrap_unapproved",
            "source_baseline_id": None,
            "base_commit": "base",
        },
        "change_identity": {
            "base_ref": "base",
            "head_ref": "head",
            "patch_sha256": "patch",
        },
        "before": {"nodes": [before_core, consumer], "edges": [edge]},
        "after": {"nodes": [after_core, consumer], "edges": [edge]},
        "added_node_ids": [],
        "removed_node_ids": [],
        "modified_node_ids": ["module.core"],
        "impacted_node_ids": ["module.consumer", "module.folded"],
        "added_edge_ids": [],
        "removed_edge_ids": [],
        "modified_edge_ids": [],
        "impact_paths": [
            {
                "changed_node_id": "module.core",
                "impacted_node_id": "module.consumer",
                "relation": "imported_by",
                "depth": 1,
                "evidence_refs": ["git:path:src/consumer.py"],
            }
        ],
        "display_omissions": {
            "max_display_nodes": 2,
            "omitted_node_ids": ["module.folded"],
            "omitted_impacted_node_ids": ["module.folded"],
            "omitted_context_node_ids": [],
        },
        "unknowns": ["dynamic imports remain unknown"],
        "limitations": ["module-level static imports only"],
        "analysis_stats": {
            "supported_files_total": 2,
            "parsed_base_files": 2,
            "parsed_head_files": 2,
            "reused_nodes": 0,
            "invalidated_nodes": 1,
            "displayed_nodes": 2,
            "omitted_nodes": 1,
        },
    }
    function_text = malicious_text or "调用前会先统一检查参数。"
    claims = [
        {
            "id": "function.change",
            "section": "function",
            "scope": "user_behavior_change",
            "status": "accepted",
            "original_text": function_text,
            "text": function_text,
            "claim_type": "verified_fact",
            "original_claim_type": "verified_fact",
            "confidence": "high",
            "importance": "high",
            "evidence_ids": ["task.original", "git.patch"],
            "limitations": [],
            "next_check": None,
        },
        {
            "id": "function.intent",
            "section": "function",
            "scope": "task_intent",
            "status": "accepted",
            "original_text": "把分散检查收口到统一入口。",
            "text": "把分散检查收口到统一入口。",
            "claim_type": "verified_fact",
            "original_claim_type": "verified_fact",
            "confidence": "high",
            "importance": "high",
            "evidence_ids": ["task.original"],
            "limitations": [],
            "next_check": None,
        },
        {
            "id": "architecture.core",
            "section": "architecture",
            "scope": "architecture_change",
            "status": "accepted",
            "original_text": "统一校验职责发生改变。",
            "text": "统一校验职责发生改变。",
            "claim_type": "verified_fact",
            "original_claim_type": "verified_fact",
            "confidence": "high",
            "importance": "high",
            "evidence_ids": ["arch.node.001"],
            "limitations": [],
            "next_check": None,
        },
        {
            "id": "attention.tests",
            "section": "attention",
            "scope": "test_status",
            "status": "downgraded",
            "original_text": "测试已通过。",
            "text": "需要人工检查证据包中的测试缺口。",
            "claim_type": "unknown",
            "original_claim_type": "verified_fact",
            "confidence": "low",
            "importance": "high",
            "evidence_ids": [],
            "limitations": ["缺少 actual_test_receipt"],
            "next_check": "运行独立测试。",
        },
    ]
    return {
        "schema_version": "change-passport.validated-brief.v1",
        "sample_id": "sample.review",
        "brief_identity": "brief.identity",
        "packet_sha256": "packet",
        "raw_brief_sha256": "raw",
        "change": {
            "repository_name": "sample",
            "base_commit": "base",
            "head_commit": "head",
            "changed_files": 1,
            "added_lines": 4,
            "deleted_lines": 1,
            "patch_sha256": "patch",
            "patch_truncated": False,
        },
        "claims": claims,
        "rejected_claims": [],
        "validation_summary": {"accepted": 3, "downgraded": 1, "rejected": 0},
        "architecture_delta": delta,
    }


def test_beginner_review_preserves_claim_node_omission_and_truth_boundaries():
    model = build_beginner_review_model(validated_brief())

    assert [item["question"] for item in model["summary"]] == [
        "发生了什么",
        "为什么这样改",
        "对谁有影响",
        "需要注意什么",
    ]
    assert model["summary"][1]["claim_ids"] == ["function.intent"]
    assert model["summary"][2]["truth_state"] == "inference"
    assert "不等于" in model["summary"][2]["text"]
    assert model["summary"][3]["truth_state"] == "unknown"
    assert model["node_details"]["module.core"]["claim_ids"] == ["architecture.core"]
    assert model["node_details"]["module.core"]["label_source"] == "verified_responsibility"
    assert model["branch_groups"][0]["node_ids"] == ["module.folded"]
    assert model["validation"]["source_omitted_node_ids"] == ["module.folded"]
    assert validate_beginner_review_model(model) == model


def test_claim_input_order_does_not_change_review_identity():
    brief = validated_brief()
    reversed_brief = copy.deepcopy(brief)
    reversed_brief["claims"].reverse()

    assert (
        build_beginner_review_model(brief)["review_identity"]
        == build_beginner_review_model(reversed_brief)["review_identity"]
    )


def test_missing_task_intent_and_task_context_stays_explicitly_unknown():
    brief = validated_brief()
    brief["claims"] = [
        item for item in brief["claims"] if item["scope"] != "task_intent"
    ]
    model = build_beginner_review_model(brief)

    why = next(item for item in model["summary"] if item["id"] == "summary.why")
    assert why["truth_state"] == "unknown"
    assert why["claim_ids"] == []
    assert why["text"] == "这份报告没有拿到任务对话，暂时无法说明为什么这样改。"
    assert why["task_context"]["state"] == "unavailable"


def test_missing_intent_claim_uses_available_user_and_ai_task_clues():
    brief = validated_brief()
    brief["claims"] = [
        item for item in brief["claims"] if item["scope"] != "task_intent"
    ]
    evidence = [
        {
            "id": "task.ai",
            "kind": "task",
            "authority": "retrospective_claim",
            "content": "AI 解释：希望把分散的参数检查收口到统一入口。",
        },
        {
            "id": "task.user",
            "kind": "task",
            "authority": "original_task",
            "content": "用户原话：安全和效率我都想要。",
        },
    ]

    model = build_beginner_review_model(
        brief,
        task_evidence_value=evidence,
    )
    why = next(item for item in model["summary"] if item["id"] == "summary.why")

    assert why["truth_state"] == "context"
    assert why["truth_label"] == "已有对话线索"
    assert why["claim_ids"] == []
    assert why["task_context"]["state"] == "available"
    assert why["task_context"]["action_label"] == "查看已有任务线索"
    assert why["task_context"]["action_cost"] == "不调用模型，不消耗额外 Token"
    assert [item["role"] for item in why["task_context"]["entries"]] == [
        "user",
        "assistant",
    ]
    assert "不能代替用户确认" in why["task_context"]["entries"][1]["warning"]
    assert validate_beginner_review_model(model) == model


def test_verified_intent_stays_authoritative_when_task_clues_are_also_present():
    evidence = [
        {
            "id": "task.user",
            "kind": "task",
            "authority": "original_task",
            "content": "用户原话：把检查收口到统一入口。",
        }
    ]
    model = build_beginner_review_model(
        validated_brief(),
        task_evidence_value=evidence,
    )
    why = next(item for item in model["summary"] if item["id"] == "summary.why")

    assert why["truth_state"] == "verified"
    assert why["task_context"]["state"] == "ready"
    assert why["claim_ids"] == ["function.intent"]


def test_review_identity_tampering_fails_closed():
    model = build_beginner_review_model(validated_brief())
    model["header"]["title"] = "tampered"

    with pytest.raises(ManifestError, match="identity"):
        validate_beginner_review_model(model)


def test_beginner_summary_hides_internal_authority_enum():
    brief = validated_brief()
    attention = next(item for item in brief["claims"] if item["id"] == "attention.tests")
    attention["text"] = (
        "需要人工检查证据包中的缺口。（校验原因：缺少权威类型: actual_test_receipt）"
    )

    model = build_beginner_review_model(brief)
    rendered = next(item for item in model["summary"] if item["id"] == "summary.attention")
    assert "actual_test_receipt" not in rendered["text"]
    assert "可核对的独立测试收据" in rendered["text"]
