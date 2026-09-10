from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest


def run_git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        shell=False,
        text=True,
        encoding="utf-8",
    )
    return completed.stdout.strip()


@pytest.fixture
def sample_repo(tmp_path: Path) -> tuple[Path, str, str]:
    repo = tmp_path / "target-repo"
    repo.mkdir()
    run_git(repo, "init", "-b", "main")
    run_git(repo, "config", "user.email", "tests@example.invalid")
    run_git(repo, "config", "user.name", "Change Passport Tests")
    (repo / "app.py").write_text("def greeting():\n    return 'hello'\n", encoding="utf-8")
    run_git(repo, "add", "app.py")
    run_git(repo, "commit", "-m", "initial")
    base = run_git(repo, "rev-parse", "HEAD")
    (repo / "app.py").write_text(
        "def greeting(name: str):\n    return f'hello {name}'\n",
        encoding="utf-8",
    )
    (repo / "feature.py").write_text("ENABLED = True\n", encoding="utf-8")
    run_git(repo, "add", "app.py", "feature.py")
    run_git(repo, "commit", "-m", "add named greeting")
    head = run_git(repo, "rev-parse", "HEAD")
    return repo, base, head


def write_manifest(
    path: Path,
    repo: Path,
    base: str,
    head: str,
    *,
    evidence_inputs: list[dict[str, Any]] | None = None,
    hidden_ground_truth: list[dict[str, Any]] | None = None,
    architecture_baseline: Path | None = None,
    target_profile: Path | None = None,
) -> Path:
    data = {
        "schema_version": "change-passport.sample.v1",
        "sample_id": "sample.one",
        "repository": {"path": str(repo), "base": base, "head": head},
        "evidence_inputs": evidence_inputs
        if evidence_inputs is not None
        else [
            {
                "id": "task.original",
                "kind": "task",
                "authority": "original_task",
                "source": {
                    "type": "inline",
                    "text": "Allow greeting a user by name.",
                },
            },
            {
                "id": "test.receipt",
                "kind": "test",
                "authority": "actual_test_receipt",
                "source": {
                    "type": "inline",
                    "text": "pytest: 12 passed; exit_code=0",
                },
            },
        ],
        "hidden_ground_truth": hidden_ground_truth
        if hidden_ground_truth is not None
        else [
            {
                "id": "ground.truth",
                "source": {
                    "type": "inline",
                    "text": "The greeting now accepts a name and a feature flag was added.",
                },
            }
        ],
        "limits": {
            "max_patch_bytes": 200000,
            "max_input_bytes": 64000,
            "git_timeout_seconds": 15,
        },
    }
    if architecture_baseline is not None:
        data["architecture_baseline"] = {"path": str(architecture_baseline)}
    if target_profile is not None:
        data["target_profile"] = {"path": str(target_profile)}
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


@pytest.fixture
def manifest_factory():
    return write_manifest
