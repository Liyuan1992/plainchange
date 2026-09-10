from __future__ import annotations

import json
import base64
import gzip
import re
import subprocess
from pathlib import Path

import pytest

from plainchange.cli import main
from plainchange.git_evidence import GitEvidenceError
from plainchange.models import ManifestError
from plainchange.pipeline import analyze_sample, finalize_brief, prepare_sample
from conftest import run_git
from test_software_control import resign, software_control_sample


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


def test_cli_analyze_project_and_shorthand_generate_change_passport(
    sample_repo, tmp_path: Path, capsys, monkeypatch
):
    repo, _base, _head = sample_repo
    direct_output = tmp_path / "direct-output"

    assert main(["analyze", str(repo), "--output", str(direct_output)]) == 0
    assert (direct_output / "review.html").is_file()
    assert "Change Passport generated:" in capsys.readouterr().out

    shorthand_output = tmp_path / "shorthand-output"
    monkeypatch.chdir(repo)
    assert main([".", "--output", str(shorthand_output)]) == 0
    assert (shorthand_output / "review.html").is_file()
    assert "Change Passport generated:" in capsys.readouterr().out


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


def test_finalize_accepts_optional_generic_software_control(
    sample_repo, manifest_factory, tmp_path: Path
):
    repo, base, head = sample_repo
    manifest = manifest_factory(tmp_path / "sample.json", repo, base, head)
    output = tmp_path / "prepared"
    prepare_sample(manifest, output)
    raw_path = output / "raw.json"
    raw_path.write_text(json.dumps(_raw_brief(), ensure_ascii=False), encoding="utf-8")
    finalize_brief(output / "generator-packet.json", raw_path, output)

    brief = json.loads((output / "brief.json").read_text(encoding="utf-8"))
    review = json.loads((output / "beginner-review.json").read_text(encoding="utf-8"))
    system = json.loads((output / "system-architecture.json").read_text(encoding="utf-8"))
    control = software_control_sample()
    control["sample_id"] = brief["sample_id"]
    control["source_identity"]["brief_identity"] = brief["brief_identity"]
    control["source_identity"]["review_identity"] = review["review_identity"]
    control["source_identity"]["change_identity"] = {
        "base_commit": brief["change"]["base_commit"],
        "head_commit": brief["change"]["head_commit"],
        "patch_sha256": brief["change"]["patch_sha256"],
    }
    control["working_map"]["source"]["profile_sha256"] = system["target_profile"]["profile_sha256"]
    fallback_group_id = system["groups"][0]["group_id"]
    for node in control["working_map"]["nodes"]:
        if node["implementation_group_ids"]:
            node["implementation_group_ids"] = [fallback_group_id]
    control_path = output / "software-control.input.json"
    control_path.write_text(json.dumps(resign(control), ensure_ascii=False), encoding="utf-8")

    finalized = finalize_brief(
        output / "generator-packet.json",
        raw_path,
        output,
        control_path,
    )

    assert Path(finalized["software_control"]).exists()
    html = (output / "review.html").read_text(encoding="utf-8")
    assert "这次改了什么" in html
    assert "这个软件怎么工作" in html
    assert "software-control-data" in html


def test_prepare_reports_progress_and_reuses_content_cache(
    sample_repo, manifest_factory, tmp_path: Path, monkeypatch
):
    repo, base, head = sample_repo
    monkeypatch.setenv("PLAINCHANGE_CACHE_DIR", str(tmp_path / "cache"))
    manifest = manifest_factory(tmp_path / "sample.json", repo, base, head)
    first = prepare_sample(manifest, tmp_path / "first")
    second = prepare_sample(manifest, tmp_path / "second")

    assert first["cache_stats"]["misses"] > 0
    assert second["cache_stats"]["misses"] == 0
    assert second["cache_stats"]["hits"] > 0
    receipt = json.loads(Path(second["run_receipt"]).read_text(encoding="utf-8"))
    assert receipt["status"] == "succeeded"
    assert [item["name"] for item in receipt["stages"]] == [
        "git_preflight",
        "git_evidence",
        "architecture",
        "generator_packet",
        "write_artifacts",
    ]


def test_analyze_builds_candidate_owner_report_without_model(
    sample_repo, manifest_factory, tmp_path: Path, monkeypatch
):
    repo, base, head = sample_repo
    monkeypatch.setenv("PLAINCHANGE_CACHE_DIR", str(tmp_path / "cache"))
    manifest = manifest_factory(tmp_path / "sample.json", repo, base, head)
    before = _status(repo)

    result = analyze_sample(manifest, tmp_path / "analysis")

    assert _status(repo) == before
    assert Path(result["target_profile_draft"]).is_file()
    assert Path(result["software_control_auto"]).is_file()
    assert Path(result["review_html"]).is_file()
    html = Path(result["review_html"]).read_text(encoding="utf-8")
    match = re.search(
        r'<script id="technical-payload-data" type="application/json">(.*?)</script>',
        html,
        flags=re.DOTALL,
    )
    assert match is not None
    payload = json.loads(match.group(1))
    decoded = json.loads(gzip.decompress(base64.b64decode(payload["data"])))
    assert decoded["snapshot_identity"] == json.loads(
        Path(result["system_architecture"]).read_text(encoding="utf-8")
    )["snapshot_identity"]
    receipt = json.loads(Path(result["run_receipt"]).read_text(encoding="utf-8"))
    assert receipt["operation"] == "analyze"
    assert receipt["status"] == "succeeded"
    assert receipt["stages"][-1]["name"] == "owner_draft"
    control = json.loads(Path(result["software_control_auto"]).read_text(encoding="utf-8"))
    assert control["validation"]["human_comprehension_status"] == "pending_owner_confirmation"
    assert control["working_map"]["order_status"] == "unverified"
    assert {item["evidence_label"] for item in control["working_map"]["nodes"]} == {
        "自动候选"
    }
    assert not [
        item for item in control["working_map"]["nodes"] if item["change_state"] == "changed"
    ]
    assert "还不能可靠定位到哪个用户操作" in control["first_screen_summary"]["headline"]
    assert control["first_screen_summary"]["user_impact"]["state_label"] == "还没判断"
    assert "目前没发现" not in control["first_screen_summary"]["user_impact"]["text"]
    assert [item["id"] for item in control["five_questions"][-1]["details"]["actions"]] == [
        "verify.normal-path",
        "verify.callers",
    ]
    assert "owner-evidence-badge" in html
    assert "在软件流程中查看 →" in html
    assert "changedDetails.length !== 1" in html


def test_analyze_turns_added_stop_branch_into_two_case_owner_check(
    manifest_factory, tmp_path: Path, monkeypatch
):
    repo = tmp_path / "conditional-worker"
    (repo / "src" / "worker").mkdir(parents=True)
    (repo / "README.md").write_text(
        """# Conditional Worker

This tool checks submitted work and publishes accepted results.

## Workflow

receive -> accept submitted work
check -> inspect the submitted work
publish -> publish accepted work
archive -> retain the result
""",
        encoding="utf-8",
    )
    worker = repo / "src" / "worker" / "check.py"
    worker.write_text("def check(item):\n    return item\n", encoding="utf-8")
    run_git(repo, "init", "-b", "main")
    run_git(repo, "config", "user.email", "tests@example.invalid")
    run_git(repo, "config", "user.name", "Change Passport Tests")
    run_git(repo, "add", ".")
    run_git(repo, "commit", "-m", "initial")
    base = run_git(repo, "rev-parse", "HEAD")
    worker.write_text(
        "def check(item):\n    if not item.ready:\n        raise ItemNotReady(item.name)\n    return item\n",
        encoding="utf-8",
    )
    run_git(repo, "add", ".")
    run_git(repo, "commit", "-m", "stop unready work")
    head = run_git(repo, "rev-parse", "HEAD")
    manifest = manifest_factory(tmp_path / "conditional.json", repo, base, head)
    monkeypatch.setenv("PLAINCHANGE_CACHE_DIR", str(tmp_path / "cache-conditional"))

    result = analyze_sample(manifest, tmp_path / "conditional-analysis")
    control = json.loads(Path(result["software_control_auto"]).read_text(encoding="utf-8"))

    assert "提前停止" in control["first_screen_summary"]["headline"]
    assert control["first_screen_summary"]["user_impact"]["state_label"] == "还没判断"
    assert [item["id"] for item in control["five_questions"][-1]["details"]["actions"]] == [
        "verify.normal-path",
        "verify.stop-condition",
    ]


def test_analyze_can_use_configured_compatible_model(
    sample_repo, manifest_factory, tmp_path: Path, monkeypatch
):
    repo, base, head = sample_repo
    monkeypatch.setenv("PLAINCHANGE_CACHE_DIR", str(tmp_path / "cache"))
    manifest = manifest_factory(tmp_path / "sample.json", repo, base, head)

    config_path = tmp_path / "model-provider.json"
    config_path.write_text(
        json.dumps(
            {
                "schema_version": "change-passport.model-provider.v1",
                "provider_id": "compatible-test",
                "base_url": "https://models.example.com/v1",
                "model": "owner-selected-model",
                "api_key_env": "TEST_MODEL_API_KEY",
                "timeout_seconds": 120,
                "response_format": "json_object",
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("TEST_MODEL_API_KEY", "test-secret")

    def fake_post(_url, payload, _timeout_seconds, _headers):
        raw = _raw_brief()
        return {
            "id": "chatcmpl-test",
            "model": "provider-resolved-model",
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {"role": "assistant", "content": json.dumps(raw)},
                }
            ],
            "usage": {"prompt_tokens": 42, "completion_tokens": 24, "total_tokens": 66},
        }

    monkeypatch.setattr("plainchange.model_adapter._post_json", fake_post)
    result = analyze_sample(
        manifest,
        tmp_path / "model-analysis",
        generator="model",
        model_config_path=config_path,
    )

    assert result["generator"] == "model"
    assert result["raw_brief_auto"] is None
    assert Path(result["raw_brief_generated"]).name == "raw-brief.model.json"
    brief = json.loads(Path(result["brief_json"]).read_text(encoding="utf-8"))
    assert brief["generator_metadata"]["provider"] == "compatible-test"
    receipt = json.loads(Path(result["model_run_receipt"]).read_text(encoding="utf-8"))
    assert receipt["status"] == "succeeded"
    run_receipt = json.loads(Path(result["run_receipt"]).read_text(encoding="utf-8"))
    assert [item["name"] for item in run_receipt["stages"]][-2:] == [
        "model_generation",
        "owner_draft",
    ]


def test_cli_model_generator_requires_provider_config(capsys):
    assert main(["analyze", "unused.json", "--output", "unused", "--generator", "model"]) == 2
    assert "--model-config is required" in capsys.readouterr().err


def test_prepare_keeps_a_failure_receipt(
    sample_repo, manifest_factory, tmp_path: Path, monkeypatch
):
    repo, _, head = sample_repo
    monkeypatch.setenv("PLAINCHANGE_CACHE_DIR", str(tmp_path / "cache"))
    manifest = manifest_factory(tmp_path / "sample.json", repo, head, head)
    output = tmp_path / "failed"

    with pytest.raises(GitEvidenceError, match="same commit"):
        prepare_sample(manifest, output)

    receipt = json.loads((output / "run-receipt.json").read_text(encoding="utf-8"))
    assert receipt["status"] == "failed"
    assert receipt["error"]["type"] == "GitEvidenceError"
    assert receipt["stages"][-1]["name"] == "git_evidence"
    assert receipt["stages"][-1]["status"] == "failed"
