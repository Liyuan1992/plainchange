from __future__ import annotations

from pathlib import Path

from plainchange.generator_contract import build_generator_packet
from plainchange.git_evidence import collect_git_evidence
from plainchange.models import SampleManifest
from plainchange.validator import render_markdown, validate_raw_brief


def _packet(sample_repo, manifest_factory, tmp_path: Path):
    repo, base, head = sample_repo
    manifest = SampleManifest.load(manifest_factory(tmp_path / "sample.json", repo, base, head))
    return build_generator_packet(
        manifest, collect_git_evidence(manifest.repository, manifest.limits)
    )


def _claim(
    claim_id: str,
    section: str,
    scope: str,
    text: str,
    evidence_ids: list[str],
    *,
    claim_type: str = "verified_fact",
    importance: str = "high",
):
    return {
        "id": claim_id,
        "section": section,
        "scope": scope,
        "text": text,
        "claim_type": claim_type,
        "confidence": "high" if claim_type != "unknown" else "low",
        "importance": importance,
        "evidence_ids": evidence_ids,
        "limitations": [],
        "next_check": None,
    }


def test_valid_claim_is_accepted_and_rendered(sample_repo, manifest_factory, tmp_path: Path):
    packet = _packet(sample_repo, manifest_factory, tmp_path)
    raw = {
        "schema_version": "change-passport.raw-brief.v1",
        "claims": [
            _claim(
                "function.named-greeting",
                "function",
                "user_behavior_change",
                "问候功能现在接收姓名参数。",
                ["task.original", "git.patch"],
            )
        ],
    }

    brief = validate_raw_brief(packet, raw)
    claim = next(item for item in brief["claims"] if item["id"] == "function.named-greeting")

    assert claim["status"] == "accepted"
    assert claim["claim_type"] == "verified_fact"
    assert "问候功能" in render_markdown(brief)
    assert {item["section"] for item in brief["claims"]} == {
        "function",
        "architecture",
        "history",
        "attention",
    }


def test_unknown_evidence_id_is_rejected(sample_repo, manifest_factory, tmp_path: Path):
    packet = _packet(sample_repo, manifest_factory, tmp_path)
    raw = {
        "schema_version": "change-passport.raw-brief.v1",
        "claims": [
            _claim(
                "function.fake",
                "function",
                "code_change",
                "模型编造了事实。",
                ["git.does-not-exist"],
            )
        ],
    }

    brief = validate_raw_brief(packet, raw)
    claim = next(item for item in brief["claims"] if item["id"] == "function.fake")

    assert claim["status"] == "rejected"
    assert claim["claim_type"] == "unknown"
    assert "模型编造了事实" not in claim["text"]
    assert brief["validation_summary"]["rejected"] == 1


def test_wrong_authority_is_downgraded(sample_repo, manifest_factory, tmp_path: Path):
    packet = _packet(sample_repo, manifest_factory, tmp_path)
    raw = {
        "schema_version": "change-passport.raw-brief.v1",
        "claims": [
            _claim(
                "history.unapproved",
                "history",
                "history_relation",
                "本次修改违反了历史约束。",
                ["git.patch", "task.original"],
            )
        ],
    }

    brief = validate_raw_brief(packet, raw)
    claim = next(item for item in brief["claims"] if item["id"] == "history.unapproved")

    assert claim["status"] == "downgraded"
    assert claim["claim_type"] == "unknown"
    assert any("approved_history" in value for value in claim["limitations"])


def test_unknown_claim_uses_safe_section_text(sample_repo, manifest_factory, tmp_path: Path):
    packet = _packet(sample_repo, manifest_factory, tmp_path)
    raw = {
        "schema_version": "change-passport.raw-brief.v1",
        "claims": [
            _claim(
                "architecture.unknown",
                "architecture",
                "architecture_change",
                "系统架构肯定已经彻底重写。",
                [],
                claim_type="unknown",
            )
        ],
    }

    brief = validate_raw_brief(packet, raw)
    claim = next(item for item in brief["claims"] if item["id"] == "architecture.unknown")

    assert claim["status"] == "accepted"
    assert "彻底重写" not in claim["text"]
    assert "证据不足" in claim["text"]


def test_section_scope_mismatch_is_downgraded(sample_repo, manifest_factory, tmp_path: Path):
    packet = _packet(sample_repo, manifest_factory, tmp_path)
    raw = {
        "schema_version": "change-passport.raw-brief.v1",
        "claims": [
            _claim(
                "history.disguised-code-change",
                "history",
                "code_change",
                "普通代码变化被伪装成历史结论。",
                ["git.patch"],
            )
        ],
    }

    brief = validate_raw_brief(packet, raw)
    claim = next(
        item for item in brief["claims"] if item["id"] == "history.disguised-code-change"
    )

    assert claim["status"] == "downgraded"
    assert claim["claim_type"] == "unknown"
    assert any("不能用于" in value for value in claim["limitations"])
