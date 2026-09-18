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
from .agent_provenance import (
    AgentProvenanceProvider,
    collect_agent_provenance,
    validate_agent_provenance,
)
from .generator_contract import build_generator_packet, validate_packet
from .git_evidence import collect_git_evidence, materialize_repository
from .html_renderer import render_review_html
from .models import ManifestError, SampleManifest, canonical_json_bytes, sha256_bytes
from .model_adapter import (
    OpenAICompatibleRawBriefProvider,
    _require_requested_human_language,
    generate_change_interpretation_with_model,
    generate_project_understanding_with_model,
    generate_report_translations_with_model,
    load_model_provider_config,
    parse_model_provider_config,
)
from .progress import ProgressRecorder
from .review_model import build_beginner_review_model
from .report_localization import (
    localized_control,
    review_translation_template,
    translation_template,
    validated_review_translations,
)
from .scoring import build_annotation_template, score_annotations
from .software_control import validate_software_control
from .semantic_analysis import (
    attach_context_sources,
    build_project_context_packet,
    project_understanding_cache_key,
    read_cached_project_understanding,
    target_profile_from_understanding,
    write_cached_project_understanding,
)
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
    provenance_provider: AgentProvenanceProvider | None = None,
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
        with progress.stage("agent_provenance", "读取可选的 AI 代码来源记录") as details:
            agent_provenance = collect_agent_provenance(
                materialized.repository.path,
                git.base_commit,
                git.head_commit,
                expected_added_lines=git.added_lines,
                expected_deleted_lines=git.deleted_lines,
                provider=provenance_provider,
            )
            details.update(
                provider=agent_provenance["provider"],
                status=agent_provenance["status"],
                coverage_percent=agent_provenance["summary"]["coverage_percent"],
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
                agent_provenance,
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
                "agent_provenance_identity": agent_provenance["normalized_sha256"],
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
            _write_json(output / "agent-provenance.json", agent_provenance)
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
        "agent_provenance": str(output / "agent-provenance.json"),
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
    generator: str = "auto",
    model_config_path: str | Path | None = None,
    model_config: Mapping[str, Any] | None = None,
    model_api_key: str | None = None,
    human_language: str = "zh-CN",
    provenance_provider: AgentProvenanceProvider | None = None,
) -> dict[str, Any]:
    """Run the local path from manifest to an owner-facing candidate report."""

    if model_config_path is not None and model_config is not None:
        raise ManifestError("provide model_config_path or model_config, not both")
    if human_language not in {"zh-CN", "en"}:
        raise ManifestError("human_language must be zh-CN or en")
    configured_provider: OpenAICompatibleRawBriefProvider | None = None
    provider_config = (
        load_model_provider_config(model_config_path)
        if model_config_path is not None
        else parse_model_provider_config(model_config)
        if model_config is not None
        else None
    )
    if model_api_key is not None and provider_config is None:
        raise ManifestError("a direct model credential requires a model provider config")
    resolved_generator = generator
    if generator == "auto":
        resolved_generator = "model" if provider_config is not None else "deterministic"
    if resolved_generator == "model":
        if provider_config is None:
            raise ManifestError("--model-config is required when --generator model")
        configured_provider = OpenAICompatibleRawBriefProvider(
            provider_config, api_key=model_api_key
        )
    elif resolved_generator != "deterministic":
        raise ManifestError(f"unsupported generator: {generator}")

    manifest = SampleManifest.load(manifest_path)
    output = manifest.validate_output_path(output_path)
    output.mkdir(parents=True, exist_ok=True)
    progress = ProgressRecorder(output, "analyze", manifest.sample_id)
    project_understanding_path: Path | None = None
    project_understanding_receipt: Path | None = None
    project_understanding_cache_hit: bool | None = None
    semantic_interpretation: dict[str, Any] | None = None
    change_interpretation_receipt: Path | None = None
    report_translation_receipt: Path | None = None
    materialized = None
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
        if configured_provider is not None:
            with progress.stage(
                "project_understanding",
                "模型先理解这个软件的用途和主要工作",
            ) as details:
                if materialized is None:
                    materialized = materialize_repository(
                        manifest.repository,
                        manifest.limits,
                        cache_root=default_cache_root(),
                        progress=lambda current, total, message: progress.update(
                            current, total, message
                        ),
                    )
                base_profile = _load_json(profile_path, "target profile draft")
                context = build_project_context_packet(
                    materialized.repository.path,
                    materialized.repository.head,
                    manifest.limits.git_timeout_seconds,
                    manifest.repository.path.name,
                    base_profile,
                )
                _write_json(output / "project-context.json", context)
                cache_key = project_understanding_cache_key(
                    context,
                    configured_provider.config_sha256,
                    configured_provider.model,
                    human_language,
                )
                understanding = read_cached_project_understanding(
                    default_cache_root(), cache_key, context
                )
                project_understanding_cache_hit = understanding is not None
                if understanding is not None:
                    _require_requested_human_language(
                        understanding,
                        human_language,
                        stage="cached project understanding",
                    )
                if understanding is None:
                    understanding, project_understanding_receipt = (
                        generate_project_understanding_with_model(
                            context, output, configured_provider,
                            human_language=human_language,
                        )
                    )
                    write_cached_project_understanding(
                        default_cache_root(), cache_key, understanding
                    )
                understanding_with_sources = attach_context_sources(understanding, context)
                project_understanding_path = output / "project-understanding.json"
                _write_json(project_understanding_path, understanding)
                if manifest.target_profile_path is None:
                    profile = target_profile_from_understanding(
                        base_profile,
                        understanding_with_sources,
                        materialized.repository.head,
                        human_language=human_language,
                    )
                    profile_path = output / "target-profile.model.json"
                    _write_json(profile_path, profile)
                details.update(
                    cache_hit=project_understanding_cache_hit,
                    provider=configured_provider.provider_name,
                    model=configured_provider.model,
                    component_count=len(understanding["components"]),
                    profile_path=str(profile_path),
                )
        prepared = prepare_sample(
            manifest_path,
            output,
            target_profile_override=profile_path,
            progress_recorder=progress,
            provenance_provider=provenance_provider,
        )
        packet = validate_packet(_load_json(prepared["packet_path"], "generator packet"))
        model_receipt: Path | None = None
        if resolved_generator == "deterministic":
            raw = draft_raw_brief(packet)
            raw_path = output / "raw-brief.auto.json"
        elif resolved_generator == "model":
            with progress.stage("change_interpretation", "模型结合项目理解解释这次变化") as details:
                if configured_provider is None:
                    raise ManifestError("configured model provider is unavailable")
                if project_understanding_path is None:
                    raise ManifestError("project understanding is unavailable")
                understanding = _load_json(
                    project_understanding_path, "project understanding"
                )
                semantic_interpretation, change_interpretation_receipt = (
                    generate_change_interpretation_with_model(
                        packet, understanding, output, configured_provider,
                        human_language=human_language,
                    )
                )
                raw = semantic_interpretation["raw_brief"]
                model_receipt = change_interpretation_receipt
                raw_path = output / "raw-brief.model.json"
                _write_json(
                    output / "change-interpretation.json", semantic_interpretation
                )
                details.update(
                    provider=configured_provider.provider_name,
                    model=configured_provider.model,
                    receipt=str(change_interpretation_receipt),
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
                semantic_interpretation=semantic_interpretation,
                analysis_mode=(
                    "full_model" if resolved_generator == "model" else "basic_evidence"
                ),
                human_language=human_language,
            )
            control_path = output / "software-control.auto.json"
            _write_json(control_path, control)
            if configured_provider is not None:
                target_language = "en" if human_language == "zh-CN" else "zh-CN"
                control_pack = translation_template(control, target_language)
                review_pack = review_translation_template(review, target_language)
                source_texts = sorted(
                    set(control_pack["translations"])
                    | set(review_pack["translations"])
                )
                with progress.stage(
                    "report_translation",
                    "生成另一种语言的负责人说明",
                ) as translation_details:
                    translation_input_sha = sha256_bytes(
                        canonical_json_bytes(
                            {
                                "control_identity": control["control_identity"],
                                "review_identity": review["review_identity"],
                                "source_language": human_language,
                                "target_language": target_language,
                                "texts": source_texts,
                            }
                        )
                    )
                    translated, report_translation_receipt = (
                        generate_report_translations_with_model(
                            source_texts,
                            output,
                            configured_provider,
                            source_language=human_language,
                            target_language=target_language,
                            input_sha256=translation_input_sha,
                        )
                    )
                    translations = translated["translations"]
                    control_pack["translations"] = {
                        source: translations[source]
                        for source in control_pack["translations"]
                    }
                    control_pack["review_text"] = {
                        "review_identity": review_pack["review_identity"],
                        "translations": {
                            source: translations[source]
                            for source in review_pack["translations"]
                        },
                    }
                    # Reuse the existing identity, completeness and language checks before
                    # the pack can affect the offline report.
                    localized_control(control, control_pack)
                    validated_review_translations(review, control_pack)
                    _write_json(output / "report-translations.json", control_pack)
                    translation_details.update(
                        source_language=human_language,
                        target_language=target_language,
                        text_count=len(source_texts),
                        receipt=str(report_translation_receipt),
                    )
            final = finalize_brief(
                prepared["packet_path"],
                raw_path,
                output,
                control_path,
            )
            details.update(
                generation_mode=(
                    "deterministic_local_no_model"
                    if resolved_generator == "deterministic"
                    else "model_first_project_and_change"
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
        "raw_brief_auto": str(raw_path) if resolved_generator == "deterministic" else None,
        "raw_brief_generated": str(raw_path),
        "generator": resolved_generator,
        "requested_generator": generator,
        "analysis_mode": "full_model" if resolved_generator == "model" else "basic_evidence",
        "model_run_receipt": str(model_receipt) if model_receipt is not None else None,
        "project_understanding": str(project_understanding_path) if project_understanding_path else None,
        "project_understanding_receipt": str(project_understanding_receipt) if project_understanding_receipt else None,
        "project_understanding_cache_hit": project_understanding_cache_hit,
        "change_interpretation": str(output / "change-interpretation.json") if semantic_interpretation else None,
        "change_interpretation_receipt": str(change_interpretation_receipt) if change_interpretation_receipt else None,
        "report_translations": (
            str(output / "report-translations.json")
            if report_translation_receipt is not None else None
        ),
        "report_translation_receipt": (
            str(report_translation_receipt)
            if report_translation_receipt is not None else None
        ),
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
    agent_provenance = None
    agent_provenance_path = packet_file.parent / "agent-provenance.json"
    if agent_provenance_path.is_file():
        agent_provenance = validate_agent_provenance(
            _load_json(agent_provenance_path, "agent provenance")
        )
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
            render_review_html(beginner_review, software_control,
                _load_json(output / "report-translations.json", "report translations")
                if software_control is not None
                and (output / "report-translations.json").is_file() else None,
                agent_provenance),
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
