from __future__ import annotations

import json
from pathlib import Path

import pytest

from plainchange.auto_draft import draft_target_profile
from plainchange.models import ManifestError
from plainchange.semantic_analysis import (
    attach_context_sources,
    build_project_context_packet,
    change_interpretation_json_schema,
    project_understanding_cache_key,
    project_understanding_json_schema,
    read_cached_project_understanding,
    target_profile_from_understanding,
    validate_project_understanding,
    write_cached_project_understanding,
)
from plainchange.model_adapter import raw_brief_json_schema
from plainchange.target_profile import load_target_profile


def _understanding(context: dict) -> dict:
    paths = context["source_paths"][:1]
    sources = context["allowed_source_ids"][:1]
    return {
        "schema_version": "plainchange.project-understanding.v2",
        "purpose": {"text": "帮助调用方提交内容并得到处理结果。", "source_ids": sources},
        "structure_kind": "workflow",
        "title": "从输入到处理结果",
        "components": [
            {
                "id": f"stage-{index}",
                "label": label,
                "description": description,
                "type": kind,
                "source_ids": sources,
                "code_paths": paths,
            }
            for index, (label, description, kind) in enumerate(
                [
                    ("接收内容", "接收调用方交来的内容。", "input"),
                    ("整理内容", "检查并整理收到的信息。", "process"),
                    ("完成处理", "执行软件的主要处理工作。", "process"),
                    ("返回结果", "把结果交还给调用方。", "output"),
                ],
                start=1,
            )
        ],
        "flows": [
            {"from": f"stage-{index}", "to": f"stage-{index + 1}", "label": "下一步"}
            for index in range(1, 4)
        ],
        "unknowns": ["真实运行顺序尚未验证。"],
    }


def test_project_understanding_is_source_bound_cached_and_profile_valid(
    sample_repo, tmp_path: Path
):
    repo, _base, head = sample_repo
    base = draft_target_profile(repo, head, 15, "Sample")
    context = build_project_context_packet(repo, head, 15, "Sample", base)
    assert str(repo) not in json.dumps(context, ensure_ascii=False)
    assert all(item["kind"] in {"project_declaration", "code_outline"} for item in context["sources"])
    assert len(context["source_paths"]) <= 192
    assert context["source_path_count"] >= len(context["source_paths"])
    validated = validate_project_understanding(context, _understanding(context))
    key = project_understanding_cache_key(context, "a" * 64, "test-model")

    assert read_cached_project_understanding(tmp_path, key, context) is None
    write_cached_project_understanding(tmp_path, key, validated)
    cached = read_cached_project_understanding(tmp_path, key, context)
    assert cached is not None
    assert cached["understanding_identity"] == validated["understanding_identity"]

    profile = target_profile_from_understanding(
        base, attach_context_sources(validated, context), head
    )
    path = tmp_path / "profile.json"
    path.write_text(json.dumps(profile, ensure_ascii=False), encoding="utf-8")
    loaded = load_target_profile(path)
    assert loaded.presentation.conceptual_architecture is not None
    assert loaded.presentation.conceptual_architecture.components[0].evidence_status == (
        "model_interpreted_code_supported"
    )


def test_model_interpretation_schema_rejects_blank_limitations():
    schema = change_interpretation_json_schema(
        ["git.diff_summary"],
        ["step-1"],
        raw_brief_json_schema(["git.diff_summary"]),
    )

    assert (
        schema["properties"]["raw_brief"]["properties"]["claims"]["items"]
        ["properties"]["limitations"]["items"]["minLength"]
        == 1
    )
    assert (
        schema["properties"]["change_summary"]["properties"]["limitations"]
        ["items"]["minLength"]
        == 1
    )


def test_project_understanding_rejects_fabricated_code_path(sample_repo):
    repo, _base, head = sample_repo
    base = draft_target_profile(repo, head, 15, "Sample")
    context = build_project_context_packet(repo, head, 15, "Sample", base)
    value = _understanding(context)
    value["components"][0]["code_paths"] = ["not/in/the/fixed/tree.py"]

    with pytest.raises(ManifestError, match="unknown source or path"):
        validate_project_understanding(context, value)


def test_project_understanding_limits_the_owner_map_to_six_items(sample_repo):
    repo, _base, head = sample_repo
    base = draft_target_profile(repo, head, 15, "Sample")
    context = build_project_context_packet(repo, head, 15, "Sample", base)
    assert project_understanding_json_schema(context)["properties"]["components"]["maxItems"] == 6

    value = _understanding(context)
    value["structure_kind"] = "capability_map"
    value["flows"] = []
    for index in range(5, 8):
        template = dict(value["components"][0])
        template["id"] = f"area-{index}"
        value["components"].append(template)

    with pytest.raises(ManifestError, match="two to six"):
        validate_project_understanding(context, value)


def test_project_understanding_schema_exposes_validator_reference_limits(sample_repo):
    repo, _base, head = sample_repo
    base = draft_target_profile(repo, head, 15, "Sample")
    context = build_project_context_packet(repo, head, 15, "Sample", base)
    schema = project_understanding_json_schema(context)
    purpose_refs = schema["properties"]["purpose"]["properties"]["source_ids"]
    component = schema["properties"]["components"]["items"]["properties"]

    assert purpose_refs["maxItems"] == 12
    assert component["source_ids"]["maxItems"] == 12
    assert component["code_paths"]["maxItems"] == 24
    assert component["code_paths"]["items"]["enum"] == context["source_paths"]
    assert schema["properties"]["flows"]["maxItems"] == 5
    assert schema["properties"]["unknowns"]["maxItems"] == 12


def test_capability_map_derives_redundant_component_type(sample_repo):
    repo, _base, head = sample_repo
    base = draft_target_profile(repo, head, 15, "Sample")
    context = build_project_context_packet(repo, head, 15, "Sample", base)
    value = _understanding(context)
    value["structure_kind"] = "capability_map"
    value["flows"] = []
    for component in value["components"]:
        component["type"] = "process"

    validated = validate_project_understanding(context, value)

    assert {component["type"] for component in validated["components"]} == {"capability"}


def test_project_understanding_cache_invalidates_with_model_or_context(sample_repo, tmp_path: Path):
    repo, _base, head = sample_repo
    base = draft_target_profile(repo, head, 15, "Sample")
    context = build_project_context_packet(repo, head, 15, "Sample", base)
    validated = validate_project_understanding(context, _understanding(context))
    first = project_understanding_cache_key(context, "a" * 64, "model-a")
    second = project_understanding_cache_key(context, "a" * 64, "model-b")
    write_cached_project_understanding(tmp_path, first, validated)

    assert read_cached_project_understanding(tmp_path, first, context) is not None
    assert read_cached_project_understanding(tmp_path, second, context) is None


def test_project_understanding_cache_invalidates_with_human_language(sample_repo):
    repo, _base, head = sample_repo
    base = draft_target_profile(repo, head, 15, "Sample")
    context = build_project_context_packet(repo, head, 15, "Sample", base)

    chinese = project_understanding_cache_key(context, "a" * 64, "model", "zh-CN")
    english = project_understanding_cache_key(context, "a" * 64, "model", "en")

    assert chinese != english
