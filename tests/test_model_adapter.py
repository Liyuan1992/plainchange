from __future__ import annotations

import json
from pathlib import Path

import pytest

from plainchange.generator_contract import validate_packet
from plainchange.model_adapter import (
    ModelGenerationError,
    OpenAICompatibleRawBriefProvider,
    _bound_model_evidence_budgets,
    _bound_change_summary_evidence,
    _change_interpretation_prompt,
    _require_requested_human_language,
    generate_raw_brief_with_model,
    load_model_provider_config,
    raw_brief_json_schema,
)
from plainchange.pipeline import prepare_sample


def _write_config(path: Path, **overrides) -> Path:
    value = {
        "schema_version": "change-passport.model-provider.v1",
        "provider_id": "compatible-test",
        "base_url": "https://models.example.com/v1",
        "model": "owner-selected-model",
        "api_key_env": "TEST_MODEL_API_KEY",
        "timeout_seconds": 120,
        "response_format": "json_schema",
    }
    value.update(overrides)
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def _model_claims(packet: dict) -> dict:
    evidence_id = packet["allowed_evidence_ids"][0]
    return {
        "schema_version": "change-passport.raw-brief.v1",
        "claims": [
            {
                "id": f"{section}.model",
                "section": section,
                "scope": "code_change" if section != "attention" else "attention",
                "text": "模型候选说明。" if section != "attention" else "仍需运行验证。",
                "claim_type": "verified_fact" if section == "function" else "unknown",
                "confidence": "high" if section == "function" else "low",
                "importance": "high",
                "evidence_ids": [evidence_id] if section == "function" else [],
                "limitations": ["仅使用受约束证据包"],
                "next_check": None,
            }
            for section in ("function", "architecture", "history", "attention")
        ],
    }


def _completion(raw: dict) -> dict:
    return {
        "id": "chatcmpl-test",
        "model": "provider-resolved-model",
        "choices": [
            {
                "finish_reason": "stop",
                "message": {"role": "assistant", "content": json.dumps(raw)},
            }
        ],
        "usage": {"prompt_tokens": 120, "completion_tokens": 80, "total_tokens": 200},
    }


def test_config_rejects_embedded_secret_and_unsafe_url(tmp_path: Path):
    secret = json.loads(_write_config(tmp_path / "secret.json").read_text())
    secret["api_key"] = "must-not-be-here"
    (tmp_path / "secret.json").write_text(json.dumps(secret), encoding="utf-8")
    with pytest.raises(ModelGenerationError, match="extra=.*api_key"):
        load_model_provider_config(tmp_path / "secret.json")

    _write_config(tmp_path / "url.json", base_url="https://user:password@example.com/v1")
    with pytest.raises(ModelGenerationError, match="must not contain credentials"):
        load_model_provider_config(tmp_path / "url.json")


@pytest.mark.parametrize(
    ("mode", "expected"),
    [
        ("json_schema", "json_schema"),
        ("json_object", "json_object"),
        ("prompt_only", None),
    ],
)
def test_compatible_adapter_supports_three_output_modes(
    sample_repo, manifest_factory, tmp_path: Path, monkeypatch, mode, expected
):
    repo, base, head = sample_repo
    manifest = manifest_factory(tmp_path / "sample.json", repo, base, head)
    prepared = prepare_sample(manifest, tmp_path / "prepared")
    packet = validate_packet(
        json.loads(Path(prepared["packet_path"]).read_text(encoding="utf-8"))
    )
    config = load_model_provider_config(
        _write_config(tmp_path / "provider.json", response_format=mode)
    )
    captured = {}

    def fake_post(url, payload, timeout_seconds, headers):
        captured.update(url=url, payload=payload, timeout=timeout_seconds, headers=headers)
        return _completion(_model_claims(packet))

    monkeypatch.setenv("TEST_MODEL_API_KEY", "secret-test-value")
    monkeypatch.setattr("plainchange.model_adapter._post_json", fake_post)
    provider = OpenAICompatibleRawBriefProvider(config)
    raw, receipt_path = generate_raw_brief_with_model(packet, tmp_path / "prepared", provider)

    assert raw["generator_metadata"]["provider"] == "compatible-test"
    assert captured["url"] == "https://models.example.com/v1/chat/completions"
    assert captured["headers"]["Authorization"] == "Bearer secret-test-value"
    assert json.loads(captured["payload"]["messages"][1]["content"]) == packet
    assert str(repo) not in captured["payload"]["messages"][1]["content"]
    actual = captured["payload"].get("response_format", {}).get("type")
    assert actual == expected
    if mode == "json_schema":
        assert captured["payload"]["response_format"]["json_schema"]["schema"] == (
            raw_brief_json_schema(packet["allowed_evidence_ids"])
        )
    receipt_text = receipt_path.read_text(encoding="utf-8")
    assert "secret-test-value" not in receipt_text
    receipt = json.loads(receipt_text)
    assert receipt["status"] == "succeeded"
    assert receipt["telemetry"]["prompt_tokens"] == 120
    assert receipt["telemetry"]["endpoint_origin"] == "https://models.example.com"
    assert receipt["provider_config_sha256"] == config.config_sha256


def test_missing_environment_credential_fails_before_request_and_keeps_receipt(
    sample_repo, manifest_factory, tmp_path: Path, monkeypatch
):
    repo, base, head = sample_repo
    manifest = manifest_factory(tmp_path / "sample.json", repo, base, head)
    prepared = prepare_sample(manifest, tmp_path / "prepared")
    packet = validate_packet(
        json.loads(Path(prepared["packet_path"]).read_text(encoding="utf-8"))
    )
    config = load_model_provider_config(_write_config(tmp_path / "provider.json"))
    monkeypatch.delenv("TEST_MODEL_API_KEY", raising=False)

    def should_not_call(*_args, **_kwargs):
        raise AssertionError("request must not be sent without the configured credential")

    monkeypatch.setattr("plainchange.model_adapter._post_json", should_not_call)
    with pytest.raises(ModelGenerationError, match="TEST_MODEL_API_KEY"):
        generate_raw_brief_with_model(
            packet,
            tmp_path / "prepared",
            OpenAICompatibleRawBriefProvider(config),
        )

    receipt = json.loads(
        (tmp_path / "prepared" / "model-run-receipt.json").read_text(encoding="utf-8")
    )
    assert receipt["status"] == "failed"
    assert receipt["output_sha256"] is None


def test_raw_brief_schema_requires_bounded_claims():
    claims = raw_brief_json_schema(["git.diff_summary"])["properties"]["claims"]
    assert claims["minItems"] == 4
    assert claims["maxItems"] == 12


def test_model_prompt_uses_explicit_english_owner_language(
    sample_repo, manifest_factory, tmp_path: Path, monkeypatch
):
    repo, base, head = sample_repo
    manifest = manifest_factory(tmp_path / "sample.json", repo, base, head)
    prepared = prepare_sample(manifest, tmp_path / "prepared")
    packet = validate_packet(json.loads(Path(prepared["packet_path"]).read_text(encoding="utf-8")))
    config = load_model_provider_config(_write_config(tmp_path / "provider.json"))
    captured = {}

    def fake_post(_url, payload, _timeout, _headers):
        captured.update(payload=payload)
        raw = _model_claims(packet)
        for claim in raw["claims"]:
            claim["text"] = "Model candidate explanation."
            claim["limitations"] = ["Only the bounded evidence packet was used."]
        return _completion(raw)

    monkeypatch.setenv("TEST_MODEL_API_KEY", "secret-test-value")
    monkeypatch.setattr("plainchange.model_adapter._post_json", fake_post)
    raw, _telemetry = OpenAICompatibleRawBriefProvider(config).generate(
        packet, human_language="en"
    )

    assert "Use English for all human-facing text" in captured["payload"]["messages"][0]["content"]
    assert raw["generator_metadata"]["human_language"] == "en"


def test_model_evidence_budget_only_removes_surplus_references():
    raw = {"change_summary": {"evidence_ids": [f"git.file.{index:03d}" for index in range(30)]}}

    bounded, normalizations = _bound_change_summary_evidence(raw)

    assert len(bounded["change_summary"]["evidence_ids"]) == 24
    assert bounded["change_summary"]["evidence_ids"] == raw["change_summary"]["evidence_ids"][:24]
    assert normalizations == ["change_summary.evidence_ids deduplicated and capped at 24"]


def test_model_evidence_budgets_cover_all_nested_contracts():
    raw = {
        "raw_brief": {"claims": [{"evidence_ids": [f"git.file.{index}" for index in range(20)]}]},
        "change_summary": {
            "evidence_ids": [f"git.summary.{index}" for index in range(30)],
            "audience_candidates": [{"evidence_ids": [f"git.audience.{index}" for index in range(20)]}],
        },
        "owner_checks": [{"evidence_ids": [f"git.check.{index}" for index in range(20)]}],
    }

    bounded, normalizations = _bound_model_evidence_budgets(raw)

    assert len(bounded["raw_brief"]["claims"][0]["evidence_ids"]) == 16
    assert len(bounded["change_summary"]["evidence_ids"]) == 24
    assert len(bounded["change_summary"]["audience_candidates"][0]["evidence_ids"]) == 12
    assert len(bounded["owner_checks"][0]["evidence_ids"]) == 12
    assert len(normalizations) == 4


def test_english_change_prompt_has_no_chinese_instruction_text():
    assert not any("\u3400" <= char <= "\u9fff" for char in _change_interpretation_prompt("en"))


def test_english_model_output_rejects_mixed_owner_prose_but_not_identifiers():
    _require_requested_human_language(
        {"id": "中文_identifier", "evidence_ids": ["git.中文"], "headline": "English result"},
        "en",
        stage="change interpretation",
    )

    with pytest.raises(ModelGenerationError, match="non-English owner text"):
        _require_requested_human_language(
            {"headline": "中文标题"}, "en", stage="change interpretation"
        )
