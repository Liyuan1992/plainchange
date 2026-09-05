from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from change_passport.cli import main
from change_passport.models import ManifestError
from change_passport.pipeline import finalize_brief, prepare_sample


def _status(repo: Path) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), "status", "--porcelain"],
        check=True,
        capture_output=True,
        shell=False,
        text=True,
    ).stdout


def _raw_brief() -> dict:
    def claim(claim_id, section, scope, text, refs, claim_type="verified_fact"):
        return {
            "id": claim_id,
            "section": section,
            "scope": scope,
            "text": text,
            "claim_type": claim_type,
            "confidence": "high" if claim_type != "unknown" else "low",
            "importance": "high",
            "evidence_ids": refs,
            "limitations": [],
            "next_check": None,
        }

    return {
        "schema_version": "change-passport.raw-brief.v1",
        "claims": [
            claim(
                "function.one",
                "function",
                "user_behavior_change",
                "问候现在可以包含姓名。",
                ["task.original", "git.patch"],
            ),
            claim(
                "architecture.one",
                "architecture",
                "architecture_change",
                "新增了 feature.py 模块。",
                ["git.file.002"],
                "inference",
            ),
            claim(
                "history.none",
                "history",
                "history_relation",
                "没有证据确认历史关联。",
                [],
                "unknown",
            ),
            claim(
                "attention.tests",
                "attention",
                "test_status",
                "提供的测试回执记录了通过结果。",
                ["test.receipt"],
            ),
        ],
    }


def test_end_to_end_file_bridge_does_not_change_target_repo(
    sample_repo, manifest_factory, tmp_path: Path
):
    repo, base, head = sample_repo
    manifest = manifest_factory(tmp_path / "sample.json", repo, base, head)
    output = tmp_path / "artifacts"
    before = _status(repo)

    prepared = prepare_sample(manifest, output)
    packet_text = (output / "generator-packet.json").read_text(encoding="utf-8")
    raw_path = output / "raw-brief.input.json"
    raw_path.write_text(json.dumps(_raw_brief(), ensure_ascii=False), encoding="utf-8")
    finalized = finalize_brief(prepared["packet_path"], raw_path, output)

    assert "ground.truth" not in packet_text
    assert "feature flag was added" not in packet_text
    assert Path(finalized["brief_markdown"]).exists()
    assert Path(finalized["architecture_map"]).exists()
    assert Path(finalized["system_architecture"]).exists()
    assert Path(finalized["beginner_review"]).exists()
    assert Path(finalized["review_html"]).exists()
    assert (output / "architecture-baseline.proposal.json").exists()
    assert (output / "baseline-decision.template.json").exists()
    assert "ARCHITECTURE DELTA MAP" in (output / "brief.md").read_text(encoding="utf-8")
    assert "问候现在可以包含姓名" in (output / "brief.md").read_text(encoding="utf-8")
    review = json.loads((output / "beginner-review.json").read_text(encoding="utf-8"))
    system_architecture = json.loads(
        (output / "system-architecture.json").read_text(encoding="utf-8")
    )
    assert review["brief_identity"] == json.loads(
        (output / "brief.json").read_text(encoding="utf-8")
    )["brief_identity"]
    assert review["system_architecture"]["snapshot_identity"] == system_architecture[
        "snapshot_identity"
    ]
    assert review["validation"]["system_node_count"] == system_architecture[
        "coverage"
    ]["node_count"]
    why = next(item for item in review["summary"] if item["id"] == "summary.why")
    assert why["task_context"]["state"] == "available"
    assert why["task_context"]["entries"][0]["role"] == "user"
    assert "这次 AI 改了什么？" in (output / "review.html").read_text(encoding="utf-8")
    assert "整体架构" in (output / "review.html").read_text(encoding="utf-8")
    assert (output / "annotation.template.json").exists()
    assert _status(repo) == before


def test_cli_prepare_and_finalize(sample_repo, manifest_factory, tmp_path: Path, capsys):
    repo, base, head = sample_repo
    manifest = manifest_factory(tmp_path / "sample.json", repo, base, head)
    output = tmp_path / "cli-output"

    assert main(["prepare", str(manifest), "--output", str(output)]) == 0
    raw_path = output / "raw-brief.input.json"
    raw_path.write_text(json.dumps(_raw_brief(), ensure_ascii=False), encoding="utf-8")
    assert (
        main(
            [
                "finalize",
                str(output / "generator-packet.json"),
                str(raw_path),
                "--output",
                str(output),
            ]
        )
        == 0
    )
    captured = capsys.readouterr()
    assert '"ok": true' in captured.out

    annotation = json.loads((output / "annotation.template.json").read_text(encoding="utf-8"))
    for item in annotation["claims"]:
        item["label"] = "supported"
    annotation["ground_truth"] = [
        {
            "ground_truth_id": "gt.one",
            "critical": True,
            "matched_claim_ids": ["function.one"],
            "notes": "",
        }
    ]
    annotation_path = output / "annotation.json"
    annotation_path.write_text(json.dumps(annotation, ensure_ascii=False), encoding="utf-8")
    assert (
        main(
            [
                "score",
                str(output / "brief.json"),
                str(annotation_path),
                "--output",
                str(output / "score.json"),
            ]
        )
        == 0
    )
    assert json.loads((output / "score.json").read_text(encoding="utf-8"))["outcome"] == "pass"


def test_cli_rejects_output_inside_target_repo(sample_repo, manifest_factory, tmp_path: Path, capsys):
    repo, base, head = sample_repo
    manifest = manifest_factory(tmp_path / "sample.json", repo, base, head)

    assert main(["prepare", str(manifest), "--output", str(repo / "artifacts")]) == 2
    assert "must not be inside" in capsys.readouterr().err


def test_finalize_cannot_escape_prepared_artifact_directory(
    sample_repo, manifest_factory, tmp_path: Path
):
    repo, base, head = sample_repo
    manifest = manifest_factory(tmp_path / "sample.json", repo, base, head)
    prepared_dir = tmp_path / "prepared"
    prepare_sample(manifest, prepared_dir)
    raw_path = prepared_dir / "raw.json"
    raw_path.write_text(json.dumps(_raw_brief(), ensure_ascii=False), encoding="utf-8")

    with pytest.raises(ManifestError, match="must stay inside"):
        finalize_brief(
            prepared_dir / "generator-packet.json",
            raw_path,
            tmp_path / "escaped-output",
        )
