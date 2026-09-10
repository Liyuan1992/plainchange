from __future__ import annotations

import re
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

from .git_evidence import list_git_tree, read_git_blob
from .models import canonical_json_bytes, sha256_bytes
from .project_declarations import (
    collect_declarations,
    declared_purpose,
    reconcile_workflow,
)


_CATEGORY_META = {
    "entry": ("调用与用户入口", "接收用户、程序或外部系统交给软件的输入。", "main"),
    "data": ("数据与状态", "整理软件需要读取、保存或传递的数据。", "main"),
    "core": ("主要功能", "执行这个软件最主要的处理工作。", "main"),
    "quality": ("测试与质量保障", "检查主要功能是否仍按预期工作。", "support"),
    "delivery": ("说明与工程辅助", "承载说明、示例、构建和维护工具。", "support"),
}


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
    supported = sorted(
        path for path in tree
        if PurePosixPath(path).suffix in {".py", ".js", ".jsx", ".ts", ".tsx"}
    )
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
    fallback_purpose, fallback_workflow = _workflow_for_kind(kind)
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
    main_ids = [item for item in active_ids if _CATEGORY_META[item][2] == "main"]
    if workflow_evidence:
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
            }
            for index, item in enumerate(workflow_evidence["steps"])
        ]
        component_ids = [str(item["id"]) for item in components]
        flows = [
            {
                "from": component_ids[index],
                "to": component_ids[index + 1],
                "label": "项目说明的下一步",
            }
            for index in range(len(component_ids) - 1)
        ]
        boundary_note = (
            "这张图来自固定版本的项目说明，并与代码位置进行对账；"
            f"{workflow_evidence['order_label']}，但仍不是运行记录。"
        )
        architecture_extra = {
            "source_refs": list(workflow_evidence["source_refs"]),
            "workflow_order_status": str(workflow_evidence["order_status"]),
            "workflow_order_label": str(workflow_evidence["order_label"]),
            "workflow_order_note": str(workflow_evidence["order_note"]),
            "workflow_order_source_refs": list(workflow_evidence["order_source_refs"]),
        }
        architecture_title = f"{display_name} 项目说明中的工作流程"
    else:
        component_ids = ("receive_input", "prepare_input", "perform_work", "return_result")
        component_groups = (
            [item for item in ("entry",) if item in active_ids],
            [item for item in ("entry", "data") if item in active_ids],
            main_ids,
            [item for item in ("entry", "data") if item in active_ids],
        )
        components = [
            {
                "id": component_ids[index],
                "type": item[2],
                "label": item[0],
                "description": item[1],
                "grid_column": 1,
                "grid_row": index + 1,
                "group_ids": component_groups[index],
                "evidence_status": "generated_candidate",
                "evidence_label": "自动候选",
                "evidence_note": "没有找到明确的项目工作流程说明，这一步是通用候选，需负责人确认。",
                "source_refs": [],
            }
            for index, item in enumerate(fallback_workflow)
        ]
        flows = [
            {"from": component_ids[0], "to": component_ids[1], "label": "候选顺序"},
            {"from": component_ids[1], "to": component_ids[2], "label": "候选顺序"},
            {"from": component_ids[2], "to": component_ids[3], "label": "候选顺序"},
        ]
        boundary_note = "没有找到明确的项目流程说明；这是通用候选图，不是项目事实或运行记录。"
        architecture_extra = {
            "source_refs": list(purpose["source_refs"]),
            "workflow_order_status": "unverified",
            "workflow_order_label": "顺序未验证",
            "workflow_order_note": "没有项目声明或编排证据支持这组通用候选步骤。",
            "workflow_order_source_refs": [],
        }
        architecture_title = f"{display_name} 怎样接收输入并完成处理"
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
        exact_scores.append(len(source_paths & changed_paths))
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


def draft_software_control(
    brief: Mapping[str, Any],
    review: Mapping[str, Any],
    system_architecture: Mapping[str, Any],
    evidence: list[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
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
    interpretation_claim_ids = [str(interpretation["id"])]
    interpretation_evidence_ids = [str(item) for item in interpretation.get("evidence_ids", [])]
    components = profile.get("conceptual_architecture", {}).get("components", [])
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
    if len(components) >= 4:
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
    changed_step_index = _changed_component_index(
        [item[4] for item in detail_defs],
        primary_behavior_paths or changed_paths,
        set() if primary_behavior_paths else set(groups),
    )
    mapped_step_label = (
        detail_defs[changed_step_index][1] if changed_step_index is not None else None
    )
    behavior_evidence_ids = [str(item["id"]) for item in behavior_items]
    if behavior_items:
        signal_text = _behavior_phrase(behavior_items)
        if has_stop_signal:
            workflow_change_text = (
                f"固定代码差异显示，这次在“{mapped_step_label}”附近新增了{signal_text}。"
                "这些变化只会在特定条件下触发；实际运行和用户影响还没验证。"
                if mapped_step_label is not None
                else f"固定代码差异显示，这次新增了{signal_text}，但还不能可靠定位到哪个用户操作。"
                "实际运行和用户影响还没验证。"
            )
        else:
            workflow_change_text = (
                f"固定代码差异显示，这次在“{mapped_step_label}”附近出现了{signal_text}。"
                "现有调用方是否需要调整还没验证。"
                if mapped_step_label is not None
                else f"固定代码差异显示，这次出现了{signal_text}，但还不能可靠定位到哪个用户操作。"
                "现有调用方是否需要调整还没验证。"
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
            else "已发现代码变化，但目前无法确认它对应项目工作流程中的哪一步。"
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
    if user_behavior_claim is not None:
        impact_text = str(user_behavior_claim["text"])
        impact_label = "已确认" if user_behavior_claim.get("claim_type") == "verified_fact" else "有依据的判断"
        impact_state = "supported_interpretation"
        impact_explanation = "这条影响判断来自受约束说明，并保留其证据和限制。"
        impact_basis = _basis(
            [str(user_behavior_claim["id"])],
            [str(item) for item in user_behavior_claim.get("evidence_ids", [])],
        )
    elif no_model_semantics:
        impact_text = "这次只完成了代码和结构检查，还没有判断普通用户会不会感觉到变化。"
        impact_label = "还没判断"
        impact_state = "unknown"
        impact_explanation = "没有运行行为语义解释，不能把未分析写成“目前没发现”。"
        impact_basis = _basis(source_refs=["limitation:semantic-interpretation-not-run"])
    else:
        impact_text = "目前没有足够证据确认普通用户已经直接感觉到变化。"
        impact_label = "目前没发现"
        impact_state = "unknown"
        impact_explanation = "没有发现不等于已经证明不存在。"
        impact_basis = _basis(source_refs=["limitation:static-impact-is-not-user-impact"])

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

    if has_stop_signal:
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
                "title": "确认软件工作图",
                "instructions": "由了解项目的人核对四步工作图，修正不符合实际业务的地方。",
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
        is_changed = changed_step_index is not None and index == changed_step_index
        evidence_status = str(component.get("evidence_status", "generated_candidate"))
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
                "statement_state": "project_declared",
                "change_state": "changed" if is_changed else "unknown",
                "implementation_group_ids": groups if is_changed else [],
                "evidence_status": evidence_status,
                "evidence_label": evidence_label,
                "evidence_note": evidence_note,
                "source_refs": component_source_refs,
                "owner_view": {
                    "meaning": description,
                    "visible_result": "这一阶段的结果会被交给下一阶段继续处理。",
                    "current_change": workflow_change_text if is_changed else "目前没有证据表明本次修改改变了这一步。",
                    "affected_people": impact_text if is_changed else "现有材料不足以确认谁会直接受到影响。",
                    "unknowns": [
                        evidence_note,
                        order_note,
                        "项目说明和代码位置都不能替代真实运行验证。",
                    ],
                    "owner_checks": owner_checks if is_changed else [
                        "核对项目说明是否仍与当前软件目标一致",
                        "需要确认顺序时，运行或检查真实编排路径",
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
    for index, group in enumerate(_four_contiguous_groups(nodes)):
        evidence_status, evidence_label, evidence_note, source_refs = _aggregate_evidence(group)
        first = group[0]
        last = group[-1]
        label = first["label"] if len(group) == 1 else f"{first['label']}到{last['label']}"
        description = (
            first["description"]
            if len(group) == 1
            else f"从“{first['label']}”到“{last['label']}”，包含 {len(group)} 个详细步骤。"
        )
        overview_nodes.append(
            {
                "id": f"overview.stage-{index + 1}",
                "label": label,
                "description": description,
                "statement_state": "project_declared",
                "change_state": "changed" if any(node["change_state"] == "changed" for node in group) else "unknown",
                "detail_node_ids": [node["id"] for node in group],
                "evidence_status": evidence_status,
                "evidence_label": evidence_label,
                "evidence_note": evidence_note,
                "source_refs": source_refs,
            }
        )
    flows = [
        {
            "from": nodes[index]["id"],
            "to": nodes[index + 1]["id"],
            "label": order_label,
            "statement_state": "project_declared",
        }
        for index in range(len(nodes) - 1)
    ]
    overview_flows = [
        {"from": overview_nodes[index]["id"], "to": overview_nodes[index + 1]["id"], "label": order_label, "statement_state": "project_declared"}
        for index in range(3)
    ]
    change_identity = brief["change"]
    document: dict[str, Any] = {
        "schema_version": "change-passport.software-control.v1",
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
            "headline": workflow_change_text,
            "internal_concept_label": "本次变化所在部分",
            "confirmed_change": {
                "text": str(changed["text"]), "statement_state": "observed_fact", "state_label": "已确认",
                "state_explanation": "固定 Git 版本中的代码证据支持这个结论。",
                "basis": _basis(claim_ids, evidence_ids),
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
            {"id": "affected_people", "question": "谁可能感觉到变化？", "answer": impact_text, "statement_state": impact_state, "state_label": impact_label, "basis": impact_basis, "details": {"audience_impacts": [{"audience": "被分析软件的普通用户", "status": "unknown" if no_model_semantics else "not_observed", "explanation": impact_text, "source_refs": impact_basis["source_refs"]}, {"audience": "依赖这个软件的其他系统", "status": "unknown", "explanation": "还没有运行集成验证；代码信号只能说明新增了停止或失败分支。" if has_stop_signal else "还没有验证现有调用方是否兼容修改后的调用方式。" if behavior_items else "还没有运行集成验证。", "source_refs": ["limitation:runtime-behavior-unverified", *behavior_evidence_ids]}]}},
            {"id": "unknowns", "question": "还有什么我们不知道？", "answer": residual_risk_text + " 还没有由负责人确认自动生成的软件工作图。", "statement_state": "unknown", "state_label": "还没验证", "basis": _basis(source_refs=["limitation:runtime-behavior-unverified", "auto-profile:candidate", *(["limitation:semantic-interpretation-not-run"] if no_model_semantics else [])]), "details": {"unknowns": ["真实运行行为是否改变", *(["完整行为语义尚未解释"] if no_model_semantics else []), *([unsupported_note] if unsupported_note else []), "自动工作图是否符合项目实际业务"]}},
            {"id": "next_verification", "question": "我接下来该检查什么？", "answer": "先完成两项最小检查：", "statement_state": "supported_interpretation", "state_label": "建议检查", "basis": _basis(claim_ids, [*evidence_ids, *behavior_evidence_ids]), "details": {"owner_checks": owner_checks, "actions": owner_actions}},
        ],
        "working_map": {
            "title": f"{product_name} 怎样从输入走到结果",
            "description": "先看四个阶段，再展开项目说明中的详细步骤和对应证据状态。",
            "screen_summary": {"headline": f"先用四个阶段理解 {product_name}", "overview": f"工作流程来自固定版本的项目说明；{order_label}，每一步都需要与代码和运行证据分开判断。", "boundary_label": "项目说明与代码对账"},
            "overview_map": {"title": "四步看懂这个软件", "nodes": overview_nodes, "flows": overview_flows},
            "statement_state": "project_declared",
            "source": {"profile_id": profile["profile_id"], "profile_sha256": profile["profile_sha256"]},
            "boundary_note": f"这张图先读取固定版本的项目说明，再核对代码位置。{order_note}它不是运行记录，负责人确认前不得当成已验证事实。",
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
            "limitations": ["软件工作图是自动候选说明，不是运行时追踪", "静态代码关系不能证明真实用户影响", "负责人尚未确认项目业务语义"],
            "human_comprehension_status": "pending_owner_confirmation",
        },
    }
    document["control_identity"] = sha256_bytes(canonical_json_bytes(document))
    return document
