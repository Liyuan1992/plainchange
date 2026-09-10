from __future__ import annotations

from typing import Any, Mapping

from .models import ManifestError

ANNOTATION_SCHEMA = "change-passport.annotation.v1"
LABELS = {
    "supported",
    "unsupported",
    "wrong_authority",
    "leaked_ground_truth",
    "not_applicable",
}
SEVERITIES = {"low", "medium", "high"}


def build_annotation_template(brief: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": ANNOTATION_SCHEMA,
        "sample_id": brief["sample_id"],
        "brief_identity": brief["brief_identity"],
        "claims": [
            {
                "claim_id": item["id"],
                "label": None,
                "severity": "medium",
                "notes": "",
            }
            for item in brief["claims"]
            if not item["id"].startswith("system.missing.")
        ],
        "ground_truth": [
            {
                "ground_truth_id": "replace-with-hidden-ground-truth-id",
                "critical": True,
                "matched_claim_ids": [],
                "notes": "",
            }
        ],
    }


def score_annotations(brief: Mapping[str, Any], annotation: Any) -> dict[str, Any]:
    if not isinstance(annotation, Mapping):
        raise ManifestError("annotation must be an object")
    if annotation.get("schema_version") != ANNOTATION_SCHEMA:
        raise ManifestError(f"annotation schema must be {ANNOTATION_SCHEMA}")
    if annotation.get("sample_id") != brief.get("sample_id"):
        raise ManifestError("annotation sample_id does not match the brief")
    if annotation.get("brief_identity") != brief.get("brief_identity"):
        raise ManifestError("annotation brief_identity does not match the frozen brief")

    brief_claims = {item["id"]: item for item in brief.get("claims", [])}
    rows = annotation.get("claims")
    if not isinstance(rows, list):
        raise ManifestError("annotation claims must be an array")
    seen: set[str] = set()
    normalized: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            raise ManifestError(f"annotation claims[{index}] must be an object")
        claim_id = row.get("claim_id")
        label = row.get("label")
        severity = row.get("severity")
        if claim_id not in brief_claims or claim_id in seen:
            raise ManifestError(f"annotation claim_id is unknown or duplicated: {claim_id}")
        if label not in LABELS:
            raise ManifestError(f"annotation label is invalid for {claim_id}")
        if severity not in SEVERITIES:
            raise ManifestError(f"annotation severity is invalid for {claim_id}")
        seen.add(claim_id)
        normalized.append(
            {
                "claim": brief_claims[claim_id],
                "label": label,
                "severity": severity,
            }
        )

    high_fact_rows = [
        item
        for item in normalized
        if item["claim"]["importance"] == "high"
        and item["claim"]["original_claim_type"] != "unknown"
        and item["label"] != "not_applicable"
    ]
    supported = sum(item["label"] == "supported" for item in high_fact_rows)
    precision_denominator = len(high_fact_rows)
    precision = None if precision_denominator == 0 else supported / precision_denominator

    ground_truth = annotation.get("ground_truth")
    if not isinstance(ground_truth, list):
        raise ManifestError("annotation ground_truth must be an array")
    critical_total = 0
    critical_matched = 0
    for index, item in enumerate(ground_truth):
        if not isinstance(item, Mapping):
            raise ManifestError(f"ground_truth[{index}] must be an object")
        ground_truth_id = item.get("ground_truth_id")
        if not isinstance(ground_truth_id, str) or not ground_truth_id.strip():
            raise ManifestError(f"ground_truth[{index}].ground_truth_id is required")
        if not isinstance(item.get("critical"), bool):
            raise ManifestError(f"ground_truth[{index}].critical must be boolean")
        matches = item.get("matched_claim_ids")
        if not isinstance(matches, list) or any(value not in brief_claims for value in matches):
            raise ManifestError(f"ground_truth[{index}].matched_claim_ids is invalid")
        if item["critical"]:
            critical_total += 1
            if matches:
                critical_matched += 1
    critical_recall = None if critical_total == 0 else critical_matched / critical_total

    severe_unsupported = sum(
        item["label"] == "unsupported" and item["severity"] == "high"
        for item in normalized
    )
    authority_errors = sum(item["label"] == "wrong_authority" for item in normalized)
    leakage = sum(item["label"] == "leaked_ground_truth" for item in normalized)
    if precision is None or critical_recall is None:
        outcome = "inconclusive"
    elif (
        precision >= 0.95
        and critical_recall >= 0.80
        and severe_unsupported == 0
        and authority_errors == 0
        and leakage == 0
    ):
        outcome = "pass"
    else:
        outcome = "fail"

    return {
        "schema_version": "change-passport.score.v1",
        "sample_id": brief["sample_id"],
        "brief_identity": brief["brief_identity"],
        "outcome": outcome,
        "metrics": {
            "high_importance_fact_precision": precision,
            "high_importance_fact_supported": supported,
            "high_importance_fact_evaluated": precision_denominator,
            "critical_ground_truth_recall": critical_recall,
            "critical_ground_truth_matched": critical_matched,
            "critical_ground_truth_total": critical_total,
            "severe_unsupported_count": severe_unsupported,
            "authority_error_count": authority_errors,
            "leakage_count": leakage,
        },
    }
