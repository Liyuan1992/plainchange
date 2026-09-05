from __future__ import annotations

import copy
import re
from collections import Counter
from typing import Any, Mapping

from .architecture import render_mermaid
from .generator_contract import (
    CLAIM_TYPES,
    CONFIDENCE_LEVELS,
    IMPORTANCE_LEVELS,
    RAW_BRIEF_SCHEMA,
    SCOPES,
    SECTIONS,
    validate_packet,
)
from .models import ManifestError, canonical_json_bytes, sha256_bytes

CLAIM_ID_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9._-]{0,79}$")

REQUIRED_AUTHORITIES: dict[str, set[str]] = {
    "user_behavior_change": {"original_task", "git_fact"},
    "code_change": {"git_fact"},
    "task_intent": {"original_task"},
    "test_status": {"actual_test_receipt"},
    "architecture_change": {"git_fact"},
    "history_relation": {"approved_history", "git_fact"},
    "attention": set(),
}

ALLOWED_SCOPES_BY_SECTION: dict[str, set[str]] = {
    "function": {"user_behavior_change", "code_change", "task_intent"},
    "architecture": {"architecture_change", "code_change"},
    "history": {"history_relation"},
    "attention": set(SCOPES),
}

UNKNOWN_TEXT: dict[str, str] = {
    "function": "现有证据不足，无法确认用户可感知的功能变化。",
    "architecture": "现有证据不足，无法确认架构职责或依赖关系的含义。",
    "history": "没有足够证据确认本次变化与已批准历史记录的关系。",
    "attention": "需要人工检查证据包中的缺口，当前没有可验证的进一步结论。",
}


def _short_string(value: Any, label: str, *, max_length: int = 1_500) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ManifestError(f"{label} must be a non-empty string")
    result = value.strip()
    if len(result) > max_length:
        raise ManifestError(f"{label} exceeds {max_length} characters")
    return result


def _string_list(value: Any, label: str, *, max_items: int = 16) -> list[str]:
    if not isinstance(value, list) or len(value) > max_items:
        raise ManifestError(f"{label} must be an array with at most {max_items} items")
    result: list[str] = []
    for index, item in enumerate(value):
        result.append(_short_string(item, f"{label}[{index}]", max_length=300))
    return result


def _generic_unknown(section: str, reason: str) -> str:
    return f"{UNKNOWN_TEXT[section]}（校验原因：{reason}）"


def validate_raw_brief(packet_value: Any, raw_value: Any) -> dict[str, Any]:
    packet = validate_packet(packet_value)
    if not isinstance(raw_value, Mapping):
        raise ManifestError("raw brief must be an object")
    raw = copy.deepcopy(dict(raw_value))
    if raw.get("schema_version") != RAW_BRIEF_SCHEMA:
        raise ManifestError(f"raw brief schema must be {RAW_BRIEF_SCHEMA}")
    claims_raw = raw.get("claims")
    if not isinstance(claims_raw, list):
        raise ManifestError("raw brief claims must be an array")
    if len(claims_raw) > 40:
        raise ManifestError("raw brief exceeds the 40-claim safety limit")

    evidence_index = {item["id"]: item for item in packet["evidence"]}
    seen_ids: set[str] = set()
    section_counts: Counter[str] = Counter()
    claims: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []

    for index, item in enumerate(claims_raw):
        label = f"claims[{index}]"
        if not isinstance(item, Mapping):
            raise ManifestError(f"{label} must be an object")
        required_keys = {
            "id",
            "section",
            "scope",
            "text",
            "claim_type",
            "confidence",
            "importance",
            "evidence_ids",
            "limitations",
            "next_check",
        }
        if set(item) != required_keys:
            missing = sorted(required_keys - set(item))
            extra = sorted(set(item) - required_keys)
            raise ManifestError(f"{label} fields mismatch; missing={missing}, extra={extra}")

        claim_id = _short_string(item["id"], f"{label}.id", max_length=80)
        if not CLAIM_ID_PATTERN.fullmatch(claim_id) or claim_id in seen_ids:
            raise ManifestError(f"{label}.id is invalid or duplicated")
        seen_ids.add(claim_id)
        section = _short_string(item["section"], f"{label}.section", max_length=20)
        scope = _short_string(item["scope"], f"{label}.scope", max_length=40)
        claim_type = _short_string(item["claim_type"], f"{label}.claim_type", max_length=30)
        confidence = _short_string(item["confidence"], f"{label}.confidence", max_length=20)
        importance = _short_string(item["importance"], f"{label}.importance", max_length=20)
        if section not in SECTIONS:
            raise ManifestError(f"{label}.section is invalid")
        if scope not in SCOPES:
            raise ManifestError(f"{label}.scope is invalid")
        if claim_type not in CLAIM_TYPES:
            raise ManifestError(f"{label}.claim_type is invalid")
        if confidence not in CONFIDENCE_LEVELS:
            raise ManifestError(f"{label}.confidence is invalid")
        if importance not in IMPORTANCE_LEVELS:
            raise ManifestError(f"{label}.importance is invalid")
        text = _short_string(item["text"], f"{label}.text")
        evidence_ids = _string_list(item["evidence_ids"], f"{label}.evidence_ids")
        limitations = _string_list(item["limitations"], f"{label}.limitations")
        next_check_value = item["next_check"]
        next_check = None
        if next_check_value is not None:
            next_check = _short_string(next_check_value, f"{label}.next_check", max_length=500)

        reasons: list[str] = []
        if scope not in ALLOWED_SCOPES_BY_SECTION[section]:
            reasons.append(f"scope={scope} 不能用于 section={section}")
        unknown_ids = [value for value in evidence_ids if value not in evidence_index]
        if unknown_ids:
            reasons.append("引用了不存在的证据 ID: " + ", ".join(unknown_ids))
        known_evidence_ids = [value for value in evidence_ids if value in evidence_index]
        authorities = {evidence_index[value]["authority"] for value in known_evidence_ids}
        missing_authorities = REQUIRED_AUTHORITIES[scope] - authorities
        if scope == "architecture_change" and "architecture_fact" in authorities:
            missing_authorities = set()
        if (
            scope == "architecture_change"
            and claim_type == "verified_fact"
            and "architecture_fact" not in authorities
        ):
            reasons.append("verified architecture_change 缺少 architecture_fact")
        if claim_type != "unknown" and not known_evidence_ids:
            reasons.append("非 unknown 结论没有有效证据引用")
        if claim_type != "unknown" and missing_authorities:
            reasons.append("缺少权威类型: " + ", ".join(sorted(missing_authorities)))
        if section_counts[section] >= 3:
            rejected.append(
                {
                    "id": claim_id,
                    "section": section,
                    "original_text": text,
                    "reasons": ["超过每区三条的硬限制"],
                }
            )
            continue

        status = "accepted"
        validated_type = claim_type
        validated_confidence = confidence
        rendered_text = text
        if unknown_ids:
            status = "rejected"
            validated_type = "unknown"
            validated_confidence = "low"
            rendered_text = _generic_unknown(section, reasons[0])
        elif claim_type == "unknown":
            status = "accepted"
            validated_confidence = "low"
            rendered_text = UNKNOWN_TEXT[section]
        elif reasons:
            status = "downgraded"
            validated_type = "unknown"
            validated_confidence = "low"
            rendered_text = _generic_unknown(section, "；".join(reasons))

        section_counts[section] += 1
        claims.append(
            {
                "id": claim_id,
                "section": section,
                "scope": scope,
                "status": status,
                "original_text": text,
                "text": rendered_text,
                "claim_type": validated_type,
                "original_claim_type": claim_type,
                "confidence": validated_confidence,
                "importance": importance,
                "evidence_ids": known_evidence_ids,
                "limitations": limitations + reasons,
                "next_check": next_check,
            }
        )

    for section in SECTIONS:
        if section_counts[section] == 0:
            claims.append(
                {
                    "id": f"system.missing.{section}",
                    "section": section,
                    "scope": "attention" if section == "attention" else "code_change",
                    "status": "downgraded",
                    "original_text": "",
                    "text": UNKNOWN_TEXT[section],
                    "claim_type": "unknown",
                    "original_claim_type": "unknown",
                    "confidence": "low",
                    "importance": "high",
                    "evidence_ids": [],
                    "limitations": ["模型未返回该区域的结论"],
                    "next_check": None,
                }
            )

    raw_hash = sha256_bytes(canonical_json_bytes(raw))
    brief_identity = sha256_bytes(
        f"{packet['packet_sha256']}:{raw_hash}".encode("ascii")
    )
    result = {
        "schema_version": "change-passport.validated-brief.v1",
        "sample_id": packet["sample_id"],
        "brief_identity": brief_identity,
        "packet_sha256": packet["packet_sha256"],
        "raw_brief_sha256": raw_hash,
        "change": packet["change"],
        "claims": claims,
        "rejected_claims": rejected,
        "validation_summary": {
            "accepted": sum(item["status"] == "accepted" for item in claims),
            "downgraded": sum(item["status"] == "downgraded" for item in claims),
            "rejected": sum(item["status"] == "rejected" for item in claims) + len(rejected),
        },
    }
    if packet.get("architecture_delta") is not None:
        result["architecture_delta"] = copy.deepcopy(packet["architecture_delta"])
    return result


def render_markdown(brief: Mapping[str, Any]) -> str:
    titles = {
        "function": "FUNCTION｜功能",
        "architecture": "ARCHITECTURE｜架构",
        "history": "HISTORY｜历史",
        "attention": "ATTENTION｜注意事项",
    }
    change = brief["change"]
    lines = [
        f"# Change Brief — {brief['sample_id']}",
        "",
        f"- Base: `{change['base_commit']}`",
        f"- Head: `{change['head_commit']}`",
        f"- 变化规模：{change['changed_files']} 个文件，+{change['added_lines']} / -{change['deleted_lines']}",
        f"- Patch SHA-256: `{change['patch_sha256']}`",
        f"- Brief identity: `{brief['brief_identity']}`",
        "- 边界：本说明只呈现通过确定性校验的模型结论；接受本说明不等于代码已验收、合并或发布。",
        "",
    ]
    architecture_delta = brief.get("architecture_delta")
    if isinstance(architecture_delta, Mapping):
        stats = architecture_delta["analysis_stats"]
        lines.extend(
            [
                "## ARCHITECTURE DELTA MAP｜架构变化主视图",
                "",
                "```mermaid",
                render_mermaid(architecture_delta).rstrip(),
                "```",
                "",
                f"- 基线状态：`{architecture_delta['baseline_validation']['status']}`",
                f"- 节点变化：新增 {len(architecture_delta['added_node_ids'])}，删除 {len(architecture_delta['removed_node_ids'])}，修改 {len(architecture_delta['modified_node_ids'])}，直接影响 {len(architecture_delta['impacted_node_ids'])}",
                f"- 增量统计：复用 {stats['reused_nodes']} 个节点，失效 {stats['invalidated_nodes']} 个节点，head 实际解析 {stats['parsed_head_files']} 个文件",
                f"- 展示预算：显示 {stats['displayed_nodes']} 个节点，折叠 {stats.get('omitted_nodes', 0)} 个一跳/上下文节点；完整 ID 保留在 JSON。",
            ]
        )
        if architecture_delta.get("unknowns"):
            lines.append("- 未知项：" + "；".join(architecture_delta["unknowns"][:8]))
        lines.append("")
    claims = brief["claims"]
    labels = {"verified_fact": "已验证事实", "inference": "推断", "unknown": "未知"}
    for section in SECTIONS:
        lines.extend([f"## {titles[section]}", ""])
        for item in claims:
            if item["section"] != section:
                continue
            lines.append(
                f"- **{labels[item['claim_type']]} · {item['status']}**：{item['text']}"
            )
            if item["evidence_ids"]:
                refs = ", ".join(f"`{value}`" for value in item["evidence_ids"])
                lines.append(f"  - 证据：{refs}")
            if item["limitations"]:
                lines.append("  - 限制：" + "；".join(item["limitations"]))
            if item["next_check"]:
                lines.append(f"  - 建议的最小检查：{item['next_check']}")
        lines.append("")
    summary = brief["validation_summary"]
    lines.extend(
        [
            "## 校验摘要",
            "",
            f"- 接受：{summary['accepted']}",
            f"- 降级：{summary['downgraded']}",
            f"- 拒绝：{summary['rejected']}",
            "",
        ]
    )
    return "\n".join(lines)
