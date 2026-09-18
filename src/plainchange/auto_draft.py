from __future__ import annotations

import re
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

from .git_evidence import list_git_tree, read_git_blob
from .models import canonical_json_bytes, sha256_bytes
from .owner_presentation import SCHEMA as OWNER_PRESENTATION_SCHEMA, message
from .project_declarations import (
    collect_declarations,
    declared_purpose,
    reconcile_workflow,
)
from .source_scope import is_supported_source_path


_CATEGORY_META = {
    "entry": ("调用与用户入口", "接收用户、程序或外部系统交给软件的输入。", "main"),
    "data": ("数据与状态", "整理软件需要读取、保存或传递的数据。", "main"),
    "core": ("主要功能", "执行这个软件最主要的处理工作。", "main"),
    "quality": ("测试与质量保障", "检查主要功能是否仍按预期工作。", "support"),
    "delivery": ("说明与工程辅助", "承载说明、示例、构建和维护工具。", "support"),
}

_GENERIC_AUDIENCE_ROLES = {
    "用户",
    "普通用户",
    "最终用户",
    "使用者",
    "user",
    "users",
    "end user",
    "end users",
}


def _specific_audience_candidate(value: Any) -> dict[str, Any] | None:
    """Keep a source-bound role candidate, but never promote a generic label."""

    if not isinstance(value, Mapping):
        return None
    role = value.get("role")
    reason = value.get("reason")
    refs = value.get("evidence_ids")
    if not isinstance(role, str) or not isinstance(reason, str) or not isinstance(refs, list):
        return None
    normalized = role.strip().casefold()
    evidence_ids = [str(item) for item in refs if isinstance(item, str) and item]
    if not normalized or normalized in _GENERIC_AUDIENCE_ROLES or not reason.strip() or not evidence_ids:
        return None
    return {"role": role.strip(), "reason": reason.strip(), "evidence_ids": evidence_ids}


def _category(path: str) -> str:
    words = set(re.split(r"[^a-z0-9]+", path.lower()))
    if words & {"test", "tests", "spec", "specs", "benchmark", "benchmarks", "qa"}:
        return "quality"
    if words & {"docs", "doc", "examples", "example", "scripts", "tools", "build", "ci"}:
        return "delivery"
    if words & {"api", "web", "http", "cli", "route", "routes", "router", "entrypoints", "ui", "frontend"}:
        return "entry"
    if words & {"data", "db", "database", "storage", "schema", "schemas", "models", "migration", "migrations"}:
        return "data"
    return "core"


def _project_kind(paths: list[str], declaration_text: str) -> str:
    path_text = " ".join(paths).lower()
    declaration_head = declaration_text[:4_000].lower()
    video_path_signals = sum(
        token in path_text
        for token in ("/render/", "/timeline/", "/tts/", "episode", "ffmpeg")
    )
    if video_path_signals >= 3 and any(
        phrase in declaration_head for phrase in ("video production", "video factory", "视频制作")
    ):
        return "video_pipeline"
    model_path_signals = sum(
        token in path_text
        for token in ("model_executor", "inference", "kv_cache", "scheduler")
    )
    if model_path_signals >= 2:
        return "model_serving"
    if any(token in path_text for token in ("routes/", "routers/", "controllers/", "api/", "http/", "web/")):
        return "web_service"
    if any(token in path_text for token in ("/cli/", "commands/", "command_line", "argparse")):
        return "command_tool"
    return "software_library"


def _workflow_for_kind(kind: str) -> tuple[str, list[tuple[str, str, str]]]:
    if kind == "video_pipeline":
        return (
            "根据项目配置准备内容、生成视频，并检查输出是否符合交付要求。",
            [
                ("读取视频配置", "读取本次视频需要的内容、素材和制作要求。", "input"),
                ("准备声音和画面", "生成或整理视频需要的声音、画面和时间安排。", "process"),
                ("生成视频", "把准备好的内容组合并生成视频结果。", "process"),
                ("检查并交付结果", "检查视频质量，并输出可供负责人判断的结果。", "output"),
            ],
        )
    if kind == "model_serving":
        return (
            "帮助应用把输入交给模型处理，并一次性或逐步收到生成结果。",
            [
                ("请求进入软件", "程序可以直接调用，也可以通过对外接口提交请求。", "input"),
                ("整理模型输入", "把文字、图片或其他内容整理成模型可以处理的形式。", "process"),
                ("安排请求和计算资源", "决定哪些请求先计算，并协调缓存和计算任务。", "process"),
                ("运行模型并返回结果", "执行模型计算；支持时，可以边生成边返回。", "output"),
            ],
        )
    if kind == "web_service":
        return (
            "接收用户或其他系统的请求，执行对应功能并返回页面、数据或状态。",
            [
                ("用户操作或请求进入", "用户操作页面，或其他系统发来请求。", "input"),
                ("检查权限并整理输入", "确认访问条件，并把收到的内容整理好。", "process"),
                ("执行对应功能", "根据请求完成软件的主要业务处理。", "process"),
                ("返回页面、数据或状态", "把成功结果或需要处理的问题交还给调用方。", "output"),
            ],
        )
    if kind == "command_tool":
        return (
            "接收用户给出的命令和参数，执行对应工作并显示结果。",
            [
                ("用户给出命令", "用户从命令行说明要做什么。", "input"),
                ("检查并整理参数", "确认输入是否完整、可用。", "process"),
                ("执行命令对应功能", "完成命令要求的主要工作。", "process"),
                ("显示结果或错误", "告诉用户完成结果，或说明还需要处理什么。", "output"),
            ],
        )
    return (
        "向其他程序提供可以调用的功能；更具体的业务用途仍需项目说明或负责人确认。",
        [
            ("调用或输入进入软件", "用户、程序或其他系统把需要处理的内容交给这个软件。", "input"),
            ("检查并整理输入", "软件把收到的内容整理成主要功能可以处理的形式。", "process"),
            ("执行主要功能", "软件完成核心处理；具体业务含义仍需项目说明或负责人确认。", "process"),
            ("返回结果或状态", "把处理结果、状态或数据交还给调用方。", "output"),
        ],
    )


def _classification_rules(
    supported: list[str],
) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    """Return non-overlapping directory prefixes plus exact-file fallbacks."""
    categories = {path: _category(path) for path in supported}
    prefixes: dict[str, set[str]] = {key: set() for key in _CATEGORY_META}
    exact_paths: dict[str, set[str]] = {key: set() for key in _CATEGORY_META}
    for path in supported:
        parts = PurePosixPath(path).parts
        category = categories[path]
        selected: str | None = None
        for depth in range(1, len(parts)):
            prefix = "/".join(parts[:depth])
            members = [
                candidate
                for candidate in supported
                if candidate == prefix or candidate.startswith(prefix + "/")
            ]
            if members and {categories[candidate] for candidate in members} == {category}:
                selected = prefix
                break
        if selected is None:
            exact_paths[category].add(path)
        else:
            prefixes[category].add(selected)
    for category, values in prefixes.items():
        prefixes[category] = {
            value
            for value in values
            if not any(
                value != other and value.startswith(other.rstrip("/") + "/")
                for other in values
            )
        }
    return prefixes, exact_paths


def draft_target_profile(
    repo: Path,
    commit: str,
    timeout: int,
    display_name: str,
) -> dict[str, Any]:
    tree = list_git_tree(repo, commit, timeout)
    supported = sorted(path for path in tree if is_supported_source_path(path))
    declaration_parts: list[str] = []
    for candidate in ("pyproject.toml", "package.json"):
        if candidate not in tree:
            continue
        declaration_parts.append(
            read_git_blob(repo, commit, candidate, timeout)[:64_000].decode(
                "utf-8", errors="replace"
            )
        )
    declarations = collect_declarations(repo, commit, tree, timeout)
    declaration_parts.extend(item["text"] for item in declarations)
    kind = _project_kind(supported, "\n".join(declaration_parts))
    fallback_purpose, _ = _workflow_for_kind(kind)
    purpose = declared_purpose(declarations, fallback_purpose, kind)
    prefixes, exact_paths = _classification_rules(supported)
    workflow_evidence = reconcile_workflow(
        repo,
        commit,
        timeout,
        supported,
        declarations,
        _category,
    )

    sections: list[dict[str, Any]] = []
    module_areas: list[dict[str, Any]] = []
    active_ids: list[str] = []
    order = 1
    for category, (label, responsibility, lane) in _CATEGORY_META.items():
        category_prefixes = sorted(prefixes[category])
        category_exact = sorted(exact_paths[category])
        if not category_prefixes and not category_exact:
            continue
        active_ids.append(category)
        sections.append(
            {
                "id": category,
                "label": label,
                "responsibility": responsibility,
                "lane": lane,
                "path_prefixes": category_prefixes,
                "exact_paths": category_exact,
                "basename_prefixes": [],
            }
        )
        module_areas.append(
            {
                "id": category,
                "order": order,
                "path_prefixes": [prefix + "/" for prefix in category_prefixes],
                "exact_paths": category_exact,
                "basename_prefixes": [],
                "label": label,
                "description": responsibility,
            }
        )
        order += 1
    sections.append(
        {
            "id": "unclassified",
            "label": "还没归类的实现",
            "responsibility": "当前自动草稿还不能确定这些代码在软件中的作用。",
            "lane": "support",
            "path_prefixes": [],
            "exact_paths": [],
            "basename_prefixes": [],
        }
    )
    safe_id = re.sub(r"[^A-Za-z0-9._-]+", "-", display_name).strip("-.")[:70] or "repository"
    if workflow_evidence:
        structure_kind = str(workflow_evidence.get("kind", "workflow"))
        components = [
            {
                "id": str(item["id"]),
                "type": str(item["type"]),
                "label": str(item["label"]),
                "description": str(item["description"]),
                "grid_column": 1,
                "grid_row": index + 1,
                "group_ids": [
                    group_id for group_id in item["group_ids"] if group_id in active_ids
                ],
                "evidence_status": str(item["evidence_status"]),
                "evidence_label": str(item["evidence_label"]),
                "evidence_note": str(item["evidence_note"]),
                "source_refs": list(item["source_refs"]),
                **(
                    {"details": list(item["details"])}
                    if len(item.get("details", [])) >= 2
                    else {}
                ),
            }
            for index, item in enumerate(workflow_evidence["steps"])
        ]
        component_ids = [str(item["id"]) for item in components]
        flows = (
            [
                {
                    "from": component_ids[index],
                    "to": component_ids[index + 1],
                    "label": "项目说明的下一步",
                }
                for index in range(len(component_ids) - 1)
            ]
            if structure_kind == "workflow"
            else []
        )
        boundary_note = (
            "这张图来自固定版本的项目说明，并与代码位置进行对账；"
            f"{workflow_evidence['order_label']}，但仍不是运行记录。"
            if structure_kind == "workflow"
            else "这张图从固定版本的项目说明提炼并列能力，再核对代码位置；它不是调用顺序或运行记录。"
        )
        architecture_extra = {
            "architecture_kind": structure_kind,
            "source_refs": list(workflow_evidence["source_refs"]),
            "workflow_order_status": str(workflow_evidence["order_status"]),
            "workflow_order_label": str(workflow_evidence["order_label"]),
            "workflow_order_note": str(workflow_evidence["order_note"]),
            "workflow_order_source_refs": list(workflow_evidence["order_source_refs"]),
        }
        architecture_title = (
            f"{display_name} 项目说明中的工作流程"
            if structure_kind == "workflow"
            else f"{display_name} 项目说明中的能力结构"
        )
    else:
        structure_kind = "capability_map"
        discovered = active_ids or ["unclassified"]
        components = [
            {
                "id": f"code-capability-{category}",
                "type": "capability",
                "label": _CATEGORY_META.get(category, ("还没归类的实现", "", ""))[0],
                "description": _CATEGORY_META.get(category, ("", "当前代码尚未形成可识别的能力分区。", ""))[1],
                "grid_column": index % 2 + 1,
                "grid_row": index // 2 + 1,
                "group_ids": [category] if category in active_ids else [],
                "evidence_status": "code_discovered" if category in active_ids else "generated_candidate",
                "evidence_label": "从代码结构发现" if category in active_ids else "自动候选",
                "evidence_note": (
                    "固定版本代码中存在这一类实现位置，但具体业务含义仍需项目说明或负责人确认。"
                    if category in active_ids
                    else "没有项目说明或可识别代码分区支持更具体的能力结构。"
                ),
                "source_refs": [
                    f"git:{commit}:{path}"
                    for path in supported
                    if _category(path) == category
                ][:5],
            }
            for index, category in enumerate(discovered)
        ]
        component_ids = [str(item["id"]) for item in components]
        flows = []
        boundary_note = "没有找到可靠的项目流程或能力清单；这里只展示固定版本代码中发现的实现区域，不代表业务顺序或运行记录。"
        architecture_extra = {
            "architecture_kind": structure_kind,
            "source_refs": list(purpose["source_refs"]),
            "workflow_order_status": "not_applicable",
            "workflow_order_label": "没有先后顺序",
            "workflow_order_note": "这些是代码结构中的并列实现区域；当前证据不支持把它们排列成业务流程。",
            "workflow_order_source_refs": [],
        }
        architecture_title = f"{display_name} 当前可识别的能力结构"
    conceptual_architecture = {
        "title": architecture_title,
        "description": purpose["text"],
        "boundary_note": boundary_note,
        "components": components,
        "flows": flows,
        "purpose_statement_state": purpose["statement_state"],
        "purpose_source_refs": list(purpose["source_refs"]),
        **architecture_extra,
    }
    return {
        "schema_version": "change-passport.target-profile.v1",
        "profile_id": f"auto-{safe_id}",
        "display_name": display_name,
        "brand_mark": display_name[:1].upper() or "P",
        "sections": sections,
        "node_label_rules": [
            {"pattern": "api", "label": "对外调用入口"},
            {"pattern": "test_", "label": "行为检查"},
            {"pattern": "config", "label": "运行设置"},
        ],
        "term_replacements": [],
        "module_areas": module_areas,
        "conceptual_architecture": conceptual_architecture,
    }


def draft_raw_brief(packet: Mapping[str, Any]) -> dict[str, Any]:
    change = packet["change"]
    evidence = packet["evidence"]
    file_items = [item for item in evidence if str(item.get("id", "")).startswith("git.file.")]
    behavior_items = [item for item in evidence if item.get("kind") == "behavior_signal"]
    paths = []
    for item in file_items:
        match = re.search(r"(?:^|;) path=([^;]+)", str(item.get("content", "")))
        if match:
            paths.append(match.group(1))
    areas = sorted({path.split("/", 1)[0] for path in paths})[:4]
    area_text = "、".join(areas) if areas else "当前代码范围"
    owner_area_labels = {
        "entry": "软件接收和整理输入的部分",
        "data": "数据和状态处理",
        "core": "主要功能内部",
        "quality": "相关检查",
        "delivery": "说明和工程辅助",
    }
    owner_areas = []
    for path in paths:
        label = owner_area_labels[_category(path)]
        if label not in owner_areas:
            owner_areas.append(label)
    owner_area_text = "、".join(owner_areas[:3]) or "软件内部"
    architecture_ids = [str(item["id"]) for item in evidence if item.get("kind") == "architecture"]
    function_claims: list[dict[str, Any]] = []
    if behavior_items:
        kinds = {str(item.get("content", "")).split(";", 1)[0] for item in behavior_items}
        if {"kind=added_exception_raise", "kind=added_nonzero_return"} <= kinds:
            behavior_text = "固定代码差异显示，这次新增了会抛出错误或返回失败状态的处理分支；它们只在特定条件下触发，实际运行和用户影响还没验证。"
        elif "kind=added_exception_raise" in kinds:
            behavior_text = "固定代码差异显示，这次新增了会抛出错误并提前停止处理的分支；它只在特定条件下触发，实际运行和用户影响还没验证。"
        elif "kind=added_nonzero_return" in kinds:
            behavior_text = "固定代码差异显示，这次新增了会返回失败状态并提前停止处理的分支；它只在特定条件下触发，实际运行和用户影响还没验证。"
        else:
            behavior_text = "固定代码差异显示，这次修改了可调用功能的输入方式；调用方是否需要调整还没验证。"
        function_claims.append(
            {
                "id": "function.auto-behavior-signal",
                "section": "function",
                "scope": "code_change",
                "text": behavior_text,
                "claim_type": "verified_fact",
                "confidence": "high",
                "importance": "high",
                "evidence_ids": [str(item["id"]) for item in behavior_items[:6]],
                "limitations": [
                    "这里只确认固定差异中新增了相应代码分支，不证明分支可达、已经运行、属于破坏性变化或已经影响用户"
                ],
                "next_check": "分别检查正常条件和触发新增停止或失败条件时的结果",
            }
        )
    function_claims.append(
        {
            "id": "function.auto-change",
            "section": "function",
            "scope": "code_change",
            "text": f"这次 AI 修改了 {change['changed_files']} 个文件，变化主要出现在 {area_text}。",
            "claim_type": "verified_fact",
            "confidence": "high",
            "importance": "medium" if behavior_items else "high",
            "evidence_ids": ["git.diff_summary", *[str(item["id"]) for item in file_items[:4]]],
            "limitations": ["仅说明固定 Git 版本中观察到的代码变化，不等于用户已经感受到变化"],
            "next_check": None,
        }
    )
    return {
        "schema_version": "change-passport.raw-brief.v1",
        "generator_metadata": {
            "provider": "deterministic-local",
            "model": "none",
            "mode": "automatic_candidate_draft",
        },
        "claims": [
            *function_claims,
            {
                "id": "architecture.auto-location",
                "section": "architecture",
                "scope": "architecture_change",
                "text": f"从静态结构看，这次变化主要集中在{owner_area_text}。",
                "claim_type": "inference" if architecture_ids else "unknown",
                "confidence": "medium" if architecture_ids else "low",
                "importance": "high",
                "evidence_ids": architecture_ids[:6],
                "limitations": ["静态关联不是运行顺序，也不能单独证明真实用户影响"],
                "next_check": "按需展开技术实现，核对本次改动所在分区",
            },
            {
                "id": "history.auto-unknown",
                "section": "history",
                "scope": "history_relation",
                "text": "现有材料不足以确认这次变化与已批准历史结论之间的关系。",
                "claim_type": "unknown",
                "confidence": "low",
                "importance": "medium",
                "evidence_ids": [],
                "limitations": ["候选或缺失的历史不能当成已批准历史"],
                "next_check": "由负责人决定是否批准本次候选基线",
            },
            {
                "id": "attention.runtime-unknown",
                "section": "attention",
                "scope": "attention",
                "text": "还没有运行目标软件验证真实行为和最终用户影响。",
                "claim_type": "unknown",
                "confidence": "low",
                "importance": "high",
                "evidence_ids": [],
                "limitations": ["自动草稿只使用已提供材料和静态代码事实"],
                "next_check": "先验证本次改动对应的用户路径或关键行为",
            },
        ],
    }


def _basis(
    claim_ids: list[str] | None = None,
    evidence_ids: list[str] | None = None,
    component_ids: list[str] | None = None,
    source_refs: list[str] | None = None,
) -> dict[str, list[str]]:
    return {
        "claim_ids": claim_ids or [],
        "evidence_ids": evidence_ids or [],
        "component_ids": component_ids or [],
        "source_refs": source_refs or [],
    }


def _source_path(source_ref: str) -> str | None:
    match = re.match(r"^git:[0-9a-fA-F]{7,64}:(.+?)(?::sha256:|:function:|$)", source_ref)
    return match.group(1) if match else None


def _evidence_content_field(item: Mapping[str, Any], field: str) -> str | None:
    match = re.search(
        rf"(?:^|;\s*){re.escape(field)}=([^;]+)",
        str(item.get("content", "")),
    )
    return match.group(1).strip() if match else None


def _behavior_phrase(items: list[Mapping[str, Any]]) -> str:
    kinds = {_evidence_content_field(item, "kind") for item in items}
    if {"added_exception_raise", "added_nonzero_return"} <= kinds:
        return "会让处理提前停止或返回失败状态的代码分支"
    if "added_exception_raise" in kinds:
        return "会抛出错误并提前停止处理的代码分支"
    if "added_nonzero_return" in kinds:
        return "会返回失败状态并提前停止处理的代码分支"
    return "可能要求调用方调整输入方式的代码变化"


def _unsupported_changed_paths(review: Mapping[str, Any]) -> list[str]:
    prefix = "unsupported changed file: "
    paths = [
        str(item)[len(prefix) :]
        for item in review.get("limitations", [])
        if str(item).startswith(prefix)
    ]

    def priority(path: str) -> tuple[int, str]:
        lowered = path.lower()
        important = any(
            marker in lowered
            for marker in ("/decisions/", "adr-", "changelog", "migration", "breaking")
        )
        return (0 if important else 1, lowered)

    return sorted(set(paths), key=priority)


def _changed_component_index(
    components: list[Mapping[str, Any]],
    changed_paths: set[str],
    changed_groups: set[str],
) -> int | None:
    exact_scores: list[int] = []
    group_scores: list[int] = []
    for component in components:
        source_paths = {
            path
            for ref in component.get("source_refs", [])
            if (path := _source_path(str(ref))) is not None
        }
        # A broad code-derived area is useful for orientation but does not
        # establish a business capability. Only a project-declared capability
        # that was independently reconciled to code may receive an automatic
        # change-location overlay.
        exact_scores.append(
            len(source_paths & changed_paths)
            if component.get("evidence_status") == "declared_and_code_supported"
            else 0
        )
        group_scores.append(
            len(set(map(str, component.get("group_ids", []))) & changed_groups)
        )
    best_exact = max(exact_scores, default=0)
    if best_exact > 0 and exact_scores.count(best_exact) == 1:
        return exact_scores.index(best_exact)
    eligible = [
        index
        for index, component in enumerate(components)
        if component.get("evidence_status") == "declared_and_code_supported"
    ]
    if eligible:
        best_group = max(group_scores[index] for index in eligible)
        winners = [
            index for index in eligible if group_scores[index] == best_group and best_group > 0
        ]
        if len(winners) == 1:
            return winners[0]
    return None


def _four_contiguous_groups(nodes: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    if len(nodes) < 4:
        raise ValueError("automatic owner workflow needs at least four detail steps")
    width, extra = divmod(len(nodes), 4)
    result: list[list[dict[str, Any]]] = []
    cursor = 0
    for index in range(4):
        size = width + (1 if index < extra else 0)
        result.append(nodes[cursor : cursor + size])
        cursor += size
    return result


def _aggregate_evidence(nodes: list[dict[str, Any]]) -> tuple[str, str, str, list[str]]:
    statuses = {str(node.get("evidence_status", "generated_candidate")) for node in nodes}
    if statuses == {"declared_and_code_supported"}:
        status = "declared_and_code_supported"
        label = "找到对应代码"
        note = "这个阶段内的项目说明步骤都找到了固定版本代码位置；仍未运行验证。"
    elif "declared_and_code_supported" in statuses:
        status = "partially_supported"
        label = "部分找到代码"
        note = "这个阶段只有部分项目说明步骤找到了固定版本代码位置。"
    elif statuses == {"declared_only"}:
        status = "declared_only"
        label = "仅来自项目说明"
        note = "这个阶段来自项目说明，但当前没有找到稳定的代码对应位置。"
    elif statuses == {"model_interpreted_code_supported"}:
        status = "model_interpreted_code_supported"
        label = "模型理解，已找到代码位置"
        note = "模型候选理解已通过本地来源和代码路径校验；仍未运行验证。"
    elif statuses <= {"model_interpreted_code_supported", "model_interpreted_only"}:
        status = "model_interpreted_only"
        label = "模型候选理解"
        note = "模型给出了候选理解，但这个阶段只有部分或没有稳定代码位置支持。"
    else:
        status = "generated_candidate"
        label = "自动候选"
        note = "这个阶段是自动候选，需要项目负责人确认。"
    refs = list(
        dict.fromkeys(
            str(ref)
            for node in nodes
            for ref in node.get("source_refs", [])
        )
    )
    return status, label, note, refs


def _owner_excerpt(value: str, limit: int = 180) -> str:
    value = value.strip()
    if len(value) <= limit:
        return value
    candidates = [position for mark in ("。", ". ", "；", "; ") if 32 <= (position := value.find(mark)) < limit]
    if candidates:
        position = min(candidates)
        return value[: position + 1].strip()
    return value[: limit - 1].rstrip(" ,，;；") + "…"


def _automatic_owner_presentation(
    document: Mapping[str, Any],
    *,
    behavior_kind: str,
    changed_file_count: int,
    changed_claim_id: str,
    has_behavior: bool,
    has_stop_signal: bool,
    impact_mode: str,
    map_kind: str,
    mapped_step_label: str | None,
    no_model_semantics: bool,
    semantic_generated: bool,
    unsupported_paths: list[str],
) -> dict[str, Any]:
    """Describe PlainChange-owned prose without translating project source text."""
    messages: list[dict[str, Any]] = []
    source_paths: list[list[str | int]] = []

    def add(path: list[str | int], key: str, **args: Any) -> None:
        messages.append(message(path, key, **args))

    def generated_node(node: Mapping[str, Any]) -> tuple[str, str] | None:
        if str(node.get("evidence_status")) != "code_discovered":
            return None
        node_id = str(node.get("id", ""))
        suffix = node_id.rsplit(".", 1)[-1]
        if suffix in {"input", "context", "decision", "execution", "delivery", "state"}:
            return "responsibility", suffix
        prefix = "code-capability-"
        if node_id.startswith(prefix):
            return "category", node_id[len(prefix):]
        return None

    change_args = {
        "behavior_kind": behavior_kind,
        "mapped": mapped_step_label is not None,
        "step_label": mapped_step_label or "",
        "stop": has_stop_signal,
        "map_kind": map_kind,
    }
    location_args = {
        "step_label": mapped_step_label or "",
        "map_kind": map_kind,
        "no_model_semantics": no_model_semantics,
    }
    change_key = "change.behavior" if has_behavior else "change.location"
    selected_change_args = change_args if has_behavior else location_args
    unsupported_example = unsupported_paths[0].rsplit("/", 1)[-1] if unsupported_paths else ""
    risk_args = {
        "no_model_semantics": no_model_semantics,
        "unsupported_count": len(unsupported_paths),
        "unsupported_example": unsupported_example,
        "map_kind": map_kind,
    }
    project_state = str(document["product"].get("statement_state", "project_declared"))
    purpose_is_source = project_state == "project_declared"
    if purpose_is_source:
        source_paths.append(["product", "purpose"])
    elif semantic_generated:
        source_paths.append(["product", "purpose"])
    else:
        add(
            ["product", "purpose"],
            "product.purpose_unknown",
            product_name=str(document["product"]["name"]),
        )

    if semantic_generated:
        source_paths.append(["first_screen_summary", "headline"])
    else:
        add(["first_screen_summary", "headline"], change_key, **selected_change_args)
    add(["first_screen_summary", "internal_concept_label"], "summary.internal_area")
    if changed_claim_id == "function.auto-behavior-signal":
        add(["first_screen_summary", "confirmed_change", "text"], "claim.behavior", behavior_kind=behavior_kind)
    else:
        add(
            ["first_screen_summary", "confirmed_change", "text"],
            "claim.changed_files",
            count=changed_file_count,
        )
    add(["first_screen_summary", "confirmed_change", "state_label"], "state.confirmed")
    add(["first_screen_summary", "confirmed_change", "state_explanation"], "state.code_evidence")
    if impact_mode == "unassessed":
        impact_key = "impact.unassessed"
        add(["first_screen_summary", "user_impact", "text"], impact_key)
        add(["first_screen_summary", "user_impact", "state_label"], "state.unassessed")
        add(["first_screen_summary", "user_impact", "state_explanation"], "state.unassessed_explanation")
    elif impact_mode == "not_found":
        impact_key = "impact.not_found"
        add(["first_screen_summary", "user_impact", "text"], impact_key)
        add(["first_screen_summary", "user_impact", "state_label"], "state.not_found")
        add(["first_screen_summary", "user_impact", "state_explanation"], "state.not_found_explanation")
    elif impact_mode == "role_candidate":
        impact_key = None
        source_paths.append(["first_screen_summary", "user_impact", "text"])
        add(["first_screen_summary", "user_impact", "state_label"], "state.possible")
        add(["first_screen_summary", "user_impact", "state_explanation"], "state.possible_explanation")
    else:
        impact_key = None
        source_paths.append(["first_screen_summary", "user_impact", "text"])
        add(
            ["first_screen_summary", "user_impact", "state_label"],
            "state.confirmed" if impact_mode == "confirmed_source_claim" else "state.supported",
        )
        add(["first_screen_summary", "user_impact", "state_explanation"], "state.supported_explanation")
    add(["first_screen_summary", "residual_risk", "text"], "risk.runtime", **risk_args)
    add(["first_screen_summary", "residual_risk", "state_label"], "state.not_verified")
    add(["first_screen_summary", "residual_risk", "state_explanation"], "state.runtime_explanation")
    if semantic_generated:
        source_paths.append(["first_screen_summary", "owner_action", "text"])
    else:
        add(
            ["first_screen_summary", "owner_action", "text"],
            "action.summary",
            stop=has_stop_signal,
            has_behavior=has_behavior,
        )
    add(["first_screen_summary", "owner_action", "state_label"], "state.next_action")
    add(["first_screen_summary", "owner_action", "state_explanation"], "state.next_action_explanation")

    question_keys = [
        "question.software",
        "question.change",
        "question.audience",
        "question.unknowns",
        "question.next",
    ]
    for index, key in enumerate(question_keys):
        add(["five_questions", index, "question"], key)
    if semantic_generated:
        source_paths.append(["five_questions", 0, "answer"])
    else:
        add(
            ["five_questions", 0, "answer"],
            "question.software_answer",
            product_name=str(document["product"]["name"]),
            purpose=str(document["product"]["purpose"]),
            purpose_is_source=purpose_is_source,
        )
    add(
        ["five_questions", 0, "state_label"],
        "question.from_project" if project_state == "project_declared" else "question.auto_candidate",
    )
    for index, node in enumerate(document["working_map"]["nodes"]):
        generated = generated_node(node)
        if generated is None:
            source_paths.append(["five_questions", 0, "details", "software_steps", index])
        else:
            kind, identifier = generated
            add(
                ["five_questions", 0, "details", "software_steps", index],
                "node.generated",
                kind=kind,
                identifier=identifier,
                field="label",
            )
    if semantic_generated:
        source_paths.append(["five_questions", 1, "answer"])
    else:
        add(["five_questions", 1, "answer"], change_key, **selected_change_args)
    add(
        ["five_questions", 1, "state_label"],
        "question.located" if mapped_step_label is not None else "question.unmapped",
    )
    if semantic_generated:
        source_paths.append(["five_questions", 1, "details", "change_points", 0])
    else:
        add(["five_questions", 1, "details", "change_points", 0], change_key, **selected_change_args)
    if impact_key is not None:
        add(["five_questions", 2, "answer"], impact_key)
        add(["five_questions", 2, "details", "audience_impacts", 0, "explanation"], impact_key)
    else:
        source_paths.extend(
            [
                ["five_questions", 2, "answer"],
                ["five_questions", 2, "details", "audience_impacts", 0, "explanation"],
            ]
        )
    add(
        ["five_questions", 2, "state_label"],
        "state.unassessed"
        if impact_mode == "unassessed"
        else "state.not_found"
        if impact_mode == "not_found"
        else "state.possible"
        if impact_mode == "role_candidate"
        else "state.confirmed"
        if impact_mode == "confirmed_source_claim"
        else "state.supported",
    )
    if impact_mode == "role_candidate":
        source_paths.append(["five_questions", 2, "details", "audience_impacts", 0, "audience"])
    else:
        add(["five_questions", 2, "details", "audience_impacts", 0, "audience"], "audience.users")
    add(["five_questions", 2, "details", "audience_impacts", 1, "audience"], "audience.systems")
    integration_key = (
        "audience.integration_stop"
        if has_stop_signal
        else "audience.integration_callers"
        if has_behavior
        else "audience.integration_unknown"
    )
    add(["five_questions", 2, "details", "audience_impacts", 1, "explanation"], integration_key)
    add(["five_questions", 3, "answer"], "risk.unknowns_answer", **risk_args)
    add(["five_questions", 3, "state_label"], "state.not_verified")
    unknown_index = 0
    add(["five_questions", 3, "details", "unknowns", unknown_index], "unknown.runtime")
    unknown_index += 1
    if no_model_semantics:
        add(["five_questions", 3, "details", "unknowns", unknown_index], "unknown.semantic")
        unknown_index += 1
    if unsupported_paths:
        add(
            ["five_questions", 3, "details", "unknowns", unknown_index],
            "risk.unsupported",
            unsupported_count=len(unsupported_paths),
            unsupported_example=unsupported_example,
        )
        unknown_index += 1
    add(
        ["five_questions", 3, "details", "unknowns", unknown_index],
        "unknown.capability_map" if map_kind == "capability_map" else "unknown.workflow",
    )
    add(["five_questions", 4, "answer"], "question.minimum_checks")
    add(["five_questions", 4, "state_label"], "state.next_action")

    checks = document["five_questions"][4]["details"]["owner_checks"]
    actions = document["five_questions"][4]["details"]["actions"]
    if semantic_generated:
        for index in range(len(checks)):
            source_paths.append(["five_questions", 4, "details", "owner_checks", index])
        for index in range(len(actions)):
            source_paths.extend(
                [
                    ["five_questions", 4, "details", "actions", index, "title"],
                    ["five_questions", 4, "details", "actions", index, "instructions"],
                ]
            )
    elif has_stop_signal:
        add(["five_questions", 4, "details", "owner_checks", 0], "check.normal", step_label=mapped_step_label or "")
        add(["five_questions", 4, "details", "owner_checks", 1], "check.stop")
        add(["five_questions", 4, "details", "actions", 0, "title"], "action.normal.title")
        add(["five_questions", 4, "details", "actions", 0, "instructions"], "check.normal", step_label=mapped_step_label or "")
        add(["five_questions", 4, "details", "actions", 1, "title"], "action.stop.title")
        add(["five_questions", 4, "details", "actions", 1, "instructions"], "check.stop")
    elif has_behavior:
        add(["five_questions", 4, "details", "owner_checks", 0], "check.normal", step_label=mapped_step_label or "")
        add(["five_questions", 4, "details", "owner_checks", 1], "check.callers")
        add(["five_questions", 4, "details", "actions", 0, "title"], "action.normal.title")
        add(["five_questions", 4, "details", "actions", 0, "instructions"], "check.normal", step_label=mapped_step_label or "")
        add(["five_questions", 4, "details", "actions", 1, "title"], "action.callers.title")
        add(["five_questions", 4, "details", "actions", 1, "instructions"], "check.callers")
    elif len(checks) >= 2 and len(actions) >= 2:
        add(["five_questions", 4, "details", "owner_checks", 0], "check.location")
        add(["five_questions", 4, "details", "owner_checks", 1], "check.runtime")
        add(
            ["five_questions", 4, "details", "actions", 0, "title"],
            "action.map.capability.title" if map_kind == "capability_map" else "action.map.workflow.title",
        )
        add(
            ["five_questions", 4, "details", "actions", 0, "instructions"],
            "action.map.capability.instructions" if map_kind == "capability_map" else "action.map.workflow.instructions",
        )
        add(["five_questions", 4, "details", "actions", 1, "title"], "action.runtime.title")
        add(["five_questions", 4, "details", "actions", 1, "instructions"], "action.runtime.instructions")

    add(["working_map", "title"], "map.title", product_name=str(document["product"]["name"]), map_kind=map_kind)
    add(
        ["working_map", "description"],
        "map.capability.description" if map_kind == "capability_map" else "map.workflow.description",
    )
    add(
        ["working_map", "screen_summary", "headline"],
        "map.headline",
        product_name=str(document["product"]["name"]),
        map_kind=map_kind,
    )
    add(
        ["working_map", "screen_summary", "overview"],
        "map.capability.overview" if map_kind == "capability_map" else "map.workflow.overview",
    )
    add(
        ["working_map", "screen_summary", "boundary_label"],
        "map.capability.boundary_label" if map_kind == "capability_map" else "map.workflow.boundary_label",
    )
    add(
        ["working_map", "overview_map", "title"],
        "map.capability.overview_title" if map_kind == "capability_map" else "map.workflow.overview_title",
    )
    add(
        ["working_map", "boundary_note"],
        "map.boundary",
        map_kind=map_kind,
        order_status=str(document["working_map"]["order_status"]),
        project_declared=purpose_is_source,
    )
    add(
        ["working_map", "order_label"],
        "order.label",
        order_status=str(document["working_map"]["order_status"]),
    )
    add(
        ["working_map", "order_note"],
        "order.note",
        order_status=str(document["working_map"]["order_status"]),
        project_declared=purpose_is_source,
    )

    for node_index, node in enumerate(document["working_map"]["nodes"]):
        generated = generated_node(node)
        if generated is None:
            source_paths.extend(
                [
                    ["working_map", "nodes", node_index, "label"],
                    ["working_map", "nodes", node_index, "description"],
                    ["working_map", "nodes", node_index, "owner_view", "meaning"],
                ]
            )
        else:
            kind, identifier = generated
            for path, field in (
                (["working_map", "nodes", node_index, "label"], "label"),
                (["working_map", "nodes", node_index, "description"], "description"),
                (["working_map", "nodes", node_index, "owner_view", "meaning"], "description"),
            ):
                add(path, "node.generated", kind=kind, identifier=identifier, field=field)
        evidence_args = {
            "status": str(node["evidence_status"]),
            "internal_responsibility": generated is not None and generated[0] == "responsibility",
        }
        add(
            ["working_map", "nodes", node_index, "evidence_label"],
            "evidence.presentation",
            field="label",
            **evidence_args,
        )
        add(
            ["working_map", "nodes", node_index, "evidence_note"],
            "evidence.presentation",
            field="description",
            **evidence_args,
        )
        add(
            ["working_map", "nodes", node_index, "owner_view", "visible_result"],
            "node.capability.result" if map_kind == "capability_map" else "node.workflow.result",
        )
        if node["change_state"] == "changed":
            add(["working_map", "nodes", node_index, "owner_view", "current_change"], change_key, **selected_change_args)
            if impact_key is not None:
                add(["working_map", "nodes", node_index, "owner_view", "affected_people"], impact_key)
            else:
                source_paths.append(["working_map", "nodes", node_index, "owner_view", "affected_people"])
            for check_index in range(len(node["owner_view"]["owner_checks"])):
                source_paths.append(["working_map", "nodes", node_index, "owner_view", "owner_checks", check_index])
        else:
            add(["working_map", "nodes", node_index, "owner_view", "current_change"], "node.unchanged")
            add(["working_map", "nodes", node_index, "owner_view", "affected_people"], "node.audience_unknown")
            add(["working_map", "nodes", node_index, "owner_view", "owner_checks", 0], "node.check_project")
            add(
                ["working_map", "nodes", node_index, "owner_view", "owner_checks", 1],
                "node.check_capability_use" if map_kind == "capability_map" else "node.check_workflow_order",
            )
        for unknown_index, _ in enumerate(node["owner_view"]["unknowns"]):
            if unknown_index == 0:
                add(
                    ["working_map", "nodes", node_index, "owner_view", "unknowns", unknown_index],
                    "evidence.presentation",
                    field="description",
                    **evidence_args,
                )
            elif unknown_index == 1:
                add(
                    ["working_map", "nodes", node_index, "owner_view", "unknowns", unknown_index],
                    "order.note",
                    order_status=str(document["working_map"]["order_status"]),
                    project_declared=purpose_is_source,
                )
            elif unknown_index == len(node["owner_view"]["unknowns"]) - 1:
                add(
                    ["working_map", "nodes", node_index, "owner_view", "unknowns", unknown_index],
                    "node.runtime_boundary",
                )
            else:
                source_paths.append(["working_map", "nodes", node_index, "owner_view", "unknowns", unknown_index])

    for overview_index, node in enumerate(document["working_map"]["overview_map"]["nodes"]):
        detail_nodes = {
            str(item["id"]): item for item in document["working_map"]["nodes"]
        }
        details = [detail_nodes[item] for item in node["detail_node_ids"]]
        generated = generated_node(details[0]) if len(details) == 1 else None
        if generated is None:
            source_paths.extend(
                [
                    ["working_map", "overview_map", "nodes", overview_index, "label"],
                    ["working_map", "overview_map", "nodes", overview_index, "description"],
                ]
            )
        else:
            kind, identifier = generated
            add(
                ["working_map", "overview_map", "nodes", overview_index, "label"],
                "node.generated",
                kind=kind,
                identifier=identifier,
                field="label",
            )
            add(
                ["working_map", "overview_map", "nodes", overview_index, "description"],
                "node.generated",
                kind=kind,
                identifier=identifier,
                field="description",
            )
        overview_evidence_args = {
            "status": str(node["evidence_status"]),
            "internal_responsibility": False,
        }
        add(
            ["working_map", "overview_map", "nodes", overview_index, "evidence_label"],
            "evidence.presentation",
            field="label",
            **overview_evidence_args,
        )
        add(
            ["working_map", "overview_map", "nodes", overview_index, "evidence_note"],
            "evidence.presentation",
            field="description",
            **overview_evidence_args,
        )

    layer_keys = [
        ("layer.control.label", "layer.control.purpose"),
        ("layer.explanation.label", "layer.explanation.purpose"),
        ("layer.technical.label", "layer.technical.purpose"),
    ]
    for index, (label_key, purpose_key) in enumerate(layer_keys):
        add(["evidence_layers", index, "label"], label_key)
        add(["evidence_layers", index, "purpose"], purpose_key)

    return {
        "schema_version": OWNER_PRESENTATION_SCHEMA,
        "source_language": "zh-CN",
        "messages": messages,
        "source_language_paths": source_paths,
    }


def draft_software_control(
    brief: Mapping[str, Any],
    review: Mapping[str, Any],
    system_architecture: Mapping[str, Any],
    evidence: list[Mapping[str, Any]] | None = None,
    *,
    semantic_interpretation: Mapping[str, Any] | None = None,
    analysis_mode: str = "basic_evidence",
    human_language: str = "zh-CN",
) -> dict[str, Any]:
    if human_language not in {"zh-CN", "en"}:
        raise ValueError("human_language must be zh-CN or en")
    english = human_language == "en"
    profile = system_architecture["target_profile"]
    product_name = str(profile["display_name"])
    claims = [item for item in brief["claims"] if isinstance(item, Mapping)]
    accepted_function_claims = [
        item
        for item in claims
        if item.get("section") == "function"
        and item.get("claim_type") != "unknown"
        and item.get("evidence_ids")
    ]
    changed = next(
        (
            item
            for item in accepted_function_claims
            if item.get("scope") == "user_behavior_change"
        ),
        next(
            (
                item
                for item in accepted_function_claims
                if item.get("id") == "function.auto-behavior-signal"
            ),
            accepted_function_claims[0] if accepted_function_claims else claims[0],
        ),
    )
    has_confirmed_function_change = bool(accepted_function_claims)
    interpretation = next(
        (
            item for item in claims
            if item.get("section") == "architecture"
            and item.get("claim_type") != "unknown"
            and item.get("evidence_ids")
        ),
        changed,
    )
    claim_ids = [str(changed["id"])]
    evidence_ids = [str(item) for item in changed.get("evidence_ids", [])]
    if has_confirmed_function_change:
        confirmed_change_text = str(changed["text"])
        confirmed_change_state = "observed_fact"
        confirmed_change_label = "已确认"
        confirmed_change_explanation = "固定 Git 版本中的代码证据支持这个结论。"
        confirmed_change_basis = _basis(claim_ids, evidence_ids)
    else:
        changed_file_count = int(brief["change"]["changed_files"])
        confirmed_change_text = (
            f"固定 Git 差异确认这次修改了 {changed_file_count} 个文件；"
            "具体功能或架构含义还不能确定。"
        )
        confirmed_change_state = "observed_fact"
        confirmed_change_label = "已确认"
        confirmed_change_explanation = (
            "这里仅确认固定版本中的文件变化，不把未被支持的语义解释当成事实。"
        )
        confirmed_change_basis = _basis(
            evidence_ids=["git.change_identity", "git.diff_summary"]
        )
    interpretation_claim_ids = [str(interpretation["id"])]
    interpretation_evidence_ids = [str(item) for item in interpretation.get("evidence_ids", [])]
    components = profile.get("conceptual_architecture", {}).get("components", [])
    map_kind = str(
        profile.get("conceptual_architecture", {}).get("architecture_kind", "workflow")
    )
    is_capability_map = map_kind == "capability_map"
    component_ids = [str(item["id"]) for item in components]
    changed_node_ids = set(system_architecture.get("change_overlay", {}).get("added", [])) | set(
        system_architecture.get("change_overlay", {}).get("modified", [])
    )
    changed_nodes = [
        item
        for item in system_architecture.get("nodes", [])
        if item.get("node_id") in changed_node_ids
    ]
    groups = sorted(
        {
            str(item["group_id"])
            for item in changed_nodes
        }
    )
    changed_paths = {
        str(path)
        for item in changed_nodes
        for path in item.get("owned_paths", [])
    }
    evidence_items = [item for item in (evidence or []) if isinstance(item, Mapping)]
    behavior_items = [item for item in evidence_items if item.get("kind") == "behavior_signal"]
    behavior_kinds = {
        _evidence_content_field(item, "kind") for item in behavior_items
    }
    if {"added_exception_raise", "added_nonzero_return"} <= behavior_kinds:
        behavior_kind = "stop_or_failure"
    elif "added_exception_raise" in behavior_kinds:
        behavior_kind = "exception_stop"
    elif "added_nonzero_return" in behavior_kinds:
        behavior_kind = "failure_stop"
    else:
        behavior_kind = "call_signature"
    has_stop_signal = bool(
        behavior_kinds & {"added_exception_raise", "added_nonzero_return"}
    )
    behavior_paths = [
        path
        for item in behavior_items
        if (path := _evidence_content_field(item, "path")) is not None
    ]
    primary_behavior_paths = set(behavior_paths[:1])
    unsupported_paths = _unsupported_changed_paths(review)
    generator_metadata = brief.get("generator_metadata", {})
    no_model_semantics = (
        isinstance(generator_metadata, Mapping)
        and str(generator_metadata.get("model", "")).lower() == "none"
    )
    detail_defs: list[tuple[str, str, str, str, Mapping[str, Any]]] = [
        (
            "receive",
            "输入进入软件",
            "软件接收用户、程序或其他系统交给它的内容。",
            "input",
            {},
        ),
        (
            "prepare",
            "检查并整理输入",
            "软件把收到的内容整理成主要功能可以处理的形式。",
            "process",
            {},
        ),
        ("work", "执行主要功能", "软件完成它最主要的处理工作。", "process", {}),
        (
            "return",
            "返回结果或状态",
            "把处理结果、状态或数据交还给调用方。",
            "output",
            {},
        ),
    ]
    capability_detail_ids: dict[str, list[str]] = {}
    if components and is_capability_map:
        detail_defs = []
        for component in components:
            raw_details = component.get("details", [])
            details = (
                [item for item in raw_details if isinstance(item, Mapping)]
                if isinstance(raw_details, list) and len(raw_details) >= 2
                else [component]
            )
            capability_detail_ids[str(component["id"])] = [str(item["id"]) for item in details]
            detail_defs.extend(
                (
                    str(item["id"]),
                    str(item["label"]),
                    str(item["description"]),
                    str(item["type"]),
                    item,
                )
                for item in details
            )
    elif components:
        detail_defs = [
            (
                str(item["id"]),
                str(item["label"]),
                str(item["description"]),
                str(item["type"]),
                item,
            )
            for item in components
        ]
    changed_parent_index = _changed_component_index(
        [item for item in components if isinstance(item, Mapping)],
        primary_behavior_paths or changed_paths,
        set() if primary_behavior_paths else set(groups),
    )
    changed_detail_id: str | None = None
    if is_capability_map and changed_parent_index is not None:
        changed_parent = components[changed_parent_index]
        raw_details = changed_parent.get("details", [])
        details = [item for item in raw_details if isinstance(item, Mapping)] if isinstance(raw_details, list) else []
        if len(details) >= 2:
            changed_detail_index = _changed_component_index(
                details,
                primary_behavior_paths or changed_paths,
                set() if primary_behavior_paths else set(groups),
            )
            if changed_detail_index is not None:
                changed_detail_id = str(details[changed_detail_index]["id"])
        else:
            changed_detail_id = str(changed_parent["id"])
    changed_step_index = changed_parent_index if is_capability_map else _changed_component_index(
        [item[4] for item in detail_defs],
        primary_behavior_paths or changed_paths,
        set() if primary_behavior_paths else set(groups),
    )
    semantic_summary = (
        semantic_interpretation.get("change_summary")
        if isinstance(semantic_interpretation, Mapping)
        and isinstance(semantic_interpretation.get("change_summary"), Mapping)
        else None
    )
    semantic_component_ids = (
        [str(value) for value in semantic_summary.get("changed_component_ids", [])]
        if isinstance(semantic_summary, Mapping)
        else []
    )
    if len(semantic_component_ids) == 1 and semantic_component_ids[0] in component_ids:
        changed_parent_index = component_ids.index(semantic_component_ids[0])
        changed_step_index = changed_parent_index
        if is_capability_map:
            changed_detail_id = str(components[changed_parent_index]["id"])
        else:
            changed_step_index = changed_parent_index
    mapped_step_label = (
        str(components[changed_parent_index]["label"])
        if is_capability_map and changed_parent_index is not None
        else detail_defs[changed_step_index][1] if changed_step_index is not None else None
    )
    behavior_evidence_ids = [str(item["id"]) for item in behavior_items]
    first_screen_change_headline: str | None = None
    if semantic_summary is not None and semantic_summary.get("evidence_ids"):
        semantic_evidence_ids = [str(value) for value in semantic_summary["evidence_ids"]]
        first_screen_change_headline = str(semantic_summary["headline"])
        workflow_change_text = (
            f"{semantic_summary['headline']} {semantic_summary['explanation']}"
        ).strip()
        interpretation_evidence_ids = semantic_evidence_ids
        evidence_ids = sorted(set([*evidence_ids, *semantic_evidence_ids]))
    elif behavior_items:
        signal_text = _behavior_phrase(behavior_items)
        if has_stop_signal:
            workflow_change_text = (
                f"固定代码差异显示，这次在“{mapped_step_label}”附近新增了{signal_text}。"
                "这些变化只会在特定条件下触发；实际运行和用户影响还没验证。"
                if mapped_step_label is not None
                else f"固定代码差异显示，这次新增了{signal_text}，但还不能可靠定位到"
                + ("哪项软件能力。" if is_capability_map else "哪个用户操作。")
                + "实际运行和用户影响还没验证。"
            )
        else:
            workflow_change_text = (
                f"固定代码差异显示，这次在“{mapped_step_label}”附近出现了{signal_text}。"
                "现有调用方是否需要调整还没验证。"
                if mapped_step_label is not None
                else f"固定代码差异显示，这次出现了{signal_text}，但还不能可靠定位到"
                + ("哪项软件能力。" if is_capability_map else "哪个用户操作。")
                + "现有调用方是否需要调整还没验证。"
            )
    else:
        workflow_change_text = (
            f"从固定版本的代码位置看，这次变化最可能对应“{mapped_step_label}”这一步；"
            + (
                "确定性检查尚未解释具体行为，实际效果也还没运行验证。"
                if no_model_semantics
                else "还没有运行软件验证实际效果。"
            )
            if mapped_step_label is not None
            else (
                "已发现代码变化，但目前无法确认它对应软件能力结构中的哪一项。"
                if is_capability_map
                else "已发现代码变化，但目前无法确认它对应项目工作流程中的哪一步。"
            )
        )

    user_behavior_claim = next(
        (
            item
            for item in claims
            if item.get("scope") == "user_behavior_change"
            and item.get("claim_type") != "unknown"
            and item.get("evidence_ids")
        ),
        None,
    )
    semantic_audience = next(
        (
            candidate
            for candidate in (
                _specific_audience_candidate(item)
                for item in (semantic_summary or {}).get("audience_candidates", [])
            )
            if candidate is not None
        ),
        None,
    )
    if user_behavior_claim is not None:
        impact_mode = (
            "confirmed_source_claim"
            if user_behavior_claim.get("claim_type") == "verified_fact"
            else "source_claim"
        )
        impact_text = str(user_behavior_claim["text"])
        impact_label = "已确认" if user_behavior_claim.get("claim_type") == "verified_fact" else "有依据的判断"
        impact_state = "supported_interpretation"
        impact_explanation = "这条影响判断来自受约束说明，并保留其证据和限制。"
        impact_basis = _basis(
            [str(user_behavior_claim["id"])],
            [str(item) for item in user_behavior_claim.get("evidence_ids", [])],
        )
        primary_audience = "被分析软件的普通用户"
        primary_audience_status = "very_likely"
    elif semantic_audience is not None:
        impact_mode = "role_candidate"
        impact_text = (
            f"The person most likely to need to review this change is “{semantic_audience['role']}”. "
            f"{semantic_audience['reason']} Whether this changes real usage has not been run or verified."
            if english
            else f"最可能需要关注这次变化的是“{semantic_audience['role']}”。"
            f"{semantic_audience['reason']} 是否会在实际使用中出现变化，还没有运行确认。"
        )
        impact_label = "可能受影响"
        impact_state = "unknown"
        impact_explanation = "这是模型基于固定代码证据提出的角色候选，不代表已经确认实际用户影响。"
        impact_basis = _basis(evidence_ids=list(semantic_audience["evidence_ids"]))
        primary_audience = str(semantic_audience["role"])
        primary_audience_status = "possible"
    elif no_model_semantics:
        impact_mode = "unassessed"
        impact_text = "这次只完成了代码和结构检查，还没有判断普通用户会不会感觉到变化。"
        impact_label = "还没判断"
        impact_state = "unknown"
        impact_explanation = "没有运行行为语义解释，不能把未分析写成“目前没发现”。"
        impact_basis = _basis(source_refs=["limitation:semantic-interpretation-not-run"])
        primary_audience = "被分析软件的普通用户"
        primary_audience_status = "unknown"
    else:
        impact_mode = "not_found"
        impact_text = "目前没有足够证据确认普通用户已经直接感觉到变化。"
        impact_label = "目前没发现"
        impact_state = "unknown"
        impact_explanation = "没有发现不等于已经证明不存在。"
        impact_basis = _basis(source_refs=["limitation:static-impact-is-not-user-impact"])
        primary_audience = "被分析软件的普通用户"
        primary_audience_status = "not_observed"

    unsupported_note = ""
    if unsupported_paths:
        unsupported_note = (
            f"另有 {len(unsupported_paths)} 个说明或配置变化已收集但不能建立结构关系；"
            f"其中包括 {unsupported_paths[0].rsplit('/', 1)[-1]}，需要结合代码核对，不能直接当成事实。"
        )
    residual_risk_text = "还没有运行目标软件验证真实行为。"
    if no_model_semantics:
        residual_risk_text += " 也没有完成完整的行为语义解释。"
    if unsupported_note:
        residual_risk_text += " " + unsupported_note

    semantic_checks = (
        semantic_interpretation.get("owner_checks")
        if isinstance(semantic_interpretation, Mapping)
        and isinstance(semantic_interpretation.get("owner_checks"), list)
        else []
    )
    if semantic_checks:
        owner_checks = [str(item["instructions"]) for item in semantic_checks]
        owner_actions = [
            {
                "id": f"verify.model-{index + 1}",
                "title": str(item["title"]),
                "instructions": str(item["instructions"]),
                "basis_type": "supported_interpretation",
                "completion_status": "recommended_not_run",
                "source_refs": [str(value) for value in item["evidence_ids"]],
            }
            for index, item in enumerate(semantic_checks)
        ]
    elif has_stop_signal:
        owner_checks = [
            (
                f"在“{mapped_step_label}”完成一次正常操作，确认仍能得到预期结果"
                if mapped_step_label is not None
                else "完成一次正常操作，确认仍能得到预期结果"
            ),
            "再用容易触发新增停止或失败分支的情况检查一次，确认提示和退出方式符合预期",
        ]
        owner_actions = [
            {
                "id": "verify.normal-path",
                "title": "确认正常情况",
                "instructions": owner_checks[0],
                "basis_type": "code_change",
                "completion_status": "recommended_not_run",
                "source_refs": behavior_evidence_ids,
            },
            {
                "id": "verify.stop-condition",
                "title": "确认停止条件",
                "instructions": owner_checks[1],
                "basis_type": "code_change",
                "completion_status": "recommended_not_run",
                "source_refs": behavior_evidence_ids,
            },
        ]
    elif behavior_items:
        owner_checks = [
            (
                f"在“{mapped_step_label}”完成一次正常操作，确认仍能得到预期结果"
                if mapped_step_label is not None
                else "完成一次正常操作，确认仍能得到预期结果"
            ),
            "核对现有调用方传入的信息，确认修改后的调用方式仍然兼容",
        ]
        owner_actions = [
            {
                "id": "verify.normal-path",
                "title": "确认正常情况",
                "instructions": owner_checks[0],
                "basis_type": "code_change",
                "completion_status": "recommended_not_run",
                "source_refs": behavior_evidence_ids,
            },
            {
                "id": "verify.callers",
                "title": "确认调用方",
                "instructions": owner_checks[1],
                "basis_type": "code_change",
                "completion_status": "recommended_not_run",
                "source_refs": behavior_evidence_ids,
            },
        ]
    else:
        owner_checks = [
            "确认高亮位置确实是本次改动所在功能",
            "运行一条最重要的真实使用路径",
        ]
        owner_actions = [
            {
                "id": "verify.owner-map",
                "title": "确认软件能力图" if is_capability_map else "确认软件工作图",
                "instructions": (
                    "由了解项目的人核对能力结构，修正遗漏或不符合实际业务的地方；不要补写没有证据的先后顺序。"
                    if is_capability_map
                    else "由了解项目的人核对四步工作图，修正不符合实际业务的地方。"
                ),
                "basis_type": "evidence_gap",
                "completion_status": "recommended_not_run",
                "source_refs": ["auto-profile:candidate"],
            },
            {
                "id": "verify.runtime",
                "title": "验证真实行为",
                "instructions": "运行与本次改动最相关的一条用户路径或接口，记录实际结果。",
                "basis_type": "evidence_gap",
                "completion_status": "recommended_not_run",
                "source_refs": ["limitation:runtime-behavior-unverified"],
            },
        ]
    nodes = []
    order_label = str(
        profile.get("conceptual_architecture", {}).get(
            "workflow_order_label", "顺序未验证"
        )
    )
    order_note = str(
        profile.get("conceptual_architecture", {}).get(
            "workflow_order_note", "这组步骤尚未经过运行顺序验证。"
        )
    )
    order_status = str(
        profile.get("conceptual_architecture", {}).get(
            "workflow_order_status", "unverified"
        )
    )
    for index, (node_id, label, description, node_type, component) in enumerate(detail_defs):
        is_changed = (
            node_id == changed_detail_id
            if is_capability_map
            else changed_step_index is not None and index == changed_step_index
        )
        evidence_status = str(component.get("evidence_status", "generated_candidate"))
        component_statement_state = (
            "supported_interpretation"
            if evidence_status.startswith("model_interpreted")
            else "project_declared"
        )
        evidence_label = str(component.get("evidence_label", "自动候选"))
        evidence_note = str(
            component.get(
                "evidence_note", "这一步是自动候选，需要项目负责人确认。"
            )
        )
        component_source_refs = [str(ref) for ref in component.get("source_refs", [])]
        nodes.append(
            {
                "id": node_id,
                "label": label,
                "description": description,
                "type": node_type,
                "statement_state": component_statement_state,
                "change_state": "changed" if is_changed else "unknown",
                "implementation_group_ids": groups if is_changed else [],
                "evidence_status": evidence_status,
                "evidence_label": evidence_label,
                "evidence_note": evidence_note,
                "source_refs": component_source_refs,
                "owner_view": {
                    "meaning": description,
                    "visible_result": (
                        "这项能力向使用它的人或其他功能提供对应结果；当前证据不声明固定的下一步。"
                        if is_capability_map
                        else "这一阶段的结果会被交给下一阶段继续处理。"
                    ),
                    "current_change": workflow_change_text if is_changed else "目前没有证据表明本次修改改变了这一步。",
                    "affected_people": impact_text if is_changed else "现有材料不足以确认谁会直接受到影响。",
                    "unknowns": [
                        evidence_note,
                        order_note,
                        "项目说明和代码位置都不能替代真实运行验证。",
                    ],
                    "owner_checks": owner_checks if is_changed else [
                        "核对项目说明是否仍与当前软件目标一致",
                        (
                            "核对这项能力通常由哪些入口或其他功能调用"
                            if is_capability_map
                            else "需要确认顺序时，运行或检查真实编排路径"
                        ),
                    ],
                    "basis": _basis(
                        interpretation_claim_ids if is_changed else [],
                        interpretation_evidence_ids if is_changed else [],
                        component_ids,
                        ["auto-draft:static-structure", *component_source_refs],
                    ),
                },
            }
        )
    overview_nodes = []
    if is_capability_map:
        nodes_by_id = {str(node["id"]): node for node in nodes}
        for index, component in enumerate(components):
            detail_ids = capability_detail_ids.get(str(component["id"]), [str(component["id"])])
            group = [nodes_by_id[detail_id] for detail_id in detail_ids]
            overview_nodes.append(
                {
                    "id": f"overview.stage-{index + 1}",
                    "label": str(component["label"]),
                    "description": _owner_excerpt(str(component["description"])),
                    "statement_state": (
                        "supported_interpretation"
                        if str(component.get("evidence_status", "")).startswith("model_interpreted")
                        else "project_declared"
                    ),
                    "change_state": "changed" if changed_parent_index == index else "unknown",
                    "detail_node_ids": detail_ids,
                    "evidence_status": str(component.get("evidence_status", "generated_candidate")),
                    "evidence_label": str(component.get("evidence_label", "自动候选")),
                    "evidence_note": str(component.get("evidence_note", "这项能力需要项目负责人确认。")),
                    "source_refs": [str(ref) for ref in component.get("source_refs", [])],
                }
            )
    else:
        overview_groups = _four_contiguous_groups(nodes)
        for index, group in enumerate(overview_groups):
            evidence_status, evidence_label, evidence_note, source_refs = _aggregate_evidence(group)
            first = group[0]
            last = group[-1]
            label = (
                first["label"]
                if len(group) == 1
                else f"{first['label']} to {last['label']}"
                if english
                else f"{first['label']}到{last['label']}"
            )
            description = (
                _owner_excerpt(first["description"])
                if len(group) == 1
                else f"From “{first['label']}” to “{last['label']}”, this stage contains {len(group)} detailed steps."
                if english
                else f"从“{first['label']}”到“{last['label']}”，包含 {len(group)} 个详细步骤。"
            )
            overview_nodes.append(
                {
                    "id": f"overview.stage-{index + 1}",
                    "label": label,
                    "description": description,
                    "statement_state": (
                        "supported_interpretation"
                        if any(node["statement_state"] == "supported_interpretation" for node in group)
                        else "project_declared"
                    ),
                    "change_state": "changed" if any(node["change_state"] == "changed" for node in group) else "unknown",
                    "detail_node_ids": [node["id"] for node in group],
                    "evidence_status": evidence_status,
                    "evidence_label": evidence_label,
                    "evidence_note": evidence_note,
                    "source_refs": source_refs,
                }
            )
    flows = [] if is_capability_map else [
        {
            "from": nodes[index]["id"],
            "to": nodes[index + 1]["id"],
            "label": order_label,
            "statement_state": (
                "supported_interpretation"
                if analysis_mode == "full_model"
                else "project_declared"
            ),
        }
        for index in range(len(nodes) - 1)
    ]
    overview_flows = [] if is_capability_map else [
        {"from": overview_nodes[index]["id"], "to": overview_nodes[index + 1]["id"], "label": order_label, "statement_state": "supported_interpretation" if analysis_mode == "full_model" else "project_declared"}
        for index in range(len(overview_nodes) - 1)
    ]
    change_identity = brief["change"]
    document: dict[str, Any] = {
        "schema_version": "change-passport.software-control.v1",
        "analysis_mode": analysis_mode,
        "sample_id": brief["sample_id"],
        "source_identity": {
            "brief_identity": brief["brief_identity"],
            "review_identity": review["review_identity"],
            "change_identity": {
                "base_commit": change_identity["base_commit"],
                "head_commit": change_identity["head_commit"],
                "patch_sha256": change_identity["patch_sha256"],
            },
            "artifacts": [],
        },
        "product": {
            "name": product_name,
            "purpose": str(profile.get("conceptual_architecture", {}).get("description") or f"{product_name} 的具体业务目的仍需负责人确认。"),
            "statement_state": str(profile.get("conceptual_architecture", {}).get("purpose_statement_state", "project_declared")),
            "source_refs": [
                f"target-profile:{profile['profile_id']}:sha256:{profile['profile_sha256']}",
                *[str(ref) for ref in profile.get("conceptual_architecture", {}).get("purpose_source_refs", [])],
            ],
        },
        "first_screen_summary": {
            # The first screen is the ten-second decision surface. A validated
            # model headline is intentionally kept separate from its longer
            # explanation, which remains in the five-question detail below.
            "headline": first_screen_change_headline or workflow_change_text,
            "internal_concept_label": "本次变化所在部分",
            "confirmed_change": {
                "text": confirmed_change_text,
                "statement_state": confirmed_change_state,
                "state_label": confirmed_change_label,
                "state_explanation": confirmed_change_explanation,
                "basis": confirmed_change_basis,
            },
            "user_impact": {
                "text": impact_text, "statement_state": impact_state, "state_label": impact_label,
                "state_explanation": impact_explanation,
                "basis": impact_basis,
            },
            "residual_risk": {
                "text": residual_risk_text, "statement_state": "unknown", "state_label": "还没验证",
                "state_explanation": "静态代码事实不能替代实际运行检查。",
                "basis": _basis(source_refs=["limitation:runtime-behavior-unverified", *(["limitation:semantic-interpretation-not-run"] if no_model_semantics else []), *[f"unsupported:{path}" for path in unsupported_paths[:3]]]),
            },
            "owner_action": {
                "text": (
                    owner_checks[0]
                    if semantic_checks
                    else
                    "先分别确认正常情况和新增的停止或失败条件。"
                    if has_stop_signal
                    else "先确认正常情况，再核对现有调用方是否仍然兼容。"
                    if behavior_items
                    else "先核对这次改动所在功能，再验证一条最重要的真实使用路径。"
                ), "statement_state": "supported_interpretation", "state_label": "接下来做",
                "state_explanation": "这是根据当前证据缺口给出的建议，不代表已经检查完成。",
                "basis": _basis(claim_ids, [*evidence_ids, *behavior_evidence_ids]),
            },
        },
        "five_questions": [
            {"id": "software_operation", "question": "这是个什么软件？", "answer": f"这是 {product_name}。{profile.get('conceptual_architecture', {}).get('description', '当前自动草稿只能确认它的静态结构，具体业务目的仍需确认。')}", "statement_state": str(profile.get("conceptual_architecture", {}).get("purpose_statement_state", "project_declared")), "state_label": "来自项目说明" if profile.get("conceptual_architecture", {}).get("purpose_statement_state", "project_declared") == "project_declared" else "自动候选", "basis": _basis(component_ids=component_ids, source_refs=["auto-profile:conceptual-architecture", *[str(ref) for ref in profile.get("conceptual_architecture", {}).get("purpose_source_refs", [])]]), "details": {"software_steps": [item[1] for item in detail_defs]}},
            {"id": "current_change", "question": "AI 这次主要改变了什么？", "answer": workflow_change_text, "statement_state": "supported_interpretation" if changed_step_index is not None else "unknown", "state_label": "有依据的判断" if changed_step_index is not None else "暂时无法定位", "basis": _basis(interpretation_claim_ids, interpretation_evidence_ids), "details": {"change_points": [workflow_change_text]}},
            {"id": "affected_people", "question": "谁可能感觉到变化？", "answer": impact_text, "statement_state": impact_state, "state_label": impact_label, "basis": impact_basis, "details": {"audience_impacts": [{"audience": primary_audience, "status": primary_audience_status, "explanation": impact_text, "source_refs": impact_basis["source_refs"]}, {"audience": "依赖这个软件的其他系统", "status": "unknown", "explanation": "还没有运行集成验证；代码信号只能说明新增了停止或失败分支。" if has_stop_signal else "还没有验证现有调用方是否兼容修改后的调用方式。" if behavior_items else "还没有运行集成验证。", "source_refs": ["limitation:runtime-behavior-unverified", *behavior_evidence_ids]}]}},
            {"id": "unknowns", "question": "还有什么我们不知道？", "answer": residual_risk_text + (" 还没有由负责人确认自动生成的软件能力图。" if is_capability_map else " 还没有由负责人确认自动生成的软件工作图。"), "statement_state": "unknown", "state_label": "还没验证", "basis": _basis(source_refs=["limitation:runtime-behavior-unverified", "auto-profile:candidate", *(["limitation:semantic-interpretation-not-run"] if no_model_semantics else [])]), "details": {"unknowns": ["真实运行行为是否改变", *(["完整行为语义尚未解释"] if no_model_semantics else []), *([unsupported_note] if unsupported_note else []), "自动能力图是否符合项目实际业务" if is_capability_map else "自动工作图是否符合项目实际业务"]}},
            {"id": "next_verification", "question": "我接下来该检查什么？", "answer": "先完成两项最小检查：", "statement_state": "supported_interpretation", "state_label": "建议检查", "basis": _basis(claim_ids, [*evidence_ids, *behavior_evidence_ids]), "details": {"owner_checks": owner_checks, "actions": owner_actions}},
        ],
        "working_map": {
            "map_kind": map_kind,
            "title": (
                f"{product_name} 包含哪些主要能力"
                if is_capability_map
                else f"{product_name} 怎样从输入走到结果"
            ),
            "description": (
                "先看项目的主要能力，再展开项目说明与代码位置；这些能力没有固定先后顺序。"
                if is_capability_map
                else "先看四个阶段，再展开项目说明中的详细步骤和对应证据状态。"
            ),
            "screen_summary": {
                "headline": (
                    f"先看 {product_name} 能做什么"
                    if is_capability_map
                    else f"先用四个阶段理解 {product_name}"
                ),
                "overview": (
                    "下面是从固定版本项目说明和代码位置提炼的能力结构；它们可以被不同入口组合使用，不代表运行顺序。"
                    if is_capability_map
                    else f"工作流程来自固定版本的项目说明；{order_label}，每一步都需要与代码和运行证据分开判断。"
                ),
                "boundary_label": "能力说明与代码对账" if is_capability_map else "项目说明与代码对账",
            },
            "overview_map": {
                "title": "主要能力（没有先后顺序）" if is_capability_map else "四步看懂这个软件",
                "nodes": overview_nodes,
                "flows": overview_flows,
            },
            "statement_state": "supported_interpretation" if analysis_mode == "full_model" else "project_declared",
            "source": {"profile_id": profile["profile_id"], "profile_sha256": profile["profile_sha256"]},
            "boundary_note": (
                f"这张图先读取固定版本的项目说明，再核对代码位置。{order_note}"
                "它不是调用图或运行记录，负责人确认前不得当成已验证事实。"
                if is_capability_map
                else f"这张图先读取固定版本的项目说明，再核对代码位置。{order_note}它不是运行记录，负责人确认前不得当成已验证事实。"
            ),
            "order_status": order_status,
            "order_label": order_label,
            "order_note": order_note,
            "order_source_refs": [str(ref) for ref in profile.get("conceptual_architecture", {}).get("workflow_order_source_refs", [])],
            "nodes": nodes,
            "flows": flows,
        },
        "evidence_layers": [
            {"id": "software_control", "label": "软件掌控层", "purpose": "先回答软件怎样工作、改了什么和下一步检查什么。"},
            {"id": "explanation", "label": "解释分析层", "purpose": "区分已确认、目前没发现和还没验证。"},
            {"id": "technical_evidence", "label": "技术证据层", "purpose": "按需展开固定版本、文件和静态关系。"},
        ],
        "validation": {
            "allowed_statement_states": ["observed_fact", "supported_interpretation", "project_declared", "unknown"],
            "source_claim_ids": sorted({str(item["id"]) for item in claims}),
            "source_evidence_ids": sorted({str(value) for item in claims for value in item.get("evidence_ids", [])}),
            "source_component_ids": [item["id"] for item in nodes],
            "limitations": [("软件能力图是自动候选说明，不是调用顺序或运行时追踪" if is_capability_map else "软件工作图是自动候选说明，不是运行时追踪"), "静态代码关系不能证明真实用户影响", "负责人尚未确认项目业务语义"],
            "human_comprehension_status": "pending_owner_confirmation",
        },
    }
    document["presentation"] = _automatic_owner_presentation(
        document,
        behavior_kind=behavior_kind,
        changed_file_count=int(brief["change"]["changed_files"]),
        changed_claim_id=str(changed["id"]),
        has_behavior=bool(behavior_items),
        has_stop_signal=has_stop_signal,
        impact_mode=impact_mode,
        map_kind=map_kind,
        mapped_step_label=mapped_step_label,
        no_model_semantics=no_model_semantics,
        semantic_generated=semantic_summary is not None,
        unsupported_paths=unsupported_paths,
    )
    document["control_identity"] = sha256_bytes(canonical_json_bytes(document))
    return document
