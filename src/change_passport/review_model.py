from __future__ import annotations

from collections import defaultdict
import re
from typing import Any, Iterable, Mapping

from .architecture import (
    DELTA_SCHEMA,
    architecture_evidence_bindings,
    validate_system_architecture_snapshot,
)
from .models import ManifestError, canonical_json_bytes, sha256_bytes

REVIEW_SCHEMA = "change-passport.beginner-review.v2"

_TRUTH = {
    "verified_fact": ("verified", "已证实", 2),
    "inference": ("inference", "有依据的推断", 1),
    "unknown": ("unknown", "尚不清楚", 0),
}
_IMPORTANCE = {"high": 0, "medium": 1, "low": 2}
_STATUS_LABELS = {
    "added": "新增",
    "removed": "移除",
    "modified": "改变",
    "impacted": "有关联",
    "unchanged_context": "未改变的上下文",
}
_STATUS_ORDER = {
    "added": 0,
    "removed": 0,
    "modified": 1,
    "impacted": 2,
    "unchanged_context": 3,
}

# Presentation-only translations confirmed by the v1.2 prototype. Exact technical
# labels remain in the model and these labels never create nodes, edges, or claims.
_PRESENTATION_LABEL_PATTERNS = (
    ("test_skill_argument_validation", "验证参数检查与错误分类"),
    ("argument_validation", "统一检查并整理参数"),
    ("tool_execution_policy", "判断失败是否值得重试"),
    ("skills.errors", "把异常归成统一类别"),
    ("skills.registry", "登记并调用工具"),
    ("skills.base", "返回结构化工具结果"),
    ("skills.web", "网页访问工具"),
    ("skill_execution", "聊天中的工具执行入口"),
    ("image_generation", "图像生成工具"),
    ("ai_coding_feedback", "AI 编码反馈工具"),
    ("local_file", "本地文件工具"),
    ("local_search", "项目内文本搜索"),
    ("skills.control", "控制与执行桥接"),
    ("chat_engine.engine", "聊天运行入口"),
)
_PLAIN_TERM_REPLACEMENTS = (
    ("SkillRegistry", "工具调用入口"),
    ("本地 provider completion 回执", "AI 完成说明"),
    ("的事后自报目标", "当时解释的目标"),
    ("回执自报实现包括", "AI 回复中还说实现包括"),
    ("input_schema", "参数声明"),
    ("参数声明 成为唯一校验事实来源", "统一负责参数检查"),
    ("参数声明成为唯一校验事实来源", "统一负责参数检查"),
    ("让 统一负责参数检查", "统一负责参数检查"),
    ("让统一负责参数检查", "统一负责参数检查"),
    ("并让工具失败对模型和重试策略可判断", "并让系统知道失败后是否值得重试"),
    ("argument_clamps", "参数调整记录"),
    ("minimum/maximum", "允许范围"),
    ("uniqueItems", "去重规则"),
    ("JSON Schema", "参数规则"),
    ("type 关键字", "类型规则"),
    ("缺少权威类型: actual_test_receipt", "没有可核对的独立测试收据"),
    ("actual_test_receipt", "可核对的独立测试收据"),
    ("缺少权威类型:", "缺少所需证据："),
    ("校验原因：", "原因："),
    ("retryable", "是否值得重试"),
    ("归一化", "整理"),
    ("集中参数整理、错误分类、是否值得重试 语义和对旧行为的兼容保留", "集中整理参数、统一错误分类、判断失败是否值得重试，并兼容旧行为"),
    ("技能", "工具"),
)
_TASK_CONTEXT_ROLES = {
    "original_task": (0, "user", "用户原话", "用户实际说过的内容"),
    "retrospective_claim": (1, "assistant", "AI 回复", "AI 当时的理解或完成说明"),
}


def _require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ManifestError(f"{label} must be an object")
    return value


def _require_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise ManifestError(f"{label} must be an array")
    return value


def _stable_unique(values: Iterable[str]) -> list[str]:
    return sorted({value for value in values if isinstance(value, str) and value})


def _claim_sort_key(claim: Mapping[str, Any]) -> tuple[int, int, str]:
    truth_rank = _TRUTH.get(str(claim.get("claim_type")), _TRUTH["unknown"])[2]
    return (
        _IMPORTANCE.get(str(claim.get("importance")), 9),
        -truth_rank,
        str(claim.get("id", "")),
    )


def _truth_for_claims(claims: list[Mapping[str, Any]]) -> tuple[str, str]:
    if not claims:
        return "unknown", "尚不清楚"
    lowest = min(
        (_TRUTH.get(str(claim.get("claim_type")), _TRUTH["unknown"]) for claim in claims),
        key=lambda item: item[2],
    )
    return lowest[0], lowest[1]


def _plain_excerpt(value: str, *, max_length: int = 72) -> str:
    result = value.replace("`", "").strip()
    result = re.sub(r"\baicr_[0-9a-f]+\b", "", result, flags=re.IGNORECASE)
    for source, target in _PLAIN_TERM_REPLACEMENTS:
        result = result.replace(source, target)
    result = re.sub(r"\s+", " ", result)
    result = re.sub(r"(?<=[\u3400-\u9fff])\s+(?=[\u3400-\u9fff])", "", result)
    first_clause = re.split(r"[；\n]", result, maxsplit=1)[0].strip()
    if len(first_clause) > max_length:
        boundary = max(
            first_clause.rfind(mark, 0, max_length + 1)
            for mark in ("，", "。", "：", ",", ".", ":")
        )
        if boundary >= 24:
            first_clause = first_clause[: boundary + 1]
        else:
            first_clause = first_clause[:max_length].rstrip() + "…"
    if first_clause and first_clause[-1] not in "。！？…":
        first_clause += "。"
    return first_clause


def _bounded_context_excerpt(value: Any, *, max_length: int = 280) -> str:
    if not isinstance(value, str):
        return ""
    result = value.replace("`", "").strip()
    for source, target in _PLAIN_TERM_REPLACEMENTS:
        result = result.replace(source, target)
    result = re.sub(r"\s+", " ", result)
    if len(result) > max_length:
        result = result[:max_length].rstrip("，。；:：, ") + "…"
    return result


def _task_context_from_evidence(evidence_value: Any) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    if isinstance(evidence_value, list):
        for index, raw_item in enumerate(evidence_value):
            if not isinstance(raw_item, Mapping) or raw_item.get("kind") != "task":
                continue
            authority = str(raw_item.get("authority", ""))
            role = _TASK_CONTEXT_ROLES.get(authority)
            if role is None:
                continue
            text = _bounded_context_excerpt(raw_item.get("content"))
            if not text:
                continue
            order, role_id, role_label, source_label = role
            entries.append(
                {
                    "evidence_id": str(raw_item.get("id") or f"task-context-{index}"),
                    "role": role_id,
                    "role_label": role_label,
                    "source_label": source_label,
                    "text": text,
                    "warning": (
                        "AI 的解释可以帮助理解，但不能代替用户确认。"
                        if role_id == "assistant"
                        else None
                    ),
                    "_order": order,
                }
            )
    entries = sorted(entries, key=lambda item: (item["_order"], item["evidence_id"]))[:4]
    for item in entries:
        item.pop("_order", None)
    roles = {item["role"] for item in entries}
    if not entries:
        return {
            "state": "unavailable",
            "state_label": "未获得任务对话",
            "summary": "这份报告没有拿到任务对话，暂时无法说明为什么这样改。",
            "entries": [],
            "action_label": None,
            "action_cost": None,
        }
    if roles == {"user", "assistant"}:
        summary = "已找到用户任务和 AI 回复线索；先区分用户说过什么、AI 当时怎样理解，再判断真正的改动原因。"
    elif "user" in roles:
        summary = "已找到用户任务线索，可以继续核对它是否说明了这次改动的原因。"
    else:
        summary = "已找到 AI 回复线索，但它只能说明 AI 当时的理解，不能代替用户意图。"
    return {
        "state": "available",
        "state_label": "已有任务线索",
        "summary": summary,
        "entries": entries,
        "action_label": "查看已有任务线索",
        "action_cost": "不调用模型，不消耗额外 Token",
    }


def _summary_from_claims(
    *,
    item_id: str,
    question: str,
    icon: str,
    claims: list[Mapping[str, Any]],
    binding_index: Mapping[str, Mapping[str, Any]],
    fallback: str,
) -> dict[str, Any]:
    selected = sorted(claims, key=_claim_sort_key)[:3]
    truth_state, truth_label = _truth_for_claims(selected)
    claim_ids = [str(item["id"]) for item in selected]
    evidence_ids = _stable_unique(
        evidence_id
        for item in selected
        for evidence_id in item.get("evidence_ids", [])
    )
    node_ids = _stable_unique(
        node_id
        for evidence_id in evidence_ids
        for node_id in binding_index.get(evidence_id, {}).get("node_ids", [])
    )
    texts = [_plain_excerpt(str(item["text"])).rstrip("。；") for item in selected]
    text = "；".join(texts) + ("。" if texts else "")
    limitations = _stable_unique(
        limitation
        for item in selected
        for limitation in item.get("limitations", [])
    )
    next_checks = [
        str(item["next_check"])
        for item in selected
        if isinstance(item.get("next_check"), str) and item["next_check"].strip()
    ]
    if not selected:
        text = fallback
    return {
        "id": item_id,
        "question": question,
        "icon": icon,
        "text": text,
        "truth_state": truth_state,
        "truth_label": truth_label,
        "claim_ids": claim_ids,
        "node_ids": node_ids,
        "evidence_ids": evidence_ids,
        "limitations": limitations,
        "next_check": next_checks[0] if next_checks else None,
        "items": [
            {
                "claim_id": str(item["id"]),
                "text": _plain_excerpt(str(item["text"])),
                "truth_state": _TRUTH.get(
                    str(item.get("claim_type")), _TRUTH["unknown"]
                )[0],
                "truth_label": _TRUTH.get(
                    str(item.get("claim_type")), _TRUTH["unknown"]
                )[1],
            }
            for item in selected
        ],
    }


def _node_indexes(
    delta: Mapping[str, Any],
) -> tuple[dict[str, Mapping[str, Any]], dict[str, Mapping[str, Any]]]:
    before = {
        str(item["node_id"]): _require_mapping(item, "before node")
        for item in _require_list(delta["before"]["nodes"], "before.nodes")
    }
    after = {
        str(item["node_id"]): _require_mapping(item, "after node")
        for item in _require_list(delta["after"]["nodes"], "after.nodes")
    }
    return before, after


def _responsibility(node: Mapping[str, Any] | None) -> str | None:
    if not node:
        return None
    values = node.get("responsibilities", [])
    if not isinstance(values, list):
        return None
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _node_status(
    node_id: str,
    before: Mapping[str, Mapping[str, Any]],
    after: Mapping[str, Mapping[str, Any]],
) -> str:
    node = after.get(node_id) or before[node_id]
    return str(node.get("change_status", "unchanged_context"))


def _plain_label(
    node_id: str,
    before: Mapping[str, Mapping[str, Any]],
    after: Mapping[str, Mapping[str, Any]],
) -> str:
    responsibility = _responsibility(after.get(node_id)) or _responsibility(before.get(node_id))
    if responsibility and re.search(r"[\u3400-\u9fff]", responsibility):
        return _plain_excerpt(responsibility, max_length=32)
    technical_label = _technical_label(node_id, before, after)
    for pattern, label in _PRESENTATION_LABEL_PATTERNS:
        if pattern in technical_label:
            return label
    return "职责名称尚不清楚"


def _plain_label_source(
    node_id: str,
    before: Mapping[str, Mapping[str, Any]],
    after: Mapping[str, Mapping[str, Any]],
) -> str:
    responsibility = _responsibility(after.get(node_id)) or _responsibility(before.get(node_id))
    if responsibility and re.search(r"[\u3400-\u9fff]", responsibility):
        return "verified_responsibility"
    technical_label = _technical_label(node_id, before, after)
    if any(pattern in technical_label for pattern, _ in _PRESENTATION_LABEL_PATTERNS):
        return "confirmed_prototype_glossary"
    return "unknown"


def _technical_label(
    node_id: str,
    before: Mapping[str, Mapping[str, Any]],
    after: Mapping[str, Mapping[str, Any]],
) -> str:
    node = after.get(node_id) or before[node_id]
    return str(node.get("label") or node_id)


def _view_node(
    node_id: str,
    before: Mapping[str, Mapping[str, Any]],
    after: Mapping[str, Mapping[str, Any]],
    node_claims: Mapping[str, list[str]],
) -> dict[str, Any]:
    status = _node_status(node_id, before, after)
    return {
        "node_id": node_id,
        "label": _plain_label(node_id, before, after),
        "label_source": _plain_label_source(node_id, before, after),
        "technical_label": _technical_label(node_id, before, after),
        "status": status,
        "status_label": _STATUS_LABELS.get(status, status),
        "claim_ids": sorted(node_claims.get(node_id, [])),
    }


def _build_view(
    side: str,
    nodes: Mapping[str, Mapping[str, Any]],
    edges: list[Mapping[str, Any]],
    impact_paths: list[Mapping[str, Any]],
    before: Mapping[str, Mapping[str, Any]],
    after: Mapping[str, Mapping[str, Any]],
    node_claims: Mapping[str, list[str]],
) -> dict[str, Any]:
    ordered_ids = sorted(
        nodes,
        key=lambda node_id: (
            _STATUS_ORDER.get(_node_status(node_id, before, after), 9),
            node_id,
        ),
    )
    visible = set(ordered_ids)
    paths = [
        {
            "changed_node_id": str(item["changed_node_id"]),
            "impacted_node_id": str(item["impacted_node_id"]),
            "relation": str(item["relation"]),
            "relation_label": "代码直接关联",
            "depth": item["depth"],
            "evidence_refs": list(item.get("evidence_refs", [])),
        }
        for item in impact_paths
        if item.get("changed_node_id") in visible
        and item.get("impacted_node_id") in visible
    ]
    return {
        "id": side,
        "nodes": [
            _view_node(node_id, before, after, node_claims) for node_id in ordered_ids
        ],
        "paths": sorted(
            paths,
            key=lambda item: (item["changed_node_id"], item["impacted_node_id"]),
        ),
        "edges": sorted(
            [dict(item) for item in edges],
            key=lambda item: str(item.get("edge_id", "")),
        ),
    }


def build_beginner_review_model(
    brief_value: Any,
    system_architecture_value: Any | None = None,
    task_evidence_value: Any | None = None,
) -> dict[str, Any]:
    brief = _require_mapping(brief_value, "validated brief")
    if brief.get("schema_version") != "change-passport.validated-brief.v1":
        raise ManifestError("validated brief schema is invalid")
    delta = _require_mapping(brief.get("architecture_delta"), "architecture_delta")
    if delta.get("schema_version") != DELTA_SCHEMA:
        raise ManifestError("architecture delta schema is invalid")
    system_architecture = None
    if system_architecture_value is not None:
        system_architecture = validate_system_architecture_snapshot(
            system_architecture_value
        )
        if (
            system_architecture.get("commit_identity")
            != delta.get("change_identity", {}).get("head_ref")
        ):
            raise ManifestError(
                "system architecture commit does not match architecture delta head"
            )
        overlay = _require_mapping(
            system_architecture.get("change_overlay"),
            "system_architecture.change_overlay",
        )
        for status, delta_key in (
            ("added", "added_node_ids"),
            ("modified", "modified_node_ids"),
            ("removed", "removed_node_ids"),
            ("impacted", "impacted_node_ids"),
        ):
            if _stable_unique(overlay.get(status, [])) != _stable_unique(
                delta.get(delta_key, [])
            ):
                raise ManifestError(
                    f"system architecture {status} overlay does not match delta"
                )
    claims = [
        _require_mapping(item, f"claims[{index}]")
        for index, item in enumerate(_require_list(brief.get("claims"), "claims"))
    ]
    claims = sorted(claims, key=lambda item: str(item.get("id", "")))
    claim_ids = [str(item["id"]) for item in claims]
    if len(claim_ids) != len(set(claim_ids)):
        raise ManifestError("validated brief contains duplicate claim IDs")

    bindings = architecture_evidence_bindings(delta)
    binding_index = {str(item["evidence_id"]): item for item in bindings}
    node_claims: defaultdict[str, list[str]] = defaultdict(list)
    for claim in claims:
        for evidence_id in claim.get("evidence_ids", []):
            for node_id in binding_index.get(str(evidence_id), {}).get("node_ids", []):
                node_claims[str(node_id)].append(str(claim["id"]))

    what = _summary_from_claims(
        item_id="summary.what",
        question="发生了什么",
        icon="变",
        claims=[
            item
            for item in claims
            if item.get("section") == "function"
            and item.get("scope") in {"user_behavior_change", "code_change"}
        ],
        binding_index=binding_index,
        fallback="现有证据不足，无法确认用户可感知的功能变化。",
    )
    why = _summary_from_claims(
        item_id="summary.why",
        question="为什么这样改",
        icon="因",
        claims=[item for item in claims if item.get("scope") == "task_intent"],
        binding_index=binding_index,
        fallback="这份报告没有拿到任务对话，暂时无法说明为什么这样改。",
    )
    task_context = _task_context_from_evidence(task_evidence_value)
    if why["claim_ids"]:
        task_context["state"] = "ready"
        task_context["state_label"] = "原因已有证据"
    elif task_context["state"] == "available":
        why["text"] = task_context["summary"]
        why["truth_state"] = "context"
        why["truth_label"] = "已有对话线索"
    why["task_context"] = task_context

    impact_paths = [
        _require_mapping(item, f"impact_paths[{index}]")
        for index, item in enumerate(
            _require_list(delta.get("impact_paths", []), "impact_paths")
        )
    ]
    impact_evidence_ids = [
        str(item["evidence_id"])
        for item in bindings
        if item["subject_type"] == "impact_path"
    ]
    impact_claim_ids = sorted(
        str(claim["id"])
        for claim in claims
        if set(claim.get("evidence_ids", [])) & set(impact_evidence_ids)
    )
    impact_node_ids = _stable_unique(
        node_id
        for item in impact_paths
        for node_id in (item["changed_node_id"], item["impacted_node_id"])
    )
    impact = {
        "id": "summary.impact",
        "question": "对谁有影响",
        "icon": "及",
        "text": (
            f"代码层面发现 {len(delta.get('impacted_node_ids', []))} 个直接关联位置；"
            "这不等于这些用户功能已经在运行时发生变化。"
            if impact_paths
            else "现有静态证据没有确认直接关联范围。"
        ),
        "truth_state": "inference" if impact_paths else "unknown",
        "truth_label": "有依据的推断" if impact_paths else "尚不清楚",
        "claim_ids": impact_claim_ids,
        "node_ids": impact_node_ids,
        "evidence_ids": impact_evidence_ids,
        "limitations": _stable_unique(
            [
                *delta.get("limitations", []),
                "静态代码关联不等于真实运行影响或用户影响",
            ]
        ),
        "next_check": "如需确认真实影响，请核对运行路径和独立测试收据。",
        "items": [],
    }
    attention = _summary_from_claims(
        item_id="summary.attention",
        question="需要注意什么",
        icon="注",
        claims=[item for item in claims if item.get("section") == "attention"],
        binding_index=binding_index,
        fallback="需要人工检查证据包中的缺口，当前没有可验证的进一步结论。",
    )
    summary = [what, why, impact, attention]

    before, after = _node_indexes(delta)
    all_node_ids = sorted(set(before) | set(after))
    node_details: dict[str, dict[str, Any]] = {}
    for node_id in all_node_ids:
        before_node = before.get(node_id)
        after_node = after.get(node_id)
        status = _node_status(node_id, before, after)
        related_paths = [
            item
            for item in impact_paths
            if node_id in {item.get("changed_node_id"), item.get("impacted_node_id")}
        ]
        source_node = after_node or before_node or {}
        before_text = _responsibility(before_node)
        after_text = _responsibility(after_node)
        if before_node is None:
            before_text = "这项职责在变更前不存在。"
        elif not before_text:
            before_text = "现有证据没有可靠说明它原来的业务职责。"
        if after_node is None:
            after_text = "这项职责在变更后已不存在。"
        elif not after_text:
            after_text = "现有证据没有可靠说明它现在的业务职责。"
        if status == "impacted":
            impact_text = (
                f"代码层面与 {len(related_paths)} 个变化职责有直接关联；"
                "静态证据未证明真实运行影响。"
            )
        elif related_paths:
            impact_text = (
                f"代码层面找到 {len(related_paths)} 条一跳直接关联；"
                "是否影响真实运行仍需另外验证。"
            )
        else:
            impact_text = "它用于补充理解上下文，现有证据没有确认直接运行影响。"
        node_details[node_id] = {
            "node_id": node_id,
            "label": _plain_label(node_id, before, after),
            "label_source": _plain_label_source(node_id, before, after),
            "technical_label": _technical_label(node_id, before, after),
            "status": status,
            "status_label": _STATUS_LABELS.get(status, status),
            "before": before_text,
            "after": after_text,
            "impact": impact_text,
            "evidence_boundary": "已确认对应代码位置和静态结构关系；具体引用见技术依据。",
            "unknown": "动态调用、配置注入和真实运行行为仍不在这次静态证明范围内。",
            "claim_ids": sorted(node_claims.get(node_id, [])),
            "evidence_refs": _stable_unique(source_node.get("evidence_refs", [])),
            "owned_paths": _stable_unique(source_node.get("owned_paths", [])),
            "interfaces": _stable_unique(source_node.get("interfaces", [])),
        }

    before_edges = [
        _require_mapping(item, f"before.edges[{index}]")
        for index, item in enumerate(_require_list(delta["before"]["edges"], "before.edges"))
    ]
    after_edges = [
        _require_mapping(item, f"after.edges[{index}]")
        for index, item in enumerate(_require_list(delta["after"]["edges"], "after.edges"))
    ]
    diff_nodes = {
        node_id: node
        for node_id, node in {**before, **after}.items()
        if _node_status(node_id, before, after) != "unchanged_context"
    }
    edge_index = {
        str(item["edge_id"]): item for item in [*before_edges, *after_edges]
    }
    diff_edges = [
        item
        for item in edge_index.values()
        if item.get("source_node_id") in diff_nodes
        and item.get("target_node_id") in diff_nodes
    ]
    views = {
        "before": _build_view(
            "before", before, before_edges, impact_paths, before, after, node_claims
        ),
        "after": _build_view(
            "after", after, after_edges, impact_paths, before, after, node_claims
        ),
        "diff": _build_view(
            "diff", diff_nodes, diff_edges, impact_paths, before, after, node_claims
        ),
    }

    omissions = _require_mapping(delta.get("display_omissions", {}), "display_omissions")
    omitted_impacted = _stable_unique(omissions.get("omitted_impacted_node_ids", []))
    omitted_context = _stable_unique(omissions.get("omitted_context_node_ids", []))
    branch_groups = []
    if omitted_impacted:
        branch_groups.append(
            {
                "id": "omitted.impacted",
                "label": "代码直接关联",
                "count": len(omitted_impacted),
                "node_ids": omitted_impacted,
                "limitation": "这里只证明静态代码关联，不证明真实运行影响。",
            }
        )
    if omitted_context:
        branch_groups.append(
            {
                "id": "omitted.context",
                "label": "未变化上下文",
                "count": len(omitted_context),
                "node_ids": omitted_context,
                "limitation": "这些位置用于帮助理解依赖上下文，没有被标记为本次改变。",
            }
        )

    test_verified = any(
        item.get("scope") == "test_status"
        and item.get("status") == "accepted"
        and item.get("claim_type") == "verified_fact"
        for item in claims
    )
    unknown_count = sum(item["truth_state"] == "unknown" for item in summary)
    changed_node_ids = _stable_unique(
        [
            *delta.get("added_node_ids", []),
            *delta.get("removed_node_ids", []),
            *delta.get("modified_node_ids", []),
        ]
    )
    default_node_id = changed_node_ids[0] if changed_node_ids else (all_node_ids[0] if all_node_ids else None)
    all_edge_ids = _stable_unique(
        str(item.get("edge_id", "")) for item in [*before_edges, *after_edges]
    )
    omitted_ids = _stable_unique(omissions.get("omitted_node_ids", []))
    model: dict[str, Any] = {
        "schema_version": REVIEW_SCHEMA,
        "sample_id": str(brief["sample_id"]),
        "brief_identity": str(brief["brief_identity"]),
        "change": dict(_require_mapping(brief.get("change"), "change")),
        "change_identity": dict(delta["change_identity"]),
        "baseline_validation": dict(delta["baseline_validation"]),
        "header": {
            "eyebrow": "本地只读变化说明",
            "title": "这次 AI 改了什么？",
            "subtitle": (
                what["items"][0]["text"] if what["items"] else what["text"]
            ),
            "scope_note": "这是一次代码变化说明，不代表代码已经独立验收、合并或发布。",
            "statuses": [
                {"tone": "good", "label": "代码变化已确认"},
                {
                    "tone": "good" if test_verified else "warn",
                    "label": "有独立测试证据" if test_verified else "测试证据不完整",
                },
                {
                    "tone": "warn" if unknown_count else "good",
                    "label": f"仍有 {unknown_count} 项需要确认" if unknown_count else "四问均有证据",
                },
                *(
                    [
                        {
                            "tone": "info",
                            "label": (
                                f"整体结构 {system_architecture['coverage']['group_count']} 区"
                            ),
                        }
                    ]
                    if system_architecture is not None
                    else []
                ),
            ],
        },
        "summary": summary,
        "views": views,
        "node_details": node_details,
        "default_node_id": default_node_id,
        "branch_groups": branch_groups,
        "claims": [dict(item) for item in claims],
        "display_omissions": dict(omissions),
        "limitations": _stable_unique(
            [*delta.get("limitations", []), *delta.get("unknowns", [])]
        ),
        "system_architecture": system_architecture,
        "validation": {
            "source_claim_ids": claim_ids,
            "source_node_ids": all_node_ids,
            "source_edge_ids": all_edge_ids,
            "source_omitted_node_ids": omitted_ids,
            "claim_count": len(claim_ids),
            "displayed_node_count": len(all_node_ids),
            "edge_count": len(all_edge_ids),
            "omitted_node_count": len(omitted_ids),
            "system_snapshot_identity": (
                system_architecture["snapshot_identity"]
                if system_architecture is not None
                else None
            ),
            "system_node_count": (
                system_architecture["coverage"]["node_count"]
                if system_architecture is not None
                else 0
            ),
            "system_edge_count": (
                system_architecture["coverage"]["edge_count"]
                if system_architecture is not None
                else 0
            ),
            "system_group_count": (
                system_architecture["coverage"]["group_count"]
                if system_architecture is not None
                else 0
            ),
        },
    }
    identity_source = dict(model)
    model["review_identity"] = sha256_bytes(canonical_json_bytes(identity_source))
    return model


def validate_beginner_review_model(value: Any) -> dict[str, Any]:
    model = dict(_require_mapping(value, "beginner review"))
    if model.get("schema_version") != REVIEW_SCHEMA:
        raise ManifestError("beginner review schema is invalid")
    claimed_identity = model.pop("review_identity", None)
    actual_identity = sha256_bytes(canonical_json_bytes(model))
    if claimed_identity != actual_identity:
        raise ManifestError("beginner review identity does not match its content")
    model["review_identity"] = claimed_identity
    return model
