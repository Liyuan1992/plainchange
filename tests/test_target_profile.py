from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest

from plainchange.models import ManifestError
from plainchange.pipeline import finalize_brief, prepare_sample
from plainchange.target_profile import load_target_profile


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        shell=False,
        text=True,
        encoding="utf-8",
    ).stdout.strip()


def _profile(path: Path) -> Path:
    value = {
        "schema_version": "change-passport.target-profile.v1",
        "profile_id": "fixture-profile",
        "display_name": "Fixture Project",
        "brand_mark": "F",
        "sections": [
            {
                "id": "product",
                "label": "产品代码",
                "responsibility": "承载可执行的产品逻辑。",
                "lane": "main",
                "path_prefixes": ["src"],
                "exact_paths": [],
                "basename_prefixes": [],
            },
            {
                "id": "quality",
                "label": "质量验证",
                "responsibility": "验证系统的回归边界。",
                "lane": "support",
                "path_prefixes": ["tests"],
                "exact_paths": [],
                "basename_prefixes": [],
            },
            {
                "id": "unclassified",
                "label": "待归类",
                "responsibility": "尚未命中分区规则。",
                "lane": "support",
                "path_prefixes": [],
                "exact_paths": [],
                "basename_prefixes": [],
            },
        ],
        "node_label_rules": [{"pattern": "core", "label": "核心计算"}],
        "term_replacements": [],
        "conceptual_architecture": {
            "title": "从输入到说明",
            "description": "把固定输入转换成可核对的说明。",
            "boundary_note": "这是目标配置声明的流程，不是静态 import 图。",
            "components": [
                {"id": "input", "type": "input", "label": "固定输入", "description": "明确范围。", "grid_column": 1, "grid_row": 1, "group_ids": []},
                {"id": "core", "type": "process", "label": "核心处理", "description": "采集和校验。", "grid_column": 2, "grid_row": 1, "group_ids": ["product"]},
                {"id": "output", "type": "output", "label": "可读结果", "description": "输出说明。", "grid_column": 3, "grid_row": 1, "group_ids": ["product"]},
                {"id": "gate", "type": "human_gate", "label": "人工决定", "description": "由人明确决定。", "grid_column": 3, "grid_row": 2, "group_ids": []},
            ],
            "flows": [
                {"from": "input", "to": "core", "label": "采集"},
                {"from": "core", "to": "output", "label": "校验"},
                {"from": "output", "to": "gate", "label": "提交决定"},
            ],
        },
    }
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
    return path


def _raw_brief() -> dict:
    return {
        "schema_version": "change-passport.raw-brief.v1",
        "claims": [
            {
                "id": "function.changed",
                "section": "function",
                "scope": "code_change",
                "text": "核心逻辑更新了返回值。",
                "claim_type": "verified_fact",
                "confidence": "high",
                "importance": "high",
                "evidence_ids": ["task.original", "git.patch"],
                "limitations": [],
                "next_check": None,
            }
        ],
    }


def test_profile_groups_and_brands_without_changing_architecture_facts(
    manifest_factory, tmp_path: Path
):
    repo = tmp_path / "fixture-repo"
    (repo / "src").mkdir(parents=True)
    (repo / "tests").mkdir()
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.email", "tests@example.invalid")
    _git(repo, "config", "user.name", "Change Passport Tests")
    (repo / "src" / "core.py").write_text("VALUE = 1\n", encoding="utf-8")
    (repo / "tests" / "test_core.py").write_text(
        "from src.core import VALUE\n", encoding="utf-8"
    )
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "initial fixture")
    base = _git(repo, "rev-parse", "HEAD")
    (repo / "src" / "core.py").write_text("VALUE = 2\n", encoding="utf-8")
    _git(repo, "add", "src/core.py")
    _git(repo, "commit", "-m", "change core value")
    head = _git(repo, "rev-parse", "HEAD")

    profile = _profile(tmp_path / "fixture-profile.json")
    profile_value = json.loads(profile.read_text(encoding="utf-8"))
    profile_value["module_areas"] = [
        {
            "id": "core-file",
            "order": 1,
            "path_prefixes": [],
            "exact_paths": ["src/core.py"],
            "basename_prefixes": [],
            "label": "核心文件",
            "description": "精确匹配的实现子域。",
        },
        {
            "id": "tests-by-name",
            "order": 2,
            "path_prefixes": [],
            "exact_paths": [],
            "basename_prefixes": ["test_"],
            "label": "按文件名匹配的测试",
            "description": "文件名规则的实现子域。",
        },
    ]
    profile.write_text(json.dumps(profile_value, ensure_ascii=False), encoding="utf-8")
    generic_output = tmp_path / "generic-output"
    profile_output = tmp_path / "profile-output"
    prepare_sample(
        manifest_factory(tmp_path / "generic.json", repo, base, head), generic_output
    )
    prepared = prepare_sample(
        manifest_factory(
            tmp_path / "profile.json",
            repo,
            base,
            head,
            target_profile=profile,
        ),
        profile_output,
    )
    assert json.loads(
        (generic_output / "architecture-delta.json").read_text(encoding="utf-8")
    ) == json.loads(
        (profile_output / "architecture-delta.json").read_text(encoding="utf-8")
    )

    snapshot = json.loads(
        (profile_output / "system-architecture.json").read_text(encoding="utf-8")
    )
    profile_sha256 = hashlib.sha256(profile.read_bytes()).hexdigest()
    assert snapshot["target_profile"]["profile_id"] == "fixture-profile"
    assert snapshot["target_profile"]["profile_sha256"] == profile_sha256
    assert snapshot["target_profile"]["module_areas"] == profile_value["module_areas"]
    assert {node["group_id"] for node in snapshot["nodes"]} == {"product", "quality"}
    assert {
        group["group_source"]
        for group in snapshot["groups"]
    } == {f"target-profile:fixture-profile:sha256:{profile_sha256}"}

    raw_path = profile_output / "raw-brief.input.json"
    raw_path.write_text(json.dumps(_raw_brief(), ensure_ascii=False), encoding="utf-8")
    finalize_brief(prepared["packet_path"], raw_path, profile_output)
    review = json.loads(
        (profile_output / "beginner-review.json").read_text(encoding="utf-8")
    )
    assert review["header"]["brand"] == {"mark": "F", "name": "Fixture Project"}
    assert any(
        detail["label"] == "核心计算"
        and detail["label_source"] == "target_profile"
        for detail in review["node_details"].values()
    )
    conceptual = review["conceptual_architecture"]
    assert conceptual["source"]["kind"] == "target_profile"
    assert conceptual["title"] == "从输入到说明"
    assert [item["label"] for item in conceptual["components"]] == [
        "固定输入",
        "核心处理",
        "可读结果",
        "人工决定",
    ]
    assert conceptual["components"][1]["implementation_groups"] == [
        {"id": "product", "label": "产品代码"}
    ]
    assert conceptual["flows"][-1] == {
        "from": "output",
        "to": "gate",
        "label": "提交决定",
    }


def test_profile_rejects_a_configured_unclassified_fallback(tmp_path: Path):
    profile = _profile(tmp_path / "invalid-profile.json")
    value = json.loads(profile.read_text(encoding="utf-8"))
    value["sections"][-1]["path_prefixes"] = ["everything"]
    profile.write_text(json.dumps(value), encoding="utf-8")

    with pytest.raises(ManifestError, match="unclassified fallback"):
        load_target_profile(profile)


def test_profile_rejects_conceptual_mapping_to_unknown_section(tmp_path: Path):
    profile = _profile(tmp_path / "invalid-concept-profile.json")
    value = json.loads(profile.read_text(encoding="utf-8"))
    value["conceptual_architecture"]["components"][1]["group_ids"] = ["missing"]
    profile.write_text(json.dumps(value), encoding="utf-8")

    with pytest.raises(ManifestError, match="unknown section IDs"):
        load_target_profile(profile)


def test_profile_accepts_branch_merge_and_multiple_human_gates(tmp_path: Path):
    profile = _profile(tmp_path / "layered-profile.json")
    value = json.loads(profile.read_text(encoding="utf-8"))
    value["conceptual_architecture"]["components"] = [
        {"id": "code", "type": "input", "label": "代码变化", "description": "范围输入。", "grid_column": 1, "grid_row": 1, "group_ids": []},
        {"id": "task", "type": "input", "label": "任务说明", "description": "意图输入。", "grid_column": 1, "grid_row": 2, "group_ids": []},
        {"id": "collect", "type": "process", "label": "证据采集", "description": "固定事实。", "grid_column": 2, "grid_row": 1, "group_ids": ["product"]},
        {"id": "structure", "type": "process", "label": "结构提取", "description": "分析结构。", "grid_column": 3, "grid_row": 1, "group_ids": ["product"]},
        {"id": "quality", "type": "process", "label": "质量校验", "description": "分析边界。", "grid_column": 3, "grid_row": 2, "group_ids": ["quality"]},
        {"id": "merge", "type": "process", "label": "合并说明", "description": "汇合结论。", "grid_column": 4, "grid_row": 1, "group_ids": ["product"]},
        {"id": "report", "type": "output", "label": "可读报告", "description": "输出解释。", "grid_column": 5, "grid_row": 1, "group_ids": ["product"]},
        {"id": "review", "type": "human_gate", "label": "人工复核", "description": "人工决定。", "grid_column": 6, "grid_row": 1, "group_ids": []},
        {"id": "approve", "type": "human_gate", "label": "人工批准", "description": "人工决定。", "grid_column": 6, "grid_row": 2, "group_ids": []},
        {"id": "baseline", "type": "state", "label": "可复用基线", "description": "持久状态。", "grid_column": 7, "grid_row": 1, "group_ids": []},
    ]
    value["conceptual_architecture"]["flows"] = [
        {"from": "code", "to": "collect", "label": "范围"},
        {"from": "task", "to": "collect", "label": "意图"},
        {"from": "collect", "to": "structure", "label": "提取"},
        {"from": "collect", "to": "quality", "label": "校验"},
        {"from": "structure", "to": "merge", "label": "结构结论"},
        {"from": "quality", "to": "merge", "label": "质量结论"},
        {"from": "merge", "to": "report", "label": "编写"},
        {"from": "report", "to": "review", "label": "提交复核"},
        {"from": "report", "to": "approve", "label": "提交批准"},
        {"from": "review", "to": "baseline", "label": "确认"},
        {"from": "approve", "to": "baseline", "label": "批准"},
    ]
    profile.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")

    loaded = load_target_profile(profile)

    assert loaded.presentation.conceptual_architecture is not None
    assert len(loaded.presentation.conceptual_architecture.components) == 10
    assert len(loaded.presentation.conceptual_architecture.flows) == 11
    assert {component.component_type for component in loaded.presentation.conceptual_architecture.components} >= {"input", "process", "human_gate", "state"}


def test_capability_profile_accepts_two_details_and_rejects_fake_single_detail(
    tmp_path: Path,
):
    profile = _profile(tmp_path / "capability-profile.json")
    value = json.loads(profile.read_text(encoding="utf-8"))
    value["conceptual_architecture"].update(
        {
            "architecture_kind": "capability_map",
            "purpose_statement_state": "project_declared",
            "purpose_source_refs": ["git:abc:README.md"],
            "source_refs": ["git:abc:README.md"],
            "workflow_order_status": "not_applicable",
            "workflow_order_label": "No order",
            "workflow_order_note": "These capabilities are parallel.",
            "workflow_order_source_refs": ["git:abc:README.md"],
            "flows": [],
            "components": [
                {
                    "id": "conversation",
                    "type": "capability",
                    "label": "Conversation",
                    "description": "Handles an owner conversation.",
                    "grid_column": 1,
                    "grid_row": 1,
                    "group_ids": ["product"],
                    "details": [
                        {
                            "id": "conversation.input",
                            "type": "capability",
                            "label": "Receive input",
                            "description": "Accepts a new message.",
                            "group_ids": ["product"],
                            "evidence_status": "declared_and_code_supported",
                            "evidence_label": "Code located",
                            "evidence_note": "Exact code scope located.",
                            "source_refs": ["git:abc:src/conversation/messages.py"],
                        },
                        {
                            "id": "conversation.output",
                            "type": "capability",
                            "label": "Return output",
                            "description": "Returns the prepared answer.",
                            "group_ids": ["product"],
                            "evidence_status": "declared_and_code_supported",
                            "evidence_label": "Code located",
                            "evidence_note": "Exact code scope located.",
                            "source_refs": ["git:abc:src/conversation/response.py"],
                        },
                    ],
                }
            ],
        }
    )
    profile.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")

    loaded = load_target_profile(profile)
    assert loaded.presentation.conceptual_architecture is not None
    assert len(loaded.presentation.conceptual_architecture.components[0].details) == 2

    value["conceptual_architecture"]["components"][0]["details"] = value[
        "conceptual_architecture"
    ]["components"][0]["details"][:1]
    profile.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(ManifestError, match="two to six"):
        load_target_profile(profile)


def test_profile_consumers_have_no_embedded_target_or_self_sample_identity():
    source_root = Path(__file__).parents[1] / "src" / "plainchange"
    source = "\n".join(
        (source_root / name).read_text(encoding="utf-8")
        for name in (
            "architecture.py",
            "review_model.py",
            "html_renderer.py",
            "target_profile.py",
            "templates/review.html",
            "templates/review-i18n.js",
            "templates/review.js",
        )
    )
    assert "digital_self" not in source
    assert "DigitalSelf" not in source
    assert "a4576ec" not in source
    assert "688fc5f" not in source
    assert "FastAPI" not in source
    assert "fastapi" not in source
