from __future__ import annotations

import json
from pathlib import Path

from change_passport.auto_draft import draft_target_profile
from change_passport.target_profile import load_target_profile
from conftest import run_git


def _commit_repo(repo: Path, message: str = "fixture") -> str:
    run_git(repo, "init", "-b", "main")
    run_git(repo, "config", "user.email", "tests@example.invalid")
    run_git(repo, "config", "user.name", "Change Passport Tests")
    run_git(repo, "add", ".")
    run_git(repo, "commit", "-m", message)
    return run_git(repo, "rev-parse", "HEAD")


def test_model_serving_workflow_is_detected_without_repository_name_special_case(
    tmp_path: Path,
):
    repo = tmp_path / "unrelated-alpha"
    (repo / "engine").mkdir(parents=True)
    (repo / "model_executor").mkdir()
    (repo / "engine" / "scheduler.py").write_text("class Queue:\n    pass\n", encoding="utf-8")
    (repo / "model_executor" / "runner.py").write_text("def run():\n    pass\n", encoding="utf-8")
    run_git(repo, "init", "-b", "main")
    run_git(repo, "config", "user.email", "tests@example.invalid")
    run_git(repo, "config", "user.name", "Change Passport Tests")
    run_git(repo, "add", ".")
    run_git(repo, "commit", "-m", "model service fixture")
    commit = run_git(repo, "rev-parse", "HEAD")

    profile = draft_target_profile(repo, commit, 15, "unrelated-alpha")
    labels = [item["label"] for item in profile["conceptual_architecture"]["components"]]

    assert labels == [
        "请求进入软件",
        "整理模型输入",
        "安排请求和计算资源",
        "运行模型并返回结果",
    ]
    assert "vllm" not in json.dumps(profile).lower()
    path = tmp_path / "profile.json"
    path.write_text(json.dumps(profile, ensure_ascii=False), encoding="utf-8")
    assert load_target_profile(path).profile_id == "auto-unrelated-alpha"


def test_declared_workflow_is_source_bound_and_code_reconciled(tmp_path: Path):
    repo = tmp_path / "declared-product"
    (repo / "src" / "package").mkdir(parents=True)
    (repo / "README.md").write_text(
        """# Declared Product

This tool turns submitted material into a reviewed release.

## Pipeline

```text
ingest -> accept submitted material
transform -> prepare the material
publish -> create the release
archive -> retain the accepted release
```
""",
        encoding="utf-8",
    )
    (repo / "src" / "package" / "cli.py").write_text(
        "def run():\n    ingest()\n    transform()\n    publish()\n",
        encoding="utf-8",
    )
    for name in ("ingest", "transform", "publish"):
        (repo / "src" / "package" / f"{name}.py").write_text(
            f"def {name}():\n    pass\n", encoding="utf-8"
        )
    commit = _commit_repo(repo)

    profile = draft_target_profile(repo, commit, 15, "declared-product")
    architecture = profile["conceptual_architecture"]

    assert architecture["purpose_statement_state"] == "project_declared"
    assert architecture["purpose_source_refs"][0].startswith(
        f"git:{commit}:README.md:sha256:"
    )
    assert architecture["workflow_order_status"] == "partially_supported"
    assert len(architecture["components"]) == 4
    assert [item["evidence_status"] for item in architecture["components"]] == [
        "declared_and_code_supported",
        "declared_and_code_supported",
        "declared_and_code_supported",
        "declared_only",
    ]
    assert all(
        item["statement_state"] != "observed_fact"
        for item in [
            {"statement_state": architecture["purpose_statement_state"]},
            *architecture["components"],
        ]
        if "statement_state" in item
    )
    path = tmp_path / "declared-profile.json"
    path.write_text(json.dumps(profile, ensure_ascii=False), encoding="utf-8")
    loaded = load_target_profile(path)
    assert loaded.presentation.conceptual_architecture is not None
    assert (
        loaded.presentation.conceptual_architecture.workflow_order_status
        == "partially_supported"
    )


def test_declared_order_conflict_is_not_silently_accepted(tmp_path: Path):
    repo = tmp_path / "order-conflict"
    (repo / "src").mkdir(parents=True)
    (repo / "README.md").write_text(
        """# Order Conflict

An example processing tool.

## Workflow

ingest -> accept input
transform -> prepare input
publish -> produce output
audit -> inspect output
""",
        encoding="utf-8",
    )
    (repo / "src" / "pipeline.py").write_text(
        "def run():\n    ingest()\n    publish()\n    transform()\n    audit()\n",
        encoding="utf-8",
    )
    commit = _commit_repo(repo)

    profile = draft_target_profile(repo, commit, 15, "order-conflict")
    architecture = profile["conceptual_architecture"]

    assert architecture["workflow_order_status"] == "conflicting"
    assert architecture["workflow_order_label"] == "顺序有冲突"
    assert "不能把文档顺序当成实际顺序" in architecture["workflow_order_note"]


def test_generated_sections_are_mutually_discriminating(tmp_path: Path):
    repo = tmp_path / "mixed-package"
    (repo / "src" / "package").mkdir(parents=True)
    (repo / "tests").mkdir()
    (repo / "src" / "package" / "cli.py").write_text("def main():\n    pass\n", encoding="utf-8")
    (repo / "src" / "package" / "models.py").write_text("class Item:\n    pass\n", encoding="utf-8")
    (repo / "src" / "package" / "engine.py").write_text("def work():\n    pass\n", encoding="utf-8")
    (repo / "tests" / "test_engine.py").write_text("def test_work():\n    pass\n", encoding="utf-8")
    commit = _commit_repo(repo)

    profile = draft_target_profile(repo, commit, 15, "mixed-package")
    path = tmp_path / "mixed-profile.json"
    path.write_text(json.dumps(profile, ensure_ascii=False), encoding="utf-8")
    loaded = load_target_profile(path)

    expected = {
        "src/package/cli.py": "entry",
        "src/package/models.py": "data",
        "src/package/engine.py": "core",
        "tests/test_engine.py": "quality",
    }
    assert {path: loaded.section_id_for_path(path) for path in expected} == expected
    rules = [
        (section["id"], prefix)
        for section in profile["sections"]
        for prefix in section["path_prefixes"]
    ]
    assert len([prefix for _, prefix in rules]) == len(
        set(prefix for _, prefix in rules)
    )


def test_missing_workflow_stays_an_explicit_generic_candidate(tmp_path: Path):
    repo = tmp_path / "undocumented-package"
    repo.mkdir()
    (repo / "library.py").write_text("def work():\n    pass\n", encoding="utf-8")
    commit = _commit_repo(repo)

    profile = draft_target_profile(repo, commit, 15, "undocumented-package")
    architecture = profile["conceptual_architecture"]

    assert architecture["purpose_statement_state"] == "unknown"
    assert architecture["workflow_order_status"] == "unverified"
    assert {item["evidence_status"] for item in architecture["components"]} == {
        "generated_candidate"
    }
    assert "没有找到明确的项目流程说明" in architecture["boundary_note"]
