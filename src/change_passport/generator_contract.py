from __future__ import annotations

import copy
from typing import Any, Mapping

from .architecture import DELTA_SCHEMA, architecture_evidence_entries
from .behavior_signals import behavior_signal_evidence
from .git_evidence import GitEvidence
from .models import ManifestError, SampleManifest, canonical_json_bytes, sha256_bytes

PACKET_SCHEMA = "change-passport.generator-packet.v1"
RAW_BRIEF_SCHEMA = "change-passport.raw-brief.v1"

SECTIONS = ("function", "architecture", "history", "attention")
CLAIM_TYPES = ("verified_fact", "inference", "unknown")
CONFIDENCE_LEVELS = ("high", "medium", "low")
IMPORTANCE_LEVELS = ("high", "medium", "low")
SCOPES = (
    "user_behavior_change",
    "code_change",
    "task_intent",
    "test_status",
    "architecture_change",
    "history_relation",
    "attention",
)


def _git_evidence_entries(git: GitEvidence) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = [
        {
            "id": "git.change_identity",
            "kind": "git",
            "authority": "git_fact",
            "content": (
                f"repository={git.repository_name}; base={git.base_commit}; "
                f"head={git.head_commit}"
            ),
            "source_ref": "git:commit-range",
            "limitations": [],
        },
        {
            "id": "git.diff_summary",
            "kind": "git",
            "authority": "git_fact",
            "content": (
                f"changed_files={len(git.files)}; added_lines={git.added_lines}; "
                f"deleted_lines={git.deleted_lines}; patch_sha256={git.patch_sha256}"
            ),
            "source_ref": "git:diff-summary",
            "limitations": [],
        },
    ]
    for index, item in enumerate(git.files, start=1):
        entries.append(
            {
                "id": f"git.file.{index:03d}",
                "kind": "git",
                "authority": "git_fact",
                "content": (
                    f"status={item.status}; path={item.path}; added_lines={item.added_lines}; "
                    f"deleted_lines={item.deleted_lines}; binary={str(item.binary).lower()}"
                ),
                "source_ref": f"git:path:{item.path}",
                "limitations": [],
            }
        )
    entries.append(
        {
            "id": "git.patch",
            "kind": "git",
            "authority": "git_fact",
            "content": git.patch_excerpt,
            "source_ref": f"git:patch:{git.patch_sha256}",
            "limitations": ["patch_truncated"] if git.patch_truncated else [],
        }
    )
    entries.extend(
        behavior_signal_evidence(
            git.patch_excerpt,
            patch_sha256=git.patch_sha256,
            patch_truncated=git.patch_truncated,
        )
    )
    return entries


def build_generator_packet(
    manifest: SampleManifest,
    git: GitEvidence,
    architecture_delta: Mapping[str, Any] | None = None,
    system_snapshot_identity: str | None = None,
) -> dict[str, Any]:
    evidence = _git_evidence_entries(git)
    if architecture_delta is not None:
        if architecture_delta.get("schema_version") != DELTA_SCHEMA:
            raise ManifestError("architecture delta schema is invalid")
        evidence.extend(architecture_evidence_entries(architecture_delta))
    for item in manifest.evidence_inputs:
        evidence.append(
            {
                "id": item.evidence_id,
                "kind": item.kind,
                "authority": item.authority,
                "content": item.source.read_text(
                    manifest.manifest_dir, manifest.limits.max_input_bytes
                ),
                "source_ref": f"manifest:{item.evidence_id}:{item.source.source_type}",
                "limitations": [],
            }
        )

    packet: dict[str, Any] = {
        "schema_version": PACKET_SCHEMA,
        "sample_id": manifest.sample_id,
        "change": {
            "repository_name": git.repository_name,
            "base_commit": git.base_commit,
            "head_commit": git.head_commit,
            "changed_files": len(git.files),
            "added_lines": git.added_lines,
            "deleted_lines": git.deleted_lines,
            "patch_sha256": git.patch_sha256,
            "patch_truncated": git.patch_truncated,
        },
        "generator_instructions": [
            "你只能使用 evidence 数组中的内容，不得假设可以访问仓库、聊天记录或隐藏标准答案。",
            "每条结论最多引用 evidence 中已有的 ID；没有足够证据时 claim_type 必须为 unknown。",
            "任务意图不能从 Git Diff 反推，测试通过不能从代码或自报推断，历史约束必须引用 approved_history。",
            "回答为什么这样改时先检查 original_task：用户明确说出的目标可以生成 task_intent；宽泛目标只能保留边界。retrospective_claim 只能标为 AI 的解释或完成自报，不能单独充当用户意图。",
            "架构说明只能引用 architecture_delta 与 architecture_fact；不得自行增加节点、边、影响路径或另画一张图。",
            "四个 section 必须是 function、architecture、history、attention，每区最多三条。",
            "只输出符合 output_contract 的 JSON，不输出 Markdown、解释或代码围栏。",
        ],
        "output_contract": {
            "schema_version": RAW_BRIEF_SCHEMA,
            "root": {
                "schema_version": RAW_BRIEF_SCHEMA,
                "claims": "array",
                "generator_metadata": "optional self-reported object: provider, model, mode, generated_at",
            },
            "claim": {
                "required": [
                    "id",
                    "section",
                    "scope",
                    "text",
                    "claim_type",
                    "confidence",
                    "importance",
                    "evidence_ids",
                    "limitations",
                    "next_check",
                ],
                "section": list(SECTIONS),
                "scope": list(SCOPES),
                "claim_type": list(CLAIM_TYPES),
                "confidence": list(CONFIDENCE_LEVELS),
                "importance": list(IMPORTANCE_LEVELS),
                "evidence_ids": "array of IDs from allowed_evidence_ids only",
                "limitations": "array of short strings",
                "next_check": "short string or null; suggestion only, never an automatic action",
            },
        },
        "allowed_evidence_ids": [item["id"] for item in evidence],
        "evidence": evidence,
        "hard_limits": {"max_claims_per_section": 3},
    }
    if architecture_delta is not None:
        packet["architecture_delta"] = copy.deepcopy(dict(architecture_delta))
    if system_snapshot_identity is not None:
        packet["system_snapshot_identity"] = system_snapshot_identity
    packet["packet_sha256"] = sha256_bytes(canonical_json_bytes(packet))
    return packet


def validate_packet(packet: Any) -> dict[str, Any]:
    if not isinstance(packet, Mapping):
        raise ManifestError("generator packet must be an object")
    result = copy.deepcopy(dict(packet))
    if result.get("schema_version") != PACKET_SCHEMA:
        raise ManifestError(f"generator packet schema must be {PACKET_SCHEMA}")
    claimed_hash = result.pop("packet_sha256", None)
    actual_hash = sha256_bytes(canonical_json_bytes(result))
    if claimed_hash != actual_hash:
        raise ManifestError("generator packet hash does not match its content")
    result["packet_sha256"] = claimed_hash
    evidence = result.get("evidence")
    allowed = result.get("allowed_evidence_ids")
    if not isinstance(evidence, list) or not isinstance(allowed, list):
        raise ManifestError("generator packet evidence contract is invalid")
    ids = [item.get("id") for item in evidence if isinstance(item, Mapping)]
    if ids != allowed or len(ids) != len(set(ids)):
        raise ManifestError("generator packet evidence IDs are inconsistent")
    architecture_delta = result.get("architecture_delta")
    if architecture_delta is not None and (
        not isinstance(architecture_delta, Mapping)
        or architecture_delta.get("schema_version") != DELTA_SCHEMA
    ):
        raise ManifestError("generator packet architecture delta is invalid")
    forbidden_keys = {"hidden_ground_truth", "ground_truth", "manifest_path", "repository_path"}

    def walk(value: Any) -> None:
        if isinstance(value, Mapping):
            overlap = forbidden_keys & set(value)
            if overlap:
                raise ManifestError(f"generator packet contains forbidden keys: {sorted(overlap)}")
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(result)
    return result
