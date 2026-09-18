from __future__ import annotations

import copy

import pytest

from plainchange.models import ManifestError
from plainchange.owner_presentation import localized_owner_control
from plainchange.review_presentation import automatic_review_presentation
from plainchange.software_control import validate_software_control
from test_software_control import resign, software_control_sample


def _apply_generated_messages(value, spec, root):
    result = copy.deepcopy(value)
    for item in spec["messages"]:
        if item["root"] != root:
            continue
        parent = result
        for part in item["path"][:-1]:
            parent = parent[part]
        parent[item["path"][-1]] = item["text"]
    return result


def test_dynamic_owner_message_uses_arguments_not_chinese_sentence_matching():
    control = software_control_sample()
    original_headline = control["first_screen_summary"]["headline"]
    control["presentation"] = {
        "schema_version": "plainchange.owner-presentation.v1",
        "source_language": "zh-CN",
        "messages": [
            {
                "path": ["first_screen_summary", "headline"],
                "key": "risk.runtime",
                "args": {
                    "no_model_semantics": True,
                    "unsupported_count": 14,
                    "unsupported_example": "settings.json",
                },
            }
        ],
        "source_language_paths": [["product", "purpose"]],
    }
    control = resign(control)
    validated = validate_software_control(control)
    original = copy.deepcopy(validated)

    english = localized_owner_control(validated)

    assert english is not None
    assert "Another 14 documentation or configuration changes" in english["first_screen_summary"]["headline"]
    assert "settings.json" in english["first_screen_summary"]["headline"]
    assert english["product"]["purpose"] == validated["product"]["purpose"]
    assert validated == original
    assert validated["first_screen_summary"]["headline"] == original_headline


def test_owner_message_cannot_target_evidence_identity_or_state():
    for path in (
        ["source_identity", "brief_identity"],
        ["first_screen_summary", "confirmed_change", "statement_state"],
        ["first_screen_summary", "confirmed_change", "basis", "claim_ids", 0],
    ):
        control = software_control_sample()
        control["presentation"] = {
            "schema_version": "plainchange.owner-presentation.v1",
            "source_language": "zh-CN",
            "messages": [{"path": path, "key": "state.confirmed", "args": {}}],
            "source_language_paths": [],
        }
        with pytest.raises(ManifestError, match="cannot target|approved text field"):
            validate_software_control(resign(control))


def test_generated_architecture_projection_uses_stable_state_and_ids_not_chinese_text():
    system = {
        "schema_version": "change-passport.system-architecture.v1",
        "status": "candidate_static_snapshot",
        "status_label": "任意来源语言中的状态文字",
        "snapshot_identity": "frozen-architecture",
        "target_profile": {
            "profile_id": "auto-AnyProject",
            "profile_sha256": "frozen-profile",
            "node_label_rules": [{"pattern": "api", "label": "任意入口标签"}],
            "module_areas": [
                {"id": "core", "label": "任意分区名称", "description": "任意分区说明"}
            ],
            "conceptual_architecture": {
                "architecture_kind": "capability_map",
                "purpose_statement_state": "project_declared",
                "title": "任意架构标题",
                "description": "项目自己提供的用途说明",
                "boundary_note": "任意边界说明",
                "components": [],
            },
        },
        "groups": [
            {
                "group_id": "core",
                "label": "任意实现名称",
                "responsibility": "任意实现职责",
                "group_source": "target-profile:auto-AnyProject:sha256:frozen-profile",
            }
        ],
    }
    model = {
        "review_identity": "frozen-review",
        "header": {"brand": {"name": "AnyProject"}},
        "conceptual_architecture": {
            "source": {"kind": "target_profile", "label": "任意来源标签"},
            "title": "任意架构标题",
            "description": "项目自己提供的用途说明",
            "boundary_note": "任意边界说明",
            "components": [
                {
                    "id": "declared-capability-1",
                    "label": "项目自己的能力名称",
                    "description": "项目自己的能力说明",
                    "implementation_groups": [{"id": "core", "label": "任意实现名称"}],
                }
            ],
        },
        "system_architecture": system,
    }
    original = copy.deepcopy(model)

    spec = automatic_review_presentation(model)

    assert spec is not None
    projected_review = _apply_generated_messages(model, spec, "review")
    projected_architecture = _apply_generated_messages(system, spec, "architecture")
    assert model == original
    assert projected_review["conceptual_architecture"]["title"] == (
        "Capabilities described in AnyProject's project documentation"
    )
    assert projected_review["conceptual_architecture"]["components"][0]["label"] == "项目自己的能力名称"
    assert projected_review["conceptual_architecture"]["components"][0]["description"] == "项目自己的能力说明"
    assert projected_review["conceptual_architecture"]["components"][0]["implementation_groups"][0]["label"] == "Core functions"
    assert projected_architecture["status_label"] == (
        "Candidate static snapshot; not approved as a long-term baseline"
    )
    assert projected_architecture["groups"][0]["label"] == "Core functions"
    assert projected_architecture["groups"][0]["responsibility"] == "Perform the software's main work."
    assert projected_architecture["target_profile"]["conceptual_architecture"]["description"] == (
        "项目自己提供的用途说明"
    )


def test_generated_change_technical_projection_uses_ids_counts_and_states():
    system = {
        "schema_version": "change-passport.system-architecture.v1",
        "status": "candidate_static_snapshot",
        "status_label": "任意状态原文",
        "snapshot_identity": "frozen-architecture",
        "change_overlay": {
            "added": [],
            "modified": ["module.api"],
            "removed": [],
            "impacted": ["module.docs"],
        },
        "target_profile": {
            "profile_id": "auto-AnyProject",
            "profile_sha256": "frozen-profile",
            "node_label_rules": [{"pattern": "api", "label": "任意入口标签"}],
            "module_areas": [],
            "conceptual_architecture": {
                "architecture_kind": "capability_map",
                "purpose_statement_state": "supported_interpretation",
                "title": "任意架构标题",
                "description": "任意自动用途说明",
                "boundary_note": "任意边界说明",
                "components": [],
            },
        },
        "groups": [
            {
                "group_id": "entry",
                "label": "任意实现名称",
                "responsibility": "任意实现职责",
                "node_ids": ["module.api"],
            }
        ],
    }
    summary = [
        {
            "id": "summary.what",
            "question": "任意问题原文",
            "text": "任意变化原文",
            "truth_state": "verified",
            "truth_label": "任意状态原文",
            "claim_ids": ["function.auto-change"],
            "items": [
                {
                    "text": "任意条目原文",
                    "truth_state": "verified",
                    "truth_label": "任意状态原文",
                }
            ],
            "next_check": None,
        },
        {
            "id": "summary.why",
            "question": "任意原因问题",
            "text": "任意上下文摘要",
            "truth_state": "context",
            "truth_label": "任意上下文状态",
            "claim_ids": [],
            "items": [],
            "next_check": None,
            "task_context": {
                "state": "available",
                "state_label": "任意上下文状态",
                "summary": "任意上下文摘要",
                "action_label": "任意操作",
                "action_cost": "任意费用",
                "entries": [
                    {
                        "role": "user",
                        "role_label": "任意角色",
                        "source_label": "任意来源",
                        "text": "Keep this project-authored task text unchanged.",
                        "warning": None,
                    }
                ],
            },
        },
        {
            "id": "summary.impact",
            "question": "任意影响问题",
            "text": "任意影响原文",
            "truth_state": "inference",
            "truth_label": "任意推断状态",
            "claim_ids": [],
            "items": [],
            "next_check": "任意检查原文",
        },
        {
            "id": "summary.attention",
            "question": "任意注意问题",
            "text": "任意注意原文",
            "truth_state": "unknown",
            "truth_label": "任意未知状态",
            "claim_ids": ["attention.runtime-unknown"],
            "items": [],
            "next_check": "任意检查原文",
        },
    ]
    view = {
        "nodes": [
            {
                "node_id": "module.api",
                "label": "任意入口标签",
                "label_source": "target_profile",
                "technical_label": "package.api",
                "status": "modified",
                "status_label": "任意变化状态",
            },
            {
                "node_id": "module.docs",
                "label": "任意未知标签",
                "label_source": "unknown",
                "technical_label": "package.docs",
                "status": "impacted",
                "status_label": "任意关联状态",
            },
        ],
        "paths": [{"changed_node_id": "module.api", "impacted_node_id": "module.docs", "relation_label": "任意关系"}],
    }
    model = {
        "review_identity": "frozen-review",
        "header": {"brand": {"name": "AnyProject"}},
        "change": {"changed_files": 4},
        "summary": summary,
        "views": {"after": view},
        "node_details": {
            "module.docs": {
                "label": "任意未知标签",
                "label_source": "unknown",
                "technical_label": "package.docs",
                "status": "impacted",
                "status_label": "任意关联状态",
                "before_state": "present_without_responsibility",
                "after_state": "present_without_responsibility",
                "before": "任意原职责",
                "after": "任意现职责",
                "impact": "任意影响",
                "evidence_boundary": "任意证据边界",
                "unknown": "任意未知项",
            }
        },
        "branch_groups": [
            {
                "id": "omitted.impacted",
                "label": "任意折叠标签",
                "limitation": "任意折叠边界",
            }
        ],
        "claims": [
            {"id": "function.auto-change", "text": "任意变化结论"},
            {"id": "attention.runtime-unknown", "text": "任意未知结论"},
        ],
        "system_architecture": system,
    }
    original = copy.deepcopy(model)

    spec = automatic_review_presentation(model)
    projected = _apply_generated_messages(model, spec, "review")

    assert model == original
    assert projected["summary"][0]["question"] == "What happened"
    assert projected["summary"][0]["text"] == "AI changed 4 files in the fixed comparison."
    assert projected["summary"][1]["task_context"]["entries"][0]["text"] == (
        "Keep this project-authored task text unchanged."
    )
    assert projected["summary"][2]["text"].startswith("Static code analysis found 1")
    assert projected["views"]["after"]["nodes"][0]["label"] == "External API entry point"
    assert projected["views"]["after"]["nodes"][1]["label"] == "Responsibility not yet clear"
    assert projected["views"]["after"]["paths"][0]["relation_label"] == "Direct code relationship"
    assert projected["node_details"]["module.docs"]["impact"].startswith(
        "The code has a direct relationship"
    )
    assert projected["branch_groups"][0]["limitation"].startswith("This proves only")
    assert projected["claims"][0]["text"] == "AI changed 4 files in the fixed comparison."
