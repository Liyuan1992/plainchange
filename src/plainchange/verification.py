from __future__ import annotations

import copy
import json
from typing import Any, Mapping, Sequence

from .models import ID_PATTERN, ManifestError, canonical_json_bytes, sha256_bytes

VERIFICATION_RECEIPT_SCHEMA = "plainchange.verification-receipt.v1"
CHECK_CATEGORIES = {"tests", "build", "browser", "integration", "security", "runtime"}
CHECK_STATUSES = {"passed", "failed"}
PRODUCER_KINDS = {"agent", "ci", "local_tool", "external_tool"}

PROJECT_VERIFICATION_RESPONSIBILITY = {
    "zh-CN": "项目验证流程",
    "en": "Project verification workflow",
}
OWNER_RESPONSIBILITY = {
    "zh-CN": "产品负责人或真实使用者",
    "en": "Product owner or actual user",
}


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ManifestError(f"{label} must be an object")
    return value


def _text(value: Any, label: str, maximum: int = 500) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ManifestError(f"{label} must be a non-empty string")
    result = value.strip()
    if result != value:
        raise ManifestError(f"{label} must not contain surrounding whitespace")
    if len(result) > maximum:
        raise ManifestError(f"{label} exceeds {maximum} characters")
    return result


def _localized(value: Any, label: str, maximum: int = 500) -> dict[str, str]:
    item = _mapping(value, label)
    if set(item) != {"zh-CN", "en"}:
        raise ManifestError(f"{label} must contain exactly zh-CN and en")
    return {
        "zh-CN": _text(item.get("zh-CN"), f"{label}.zh-CN", maximum),
        "en": _text(item.get("en"), f"{label}.en", maximum),
    }


def validate_verification_receipt(
    value: Any, *, expected_base: str, expected_head: str
) -> dict[str, Any]:
    receipt = copy.deepcopy(dict(_mapping(value, "verification receipt")))
    required = {
        "schema_version",
        "change_identity",
        "producer",
        "checks",
        "receipt_sha256",
    }
    if set(receipt) != required or receipt.get("schema_version") != VERIFICATION_RECEIPT_SCHEMA:
        raise ManifestError("verification receipt fields or schema are invalid")

    claimed_hash = receipt.pop("receipt_sha256", None)
    actual_hash = sha256_bytes(canonical_json_bytes(receipt))
    if claimed_hash != actual_hash:
        raise ManifestError("verification receipt hash does not match its content")

    identity = _mapping(receipt.get("change_identity"), "verification change_identity")
    if set(identity) != {"base_commit", "head_commit"}:
        raise ManifestError("verification change_identity fields are invalid")
    if identity.get("base_commit") != expected_base or identity.get("head_commit") != expected_head:
        raise ManifestError("verification receipt does not match the analyzed change")

    producer = _mapping(receipt.get("producer"), "verification producer")
    if set(producer) != {"kind", "name"}:
        raise ManifestError("verification producer fields are invalid")
    if producer.get("kind") not in PRODUCER_KINDS:
        raise ManifestError("verification producer kind is invalid")
    _text(producer.get("name"), "verification producer name", 120)

    checks = receipt.get("checks")
    if not isinstance(checks, list) or not 1 <= len(checks) <= 16:
        raise ManifestError("verification checks must contain one to sixteen items")
    seen: set[str] = set()
    normalized_checks: list[dict[str, Any]] = []
    for index, raw in enumerate(checks):
        check = _mapping(raw, f"verification checks[{index}]")
        fields = {
            "id",
            "category",
            "status",
            "label",
            "summary",
            "scope",
            "limitations",
            "observed_at",
        }
        if set(check) != fields:
            raise ManifestError(f"verification checks[{index}] fields are invalid")
        check_id = _text(check.get("id"), f"verification checks[{index}].id", 80)
        if not ID_PATTERN.fullmatch(check_id) or check_id in seen:
            raise ManifestError(f"verification checks[{index}].id is invalid or duplicated")
        seen.add(check_id)
        category = _text(check.get("category"), f"verification checks[{index}].category", 20)
        status = _text(check.get("status"), f"verification checks[{index}].status", 20)
        if category not in CHECK_CATEGORIES or status not in CHECK_STATUSES:
            raise ManifestError(f"verification checks[{index}] category or status is invalid")
        limitations = check.get("limitations")
        if not isinstance(limitations, list) or len(limitations) > 8:
            raise ManifestError(f"verification checks[{index}].limitations is invalid")
        observed_at = check.get("observed_at")
        if observed_at is not None:
            observed_at = _text(observed_at, f"verification checks[{index}].observed_at", 80)
        normalized_checks.append(
            {
                "id": check_id,
                "category": category,
                "status": status,
                "label": _localized(check.get("label"), f"verification checks[{index}].label", 120),
                "summary": _localized(check.get("summary"), f"verification checks[{index}].summary", 360),
                "scope": _localized(check.get("scope"), f"verification checks[{index}].scope", 240),
                "limitations": [
                    _localized(item, f"verification checks[{index}].limitations[{item_index}]", 300)
                    for item_index, item in enumerate(limitations)
                ],
                "observed_at": observed_at,
            }
        )
    receipt["checks"] = normalized_checks
    receipt["receipt_sha256"] = claimed_hash
    return receipt


def parse_verification_receipt(
    text: str, *, expected_base: str, expected_head: str
) -> dict[str, Any] | None:
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        return None
    if not isinstance(value, Mapping) or value.get("schema_version") != VERIFICATION_RECEIPT_SCHEMA:
        return None
    return validate_verification_receipt(
        value, expected_base=expected_base, expected_head=expected_head
    )


def build_verification_control(
    receipts: Sequence[Mapping[str, Any]], claims: Sequence[Mapping[str, Any]]
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    seen: set[str] = set()
    for receipt in receipts:
        for raw in receipt.get("checks", []):
            check = copy.deepcopy(dict(raw))
            if check["id"] in seen:
                continue
            seen.add(check["id"])
            check["producer"] = dict(receipt["producer"])
            check["receipt_sha256"] = receipt["receipt_sha256"]
            checks.append(check)

    gaps: list[dict[str, Any]] = []
    has_receipts = bool(receipts)
    seen_next_checks: set[str] = set()
    for claim in claims:
        if not claim.get("next_check"):
            continue
        # Only an explicit attention claim is a remaining owner-facing gap.
        # A test-status claim downgraded in another section may still describe
        # a successfully completed receipt and must not be reclassified as work.
        if claim.get("section") != "attention":
            continue
        claim_type = str(claim.get("claim_type") or "")
        reason = next(
            (
                str(item)
                for item in claim.get("limitations", [])
                if isinstance(item, str) and item.strip()
            ),
            "现有证据没有包含完成这项判断所需的运行或验收结果。",
        )
        combined_gap_text = " ".join(
            [
                str(claim.get("text") or ""),
                str(claim.get("original_text") or ""),
                reason,
                str(claim.get("next_check") or ""),
            ]
        ).lower()
        if has_receipts and (
            "没有 actual_test_receipt" in combined_gap_text
            or "缺少 actual_test_receipt" in combined_gap_text
            or "no actual_test_receipt" in combined_gap_text
        ):
            # A model-authored unknown must not override a fixed, hash-bound
            # verification receipt. Receipt limitations remain visible on the
            # completed checks, so removing this contradiction loses no boundary.
            continue
        how = str(claim["next_check"]).strip()
        if how in seen_next_checks:
            continue
        seen_next_checks.add(how)
        original = str(claim.get("original_text") or "").strip()
        if claim_type == "unknown":
            label = original or str(claim.get("text") or "尚有一项结果没有验证")
        else:
            label = f"仍需完成：{how}"
            reason = next(
                (
                    str(item)
                    for item in claim.get("limitations", [])
                    if isinstance(item, str) and item.strip()
                ),
                "已完成的证据只覆盖其明确记录的范围，不能替代这项验收。",
            )
        if len(label) > 140:
            label = label[:137].rstrip() + "…"
        responsibility = copy.deepcopy(
            OWNER_RESPONSIBILITY
            if claim.get("scope") == "user_behavior_change" or claim_type != "unknown"
            else PROJECT_VERIFICATION_RESPONSIBILITY
        )
        gaps.append(
            {
                "id": str(claim.get("id")),
                "label": label,
                "reason": reason,
                "how": how,
                "responsibility": responsibility,
            }
        )
        if len(gaps) == 4:
            break

    passed = [item for item in checks if item["status"] == "passed"]
    failed = [item for item in checks if item["status"] == "failed"]
    if failed:
        decision = {
            "tone": "stop",
            "title": {
                "zh-CN": f"先暂停：有 {len(failed)} 项检查没有通过",
                "en": f"Pause first: {len(failed)} check{'s' if len(failed) != 1 else ''} failed",
            },
            "text": {
                "zh-CN": "先处理下面的失败项，再决定是否接受这次变化。失败检查不会被当作已经通过。",
                "en": "Resolve the failed checks below before accepting this change. Failed checks remain failed until new evidence is supplied.",
            },
            "items": [
                {
                    "id": item["id"],
                    "label": copy.deepcopy(item["label"]),
                    "responsibility": copy.deepcopy(PROJECT_VERIFICATION_RESPONSIBILITY),
                }
                for item in failed
            ],
        }
    elif gaps:
        decision = {
            "tone": "decide",
            "title": {
                "zh-CN": f"是否在完成剩余 {len(gaps)} 项验证前接受这次变化？",
                "en": f"Accept this change before the remaining {len(gaps)} verification item{'s are' if len(gaps) != 1 else ' is'} complete?",
            },
            "text": {
                "zh-CN": "如果现在接受，下面列出的事项仍保持“未验证”，不会被当作已经通过。你不需要亲自执行工程命令；只需决定是否接受这个边界。",
                "en": "If you accept now, the items below remain unverified and will not be treated as passed. You do not need to run engineering commands; decide only whether this boundary is acceptable.",
            },
            "items": [
                {
                    "id": item["id"],
                    "label": copy.deepcopy(item["label"]),
                    "responsibility": copy.deepcopy(item["responsibility"]),
                }
                for item in gaps
            ],
        }
    else:
        decision = {
            "tone": "ready",
            "title": {
                "zh-CN": "目前没有需要你补做的工程检查",
                "en": "No engineering checks are waiting on you",
            },
            "text": {
                "zh-CN": "已提供的验证收据没有留下待处理检查；这仍不等于生产发布批准。",
                "en": "The supplied verification receipts leave no pending checks. This is still not approval for a production release.",
            },
            "items": [],
        }
    return {
        "schema_version": "plainchange.verification-control.v1",
        "passed_checks": passed,
        "failed_checks": failed,
        "gaps": gaps,
        "decision": decision,
        "receipt_count": len(receipts),
        "boundary": {
            "zh-CN": "验证收据只证明所列范围；测试或构建通过不等于生产运行、长期兼容或用户影响已经验证。",
            "en": "Verification receipts prove only their stated scope. Passing tests or builds does not prove production behavior, long-term compatibility, or user impact.",
        },
    }
