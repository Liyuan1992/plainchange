from __future__ import annotations

import json
from pathlib import Path

import pytest

from plainchange.generator_contract import build_generator_packet, validate_packet
from plainchange.git_evidence import collect_git_evidence
from plainchange.models import ManifestError, SampleManifest, canonical_json_bytes, sha256_bytes


def test_generator_packet_excludes_hidden_ground_truth(
    sample_repo, manifest_factory, tmp_path: Path
):
    repo, base, head = sample_repo
    manifest_path = manifest_factory(tmp_path / "sample.json", repo, base, head)
    manifest = SampleManifest.load(manifest_path)
    git = collect_git_evidence(manifest.repository, manifest.limits)

    packet = build_generator_packet(manifest, git)
    serialized = json.dumps(packet, ensure_ascii=False)

    assert "ground.truth" not in serialized
    assert "feature flag was added" not in serialized
    assert str(manifest_path) not in serialized
    assert str(repo) not in serialized
    behavior = [item for item in packet["evidence"] if item["kind"] == "behavior_signal"]
    assert len(behavior) == 1
    assert "kind=changed_callable_signature" in behavior[0]["content"]
    assert behavior[0]["id"] in packet["allowed_evidence_ids"]
    assert validate_packet(packet)["packet_sha256"] == packet["packet_sha256"]


def test_packet_tampering_is_detected(sample_repo, manifest_factory, tmp_path: Path):
    repo, base, head = sample_repo
    manifest = SampleManifest.load(manifest_factory(tmp_path / "sample.json", repo, base, head))
    packet = build_generator_packet(
        manifest, collect_git_evidence(manifest.repository, manifest.limits)
    )
    packet["change"]["changed_files"] = 999

    with pytest.raises(ManifestError, match="hash does not match"):
        validate_packet(packet)


def test_structured_actual_test_receipt_enters_packet_and_stays_range_bound(
    sample_repo, manifest_factory, tmp_path: Path
):
    repo, base, head = sample_repo
    receipt = {
        "schema_version": "plainchange.verification-receipt.v1",
        "change_identity": {"base_commit": base, "head_commit": head},
        "producer": {"kind": "ci", "name": "sample-ci"},
        "checks": [
            {
                "id": "tests.sample",
                "category": "tests",
                "status": "passed",
                "label": {"zh-CN": "示例测试", "en": "Sample tests"},
                "summary": {"zh-CN": "测试通过。", "en": "Tests passed."},
                "scope": {"zh-CN": "示例范围", "en": "Sample scope"},
                "limitations": [],
                "observed_at": None,
            }
        ],
    }
    receipt["receipt_sha256"] = sha256_bytes(canonical_json_bytes(receipt))
    manifest_path = manifest_factory(
        tmp_path / "sample.json",
        repo,
        base,
        head,
        evidence_inputs=[
            {
                "id": "tests.structured",
                "kind": "test",
                "authority": "actual_test_receipt",
                "source": {"type": "inline", "text": json.dumps(receipt)},
            }
        ],
    )
    manifest = SampleManifest.load(manifest_path)

    packet = build_generator_packet(
        manifest, collect_git_evidence(manifest.repository, manifest.limits)
    )

    assert packet["verification_receipts"][0]["checks"][0]["id"] == "tests.sample"
    assert validate_packet(packet)["verification_receipts"] == packet["verification_receipts"]
