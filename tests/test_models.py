from __future__ import annotations

import json
from pathlib import Path

import pytest

from plainchange.models import ManifestError, SampleManifest


def test_manifest_loads_and_separates_sources(sample_repo, manifest_factory, tmp_path: Path):
    repo, base, head = sample_repo
    path = manifest_factory(tmp_path / "sample.json", repo, base, head)

    manifest = SampleManifest.load(path)

    assert manifest.sample_id == "sample.one"
    assert manifest.repository.base == base
    assert len(manifest.evidence_inputs) == 2
    assert len(manifest.hidden_ground_truth) == 1


def test_inline_ground_truth_overlap_is_rejected(sample_repo, manifest_factory, tmp_path: Path):
    repo, base, head = sample_repo
    same_source = {"type": "inline", "text": "same answer"}
    path = manifest_factory(
        tmp_path / "sample.json",
        repo,
        base,
        head,
        evidence_inputs=[
            {
                "id": "task.original",
                "kind": "task",
                "authority": "original_task",
                "source": same_source,
            }
        ],
        hidden_ground_truth=[{"id": "ground.truth", "source": same_source}],
    )

    with pytest.raises(ManifestError, match="overlaps hidden ground truth"):
        SampleManifest.load(path)


def test_file_alias_ground_truth_overlap_is_rejected(sample_repo, manifest_factory, tmp_path: Path):
    repo, base, head = sample_repo
    shared = tmp_path / "shared.md"
    shared.write_text("secret answer", encoding="utf-8")
    path = manifest_factory(
        tmp_path / "sample.json",
        repo,
        base,
        head,
        evidence_inputs=[
            {
                "id": "history.one",
                "kind": "history",
                "authority": "approved_history",
                "source": {"type": "file", "path": "shared.md"},
            }
        ],
        hidden_ground_truth=[
            {"id": "ground.truth", "source": {"type": "file", "path": str(shared)}}
        ],
    )

    with pytest.raises(ManifestError, match="overlaps hidden ground truth"):
        SampleManifest.load(path)


def test_copied_ground_truth_content_is_rejected(sample_repo, manifest_factory, tmp_path: Path):
    repo, base, head = sample_repo
    first = tmp_path / "first.md"
    second = tmp_path / "second.md"
    first.write_text("copied answer", encoding="utf-8")
    second.write_text("copied answer", encoding="utf-8")
    path = manifest_factory(
        tmp_path / "sample.json",
        repo,
        base,
        head,
        evidence_inputs=[
            {
                "id": "history.one",
                "kind": "history",
                "authority": "approved_history",
                "source": {"type": "file", "path": str(first)},
            }
        ],
        hidden_ground_truth=[
            {"id": "ground.truth", "source": {"type": "file", "path": str(second)}}
        ],
    )

    with pytest.raises(ManifestError, match="overlaps hidden ground truth"):
        SampleManifest.load(path)


def test_output_inside_target_repository_is_rejected(sample_repo, manifest_factory, tmp_path: Path):
    repo, base, head = sample_repo
    path = manifest_factory(tmp_path / "sample.json", repo, base, head)
    manifest = SampleManifest.load(path)

    with pytest.raises(ManifestError, match="must not be inside"):
        manifest.validate_output_path(repo / "generated")


def test_unknown_manifest_fields_are_rejected(sample_repo, manifest_factory, tmp_path: Path):
    repo, base, head = sample_repo
    path = manifest_factory(tmp_path / "sample.json", repo, base, head)
    data = json.loads(path.read_text(encoding="utf-8"))
    data["generator_command"] = "dangerous-command"
    path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(ManifestError, match="unknown fields"):
        SampleManifest.load(path)
