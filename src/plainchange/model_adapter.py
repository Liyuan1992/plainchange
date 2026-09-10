from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from .generator_contract import (
    CLAIM_TYPES,
    CONFIDENCE_LEVELS,
    IMPORTANCE_LEVELS,
    RAW_BRIEF_SCHEMA,
    SCOPES,
    SECTIONS,
    validate_packet,
)
from .models import ManifestError, canonical_json_bytes, sha256_bytes

PROVIDER_CONFIG_SCHEMA = "change-passport.model-provider.v1"
RESPONSE_FORMATS = ("json_schema", "json_object", "prompt_only")
ENV_NAME_PATTERN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


class ModelGenerationError(ManifestError):
    """A configured model request failed before a raw brief was validated."""


@dataclass(frozen=True)
class ModelProviderConfig:
    provider_id: str
    base_url: str
    model: str
    api_key_env: str | None
    timeout_seconds: float
    response_format: str
    config_sha256: str

    @property
    def endpoint(self) -> str:
        value = self.base_url.rstrip("/")
        return value if value.endswith("/chat/completions") else value + "/chat/completions"

    @property
    def endpoint_origin(self) -> str:
        parsed = urlparse(self.base_url)
        return f"{parsed.scheme}://{parsed.netloc}"


class RawBriefProvider(Protocol):
    provider_name: str
    model: str
    config_sha256: str

    def generate(self, packet: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
        """Return the untrusted raw brief and non-secret provider telemetry."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(canonical_json_bytes(value) + b"\n")
    os.replace(temporary, path)


def _required_text(value: Any, label: str, *, max_length: int = 300) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > max_length:
        raise ModelGenerationError(f"{label} must be a non-empty string")
    return value.strip()


def load_model_provider_config(path: str | Path) -> ModelProviderConfig:
    config_path = Path(path).resolve(strict=True)
    try:
        value = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ModelGenerationError("model provider config is not valid UTF-8 JSON") from exc
    if not isinstance(value, Mapping):
        raise ModelGenerationError("model provider config must be an object")
    allowed = {
        "schema_version",
        "provider_id",
        "base_url",
        "model",
        "api_key_env",
        "timeout_seconds",
        "response_format",
    }
    if set(value) != allowed:
        missing = sorted(allowed - set(value))
        extra = sorted(set(value) - allowed)
        raise ModelGenerationError(
            f"model provider config fields mismatch; missing={missing}, extra={extra}"
        )
    if value.get("schema_version") != PROVIDER_CONFIG_SCHEMA:
        raise ModelGenerationError(f"model provider schema must be {PROVIDER_CONFIG_SCHEMA}")
    provider_id = _required_text(value.get("provider_id"), "provider_id", max_length=120)
    base_url = _required_text(value.get("base_url"), "base_url", max_length=500).rstrip("/")
    model = _required_text(value.get("model"), "model", max_length=200)
    parsed = urlparse(base_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ModelGenerationError("base_url must be an absolute HTTP(S) URL")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ModelGenerationError("base_url must not contain credentials, query, or fragment")
    api_key_env_value = value.get("api_key_env")
    if api_key_env_value is not None:
        if not isinstance(api_key_env_value, str) or not ENV_NAME_PATTERN.fullmatch(api_key_env_value):
            raise ModelGenerationError("api_key_env must be a valid environment variable name or null")
        api_key_env = api_key_env_value
    else:
        api_key_env = None
    timeout_value = value.get("timeout_seconds")
    if not isinstance(timeout_value, (int, float)) or isinstance(timeout_value, bool):
        raise ModelGenerationError("timeout_seconds must be a number")
    timeout_seconds = float(timeout_value)
    if not 1 <= timeout_seconds <= 900:
        raise ModelGenerationError("timeout_seconds must be between 1 and 900")
    response_format = value.get("response_format")
    if response_format not in RESPONSE_FORMATS:
        raise ModelGenerationError(
            "response_format must be json_schema, json_object, or prompt_only"
        )
    normalized = dict(value)
    normalized["base_url"] = base_url
    normalized["timeout_seconds"] = timeout_seconds
    return ModelProviderConfig(
        provider_id=provider_id,
        base_url=base_url,
        model=model,
        api_key_env=api_key_env,
        timeout_seconds=timeout_seconds,
        response_format=str(response_format),
        config_sha256=sha256_bytes(canonical_json_bytes(normalized)),
    )


def raw_brief_json_schema(allowed_evidence_ids: list[str]) -> dict[str, Any]:
    claim = {
        "type": "object",
        "additionalProperties": False,
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
        "properties": {
            "id": {"type": "string"},
            "section": {"type": "string", "enum": list(SECTIONS)},
            "scope": {"type": "string", "enum": list(SCOPES)},
            "text": {"type": "string"},
            "claim_type": {"type": "string", "enum": list(CLAIM_TYPES)},
            "confidence": {"type": "string", "enum": list(CONFIDENCE_LEVELS)},
            "importance": {"type": "string", "enum": list(IMPORTANCE_LEVELS)},
            "evidence_ids": {
                "type": "array",
                "items": {"type": "string", "enum": allowed_evidence_ids},
            },
            "limitations": {"type": "array", "items": {"type": "string"}},
            "next_check": {"type": ["string", "null"]},
        },
    }
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["schema_version", "claims"],
        "properties": {
            "schema_version": {"type": "string", "const": RAW_BRIEF_SCHEMA},
            "claims": {
                "type": "array",
                "minItems": 4,
                "maxItems": 12,
                "items": claim,
            },
        },
    }


def _post_json(
    url: str,
    payload: Mapping[str, Any],
    timeout_seconds: float,
    headers: Mapping[str, str],
) -> dict[str, Any]:
    request = Request(
        url,
        data=canonical_json_bytes(payload),
        headers=dict(headers),
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            raw = response.read()
    except HTTPError as exc:
        raise ModelGenerationError(f"model endpoint returned HTTP {exc.code}") from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise ModelGenerationError(f"model endpoint request failed: {type(exc).__name__}") from exc
    try:
        value = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ModelGenerationError("model endpoint returned invalid JSON") from exc
    if not isinstance(value, dict):
        raise ModelGenerationError("model endpoint response must be an object")
    return value


def _assistant_text(message: Mapping[str, Any]) -> str:
    refusal = message.get("refusal")
    if isinstance(refusal, str) and refusal:
        raise ModelGenerationError("model refused the constrained generation request")
    content = message.get("content")
    if isinstance(content, str) and content.strip():
        return content
    if isinstance(content, list):
        parts = [
            item.get("text")
            for item in content
            if isinstance(item, Mapping) and isinstance(item.get("text"), str)
        ]
        text = "".join(parts).strip()
        if text:
            return text
    raise ModelGenerationError("model response has no assistant JSON content")


class OpenAICompatibleRawBriefProvider:
    def __init__(self, config: ModelProviderConfig) -> None:
        self.config = config
        self.provider_name = config.provider_id
        self.model = config.model
        self.config_sha256 = config.config_sha256

    def _headers(self) -> dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "plainchange/0.1",
        }
        if self.config.api_key_env is not None:
            api_key = os.environ.get(self.config.api_key_env)
            if not api_key:
                raise ModelGenerationError(
                    f"required model credential environment variable is missing: {self.config.api_key_env}"
                )
            headers["Authorization"] = f"Bearer {api_key}"
        return headers

    def generate(self, packet: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
        validated = validate_packet(packet)
        schema = raw_brief_json_schema(list(validated["allowed_evidence_ids"]))
        system_prompt = (
            "你是 PlainChange 的受约束说明生成器。只依据用户消息中的证据包生成 Change Passport JSON。"
            "不得推测未提供的运行行为、用户影响、历史决定或测试结果。"
            "所有面向人的文本必须使用简体中文（代码标识符除外）。"
            "必须覆盖 function、architecture、history、attention 四个 section，且前四条按这个顺序各一条；"
            "证据不足时也必须输出对应 section，并使用 unknown。"
            "先说软件行为或负责人能感知的结果，不用文件名、函数名或工程术语作主语。"
            "每条 text 最多两句。不要输出 JSON 之外的内容。"
        )
        request_payload: dict[str, Any] = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": canonical_json_bytes(validated).decode("utf-8"),
                },
            ],
        }
        if self.config.response_format == "json_schema":
            request_payload["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": "plainchange_raw_brief",
                    "strict": True,
                    "schema": schema,
                },
            }
        elif self.config.response_format == "json_object":
            request_payload["response_format"] = {"type": "json_object"}
        response = _post_json(
            self.config.endpoint,
            request_payload,
            self.config.timeout_seconds,
            self._headers(),
        )
        choices = response.get("choices")
        if not isinstance(choices, list) or not choices or not isinstance(choices[0], Mapping):
            raise ModelGenerationError("model response contains no completion choice")
        message = choices[0].get("message")
        if not isinstance(message, Mapping):
            raise ModelGenerationError("model response contains no assistant message")
        try:
            raw = json.loads(_assistant_text(message))
        except json.JSONDecodeError as exc:
            raise ModelGenerationError("model assistant content is not valid JSON") from exc
        if not isinstance(raw, dict):
            raise ModelGenerationError("model raw brief must be an object")
        generated_at = _now()
        raw["generator_metadata"] = {
            "provider": self.config.provider_id,
            "model": str(response.get("model") or self.config.model),
            "mode": "constrained_configured_model_candidate",
            "generated_at": generated_at,
        }
        usage = response.get("usage") if isinstance(response.get("usage"), Mapping) else {}
        telemetry = {
            "endpoint_origin": self.config.endpoint_origin,
            "response_id": response.get("id"),
            "response_model": str(response.get("model") or self.config.model),
            "finish_reason": choices[0].get("finish_reason"),
            "prompt_tokens": usage.get("prompt_tokens"),
            "output_tokens": usage.get("completion_tokens"),
            "total_tokens": usage.get("total_tokens"),
            "response_format": self.config.response_format,
            "generated_at": generated_at,
        }
        return raw, telemetry


def generate_raw_brief_with_model(
    packet: Mapping[str, Any],
    output_dir: Path,
    provider: RawBriefProvider,
) -> tuple[dict[str, Any], Path]:
    validated = validate_packet(packet)
    receipt_path = output_dir / "model-run-receipt.json"
    started = time.perf_counter()
    receipt: dict[str, Any] = {
        "schema_version": "change-passport.model-run-receipt.v1",
        "status": "running",
        "provider": provider.provider_name,
        "model": provider.model,
        "provider_config_sha256": provider.config_sha256,
        "packet_sha256": validated["packet_sha256"],
        "started_at": _now(),
        "finished_at": None,
        "elapsed_seconds": 0.0,
        "output_sha256": None,
        "telemetry": {},
    }
    _write_json(receipt_path, receipt)
    try:
        raw, telemetry = provider.generate(validated)
        receipt["status"] = "succeeded"
        receipt["output_sha256"] = sha256_bytes(canonical_json_bytes(raw))
        receipt["telemetry"] = telemetry
        return raw, receipt_path
    except BaseException as exc:
        receipt["status"] = "failed"
        receipt["error"] = {"type": type(exc).__name__, "message": str(exc)}
        raise
    finally:
        receipt["finished_at"] = _now()
        receipt["elapsed_seconds"] = round(time.perf_counter() - started, 3)
        _write_json(receipt_path, receipt)
