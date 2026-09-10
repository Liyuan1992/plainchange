from __future__ import annotations

import json
from pathlib import Path

import pytest

from change_passport.generator_contract import build_generator_packet, validate_packet
from change_passport.git_evidence import collect_git_evidence
from change_passport.models import ManifestError, SampleManifest


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
