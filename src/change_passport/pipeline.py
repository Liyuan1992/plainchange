from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Mapping

from .architecture import (
    approve_baseline_proposal as approve_proposal,
    build_architecture_bundle,
    render_mermaid,
    validate_system_architecture_snapshot,
)
from .generator_contract import build_generator_packet, validate_packet
from .git_evidence import collect_git_evidence
from .html_renderer import render_review_html
from .models import ManifestError, SampleManifest, canonical_json_bytes
from .review_model import build_beginner_review_model
from .scoring import build_annotation_template, score_annotations
from .validator import render_markdown, validate_raw_brief


def _load_json(path: str | Path, label: str) -> Any:
    target = Path(path).resolve(strict=True)
    try:
        return json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ManifestError(f"{label} is not valid UTF-8 JSON: {target}") from exc


def _atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(content)
    os.replace(temporary, path)


def _write_json(path: Path, value: Any) -> None:
    _atomic_write(path, canonical_json_bytes(value) + b"\n")


def _write_text(path: Path, value: str) -> None:
    _atomic_write(path, value.encode("utf-8"))


def prepare_sample(manifest_path: str | Path, output_path: str | Path) -> dict[str, Any]:
    manifest = SampleManifest.load(manifest_path)
    output = manifest.validate_output_path(output_path)
    git = collect_git_evidence(manifest.repository, manifest.limits)
    architecture = build_architecture_bundle(manifest, git)
    packet = build_generator_packet(manifest, git, architecture["delta"])
    validate_packet(packet)
    output.mkdir(parents=True, exist_ok=True)

    evidence_bundle = {
        "schema_version": "change-passport.evidence-bundle.v1",
        "sample_id": manifest.sample_id,
        "packet_sha256": packet["packet_sha256"],
        "change": packet["change"],
        "evidence": packet["evidence"],
    }
    _write_json(output / "evidence.json", evidence_bundle)
    _write_json(output / "architecture-delta.json", architecture["delta"])
    _write_json(
        output / "system-architecture.json",
        architecture["system_architecture"],
    )
    _write_text(output / "architecture-map.mmd", render_mermaid(architecture["delta"]))
    _write_json(output / "architecture-baseline.proposal.json", architecture["proposal"])
    _write_json(output / "baseline-decision.template.json", architecture["decision_template"])
    _write_json(output / "generator-packet.json", packet)
    _write_text(
        output / "GENERATOR_REQUEST.md",
        "# 受约束模型生成请求\n\n"
        "主架构图已由确定性 `architecture-delta.json` 生成。只读取同目录的 "
        "`generator-packet.json`，按照其中的 `generator_instructions` 和 "
        "`output_contract` 生成严格 JSON，并保存为 `raw-brief.input.json`。\n\n"
        "禁止读取原始 manifest、目标仓库、hidden ground truth 或其他文件。\n",
    )
    return {
        "sample_id": manifest.sample_id,
        "output_dir": str(output),
        "packet_path": str(output / "generator-packet.json"),
        "packet_sha256": packet["packet_sha256"],
        "architecture_delta": str(output / "architecture-delta.json"),
        "architecture_map": str(output / "architecture-map.mmd"),
        "system_architecture": str(output / "system-architecture.json"),
        "baseline_proposal": str(output / "architecture-baseline.proposal.json"),
        "baseline_decision_template": str(output / "baseline-decision.template.json"),
        "baseline_status": architecture["delta"]["baseline_validation"]["status"],
        "analysis_stats": architecture["delta"]["analysis_stats"],
        "next_action": "provide generator-packet.json to a constrained model",
    }


def finalize_brief(
    packet_path: str | Path,
    raw_brief_path: str | Path,
    output_path: str | Path,
) -> dict[str, Any]:
    packet_file = Path(packet_path).resolve(strict=True)
    packet = validate_packet(_load_json(packet_file, "generator packet"))
    raw = _load_json(raw_brief_path, "raw brief")
    brief = validate_raw_brief(packet, raw)
    output = Path(output_path).resolve(strict=False)
    artifact_root = packet_file.parent
    if output != artifact_root and not output.is_relative_to(artifact_root):
        raise ManifestError("finalize output must stay inside the prepared artifact directory")
    output.mkdir(parents=True, exist_ok=True)
    _write_json(output / "raw-brief.json", raw)
    _write_json(output / "brief.json", brief)
    architecture_delta = brief.get("architecture_delta")
    beginner_review = None
    if isinstance(architecture_delta, Mapping):
        system_architecture_path = artifact_root / "system-architecture.json"
        if not system_architecture_path.is_file():
            raise ManifestError(
                "prepared system architecture snapshot is missing"
            )
        system_architecture = validate_system_architecture_snapshot(
            _load_json(system_architecture_path, "system architecture snapshot")
        )
        _write_json(output / "architecture-delta.json", architecture_delta)
        _write_json(output / "system-architecture.json", system_architecture)
        _write_text(output / "architecture-map.mmd", render_mermaid(architecture_delta))
        beginner_review = build_beginner_review_model(
            brief,
            system_architecture,
            packet["evidence"],
        )
        _write_json(output / "beginner-review.json", beginner_review)
        _write_text(output / "review.html", render_review_html(beginner_review))
    _write_text(output / "brief.md", render_markdown(brief))
    annotation = build_annotation_template(brief)
    _write_json(output / "annotation.template.json", annotation)
    return {
        "sample_id": brief["sample_id"],
        "brief_identity": brief["brief_identity"],
        "brief_json": str(output / "brief.json"),
        "brief_markdown": str(output / "brief.md"),
        "architecture_delta": (
            str(output / "architecture-delta.json")
            if isinstance(architecture_delta, Mapping)
            else None
        ),
        "architecture_map": (
            str(output / "architecture-map.mmd")
            if isinstance(architecture_delta, Mapping)
            else None
        ),
        "system_architecture": (
            str(output / "system-architecture.json")
            if isinstance(architecture_delta, Mapping)
            else None
        ),
        "beginner_review": (
            str(output / "beginner-review.json")
            if beginner_review is not None
            else None
        ),
        "review_html": (
            str(output / "review.html") if beginner_review is not None else None
        ),
        "annotation_template": str(output / "annotation.template.json"),
        "validation_summary": brief["validation_summary"],
    }


def score_sample(
    brief_path: str | Path,
    annotation_path: str | Path,
    output_path: str | Path,
) -> dict[str, Any]:
    brief_file = Path(brief_path).resolve(strict=True)
    brief = _load_json(brief_file, "validated brief")
    if not isinstance(brief, Mapping) or brief.get("schema_version") != "change-passport.validated-brief.v1":
        raise ManifestError("brief schema is invalid")
    annotation = _load_json(annotation_path, "annotation")
    score = score_annotations(brief, annotation)
    output = Path(output_path).resolve(strict=False)
    if output.exists() and output.is_dir():
        output = output / "score.json"
    artifact_root = brief_file.parent
    if output.parent != artifact_root and not output.parent.is_relative_to(artifact_root):
        raise ManifestError("score output must stay inside the validated artifact directory")
    _write_json(output, score)
    return {"score_path": str(output), **score}


def approve_baseline_proposal(
    proposal_path: str | Path,
    decision_path: str | Path,
    output_path: str | Path,
) -> dict[str, Any]:
    proposal_file = Path(proposal_path).resolve(strict=True)
    proposal = _load_json(proposal_file, "baseline proposal")
    decision = _load_json(decision_path, "baseline decision")
    approved = approve_proposal(proposal, decision)
    output = Path(output_path).resolve(strict=False)
    if output.exists() and output.is_dir():
        output = output / "architecture-baseline.approved.json"
    artifact_root = proposal_file.parent
    if output.parent != artifact_root:
        raise ManifestError("approved baseline output must stay beside its proposal")
    _write_json(output, approved)
    return {
        "baseline_path": str(output),
        "baseline_id": approved["baseline_id"],
        "commit_identity": approved["commit_identity"],
        "status": approved["status"],
    }
