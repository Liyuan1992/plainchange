from __future__ import annotations

import json
import os
from dataclasses import replace
from pathlib import Path
from typing import Any, Mapping

from .architecture import (
    approve_baseline_proposal as approve_proposal,
    build_architecture_bundle,
    render_mermaid,
    validate_system_architecture_snapshot,
)
from .analysis_cache import AnalysisCache, default_cache_root
from .auto_draft import draft_raw_brief, draft_software_control, draft_target_profile
from .generator_contract import build_generator_packet, validate_packet
from .git_evidence import collect_git_evidence, materialize_repository
from .html_renderer import render_review_html
from .models import ManifestError, SampleManifest, canonical_json_bytes
from .model_adapter import (
    OpenAICompatibleRawBriefProvider,
    generate_raw_brief_with_model,
    load_model_provider_config,
)
from .progress import ProgressRecorder
from .review_model import build_beginner_review_model
from .scoring import build_annotation_template, score_annotations
from .software_control import validate_software_control
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


def prepare_sample(
    manifest_path: str | Path,
    output_path: str | Path,
    *,
    target_profile_override: Path | None = None,
    progress_recorder: ProgressRecorder | None = None,
) -> dict[str, Any]:
    manifest = SampleManifest.load(manifest_path)
    if target_profile_override is not None:
        manifest = replace(
            manifest,
            target_profile_path=target_profile_override.resolve(strict=True),
        )
    output = manifest.validate_output_path(output_path)
    output.mkdir(parents=True, exist_ok=True)
    owns_progress = progress_recorder is None
    progress = progress_recorder or ProgressRecorder(output, "prepare", manifest.sample_id)
    cache: AnalysisCache | None = None
    try:
        with progress.stage("git_preflight", "检查并准备 Git 对象") as details:
            materialized = materialize_repository(
                manifest.repository,
                manifest.limits,
                cache_root=default_cache_root(),
                progress=lambda current, total, message: progress.update(
                    current, total, message
                ),
            )
            details.update(materialized.to_dict())
        with progress.stage("git_evidence", "收集固定版本的 Git 事实") as details:
            git = collect_git_evidence(materialized.repository, manifest.limits)
            git = replace(git, repository_name=manifest.repository.path.name)
            details.update(
                changed_files=len(git.files),
                patch_bytes=git.patch_bytes,
            )
        with progress.stage("architecture", "解析静态结构并复用缓存") as details:
            cache = AnalysisCache(default_cache_root())
            architecture = build_architecture_bundle(
                manifest,
                git,
                analysis_repo_path=materialized.repository.path,
                analysis_cache=cache,
                progress=lambda current, total, message: progress.update(
                    current, total, message
                ),
            )
            details.update(architecture["cache_stats"])
        with progress.stage("generator_packet", "生成受约束说明输入"):
            packet = build_generator_packet(
                manifest,
                git,
                architecture["delta"],
                architecture["system_architecture"]["snapshot_identity"],
            )
            validate_packet(packet)

        with progress.stage("write_artifacts", "写入可复核分析产物"):
            evidence_bundle = {
                "schema_version": "change-passport.evidence-bundle.v1",
                "sample_id": manifest.sample_id,
                "packet_sha256": packet["packet_sha256"],
                "change": packet["change"],
                "evidence": packet["evidence"],
                "git_materialization": materialized.to_dict(),
                "system_snapshot_identity": architecture["system_architecture"]["snapshot_identity"],
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
    except BaseException as exc:
        if owns_progress:
            progress.finish(status="failed", error=exc)
        raise
    finally:
        if cache is not None:
            cache.close()
    if owns_progress:
        progress.finish(status="succeeded")
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
        "cache_stats": architecture["cache_stats"],
        "git_object_status": materialized.object_status,
        "run_receipt": str(output / "run-receipt.json"),
        "next_action": "provide generator-packet.json to a constrained model",
    }


def analyze_sample(
    manifest_path: str | Path,
    output_path: str | Path,
    *,
    generator: str = "deterministic",
    model_config_path: str | Path | None = None,
) -> dict[str, Any]:
    """Run the local path from manifest to an owner-facing candidate report."""

    configured_provider: OpenAICompatibleRawBriefProvider | None = None
    if generator == "model":
        if model_config_path is None:
            raise ManifestError("--model-config is required when --generator model")
        configured_provider = OpenAICompatibleRawBriefProvider(
            load_model_provider_config(model_config_path)
        )
    elif generator != "deterministic":
        raise ManifestError(f"unsupported generator: {generator}")

    manifest = SampleManifest.load(manifest_path)
    output = manifest.validate_output_path(output_path)
    output.mkdir(parents=True, exist_ok=True)
    progress = ProgressRecorder(output, "analyze", manifest.sample_id)
    try:
        profile_path = manifest.target_profile_path
        if profile_path is None:
            with progress.stage("profile_draft", "自动生成项目分区和软件工作图初稿") as details:
                materialized = materialize_repository(
                    manifest.repository,
                    manifest.limits,
                    cache_root=default_cache_root(),
                    progress=lambda current, total, message: progress.update(
                        current, total, message
                    ),
                )
                profile = draft_target_profile(
                    materialized.repository.path,
                    materialized.repository.head,
                    manifest.limits.git_timeout_seconds,
                    manifest.repository.path.name,
                )
                profile_path = output / "target-profile.draft.json"
                _write_json(profile_path, profile)
                details.update(
                    profile_path=str(profile_path),
                    section_count=len(profile["sections"]) - 1,
                    status="candidate_requires_owner_confirmation",
                )
        prepared = prepare_sample(
            manifest_path,
            output,
            target_profile_override=profile_path,
            progress_recorder=progress,
        )
        packet = validate_packet(_load_json(prepared["packet_path"], "generator packet"))
        model_receipt: Path | None = None
        if generator == "deterministic":
            raw = draft_raw_brief(packet)
            raw_path = output / "raw-brief.auto.json"
        elif generator == "model":
            with progress.stage("model_generation", "配置模型生成受约束候选说明") as details:
                if configured_provider is None:
                    raise ManifestError("configured model provider is unavailable")
                raw, model_receipt = generate_raw_brief_with_model(
                    packet, output, configured_provider
                )
                raw_path = output / "raw-brief.model.json"
                details.update(
                    provider=configured_provider.provider_name,
                    model=configured_provider.model,
                    receipt=str(model_receipt),
                )
        with progress.stage("owner_draft", "校验并生成负责人候选说明") as details:
            _write_json(raw_path, raw)
            first = finalize_brief(prepared["packet_path"], raw_path, output)
            brief = _load_json(first["brief_json"], "validated brief")
            review = _load_json(first["beginner_review"], "beginner review")
            system_architecture = _load_json(first["system_architecture"], "system architecture")
            control = draft_software_control(
                brief,
                review,
                system_architecture,
                packet["evidence"],
            )
            control_path = output / "software-control.auto.json"
            _write_json(control_path, control)
            final = finalize_brief(
                prepared["packet_path"],
                raw_path,
                output,
                control_path,
            )
            details.update(
                generation_mode=(
                    "deterministic_local_no_model"
                    if generator == "deterministic"
                    else "constrained_configured_model"
                ),
                owner_draft_status="candidate_requires_owner_confirmation",
            )
    except BaseException as exc:
        progress.finish(status="failed", error=exc)
        raise
    progress.finish(status="succeeded")
    return {
        **prepared,
        **final,
        "target_profile_draft": str(profile_path) if manifest.target_profile_path is None else None,
        "raw_brief_auto": str(raw_path) if generator == "deterministic" else None,
        "raw_brief_generated": str(raw_path),
        "generator": generator,
        "model_run_receipt": str(model_receipt) if model_receipt is not None else None,
        "software_control_auto": str(control_path),
        "review_html": str(output / "review.html"),
        "run_receipt": str(output / "run-receipt.json"),
        "next_action": "open review.html; confirm or revise the candidate owner draft",
    }


def finalize_brief(
    packet_path: str | Path,
    raw_brief_path: str | Path,
    output_path: str | Path,
    software_control_path: str | Path | None = None,
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
        expected_snapshot_identity = packet.get("system_snapshot_identity")
        if (
            expected_snapshot_identity is not None
            and system_architecture["snapshot_identity"] != expected_snapshot_identity
        ):
            raise ManifestError(
                "prepared system architecture snapshot does not match the generator packet"
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
        software_control = None
        if software_control_path is not None:
            software_control = validate_software_control(
                _load_json(software_control_path, "software control"),
                brief=brief,
                review=beginner_review,
                system_architecture=system_architecture,
            )
            _write_json(output / "software-control.json", software_control)
        _write_text(
            output / "review.html",
            render_review_html(beginner_review, software_control),
        )
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
        "software_control": (
            str(output / "software-control.json")
            if beginner_review is not None and software_control_path is not None
            else None
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
