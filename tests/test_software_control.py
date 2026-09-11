from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from plainchange.models import ManifestError, canonical_json_bytes, sha256_bytes
from plainchange.software_control import validate_software_control


ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "docs" / "product" / "samples" / "change-passport-self-688fc5f.software-control.json"


def software_control_sample() -> dict:
    return json.loads(SAMPLE.read_text(encoding="utf-8"))


def resign(value: dict) -> dict:
    value = copy.deepcopy(value)
    value.pop("control_identity", None)
    value["control_identity"] = sha256_bytes(canonical_json_bytes(value))
    return value


def test_validates_canonical_owner_contract():
    value = software_control_sample()

    validated = validate_software_control(value)

    assert validated == value
    assert validated is not value
    assert len(validated["working_map"]["nodes"]) == 8
    assert len(validated["working_map"]["overview_map"]["nodes"]) == 4
    assert validated["first_screen_summary"]["internal_concept_label"] == "变化识别规则"


def test_rejects_tampered_identity():
    value = software_control_sample()
    value["first_screen_summary"]["headline"] = "tampered"

    with pytest.raises(ManifestError, match="canonical identity"):
        validate_software_control(value)


def test_rejects_flow_to_missing_node_even_when_resigned():
    value = software_control_sample()
    value["working_map"]["flows"][0]["to"] = "missing"

    with pytest.raises(ManifestError, match="unknown node"):
        validate_software_control(resign(value))


def test_rejects_changed_node_without_direct_evidence_even_when_resigned():
    value = software_control_sample()
    changed = next(node for node in value["working_map"]["nodes"] if node["change_state"] == "changed")
    changed["owner_view"]["basis"]["evidence_ids"] = []

    with pytest.raises(ManifestError, match="direct claim and evidence"):
        validate_software_control(resign(value))


def test_rejects_overview_that_does_not_cover_detail_nodes_once():
    value = software_control_sample()
    value["working_map"]["overview_map"]["nodes"][0]["detail_node_ids"] = ["fixed_change", "explicit_evidence"]

    with pytest.raises(ManifestError, match="every detail node exactly once"):
        validate_software_control(resign(value))


def test_rejects_overview_that_is_not_four_owner_steps():
    value = software_control_sample()
    removed = value["working_map"]["overview_map"]["nodes"].pop()
    value["working_map"]["overview_map"]["nodes"][0]["detail_node_ids"].extend(removed["detail_node_ids"])

    with pytest.raises(ManifestError, match="exactly four owner steps"):
        validate_software_control(resign(value))


def test_accepts_non_sequential_capability_map_and_rejects_ordered_edge():
    value = software_control_sample()
    value["working_map"]["map_kind"] = "capability_map"
    value["working_map"]["order_status"] = "not_applicable"
    value["working_map"]["order_label"] = "没有先后顺序"
    value["working_map"]["order_note"] = "这些能力没有固定先后顺序。"
    value["working_map"]["order_source_refs"] = []
    value["working_map"]["flows"] = []
    value["working_map"]["overview_map"]["flows"] = []

    validated = validate_software_control(resign(value))
    assert validated["working_map"]["map_kind"] == "capability_map"

    value["working_map"]["flows"] = [
        {"from": value["working_map"]["nodes"][0]["id"], "to": value["working_map"]["nodes"][1]["id"], "label": "guessed"}
    ]
    with pytest.raises(ManifestError, match="must not declare ordered flows"):
        validate_software_control(resign(value))


def test_rejects_changed_overview_not_bound_to_changed_detail():
    value = software_control_sample()
    overview = value["working_map"]["overview_map"]["nodes"]
    next(node for node in overview if node["change_state"] == "changed")["change_state"] = "unknown"
    overview[0]["change_state"] = "changed"

    with pytest.raises(ManifestError, match="contain the changed detail node"):
        validate_software_control(resign(value))


def test_rejects_unknown_workflow_evidence_state():
    value = software_control_sample()
    value["working_map"]["nodes"][0].update(
        {
            "evidence_status": "trusted_because_readme_says_so",
            "evidence_label": "已确认",
            "evidence_note": "unsafe",
            "source_refs": ["README.md"],
        }
    )

    with pytest.raises(ManifestError, match="evidence_status is unsupported"):
        validate_software_control(resign(value))
