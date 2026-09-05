from __future__ import annotations

import pytest

from change_passport.models import ManifestError
from change_passport.scoring import build_annotation_template, score_annotations


def _brief():
    return {
        "schema_version": "change-passport.validated-brief.v1",
        "sample_id": "sample.one",
        "brief_identity": "brief-hash",
        "claims": [
            {
                "id": "function.one",
                "importance": "high",
                "original_claim_type": "verified_fact",
            },
            {
                "id": "attention.one",
                "importance": "medium",
                "original_claim_type": "inference",
            },
        ],
    }


def test_score_passes_when_fidelity_gates_are_met():
    brief = _brief()
    annotation = build_annotation_template(brief)
    annotation["claims"] = [
        {
            "claim_id": "function.one",
            "label": "supported",
            "severity": "high",
            "notes": "",
        },
        {
            "claim_id": "attention.one",
            "label": "supported",
            "severity": "medium",
            "notes": "",
        },
    ]
    annotation["ground_truth"] = [
        {
            "ground_truth_id": "gt.one",
            "critical": True,
            "matched_claim_ids": ["function.one"],
            "notes": "",
        }
    ]

    score = score_annotations(brief, annotation)

    assert score["outcome"] == "pass"
    assert score["metrics"]["high_importance_fact_precision"] == 1.0
    assert score["metrics"]["critical_ground_truth_recall"] == 1.0
    assert score["metrics"]["leakage_count"] == 0


def test_score_fails_on_authority_error_and_leakage():
    brief = _brief()
    annotation = {
        "schema_version": "change-passport.annotation.v1",
        "sample_id": "sample.one",
        "brief_identity": "brief-hash",
        "claims": [
            {
                "claim_id": "function.one",
                "label": "wrong_authority",
                "severity": "high",
            },
            {
                "claim_id": "attention.one",
                "label": "leaked_ground_truth",
                "severity": "high",
            },
        ],
        "ground_truth": [
            {
                "ground_truth_id": "gt.one",
                "critical": True,
                "matched_claim_ids": [],
            }
        ],
    }

    score = score_annotations(brief, annotation)

    assert score["outcome"] == "fail"
    assert score["metrics"]["authority_error_count"] == 1
    assert score["metrics"]["leakage_count"] == 1


def test_annotation_must_match_frozen_brief():
    brief = _brief()
    annotation = build_annotation_template(brief)
    annotation["brief_identity"] = "different"

    with pytest.raises(ManifestError, match="does not match"):
        score_annotations(brief, annotation)
