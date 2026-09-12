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
from .semantic_analysis import (
    CHANGE_INTERPRETATION_SCHEMA,
    PROJECT_UNDERSTANDING_SCHEMA,
    change_interpretation_json_schema,
    project_understanding_json_schema,
    validate_change_interpretation,
    validate_project_context,
    validate_project_understanding,
)

PROVIDER_CONFIG_SCHEMA = "change-passport.model-provider.v1"
RESPONSE_FORMATS = ("json_schema", "json_object", "prompt_only")
ENV_NAME_PATTERN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
CHANGE_CONTEXT_SCHEMA = "plainchange.change-context.v1"


class ModelGenerationError(ManifestError):
    """A configured model request failed before a raw brief was validated."""


_CJK = re.compile(r"[\u3400-\u9fff]")
_LANGUAGE_STRUCTURAL_KEYS = frozenset(
    {
        "code_paths",
        "evidence_ids",
        "id",
        "schema_version",
        "source_ids",
    }
)


def _require_requested_human_language(value: Any, human_language: str, *, stage: str) -> None:
    """Reject a mixed-language model response before it becomes report prose.

    Prompting alone is not a contract: an OpenAI-compatible provider can return
    valid JSON while ignoring the requested response language. We fail closed
    for model-authored owner prose rather than publishing an English-labelled
    report containing Chinese. Source material, paths, evidence IDs, and other
    technical identifiers are not inspected here.
    """

    if human_language != "en":
        return

    def visit(item: Any, path: str) -> None:
        if isinstance(item, Mapping):
            for key, child in item.items():
                if key in _LANGUAGE_STRUCTURAL_KEYS:
                    continue
                visit(child, f"{path}.{key}")
        elif isinstance(item, list):
            for index, child in enumerate(item):
                visit(child, f"{path}[{index}]")
        elif isinstance(item, str) and _CJK.search(item):
            raise ModelGenerationError(
                f"{stage} returned non-English owner text at {path}; "
                "choose a model that follows the requested language"
            )

    visit(value, stage)


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

    def generate(
        self, packet: Mapping[str, Any], *, human_language: str = "zh-CN"
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Return the untrusted raw brief and non-secret provider telemetry."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(canonical_json_bytes(value) + b"\n")
    os.replace(temporary, path)


def _compact_change_context(packet: Mapping[str, Any]) -> dict[str, Any]:
    """Keep semantic change input bounded without weakening final validation."""

    evidence = [dict(item) for item in packet["evidence"]]
    metadata = [
        item
        for item in evidence
        if item.get("kind") == "git"
        and item.get("id") != "git.patch"
        and not str(item.get("id", "")).startswith("git.file.")
    ]
    file_items = [
        item for item in evidence if str(item.get("id", "")).startswith("git.file.")
    ]

    def churn(item: Mapping[str, Any]) -> int:
        content = str(item.get("content", ""))
        added = re.search(r"(?:^|;) added_lines=(\d+)", content)
        deleted = re.search(r"(?:^|;) deleted_lines=(\d+)", content)
        return int(added.group(1) if added else 0) + int(deleted.group(1) if deleted else 0)

    file_items.sort(key=lambda item: (-churn(item), str(item.get("id", ""))))
    behavior_and_task = [
        item
        for item in evidence
        if item.get("kind") in {"behavior_signal", "task", "test", "agent_provenance"}
    ]
    architecture_by_id = {
        str(item.get("id")): item
        for item in evidence
        if item.get("kind") == "architecture"
    }
    delta = packet["architecture_delta"]
    architecture_ids: list[str] = []
    for field in ("added_node_ids", "modified_node_ids", "impacted_node_ids", "removed_node_ids"):
        for item_id in delta.get(field, []):
            value = str(item_id)
            if value in architecture_by_id and value not in architecture_ids:
                architecture_ids.append(value)
            if len(architecture_ids) >= 32:
                break
        if len(architecture_ids) >= 32:
            break
    selected = metadata + file_items[:80] + behavior_and_task + [
        architecture_by_id[item_id] for item_id in architecture_ids
    ]
    deduplicated: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in selected:
        item_id = str(item.get("id", ""))
        if item_id and item_id not in seen:
            seen.add(item_id)
            deduplicated.append(item)
    return {
        "schema_version": CHANGE_CONTEXT_SCHEMA,
        "sample_id": packet["sample_id"],
        "change": packet["change"],
        "evidence": deduplicated,
        "allowed_evidence_ids": [item["id"] for item in deduplicated],
        "omitted_evidence_count": len(evidence) - len(deduplicated),
        "architecture_summary": {
            "analysis_stats": delta.get("analysis_stats", {}),
            "added_node_count": len(delta.get("added_node_ids", [])),
            "modified_node_count": len(delta.get("modified_node_ids", [])),
            "removed_node_count": len(delta.get("removed_node_ids", [])),
            "impacted_node_count": len(delta.get("impacted_node_ids", [])),
            "unknowns": list(delta.get("unknowns", []))[:24],
            "limitations": list(delta.get("limitations", []))[:24],
        },
        "verification_receipts": list(packet.get("verification_receipts", [])),
        "instructions": [
            "Use only the included evidence records; omitted evidence is unavailable, not negative evidence.",
            "File churn helps identify themes but does not prove user impact or runtime behavior.",
            "Structured verification receipts are authoritative for their exact recorded scope; do not describe a supplied receipt as missing.",
        ],
    }


def _required_text(value: Any, label: str, *, max_length: int = 300) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > max_length:
        raise ModelGenerationError(f"{label} must be a non-empty string")
    return value.strip()


def parse_model_provider_config(value: Any) -> ModelProviderConfig:
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


def load_model_provider_config(path: str | Path) -> ModelProviderConfig:
    config_path = Path(path).resolve(strict=True)
    try:
        value = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ModelGenerationError("model provider config is not valid UTF-8 JSON") from exc
    return parse_model_provider_config(value)


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
            "limitations": {"type": "array", "items": {"type": "string", "minLength": 1}},
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
    def __init__(self, config: ModelProviderConfig, *, api_key: str | None = None) -> None:
        self.config = config
        self.provider_name = config.provider_id
        self.model = config.model
        self.config_sha256 = config.config_sha256
        if api_key is not None:
            if not isinstance(api_key, str) or not api_key.strip() or len(api_key) > 8_192:
                raise ModelGenerationError("direct model credential is invalid")
            self._ephemeral_api_key = api_key.strip()
        else:
            self._ephemeral_api_key = None

    def _headers(self) -> dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "plainchange/0.1",
        }
        if self._ephemeral_api_key is not None:
            headers["Authorization"] = f"Bearer {self._ephemeral_api_key}"
        elif self.config.api_key_env is not None:
            api_key = os.environ.get(self.config.api_key_env)
            if not api_key:
                raise ModelGenerationError(
                    f"required model credential environment variable is missing: {self.config.api_key_env}"
                )
            headers["Authorization"] = f"Bearer {api_key}"
        return headers

    def _structured_completion(
        self,
        *,
        system_prompt: str,
        payload: Mapping[str, Any],
        schema: Mapping[str, Any],
        schema_name: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        request_payload: dict[str, Any] = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": canonical_json_bytes(payload).decode("utf-8")},
            ],
        }
        if self.config.response_format == "json_schema":
            request_payload["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": schema_name,
                    "strict": True,
                    "schema": dict(schema),
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
            raise ModelGenerationError("model structured output must be an object")
        generated_at = _now()
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
            "stage": schema_name,
        }
        return raw, telemetry

    def understand_project(
        self, packet: Mapping[str, Any], *, human_language: str = "zh-CN"
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        validated = validate_project_context(packet)
        raw, telemetry = self._structured_completion(
            system_prompt=(
                "You are PlainChange's project-understanding stage. Explain what the software does in owner language before interpreting a change. "
                "Project documentation is a claim, not truth: reconcile it with the supplied fixed-revision code paths and implementation groups. "
                "Choose workflow only for an evidence-supported ordered business path; otherwise choose capability_map. "
                "Produce a shallow owner map, never an implementation inventory: normally use four to six components, and use two or three only when the supplied evidence cannot honestly support more. "
                "Each label must name a person-visible business action, responsibility, or outcome in plain language. Keep labels short. Do not use framework, API, service, module, layer, route, import, controller, or implementation terminology as the main label unless that term is itself visible to the product owner. "
                "When structure_kind is capability_map, every component.type must be capability. "
                "When structure_kind is workflow, component.type must be input, process, output, human_gate, or state. "
                "For workflow, list components in execution order and provide exactly one flow for each adjacent pair in that same order; for capability_map, flows must be empty. "
                "Purpose and each component may cite at most 12 unique source IDs; each component may cite at most 24 unique code paths, copied exactly from source_paths. "
                "Do not claim runtime behavior, user impact, test results, or correctness. Cite only supplied source IDs and code paths. "
                f"{_human_language_instruction(human_language)} Output JSON only."
            ),
            payload=validated,
            schema=project_understanding_json_schema(validated),
            schema_name="plainchange_project_understanding",
        )
        bounded_raw, normalizations = _bound_project_understanding_contract(
            raw, validated
        )
        if normalizations:
            telemetry["local_normalizations"] = normalizations
        result = validate_project_understanding(validated, bounded_raw)
        _require_requested_human_language(
            result, human_language, stage="project understanding"
        )
        return result, telemetry

    def interpret_change(
        self,
        packet: Mapping[str, Any],
        understanding: Mapping[str, Any],
        *,
        human_language: str = "zh-CN",
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        validated = validate_packet(packet)
        compact_context = _compact_change_context(validated)
        component_ids = [str(item["id"]) for item in understanding["components"]]
        schema = change_interpretation_json_schema(
            list(compact_context["allowed_evidence_ids"]),
            component_ids,
            raw_brief_json_schema(list(compact_context["allowed_evidence_ids"])),
        )
        model_input = {
            "project_understanding": {
                key: value
                for key, value in understanding.items()
                if not str(key).startswith("_")
            },
            "change_context": compact_context,
        }
        raw, telemetry = self._structured_completion(
            system_prompt=_change_interpretation_prompt(human_language),
            payload=model_input,
            schema=schema,
            schema_name="plainchange_change_interpretation",
        )
        bounded_raw, normalizations = _bound_model_evidence_budgets(raw)
        if normalizations:
            telemetry["local_normalizations"] = normalizations
        result = validate_change_interpretation(validated, understanding, bounded_raw)
        _require_requested_human_language(
            result, human_language, stage="change interpretation"
        )
        result["raw_brief"]["generator_metadata"] = {
            "provider": self.config.provider_id,
            "model": str(telemetry["response_model"]),
            "mode": "model_first_project_and_change_candidate",
            "human_language": human_language,
            "generated_at": str(telemetry["generated_at"]),
        }
        return result, telemetry

    def generate(
        self, packet: Mapping[str, Any], *, human_language: str = "zh-CN"
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        validated = validate_packet(packet)
        schema = raw_brief_json_schema(list(validated["allowed_evidence_ids"]))
        system_prompt = (
            "你是 PlainChange 的受约束说明生成器。只依据用户消息中的证据包生成 Change Passport JSON。"
            "不得推测未提供的运行行为、用户影响、历史决定或测试结果。"
            f"{_human_language_instruction(human_language)}"
            "必须覆盖 function、architecture、history、attention 四个 section，且前四条按这个顺序各一条；"
            "证据不足时也必须输出对应 section，并使用 unknown。"
            "先说软件行为或负责人能感知的结果，不用文件名、函数名或工程术语作主语。"
            "每条 text 最多两句。不要输出 JSON 之外的内容。"
        )
        raw, telemetry = self._structured_completion(
            system_prompt=system_prompt,
            payload=validated,
            schema=schema,
            schema_name="plainchange_raw_brief",
        )
        raw, normalizations = _bound_model_evidence_budgets({"raw_brief": raw})
        raw = raw["raw_brief"]
        if normalizations:
            telemetry["local_normalizations"] = normalizations
        raw["generator_metadata"] = {
            "provider": self.config.provider_id,
            "model": str(telemetry["response_model"]),
            "mode": "constrained_configured_model_candidate",
            "human_language": human_language,
            "generated_at": str(telemetry["generated_at"]),
        }
        _require_requested_human_language(raw, human_language, stage="raw brief")
        return raw, telemetry


def _human_language_instruction(human_language: str) -> str:
    if human_language == "zh-CN":
        return "所有面向人的文本必须使用简体中文（代码标识符除外）。"
    if human_language == "en":
        return "Use English for all human-facing text, except product names and code identifiers."
    raise ModelGenerationError(f"unsupported human output language: {human_language}")


def _change_interpretation_prompt(human_language: str) -> str:
    if human_language == "en":
        return (
            "You are PlainChange's change-understanding stage. The project understanding is a bounded candidate, not a fact. "
            "Using the fixed change evidence, explain the main change in business language that a software owner can repeat in ten seconds, then select at most one most relevant software step or capability. "
            "Lead the headline with the outcome; write one sentence of at most 56 characters. Do not make engineering abstractions such as capability, pipeline, task layer, display layer, module, or API the headline subject. "
            "Use at most two explanation sentences: first say what changed, then what remains unverified. "
            "When fixed evidence supports concrete roles, provide at most three audience_candidates. Use roles such as operator, administrator, or API consumer rather than generic end user; candidates may identify who should pay attention, never claim actual impact. "
            "Do not let an incidental exception, function, or file count displace the more important product change. "
            "Every evidence_id must come from the supplied change packet; change_summary.evidence_ids may contain at most 24 items. Keep unknown when evidence is insufficient. "
            "limitations may be empty; every supplied item must be a substantive non-empty limit. "
            "Do not claim verified runtime behavior, end-user impact, or correctness. Claim a test or build result only when it cites actual_test_receipt evidence, and state only that receipt's exact scope. "
            "Write the headline as a concrete new owner-visible ability or corrected outcome, not as an implementation category such as coverage information. Use English for every human-facing field except product names and code identifiers. Output JSON only."
        )
    if human_language == "zh-CN":
        return (
            "你是 PlainChange 的变更理解阶段。项目理解只是受约束候选，不是事实。"
            "结合固定变更证据，先用软件负责人能在十秒内复述的业务语言说明主要变化，再选择至多一个最相关的软件步骤或能力。"
            "标题先说结果，只写一句且不超过 56 个字符；不要把“能力、链路、任务层、展示层、扩展上线、模块、接口”等工程抽象当作标题主语。"
            "说明不超过两句：先说发生了什么，再说明还没有验证什么。"
            "如固定证据能支持具体使用角色，给出至多三个 audience_candidates；角色应是店员、管理员、调用方等具体角色，而不是“普通用户”或“最终用户”。角色候选只能说明最可能需要关注的人，不能声称其已受到实际影响。"
            "不得用偶然出现的异常、函数或文件数量覆盖更主要的产品变化。"
            "所有 evidence_ids 必须来自变更证据包；change_summary.evidence_ids 最多只能列出 24 条。证据不足时保持 unknown。"
            "limitations 可以为空数组；如填写，每一项必须是有内容的具体限制，绝不能输出空字符串或空白项。"
            "不得声称已验证运行行为、最终用户影响或正确性。只有引用 actual_test_receipt 证据时才能陈述测试或构建结果，并且只能覆盖收据明确列出的范围。"
            "结构化验证收据是其明确范围内的优先事实；已提供收据时，不得再说没有 actual_test_receipt，也不得把已通过项目列为待验证。"
            "标题必须说清楚负责人现在具体多了什么能力或什么结果被修正，不能只写成“覆盖信息”等实现分类。所有面向人的文本使用简体中文（代码标识符除外）。只输出 JSON。"
        )
    raise ModelGenerationError(f"unsupported human output language: {human_language}")


def _bound_project_understanding_contract(
    raw: Mapping[str, Any], packet: Mapping[str, Any]
) -> tuple[dict[str, Any], list[str]]:
    """Remove unsupported project references without inventing semantics.

    Some compatible providers accept the requested JSON Schema but do not
    enforce nested enum, uniqueness, or list-size constraints. Filtering
    unknown/surplus references is loss-only. Workflow edges may be reordered or
    have extras removed only when the model already supplied every adjacent
    edge implied by its own ordered component list; a missing edge still fails
    normal validation.
    """

    result = json.loads(json.dumps(raw))
    normalizations: list[str] = []
    allowed_sources = set(map(str, packet.get("allowed_source_ids", [])))
    allowed_paths = set(map(str, packet.get("source_paths", [])))

    def bound_strings(
        container: Any,
        key: str,
        *,
        allowed: set[str] | None,
        maximum: int,
        path: str,
    ) -> None:
        if not isinstance(container, dict) or not isinstance(container.get(key), list):
            return
        original = container[key]
        bounded: list[str] = []
        for item in original:
            if not isinstance(item, str):
                continue
            if allowed is not None and item not in allowed:
                continue
            if item not in bounded:
                bounded.append(item)
            if len(bounded) == maximum:
                break
        if bounded != original:
            container[key] = bounded
            normalizations.append(
                f"{path} filtered, deduplicated and capped at {maximum}"
            )

    purpose = result.get("purpose")
    bound_strings(
        purpose,
        "source_ids",
        allowed=allowed_sources,
        maximum=12,
        path="purpose.source_ids",
    )
    components = result.get("components")
    if isinstance(components, list):
        for index, component in enumerate(components):
            bound_strings(
                component,
                "source_ids",
                allowed=allowed_sources,
                maximum=12,
                path=f"components[{index}].source_ids",
            )
            bound_strings(
                component,
                "code_paths",
                allowed=allowed_paths,
                maximum=24,
                path=f"components[{index}].code_paths",
            )
    bound_strings(
        result,
        "unknowns",
        allowed=None,
        maximum=12,
        path="unknowns",
    )

    flows = result.get("flows")
    if result.get("structure_kind") == "capability_map" and isinstance(flows, list) and flows:
        result["flows"] = []
        normalizations.append("capability_map.flows removed")
    elif (
        result.get("structure_kind") == "workflow"
        and isinstance(components, list)
        and isinstance(flows, list)
    ):
        component_ids = [
            item.get("id") if isinstance(item, Mapping) else None
            for item in components
        ]
        if all(isinstance(item, str) for item in component_ids):
            expected = list(zip(component_ids, component_ids[1:]))
            labels: dict[tuple[str, str], str] = {}
            for flow in flows:
                if not isinstance(flow, Mapping):
                    continue
                edge = (flow.get("from"), flow.get("to"))
                label = flow.get("label")
                if edge in expected and isinstance(label, str) and edge not in labels:
                    labels[edge] = label
            if all(edge in labels for edge in expected):
                ordered = [
                    {"from": edge[0], "to": edge[1], "label": labels[edge]}
                    for edge in expected
                ]
                if ordered != flows:
                    result["flows"] = ordered
                    normalizations.append(
                        "workflow.flows restricted to the supplied consecutive chain"
                    )
    return result, normalizations


def _bound_change_summary_evidence(raw: Mapping[str, Any]) -> tuple[dict[str, Any], list[str]]:
    """Apply a loss-only evidence budget before semantic validation.

    Compatible providers may accept a JSON-schema request without enforcing its
    max-items constraints. Removing duplicate or surplus references can never
    create support for a model statement; it only preserves the local contract.
    """
    result = json.loads(json.dumps(raw))
    summary = result.get("change_summary")
    if not isinstance(summary, dict) or not isinstance(summary.get("evidence_ids"), list):
        return result, []
    bounded: list[str] = []
    for item in summary["evidence_ids"]:
        if isinstance(item, str) and item not in bounded:
            bounded.append(item)
        if len(bounded) == 24:
            break
    if bounded == summary["evidence_ids"]:
        return result, []
    summary["evidence_ids"] = bounded
    return result, ["change_summary.evidence_ids deduplicated and capped at 24"]


def _bound_model_evidence_budgets(raw: Mapping[str, Any]) -> tuple[dict[str, Any], list[str]]:
    """Apply all model-output evidence budgets as loss-only normalizations.

    Some OpenAI-compatible services acknowledge a JSON Schema response format
    without enforcing nested ``maxItems``. Every list below contains only
    evidence identifiers. Deduplicating or dropping surplus IDs cannot create
    support for a model claim, so this preserves the local contract while
    retaining the provider response's strongest bounded subset.
    """

    result = json.loads(json.dumps(raw))
    normalizations: list[str] = []

    def bound(value: Any, maximum: int, path: str) -> None:
        if not isinstance(value, dict) or not isinstance(value.get("evidence_ids"), list):
            return
        bounded: list[str] = []
        for item in value["evidence_ids"]:
            if isinstance(item, str) and item not in bounded:
                bounded.append(item)
            if len(bounded) == maximum:
                break
        if bounded != value["evidence_ids"]:
            value["evidence_ids"] = bounded
            normalizations.append(f"{path} deduplicated and capped at {maximum}")

    raw_brief = result.get("raw_brief")
    if isinstance(raw_brief, dict) and isinstance(raw_brief.get("claims"), list):
        for index, claim in enumerate(raw_brief["claims"]):
            bound(claim, 16, f"raw_brief.claims[{index}].evidence_ids")
    summary = result.get("change_summary")
    bound(summary, 24, "change_summary.evidence_ids")
    if isinstance(summary, dict) and isinstance(summary.get("audience_candidates"), list):
        for index, audience in enumerate(summary["audience_candidates"]):
            bound(audience, 12, f"change_summary.audience_candidates[{index}].evidence_ids")
    checks = result.get("owner_checks")
    if isinstance(checks, list):
        for index, check in enumerate(checks):
            bound(check, 12, f"owner_checks[{index}].evidence_ids")
    return result, normalizations


def generate_raw_brief_with_model(
    packet: Mapping[str, Any],
    output_dir: Path,
    provider: RawBriefProvider,
    *,
    human_language: str = "zh-CN",
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
        "human_language": human_language,
        "started_at": _now(),
        "finished_at": None,
        "elapsed_seconds": 0.0,
        "output_sha256": None,
        "telemetry": {},
    }
    _write_json(receipt_path, receipt)
    try:
        raw, telemetry = provider.generate(validated, human_language=human_language)
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


def _run_model_stage(
    *,
    output_dir: Path,
    receipt_name: str,
    stage: str,
    input_sha256: str,
    provider: OpenAICompatibleRawBriefProvider,
    human_language: str,
    operation: Any,
) -> tuple[dict[str, Any], Path]:
    receipt_path = output_dir / receipt_name
    started = time.perf_counter()
    receipt: dict[str, Any] = {
        "schema_version": "plainchange.model-stage-receipt.v1",
        "stage": stage,
        "status": "running",
        "provider": provider.provider_name,
        "model": provider.model,
        "provider_config_sha256": provider.config_sha256,
        "input_sha256": input_sha256,
        "human_language": human_language,
        "started_at": _now(),
        "finished_at": None,
        "elapsed_seconds": 0.0,
        "output_sha256": None,
        "telemetry": {},
    }
    _write_json(receipt_path, receipt)
    try:
        result, telemetry = operation()
        receipt["status"] = "succeeded"
        receipt["output_sha256"] = sha256_bytes(canonical_json_bytes(result))
        receipt["telemetry"] = telemetry
        return result, receipt_path
    except BaseException as exc:
        receipt["status"] = "failed"
        receipt["error"] = {"type": type(exc).__name__, "message": str(exc)}
        raise
    finally:
        receipt["finished_at"] = _now()
        receipt["elapsed_seconds"] = round(time.perf_counter() - started, 3)
        _write_json(receipt_path, receipt)


def generate_project_understanding_with_model(
    packet: Mapping[str, Any],
    output_dir: Path,
    provider: OpenAICompatibleRawBriefProvider,
    *,
    human_language: str = "zh-CN",
) -> tuple[dict[str, Any], Path]:
    validated = validate_project_context(packet)
    return _run_model_stage(
        output_dir=output_dir,
        receipt_name="project-understanding-run-receipt.json",
        stage="project_understanding",
        input_sha256=str(validated["packet_sha256"]),
        provider=provider,
        human_language=human_language,
        operation=lambda: provider.understand_project(validated, human_language=human_language),
    )


def generate_change_interpretation_with_model(
    packet: Mapping[str, Any],
    understanding: Mapping[str, Any],
    output_dir: Path,
    provider: OpenAICompatibleRawBriefProvider,
    *,
    human_language: str = "zh-CN",
) -> tuple[dict[str, Any], Path]:
    validated = validate_packet(packet)
    input_sha = sha256_bytes(
        canonical_json_bytes(
            {
                "packet_sha256": validated["packet_sha256"],
                "understanding_identity": understanding["understanding_identity"],
            }
        )
    )
    return _run_model_stage(
        output_dir=output_dir,
        receipt_name="change-interpretation-run-receipt.json",
        stage="change_interpretation",
        input_sha256=input_sha,
        provider=provider,
        human_language=human_language,
        operation=lambda: provider.interpret_change(
            validated, understanding, human_language=human_language
        ),
    )
