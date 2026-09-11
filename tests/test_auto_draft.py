from __future__ import annotations

import json
from pathlib import Path

from plainchange.auto_draft import draft_target_profile
from plainchange.target_profile import load_target_profile
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

    assert labels == ["主要功能"]
    assert profile["conceptual_architecture"]["architecture_kind"] == "capability_map"
    assert profile["conceptual_architecture"]["flows"] == []
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
    assert architecture["architecture_kind"] == "capability_map"
    assert architecture["workflow_order_status"] == "not_applicable"
    assert {item["evidence_status"] for item in architecture["components"]} == {
        "code_discovered"
    }
    assert architecture["flows"] == []
    assert "不代表业务顺序" in architecture["boundary_note"]


def test_capability_list_becomes_non_sequential_source_bound_map(tmp_path: Path):
    repo = tmp_path / "capability-list-product"
    (repo / "src" / "package").mkdir(parents=True)
    (repo / "README.md").write_text(
        """# Capability Product

This tool lets an operator inspect and govern saved records.

## Features

- **Record catalog** (`catalog.py`): lists available records within a fixed budget.
- **Focused query** (`query.py`): finds matching records and explains empty results.
- **Relation trace** (`trace.py`): follows bounded links without treating them as proof.
- **Source reader** (`source.py`): opens the original declaration for review.
""",
        encoding="utf-8",
    )
    for name in ("catalog", "query", "trace", "source"):
        (repo / "src" / "package" / f"{name}.py").write_text(
            f"def {name}():\n    pass\n", encoding="utf-8"
        )
    commit = _commit_repo(repo)

    architecture = draft_target_profile(repo, commit, 15, repo.name)["conceptual_architecture"]

    assert architecture["architecture_kind"] == "capability_map"
    assert architecture["workflow_order_status"] == "not_applicable"
    assert architecture["flows"] == []
    assert [item["label"] for item in architecture["components"]] == [
        "Record catalog",
        "Focused query",
        "Relation trace",
        "Source reader",
    ]
    assert {item["evidence_status"] for item in architecture["components"]} == {
        "declared_and_code_supported"
    }


def test_capability_summary_table_becomes_non_sequential_map(tmp_path: Path):
    repo = tmp_path / "capability-table-product"
    (repo / "src").mkdir(parents=True)
    (repo / "README.md").write_text(
        """# Capability Table Product

This application coordinates several independent owner-facing surfaces.

## Current progress

| Area | Status | Evidence |
| --- | --- | --- |
| Conversation workspace | Available for daily use | `src/chat.py` |
| Memory review | Keeps proposed records review-gated | `src/memory.py` |
| Local control | Accepts bounded local actions | `src/control.py` |
| Desktop shell | Opens the owner workspace | `src/desktop.py` |
""",
        encoding="utf-8",
    )
    for name in ("chat", "memory", "control", "desktop"):
        (repo / "src" / f"{name}.py").write_text("VALUE = 1\n", encoding="utf-8")
    commit = _commit_repo(repo)

    architecture = draft_target_profile(repo, commit, 15, repo.name)["conceptual_architecture"]

    assert architecture["architecture_kind"] == "capability_map"
    assert architecture["flows"] == []
    assert [item["label"] for item in architecture["components"]] == [
        "Conversation workspace",
        "Memory review",
        "Local control",
        "Desktop shell",
    ]
    assert architecture["components"][0]["description"] == "Available for daily use"
    assert architecture["components"][0]["evidence_status"] == "declared_and_code_supported"


def test_capability_uses_explicit_scope_and_derives_distinct_internal_responsibilities(
    tmp_path: Path,
):
    repo = tmp_path / "bounded-capability-product"
    chat = repo / "src" / "product" / "conversation"
    chat.mkdir(parents=True)
    (repo / "src" / "product" / "memory.py").write_text("VALUE = 1\n", encoding="utf-8")
    (repo / "src" / "product" / "desktop.py").write_text("VALUE = 1\n", encoding="utf-8")
    for name in (
        "messages",
        "context_assembly",
        "routing_policy",
        "tool_execution",
        "response_handoff",
        "turn_state",
    ):
        (chat / f"{name}.py").write_text(f"def {name}():\n    pass\n", encoding="utf-8")
    (repo / "benchmarks").mkdir()
    (repo / "benchmarks" / "conversation_runtime.py").write_text("VALUE = 1\n", encoding="utf-8")
    (repo / "README.md").write_text(
        """# Bounded Capability Product

This application gives an owner a conversation workspace and supporting tools.

## Features

| Area | Status | Evidence |
| --- | --- | --- |
| Conversation workspace | Handles an interactive conversation | `src/product/conversation/` |
| Memory review | Reviews saved information | `src/product/memory.py` |
| Desktop shell | Opens the local workspace | `src/product/desktop.py` |
""",
        encoding="utf-8",
    )
    commit = _commit_repo(repo)

    architecture = draft_target_profile(repo, commit, 15, repo.name)["conceptual_architecture"]
    conversation = architecture["components"][0]

    assert conversation["evidence_status"] == "declared_and_code_supported"
    assert [item["label"] for item in conversation["details"]] == [
        "接收输入与会话",
        "准备上下文与已有信息",
        "判断如何处理",
        "执行实际处理工作",
        "整理并交付结果",
        "记录状态与过程",
    ]
    assert all(
        detail["evidence_status"] == "code_discovered"
        and detail["evidence_label"] == "从代码结构发现"
        for detail in conversation["details"]
    )
    assert all(
        "src/product/conversation/" in ref
        for detail in conversation["details"]
        for ref in detail["source_refs"][1:]
    )
    assert all(
        "benchmarks/conversation_runtime.py" not in ref
        for ref in conversation["source_refs"]
    )


def test_weak_generic_words_do_not_create_false_code_support(tmp_path: Path):
    repo = tmp_path / "weak-token-product"
    (repo / "benchmarks").mkdir(parents=True)
    (repo / "benchmarks" / "runtime_batch.py").write_text("VALUE = 1\n", encoding="utf-8")
    (repo / "src").mkdir()
    (repo / "src" / "main_engine.py").write_text("VALUE = 1\n", encoding="utf-8")
    (repo / "README.md").write_text(
        """# Weak Token Product

This product lists several owner-facing areas without implementation anchors.

## Features

- **Main runtime**: provides the primary experience.
- **Core system**: keeps internal work coordinated.
- **Project data**: retains the information used by the product.
""",
        encoding="utf-8",
    )
    commit = _commit_repo(repo)

    architecture = draft_target_profile(repo, commit, 15, repo.name)["conceptual_architecture"]

    assert {item["evidence_status"] for item in architecture["components"]} == {
        "declared_only"
    }
    assert all("details" not in item for item in architecture["components"])
