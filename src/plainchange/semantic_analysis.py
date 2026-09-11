from __future__ import annotations

import copy
import json
import os
import re
from pathlib import Path
from typing import Any, Mapping

from .git_evidence import list_git_tree, read_git_blob
from .models import ManifestError, canonical_json_bytes, sha256_bytes
from .project_declarations import collect_declarations
from .source_scope import is_supported_source_path


PROJECT_CONTEXT_SCHEMA = "plainchange.project-context.v1"
PROJECT_UNDERSTANDING_SCHEMA = "plainchange.project-understanding.v2"
CHANGE_INTERPRETATION_SCHEMA = "plainchange.change-interpretation.v2"
_ID = re.compile(r"^[A-Za-z][A-Za-z0-9._-]{0,79}$")
_PROJECT_FILES = (
    "README.md",
    "README.rst",
    "pyproject.toml",
    "package.json",
    "Cargo.toml",
    "go.mod",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
)
_IDENTIFIER_PATTERNS = (
    re.compile(r"^\s*(?:async\s+)?def\s+([A-Za-z_][A-Za-z0-9_]*)", re.MULTILINE),
    re.compile(r"^\s*class\s+([A-Za-z_][A-Za-z0-9_]*)", re.MULTILINE),
    re.compile(r"\bexport\s+(?:default\s+)?(?:async\s+)?(?:function|class|const|let|var)\s+([A-Za-z_$][A-Za-z0-9_$]*)"),
    re.compile(r"\b(?:function|class)\s+([A-Za-z_$][A-Za-z0-9_$]*)"),
    re.compile(r"\bname\s*:\s*['\"]([A-Za-z_$][A-Za-z0-9_$-]*)['\"]"),
)


def _text(value: Any, label: str, *, maximum: int = 2_000) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise ManifestError(f"{label} must be a non-empty string no longer than {maximum}")
    return value.strip()


def _texts(value: Any, label: str, *, maximum_items: int, maximum: int = 500) -> list[str]:
    if not isinstance(value, list) or len(value) > maximum_items:
        raise ManifestError(f"{label} must be an array with at most {maximum_items} items")
    result = [_text(item, f"{label}[{index}]", maximum=maximum) for index, item in enumerate(value)]
    if len(result) != len(set(result)):
        raise ManifestError(f"{label} contains duplicate values")
    return result


def build_project_context_packet(
    repo: Path,
    commit: str,
    timeout: int,
    display_name: str,
    base_profile: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a bounded, path-relative packet for semantic project understanding."""

    tree = list_git_tree(repo, commit, timeout)
    source_paths = sorted(path for path in tree if is_supported_source_path(path))
    declarations = collect_declarations(repo, commit, tree, timeout)
    declaration_paths = {str(item["path"]) for item in declarations}
    sources: list[dict[str, Any]] = []
    source_budget = 96_000
    for path in _PROJECT_FILES:
        if path not in tree or path in declaration_paths:
            continue
        raw = read_git_blob(repo, commit, path, timeout)[:32_000]
        declarations.append(
            {
                "path": path,
                "text": raw.decode("utf-8", errors="replace"),
                "source_ref": f"git:{commit}:{path}:sha256:{sha256_bytes(raw)}",
            }
        )
    for index, item in enumerate(declarations):
        text = str(item["text"])
        encoded = text.encode("utf-8")
        if source_budget <= 0:
            break
        if len(encoded) > source_budget:
            encoded = encoded[:source_budget]
            text = encoded.decode("utf-8", errors="ignore")
        source_budget -= len(text.encode("utf-8"))
        sources.append(
            {
                "id": f"project.source.{index + 1:03d}",
                "kind": "project_declaration",
                "path": str(item["path"]),
                "content": text,
                "source_ref": str(item["source_ref"]),
            }
        )
    outline_candidates = sorted(source_paths, key=_outline_priority)[:64]
    for path in outline_candidates:
        raw = read_git_blob(repo, commit, path, timeout)[:128_000]
        text = raw.decode("utf-8", errors="replace")
        identifiers: list[str] = []
        for pattern in _IDENTIFIER_PATTERNS:
            for name in pattern.findall(text):
                if name not in identifiers and not str(name).startswith("_"):
                    identifiers.append(str(name))
                if len(identifiers) >= 40:
                    break
            if len(identifiers) >= 40:
                break
        if not identifiers:
            continue
        sources.append(
            {
                "id": f"project.outline.{len(sources) + 1:03d}",
                "kind": "code_outline",
                "path": path,
                "content": "identifiers=" + ", ".join(identifiers),
                "source_ref": f"git:{commit}:{path}:outline",
            }
        )
    sections = [
        {
            "id": str(section["id"]),
            "label": str(section["label"]),
            "responsibility": str(section["responsibility"]),
            "example_paths": [
                path
                for path in source_paths
                if _section_matches(section, path)
            ][:24],
        }
        for section in base_profile.get("sections", [])
        if isinstance(section, Mapping) and section.get("id") != "unclassified"
    ]
    allowed_code_paths = sorted(
        {
            str(item["path"])
            for item in sources
            if item.get("kind") == "code_outline"
        }
        | {
            str(path)
            for section in sections
            for path in section["example_paths"]
        }
    )[:192]
    packet: dict[str, Any] = {
        "schema_version": PROJECT_CONTEXT_SCHEMA,
        "project_name": display_name,
        "head_commit": commit,
        "sources": sources,
        "allowed_source_ids": [item["id"] for item in sources],
        # Only expose paths that the bounded outlines or implementation-group
        # samples actually introduce. The total remains visible separately,
        # while irrelevant filenames cannot dominate model context or latency.
        "source_paths": allowed_code_paths,
        "source_path_count": len(source_paths),
        "implementation_groups": sections,
        "instructions": [
            "Project documentation is a declaration, not truth; compare it with paths and implementation groups.",
            "Describe the product in owner language. Do not use files, frameworks, controllers, services, or imports as the main story.",
            "Use workflow only when an ordered business path is supported; otherwise use capability_map.",
            "Every semantic item must cite only supplied source IDs and code paths.",
            "Do not claim runtime order, user impact, test results, or correctness.",
        ],
    }
    packet["packet_sha256"] = sha256_bytes(canonical_json_bytes(packet))
    return packet


def validate_project_context(packet: Any) -> dict[str, Any]:
    if not isinstance(packet, Mapping):
        raise ManifestError("project context must be an object")
    result = copy.deepcopy(dict(packet))
    if result.get("schema_version") != PROJECT_CONTEXT_SCHEMA:
        raise ManifestError("project context schema is invalid")
    claimed = result.pop("packet_sha256", None)
    if claimed != sha256_bytes(canonical_json_bytes(result)):
        raise ManifestError("project context packet hash does not match its content")
    result["packet_sha256"] = claimed
    sources = result.get("sources")
    allowed = result.get("allowed_source_ids")
    paths = result.get("source_paths")
    if not isinstance(sources, list) or not isinstance(allowed, list) or not isinstance(paths, list):
        raise ManifestError("project context source contract is invalid")
    ids = [item.get("id") for item in sources if isinstance(item, Mapping)]
    if ids != allowed or len(ids) != len(set(ids)):
        raise ManifestError("project context source IDs are inconsistent")
    if any(Path(str(path)).is_absolute() or ".." in Path(str(path)).parts for path in paths):
        raise ManifestError("project context contains an unsafe source path")
    return result


def project_understanding_json_schema(packet: Mapping[str, Any]) -> dict[str, Any]:
    source_ids = list(packet["allowed_source_ids"])
    component = {
        "type": "object",
        "additionalProperties": False,
        "required": ["id", "label", "description", "type", "source_ids", "code_paths"],
        "properties": {
            "id": {"type": "string", "maxLength": 80},
            "label": {"type": "string", "maxLength": 48},
            "description": {"type": "string", "maxLength": 240},
            "type": {"type": "string", "enum": ["input", "process", "output", "human_gate", "state", "capability"]},
            "source_ids": {"type": "array", "items": {"type": "string", "enum": source_ids}},
            "code_paths": {"type": "array", "items": {"type": "string"}},
        },
    }
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["schema_version", "purpose", "structure_kind", "title", "components", "flows", "unknowns"],
        "properties": {
            "schema_version": {"type": "string", "const": PROJECT_UNDERSTANDING_SCHEMA},
            "purpose": {
                "type": "object",
                "additionalProperties": False,
                "required": ["text", "source_ids"],
                "properties": {
                    "text": {"type": "string", "maxLength": 480},
                    "source_ids": {"type": "array", "items": {"type": "string", "enum": source_ids}},
                },
            },
            "structure_kind": {"type": "string", "enum": ["workflow", "capability_map"]},
            "title": {"type": "string", "maxLength": 96},
            # This is the shallow owner map, not an implementation inventory.
            # Very small projects may still need two or three truthful items;
            # normal model output is asked for four through six below.
            "components": {"type": "array", "minItems": 2, "maxItems": 6, "items": component},
            "flows": {
                "type": "array",
                "items": {
                    "type": "object", "additionalProperties": False,
                    "required": ["from", "to", "label"],
                    "properties": {"from": {"type": "string"}, "to": {"type": "string"}, "label": {"type": "string"}},
                },
            },
            "unknowns": {"type": "array", "items": {"type": "string"}},
        },
    }


def validate_project_understanding(packet: Mapping[str, Any], value: Any) -> dict[str, Any]:
    context = validate_project_context(packet)
    if not isinstance(value, Mapping):
        raise ManifestError("project understanding must be an object")
    result = copy.deepcopy(dict(value))
    required = {"schema_version", "purpose", "structure_kind", "title", "components", "flows", "unknowns"}
    if set(result) != required or result.get("schema_version") != PROJECT_UNDERSTANDING_SCHEMA:
        raise ManifestError("project understanding fields or schema are invalid")
    allowed_sources = set(context["allowed_source_ids"])
    allowed_paths = set(context["source_paths"])
    purpose = result.get("purpose")
    if not isinstance(purpose, Mapping) or set(purpose) != {"text", "source_ids"}:
        raise ManifestError("project understanding purpose is invalid")
    _text(purpose.get("text"), "project understanding purpose.text", maximum=800)
    purpose_sources = _texts(purpose.get("source_ids"), "project understanding purpose.source_ids", maximum_items=12)
    if not set(purpose_sources) <= allowed_sources:
        raise ManifestError("project understanding purpose cites an unknown source")
    kind = result.get("structure_kind")
    if kind not in {"workflow", "capability_map"}:
        raise ManifestError("project understanding structure_kind is invalid")
    _text(result.get("title"), "project understanding title", maximum=240)
    components = result.get("components")
    if not isinstance(components, list) or not 2 <= len(components) <= 6:
        raise ManifestError("project understanding needs two to six components")
    if kind == "workflow" and len(components) < 4:
        raise ManifestError("project understanding workflow needs at least four components")
    component_ids: list[str] = []
    for index, component in enumerate(components):
        if not isinstance(component, Mapping) or set(component) != {"id", "label", "description", "type", "source_ids", "code_paths"}:
            raise ManifestError(f"project understanding component {index} is invalid")
        component_id = _text(component.get("id"), f"component {index}.id", maximum=80)
        if not _ID.fullmatch(component_id):
            raise ManifestError(f"component {index}.id is invalid")
        component_ids.append(component_id)
        _text(component.get("label"), f"component {index}.label", maximum=48)
        _text(component.get("description"), f"component {index}.description", maximum=240)
        # A capability map already determines the node type. Treat the repeated
        # per-node field as derived presentation metadata so a harmless model
        # disagreement cannot invalidate otherwise source-bound semantics.
        if kind == "capability_map":
            component["type"] = "capability"
        expected_types = {"capability"} if kind == "capability_map" else {"input", "process", "output", "human_gate", "state"}
        if component.get("type") not in expected_types:
            raise ManifestError(f"component {index}.type does not match the structure kind")
        source_ids = _texts(component.get("source_ids"), f"component {index}.source_ids", maximum_items=12)
        code_paths = _texts(component.get("code_paths"), f"component {index}.code_paths", maximum_items=24, maximum=500)
        if not set(source_ids) <= allowed_sources or not set(code_paths) <= allowed_paths:
            raise ManifestError(f"component {index} cites an unknown source or path")
        if not source_ids and not code_paths:
            raise ManifestError(f"component {index} has no source support")
    if len(component_ids) != len(set(component_ids)):
        raise ManifestError("project understanding contains duplicate component IDs")
    flows = result.get("flows")
    if not isinstance(flows, list):
        raise ManifestError("project understanding flows must be an array")
    if kind == "capability_map" and flows:
        raise ManifestError("a capability map cannot declare ordered flows")
    for index, flow in enumerate(flows):
        if not isinstance(flow, Mapping) or set(flow) != {"from", "to", "label"}:
            raise ManifestError(f"project understanding flow {index} is invalid")
        if flow.get("from") not in component_ids or flow.get("to") not in component_ids:
            raise ManifestError(f"project understanding flow {index} cites an unknown component")
        _text(flow.get("label"), f"flow {index}.label", maximum=120)
    if kind == "workflow":
        expected = [(component_ids[index], component_ids[index + 1]) for index in range(len(component_ids) - 1)]
        actual = [(flow.get("from"), flow.get("to")) for flow in flows]
        if actual != expected:
            raise ManifestError("project understanding workflow must use one consecutive flow chain")
    _texts(result.get("unknowns"), "project understanding unknowns", maximum_items=12, maximum=500)
    result["context_packet_sha256"] = context["packet_sha256"]
    result["understanding_identity"] = sha256_bytes(canonical_json_bytes(result))
    return result


def change_interpretation_json_schema(
    allowed_evidence_ids: list[str], component_ids: list[str], raw_brief_schema: Mapping[str, Any]
) -> dict[str, Any]:
    audience = {
        "type": "object",
        "additionalProperties": False,
        "required": ["role", "reason", "evidence_ids"],
        "properties": {
            "role": {"type": "string", "maxLength": 80},
            "reason": {"type": "string", "maxLength": 240},
            "evidence_ids": {
                "type": "array",
                "minItems": 1,
                "maxItems": 12,
                "items": {"type": "string", "enum": allowed_evidence_ids},
            },
        },
    }
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["schema_version", "raw_brief", "change_summary", "owner_checks"],
        "properties": {
            "schema_version": {"type": "string", "const": CHANGE_INTERPRETATION_SCHEMA},
            "raw_brief": copy.deepcopy(dict(raw_brief_schema)),
            "change_summary": {
                "type": "object", "additionalProperties": False,
                "required": ["headline", "explanation", "changed_component_ids", "evidence_ids", "limitations", "audience_candidates"],
                "properties": {
                    "headline": {"type": "string", "maxLength": 56},
                    "explanation": {"type": "string", "maxLength": 360},
                    "changed_component_ids": {"type": "array", "maxItems": 1, "items": {"type": "string", "enum": component_ids}},
                    "evidence_ids": {"type": "array", "items": {"type": "string", "enum": allowed_evidence_ids}},
                    "limitations": {"type": "array", "items": {"type": "string", "minLength": 1}},
                    "audience_candidates": {"type": "array", "maxItems": 3, "items": audience},
                },
            },
            "owner_checks": {
                "type": "array", "minItems": 1, "maxItems": 3,
                "items": {
                    "type": "object", "additionalProperties": False,
                    "required": ["title", "instructions", "evidence_ids"],
                    "properties": {
                        "title": {"type": "string"}, "instructions": {"type": "string"},
                        "evidence_ids": {"type": "array", "items": {"type": "string", "enum": allowed_evidence_ids}},
                    },
                },
            },
        },
    }


def validate_change_interpretation(
    packet: Mapping[str, Any], understanding: Mapping[str, Any], value: Any
) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ManifestError("change interpretation must be an object")
    result = copy.deepcopy(dict(value))
    if set(result) != {"schema_version", "raw_brief", "change_summary", "owner_checks"} or result.get("schema_version") != CHANGE_INTERPRETATION_SCHEMA:
        raise ManifestError("change interpretation fields or schema are invalid")
    allowed_evidence = set(map(str, packet["allowed_evidence_ids"]))
    component_ids = {str(item["id"]) for item in understanding["components"]}
    summary = result.get("change_summary")
    if not isinstance(summary, Mapping) or set(summary) != {"headline", "explanation", "changed_component_ids", "evidence_ids", "limitations", "audience_candidates"}:
        raise ManifestError("change interpretation summary is invalid")
    _text(summary.get("headline"), "change_summary.headline", maximum=56)
    _text(summary.get("explanation"), "change_summary.explanation", maximum=360)
    changed = _texts(summary.get("changed_component_ids"), "change_summary.changed_component_ids", maximum_items=1, maximum=80)
    evidence = _texts(summary.get("evidence_ids"), "change_summary.evidence_ids", maximum_items=24, maximum=160)
    _texts(summary.get("limitations"), "change_summary.limitations", maximum_items=12, maximum=500)
    if not set(changed) <= component_ids or not set(evidence) <= allowed_evidence:
        raise ManifestError("change interpretation summary cites an unknown component or evidence")
    audiences = summary.get("audience_candidates")
    if not isinstance(audiences, list) or len(audiences) > 3:
        raise ManifestError("change interpretation audience candidates are invalid")
    for index, audience in enumerate(audiences):
        if not isinstance(audience, Mapping) or set(audience) != {"role", "reason", "evidence_ids"}:
            raise ManifestError(f"audience candidate {index} is invalid")
        _text(audience.get("role"), f"audience candidate {index}.role", maximum=80)
        _text(audience.get("reason"), f"audience candidate {index}.reason", maximum=240)
        refs = _texts(audience.get("evidence_ids"), f"audience candidate {index}.evidence_ids", maximum_items=12, maximum=160)
        if not refs or not set(refs) <= allowed_evidence:
            raise ManifestError(f"audience candidate {index} cites unknown or empty evidence")
    checks = result.get("owner_checks")
    if not isinstance(checks, list) or not 1 <= len(checks) <= 3:
        raise ManifestError("change interpretation needs one to three owner checks")
    for index, check in enumerate(checks):
        if not isinstance(check, Mapping) or set(check) != {"title", "instructions", "evidence_ids"}:
            raise ManifestError(f"owner check {index} is invalid")
        _text(check.get("title"), f"owner check {index}.title", maximum=120)
        _text(check.get("instructions"), f"owner check {index}.instructions", maximum=600)
        refs = _texts(check.get("evidence_ids"), f"owner check {index}.evidence_ids", maximum_items=12, maximum=160)
        if not set(refs) <= allowed_evidence:
            raise ManifestError(f"owner check {index} cites unknown evidence")
    return result


def target_profile_from_understanding(
    base_profile: Mapping[str, Any],
    understanding: Mapping[str, Any],
    commit: str,
    *,
    human_language: str = "zh-CN",
) -> dict[str, Any]:
    if human_language not in {"zh-CN", "en"}:
        raise ManifestError("human_language must be zh-CN or en")
    english = human_language == "en"
    profile = copy.deepcopy(dict(base_profile))
    source_ref_by_id = {
        str(item["id"]): str(item["source_ref"])
        for item in understanding.get("_context_sources", [])
    }
    components: list[dict[str, Any]] = []
    for index, item in enumerate(understanding["components"]):
        paths = list(map(str, item["code_paths"]))
        groups = sorted(
            {
                str(section["id"])
                for path in paths
                for section in profile.get("sections", [])
                if isinstance(section, Mapping)
                and section.get("id") != "unclassified"
                and _section_matches(section, path)
            }
        )
        source_refs = [
            source_ref_by_id[source_id]
            for source_id in item["source_ids"]
            if source_id in source_ref_by_id
        ] + [f"git:{commit}:{path}" for path in paths]
        components.append(
            {
                "id": str(item["id"]),
                "type": str(item["type"]),
                "label": str(item["label"]),
                "description": str(item["description"]),
                "grid_column": 1,
                "grid_row": index + 1,
                "group_ids": groups,
                "evidence_status": "model_interpreted_code_supported" if paths else "model_interpreted_only",
                "evidence_label": (
                    "Model interpretation with matching code"
                    if paths and english
                    else "Model interpretation without matching code"
                    if english
                    else "模型理解，已找到代码位置"
                    if paths
                    else "模型理解，尚未找到代码位置"
                ),
                "evidence_note": (
                    "A configured model interpreted this item from project material, and matching locations were found in the fixed source. It is still not runtime proof."
                    if paths and english
                    else "A configured model interpreted this item from project material, but no stable matching location was found in the fixed source. Owner confirmation is required."
                    if english
                    else "模型根据项目说明和固定版本代码位置提炼；这仍是候选理解，不是运行事实。"
                    if paths
                    else "模型根据项目说明提炼，但当前没有稳定代码位置支持；需要负责人确认。"
                ),
                "source_refs": source_refs,
            }
        )
    kind = str(understanding["structure_kind"])
    flows = [dict(item) for item in understanding["flows"]]
    purpose_sources = [
        source_ref_by_id[source_id]
        for source_id in understanding["purpose"]["source_ids"]
        if source_id in source_ref_by_id
    ]
    profile["profile_id"] = f"{str(profile['profile_id'])[:73]}-model"
    profile["conceptual_architecture"] = {
        "title": str(understanding["title"]),
        "description": str(understanding["purpose"]["text"]),
        "boundary_note": (
            "This map was produced by a configured model from fixed-revision project material and code locations, then checked locally against allowed sources. It is still not a runtime trace."
            if english
            else "这张图由配置模型根据固定版本项目材料和代码位置提炼，并已通过本地来源校验；它仍不是运行记录。"
        ),
        "components": components,
        "flows": flows,
        "purpose_statement_state": "supported_interpretation",
        "purpose_source_refs": purpose_sources,
        "architecture_kind": kind,
        "source_refs": purpose_sources,
        "workflow_order_status": "unverified" if kind == "workflow" else "not_applicable",
        "workflow_order_label": (
            "Model-proposed order; runtime not verified"
            if kind == "workflow" and english
            else "No sequence"
            if english
            else "模型候选顺序，尚未运行验证"
            if kind == "workflow"
            else "没有先后顺序"
        ),
        "workflow_order_note": (
            "The model proposed an owner-readable sequence, but no runtime evidence proves the execution order."
            if kind == "workflow" and english
            else "These capabilities are peers and do not imply runtime order."
            if english
            else "模型给出了负责人可读的候选顺序，但没有运行证据证明真实执行次序。"
            if kind == "workflow"
            else "这些是并列能力，不代表运行顺序。"
        ),
        "workflow_order_source_refs": purpose_sources if kind == "workflow" else [],
    }
    return profile


def attach_context_sources(
    understanding: Mapping[str, Any], context: Mapping[str, Any]
) -> dict[str, Any]:
    result = copy.deepcopy(dict(understanding))
    result["_context_sources"] = copy.deepcopy(list(context["sources"]))
    return result


def project_understanding_cache_key(
    context: Mapping[str, Any], provider_config_sha256: str, model: str,
    human_language: str = "zh-CN",
) -> str:
    return sha256_bytes(
        canonical_json_bytes(
            {
                "schema_version": PROJECT_UNDERSTANDING_SCHEMA,
                "head_commit": context["head_commit"],
                "context_packet_sha256": context["packet_sha256"],
                "provider_config_sha256": provider_config_sha256,
                "model": model,
                "human_language": human_language,
            }
        )
    )


def read_cached_project_understanding(
    cache_root: Path, key: str, context: Mapping[str, Any]
) -> dict[str, Any] | None:
    path = cache_root / "project-understanding" / f"{key}.json"
    if not path.is_file():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return validate_project_understanding(context, value)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ManifestError):
        return None


def write_cached_project_understanding(cache_root: Path, key: str, value: Mapping[str, Any]) -> Path:
    path = cache_root / "project-understanding" / f"{key}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    cache_value = {key: copy.deepcopy(item) for key, item in value.items() if not key.startswith("_") and key not in {"context_packet_sha256", "understanding_identity"}}
    temporary.write_bytes(canonical_json_bytes(cache_value) + b"\n")
    os.replace(temporary, path)
    return path


def _section_matches(section: Mapping[str, Any], path: str) -> bool:
    name = Path(path).name
    return (
        path in set(map(str, section.get("exact_paths", [])))
        or any(path == str(prefix) or path.startswith(str(prefix).rstrip("/") + "/") for prefix in section.get("path_prefixes", []))
        or any(name.startswith(str(prefix)) for prefix in section.get("basename_prefixes", []))
    )


def _outline_priority(path: str) -> tuple[int, int, str]:
    lowered = path.casefold()
    name = Path(path).stem.casefold()
    preferred = {
        "app", "application", "main", "cli", "server", "api", "router",
        "routes", "controller", "service", "workflow", "pipeline", "agent",
    }
    penalty = 1 if any(part in {"test", "tests", "spec", "specs", "docs", "examples"} for part in Path(path).parts) else 0
    return (0 if name in preferred else 1, penalty + lowered.count("/"), lowered)
