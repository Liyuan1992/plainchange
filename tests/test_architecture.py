from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from change_passport.architecture import (
    ArchitectureError,
    architecture_evidence_bindings,
    render_mermaid,
    validate_system_architecture_snapshot,
)
from change_passport.pipeline import approve_baseline_proposal, prepare_sample
from change_passport.models import canonical_json_bytes, sha256_bytes


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        shell=False,
        text=True,
        encoding="utf-8",
    ).stdout.strip()


def _approve(output: Path) -> Path:
    decision_path = output / "baseline-decision.json"
    decision = json.loads(
        (output / "baseline-decision.template.json").read_text(encoding="utf-8")
    )
    decision.update(
        {
            "decision": "approved",
            "actor": "test-owner",
            "decided_at": "2026-09-04T00:00:00Z",
            "notes": "fixture approval",
        }
    )
    decision_path.write_text(json.dumps(decision), encoding="utf-8")
    approved_path = output / "architecture-baseline.approved.json"
    approve_baseline_proposal(
        output / "architecture-baseline.proposal.json",
        decision_path,
        approved_path,
    )
    return approved_path


def test_bootstrap_emits_one_validated_graph_and_separate_pending_proposal(
    sample_repo, manifest_factory, tmp_path: Path
):
    repo, base, head = sample_repo
    output = tmp_path / "architecture"
    before = _git(repo, "status", "--porcelain")

    result = prepare_sample(
        manifest_factory(tmp_path / "sample.json", repo, base, head), output
    )

    delta = json.loads((output / "architecture-delta.json").read_text(encoding="utf-8"))
    proposal = json.loads(
        (output / "architecture-baseline.proposal.json").read_text(encoding="utf-8")
    )
    system_architecture = json.loads(
        (output / "system-architecture.json").read_text(encoding="utf-8")
    )
    mermaid = (output / "architecture-map.mmd").read_text(encoding="utf-8")
    assert result["baseline_status"] == "bootstrap_unapproved"
    assert proposal["decision"] == "pending"
    assert proposal["candidate_baseline"]["status"] == "candidate"
    assert validate_system_architecture_snapshot(system_architecture) == system_architecture
    assert system_architecture["commit_identity"] == head
    assert system_architecture["coverage"]["all_nodes_assigned_once"] is True
    assert system_architecture["coverage"]["node_count"] == len(
        system_architecture["nodes"]
    )
    bundled_edges = [
        edge_id
        for group_edge in system_architecture["group_edges"]
        for edge_id in group_edge["source_edge_ids"]
    ]
    assert len(bundled_edges) == len(set(bundled_edges))
    assert mermaid == render_mermaid(delta)
    localized_delta = json.loads(json.dumps(delta))
    localized_node = localized_delta["after"]["nodes"][0]
    localized_node["change_status"] = "added"
    localized_node["change_detail"] = "new module; +function:first, +method:Example.run"
    localized_mermaid = render_mermaid(localized_delta)
    assert "新增模块；新增接口：函数 first、方法 Example.run" in localized_mermaid
    assert "+function" not in localized_mermaid
    assert "+method" not in localized_mermaid
    for side in ("before", "after"):
        for node in delta[side]["nodes"]:
            assert f"%% node:{node['node_id']}" in mermaid
    assert _git(repo, "status", "--porcelain") == before


def test_retained_edge_ignores_commit_only_reverification_but_tracks_line_move(
    manifest_factory, tmp_path: Path
):
    repo = tmp_path / "edge-repo"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.email", "tests@example.invalid")
    _git(repo, "config", "user.name", "Change Passport Tests")
    (repo / "a.py").write_text(
        "from b import VALUE\n\ndef read():\n    return VALUE\n",
        encoding="utf-8",
    )
    (repo / "b.py").write_text("VALUE = 1\n", encoding="utf-8")
    _git(repo, "add", "a.py", "b.py")
    _git(repo, "commit", "-m", "initial import")
    base = _git(repo, "rev-parse", "HEAD")

    (repo / "b.py").write_text("VALUE = 2\n", encoding="utf-8")
    _git(repo, "add", "b.py")
    _git(repo, "commit", "-m", "change imported value")
    head = _git(repo, "rev-parse", "HEAD")
    first_output = tmp_path / "commit-only"
    prepare_sample(
        manifest_factory(tmp_path / "commit-only.json", repo, base, head),
        first_output,
    )
    first_delta = json.loads(
        (first_output / "architecture-delta.json").read_text(encoding="utf-8")
    )

    assert first_delta["added_edge_ids"] == []
    assert first_delta["removed_edge_ids"] == []
    assert first_delta["modified_edge_ids"] == []

    (repo / "a.py").write_text(
        "# Import kept, source line moved.\nfrom b import VALUE\n\ndef read():\n    return VALUE\n",
        encoding="utf-8",
    )
    _git(repo, "add", "a.py")
    _git(repo, "commit", "-m", "move import evidence line")
    next_head = _git(repo, "rev-parse", "HEAD")
    second_output = tmp_path / "line-move"
    prepare_sample(
        manifest_factory(tmp_path / "line-move.json", repo, head, next_head),
        second_output,
    )
    second_delta = json.loads(
        (second_output / "architecture-delta.json").read_text(encoding="utf-8")
    )

    assert second_delta["added_edge_ids"] == []
    assert second_delta["removed_edge_ids"] == []
    assert len(second_delta["modified_edge_ids"]) == 1


def test_system_architecture_identity_fails_closed_after_tampering(
    sample_repo, manifest_factory, tmp_path: Path
):
    repo, base, head = sample_repo
    output = tmp_path / "architecture"
    prepare_sample(
        manifest_factory(tmp_path / "sample.json", repo, base, head), output
    )
    snapshot = json.loads(
        (output / "system-architecture.json").read_text(encoding="utf-8")
    )
    snapshot["nodes"][0]["label"] = "tampered"

    with pytest.raises(ArchitectureError, match="identity does not match"):
        validate_system_architecture_snapshot(snapshot)


def test_system_architecture_rejects_semantically_inconsistent_group_counts(
    sample_repo, manifest_factory, tmp_path: Path
):
    repo, base, head = sample_repo
    output = tmp_path / "architecture"
    prepare_sample(
        manifest_factory(tmp_path / "sample.json", repo, base, head), output
    )
    snapshot = json.loads(
        (output / "system-architecture.json").read_text(encoding="utf-8")
    )
    snapshot["groups"][0]["module_count"] += 1
    snapshot.pop("snapshot_identity")
    snapshot["snapshot_identity"] = sha256_bytes(canonical_json_bytes(snapshot))

    with pytest.raises(ArchitectureError, match="module count does not match"):
        validate_system_architecture_snapshot(snapshot)


def test_explicit_approval_enables_incremental_reuse(
    sample_repo, manifest_factory, tmp_path: Path
):
    repo, base, head = sample_repo
    first_output = tmp_path / "first"
    prepare_sample(
        manifest_factory(tmp_path / "first.json", repo, base, head), first_output
    )
    approved_path = _approve(first_output)
    proposal = json.loads(
        (first_output / "architecture-baseline.proposal.json").read_text(encoding="utf-8")
    )
    approved = json.loads(approved_path.read_text(encoding="utf-8"))
    assert proposal["candidate_baseline"]["status"] == "candidate"
    assert approved["status"] == "approved"
    assert approved["approved_by"] == "test-owner"

    (repo / "app.py").write_text(
        "def greeting(name: str, excited: bool = False):\n"
        "    suffix = '!' if excited else ''\n"
        "    return f'hello {name}{suffix}'\n",
        encoding="utf-8",
    )
    _git(repo, "add", "app.py")
    _git(repo, "commit", "-m", "support excited greeting")
    next_head = _git(repo, "rev-parse", "HEAD")
    second_output = tmp_path / "second"

    result = prepare_sample(
        manifest_factory(
            tmp_path / "second.json",
            repo,
            head,
            next_head,
            architecture_baseline=approved_path,
        ),
        second_output,
    )
    delta = json.loads(
        (second_output / "architecture-delta.json").read_text(encoding="utf-8")
    )

    assert result["baseline_status"] == "approved"
    assert delta["analysis_stats"]["parsed_base_files"] == 0
    assert delta["analysis_stats"]["parsed_head_files"] == 1
    assert delta["analysis_stats"]["reused_nodes"] >= 1
    assert len(delta["modified_node_ids"]) == 1


def test_candidate_or_stale_baseline_fails_closed(
    sample_repo, manifest_factory, tmp_path: Path
):
    repo, base, head = sample_repo
    output = tmp_path / "first"
    prepare_sample(
        manifest_factory(tmp_path / "first.json", repo, base, head), output
    )
    candidate_path = output / "candidate.json"
    candidate_path.write_text(
        json.dumps(
            json.loads(
                (output / "architecture-baseline.proposal.json").read_text(
                    encoding="utf-8"
                )
            )["candidate_baseline"]
        ),
        encoding="utf-8",
    )
    with pytest.raises(ArchitectureError, match="baseline_invalid"):
        prepare_sample(
            manifest_factory(
                tmp_path / "candidate.json.manifest",
                repo,
                base,
                head,
                architecture_baseline=candidate_path,
            ),
            tmp_path / "candidate-output",
        )

    approved_path = _approve(output)
    with pytest.raises(ArchitectureError, match="baseline_stale"):
        prepare_sample(
            manifest_factory(
                tmp_path / "stale.json",
                repo,
                base,
                head,
                architecture_baseline=approved_path,
            ),
            tmp_path / "stale-output",
        )


def test_javascript_importer_is_a_one_hop_impacted_node(
    manifest_factory, tmp_path: Path
):
    repo = tmp_path / "js-repo"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.email", "tests@example.invalid")
    _git(repo, "config", "user.name", "Change Passport Tests")
    (repo / "a.ts").write_text(
        "import { value } from './b';\nexport const answer = value;\n",
        encoding="utf-8",
    )
    (repo / "b.ts").write_text("export const value = 1;\n", encoding="utf-8")
    _git(repo, "add", "a.ts", "b.ts")
    _git(repo, "commit", "-m", "initial modules")
    base = _git(repo, "rev-parse", "HEAD")
    (repo / "b.ts").write_text("export const value = 2;\n", encoding="utf-8")
    _git(repo, "add", "b.ts")
    _git(repo, "commit", "-m", "change value")
    head = _git(repo, "rev-parse", "HEAD")
    output = tmp_path / "js-output"

    prepare_sample(
        manifest_factory(tmp_path / "js.json", repo, base, head), output
    )
    delta = json.loads((output / "architecture-delta.json").read_text(encoding="utf-8"))

    assert len(delta["modified_node_ids"]) == 1
    assert len(delta["impacted_node_ids"]) == 1
    assert delta["impact_paths"][0]["relation"] == "imported_by"
    assert delta["impact_paths"][0]["depth"] == 1


def test_approval_requires_an_attributable_approved_decision(
    sample_repo, manifest_factory, tmp_path: Path
):
    repo, base, head = sample_repo
    output = tmp_path / "architecture"
    prepare_sample(
        manifest_factory(tmp_path / "sample.json", repo, base, head), output
    )

    with pytest.raises(ArchitectureError, match="explicitly approved"):
        approve_baseline_proposal(
            output / "architecture-baseline.proposal.json",
            output / "baseline-decision.template.json",
            output / "architecture-baseline.approved.json",
        )

    proposal_path = output / "architecture-baseline.proposal.json"
    proposal = json.loads(proposal_path.read_text(encoding="utf-8"))
    proposal["candidate_baseline"]["nodes"][0]["label"] = "tampered"
    tampered_path = output / "tampered-proposal.json"
    tampered_path.write_text(json.dumps(proposal), encoding="utf-8")
    decision = json.loads(
        (output / "baseline-decision.template.json").read_text(encoding="utf-8")
    )
    decision.update(
        {
            "decision": "approved",
            "actor": "test-owner",
            "decided_at": "2026-09-04T00:00:00Z",
        }
    )
    decision_path = output / "tampered-decision.json"
    decision_path.write_text(json.dumps(decision), encoding="utf-8")
    with pytest.raises(ArchitectureError, match="proposal hash"):
        approve_baseline_proposal(
            tampered_path,
            decision_path,
            output / "tampered-approved.json",
        )


def test_display_budget_keeps_changed_node_and_reports_folded_consumers(
    manifest_factory, tmp_path: Path
):
    repo = tmp_path / "wide-repo"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.email", "tests@example.invalid")
    _git(repo, "config", "user.name", "Change Passport Tests")
    (repo / "core.py").write_text("VALUE = 1\n", encoding="utf-8")
    for index in range(20):
        (repo / f"consumer_{index:02d}.py").write_text(
            "from core import VALUE\n", encoding="utf-8"
        )
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "initial graph")
    base = _git(repo, "rev-parse", "HEAD")
    (repo / "core.py").write_text("VALUE = 2\n", encoding="utf-8")
    _git(repo, "add", "core.py")
    _git(repo, "commit", "-m", "change core")
    head = _git(repo, "rev-parse", "HEAD")
    output = tmp_path / "wide-output"

    prepare_sample(
        manifest_factory(tmp_path / "wide.json", repo, base, head), output
    )
    delta = json.loads((output / "architecture-delta.json").read_text(encoding="utf-8"))
    mermaid = (output / "architecture-map.mmd").read_text(encoding="utf-8")

    assert len(delta["modified_node_ids"]) == 1
    assert delta["analysis_stats"]["displayed_nodes"] == 14
    assert delta["analysis_stats"]["omitted_nodes"] == 7
    assert len(delta["display_omissions"]["omitted_impacted_node_ids"]) == 7
    assert "subgraph B[变更前]" in mermaid
    assert "subgraph A[变更后]" in mermaid
    assert "静态导入" in mermaid
    assert "模块内容已修改" in mermaid
    assert "直接依赖已变更模块" in mermaid
    assert "… 其余 7 个一跳依赖/上下文模块" in mermaid
    assert "完整 ID 保留在 JSON" in mermaid
    assert "BEFORE" not in mermaid
    assert "AFTER" not in mermaid
    assert "direct consumer of a changed module" not in mermaid


def test_architecture_evidence_bindings_share_stable_node_and_impact_subjects(
    sample_repo, manifest_factory, tmp_path: Path
):
    repo, base, head = sample_repo
    output = tmp_path / "binding-output"
    prepare_sample(manifest_factory(tmp_path / "binding.json", repo, base, head), output)
    delta = json.loads((output / "architecture-delta.json").read_text(encoding="utf-8"))

    bindings = architecture_evidence_bindings(delta)
    node_bindings = [item for item in bindings if item["subject_type"] == "node"]
    assert [item["evidence_id"] for item in node_bindings] == [
        f"arch.node.{index:03d}" for index in range(1, len(node_bindings) + 1)
    ]
    assert {item["node_ids"][0] for item in node_bindings} == set(
        delta["added_node_ids"] + delta["removed_node_ids"] + delta["modified_node_ids"]
    )
