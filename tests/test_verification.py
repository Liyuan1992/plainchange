from __future__ import annotations

import copy
import json

import pytest

from plainchange.models import ManifestError, canonical_json_bytes, sha256_bytes
from plainchange.verification import (
    build_verification_control,
    parse_verification_receipt,
    validate_verification_receipt,
)


def receipt(base: str = "base", head: str = "head") -> dict:
    value = {
        "schema_version": "plainchange.verification-receipt.v1",
        "change_identity": {"base_commit": base, "head_commit": head},
        "producer": {"kind": "agent", "name": "Codex"},
        "checks": [
            {
                "id": "tests.full",
                "category": "tests",
                "status": "passed",
                "label": {"zh-CN": "完整自动测试", "en": "Full automated tests"},
                "summary": {"zh-CN": "148 项测试通过。", "en": "148 tests passed."},
                "scope": {"zh-CN": "本地测试套件", "en": "Local test suite"},
                "limitations": [
                    {"zh-CN": "不代表生产运行。", "en": "This does not prove production behavior."}
                ],
                "observed_at": "2026-09-12T03:00:00Z",
            }
        ],
    }
    value["receipt_sha256"] = sha256_bytes(canonical_json_bytes(value))
    return value


def test_verification_receipt_is_identity_and_hash_bound():
    value = receipt()

    assert validate_verification_receipt(value, expected_base="base", expected_head="head") == value
    assert parse_verification_receipt(json.dumps(value), expected_base="base", expected_head="head") == value

    wrong_range = copy.deepcopy(value)
    with pytest.raises(ManifestError, match="does not match"):
        validate_verification_receipt(wrong_range, expected_base="other", expected_head="head")

    tampered = copy.deepcopy(value)
    tampered["checks"][0]["summary"]["en"] = "Everything works."
    with pytest.raises(ManifestError, match="hash"):
        validate_verification_receipt(tampered, expected_base="base", expected_head="head")


def test_verification_control_separates_completed_checks_from_gaps_and_decision():
    claims = [
        {
            "id": "runtime.unknown",
            "section": "attention",
            "scope": "test_status",
            "claim_type": "unknown",
            "original_text": "尚未验证生产运行。",
            "text": "尚未验证生产运行。",
            "limitations": ["没有生产环境收据。"],
            "next_check": "执行一条真实使用路径。",
        }
    ]

    control = build_verification_control([receipt()], claims)

    assert [item["id"] for item in control["passed_checks"]] == ["tests.full"]
    assert control["failed_checks"] == []
    assert control["gaps"][0] == {
        "id": "runtime.unknown",
        "label": "尚未验证生产运行。",
        "reason": "没有生产环境收据。",
        "how": "执行一条真实使用路径。",
        "responsibility": {
            "zh-CN": "项目验证流程",
            "en": "Project verification workflow",
        },
    }
    assert control["decision"]["tone"] == "decide"
    assert control["decision"]["title"]["zh-CN"] == "是否在完成剩余 1 项验证前接受这次变化？"
    assert "不需要亲自执行工程命令" in control["decision"]["text"]["zh-CN"]
    assert control["decision"]["items"] == [
        {
            "id": "runtime.unknown",
            "label": "尚未验证生产运行。",
            "responsibility": {
                "zh-CN": "项目验证流程",
                "en": "Project verification workflow",
            },
        }
    ]


def test_verification_receipt_overrides_false_model_claim_that_receipt_is_missing():
    claims = [
        {
            "id": "attention.tests",
            "section": "attention",
            "scope": "test_status",
            "claim_type": "unknown",
            "original_text": "尚不能确认测试结果。",
            "text": "尚不能确认测试结果。",
            "limitations": ["没有 actual_test_receipt。"],
            "next_check": "获取实际测试收据。",
        }
    ]

    control = build_verification_control([receipt()], claims)

    assert [item["id"] for item in control["passed_checks"]] == ["tests.full"]
    assert control["gaps"] == []
    assert control["decision"]["tone"] == "ready"
    assert control["decision"]["items"] == []


def test_downgraded_receipt_claim_outside_attention_is_not_owner_work():
    claims = [
        {
            "id": "function.receipt-result",
            "section": "function",
            "scope": "test_status",
            "claim_type": "unknown",
            "original_text": "完整自动测试已通过。",
            "text": "该结果不能证明用户行为。",
            "limitations": ["收据只覆盖固定范围。"],
            "next_check": "在其他环境复核。",
        }
    ]

    control = build_verification_control([receipt()], claims)

    assert control["gaps"] == []
    assert control["decision"]["tone"] == "ready"


def test_attention_claim_with_completed_receipt_keeps_its_remaining_acceptance_step():
    claims = [
        {
            "id": "attention.visual",
            "section": "attention",
            "scope": "test_status",
            "claim_type": "verified_fact",
            "original_text": "27 项画面测试通过。",
            "text": "27 项画面测试通过。",
            "limitations": ["自动测试不能替代最终成片的视觉验收。"],
            "next_check": "观看一条重新渲染的完整视频。",
        }
    ]

    control = build_verification_control([receipt()], claims)

    assert control["gaps"] == [
        {
            "id": "attention.visual",
            "label": "仍需完成：观看一条重新渲染的完整视频。",
            "reason": "自动测试不能替代最终成片的视觉验收。",
            "how": "观看一条重新渲染的完整视频。",
            "responsibility": {
                "zh-CN": "产品负责人或真实使用者",
                "en": "Product owner or actual user",
            },
        }
    ]


def test_decision_lists_every_remaining_gap_and_uses_the_real_count():
    claims = [
        {
            "id": "runtime.unknown",
            "section": "attention",
            "scope": "test_status",
            "claim_type": "unknown",
            "original_text": "尚未验证生产运行。",
            "text": "尚未验证生产运行。",
            "limitations": ["没有生产环境收据。"],
            "next_check": "执行一条真实使用路径。",
        },
        {
            "id": "user.unknown",
            "section": "attention",
            "scope": "user_behavior_change",
            "claim_type": "unknown",
            "original_text": "尚未完成人工验收。",
            "text": "尚未完成人工验收。",
            "limitations": ["没有真实使用者反馈。"],
            "next_check": "请一名真实使用者完成验收。",
        },
    ]

    control = build_verification_control([receipt()], claims)

    assert control["decision"]["title"]["zh-CN"] == "是否在完成剩余 2 项验证前接受这次变化？"
    assert [item["id"] for item in control["decision"]["items"]] == [
        "runtime.unknown",
        "user.unknown",
    ]
    assert [item["label"] for item in control["decision"]["items"]] == [
        "尚未验证生产运行。",
        "尚未完成人工验收。",
    ]


def test_failed_checks_become_specific_stop_items():
    value = receipt()
    value.pop("receipt_sha256")
    value["checks"][0]["status"] = "failed"
    value["receipt_sha256"] = sha256_bytes(canonical_json_bytes(value))

    control = build_verification_control([value], [])

    assert control["decision"]["tone"] == "stop"
    assert control["decision"]["title"]["zh-CN"] == "先暂停：有 1 项检查没有通过"
    assert control["decision"]["items"][0]["id"] == "tests.full"
