from __future__ import annotations

import json
import re
from dataclasses import dataclass
from importlib import resources
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

from .models import ManifestError, sha256_bytes

TARGET_PROFILE_SCHEMA = "change-passport.target-profile.v1"
_ID_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9._-]{0,79}$")
_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ManifestError(f"{label} must be a non-empty string")
    return value.strip()


def _id(value: Any, label: str) -> str:
    result = _text(value, label)
    if not _ID_PATTERN.fullmatch(result):
        raise ManifestError(f"{label} has an invalid identifier")
    return result


def _text_list(value: Any, label: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise ManifestError(f"{label} must be an array")
    return tuple(_text(item, f"{label}[{index}]") for index, item in enumerate(value))


@dataclass(frozen=True)
class ProfileSection:
    section_id: str
    label: str
    responsibility: str
    lane: str
    path_prefixes: tuple[str, ...]
    exact_paths: tuple[str, ...]
    basename_prefixes: tuple[str, ...]

    @classmethod
    def from_dict(cls, value: Any, index: int) -> "ProfileSection":
        label = f"target_profile.sections[{index}]"
        if not isinstance(value, Mapping):
            raise ManifestError(f"{label} must be an object")
        allowed = {
            "id",
            "label",
            "responsibility",
            "lane",
            "path_prefixes",
            "exact_paths",
            "basename_prefixes",
        }
        unknown = set(value) - allowed
        if unknown:
            raise ManifestError(f"{label} contains unknown fields: {sorted(unknown)}")
        lane = _text(value.get("lane"), f"{label}.lane")
        if lane not in {"main", "support"}:
            raise ManifestError(f"{label}.lane must be main or support")
        result = cls(
            section_id=_id(value.get("id"), f"{label}.id"),
            label=_text(value.get("label"), f"{label}.label"),
            responsibility=_text(value.get("responsibility"), f"{label}.responsibility"),
            lane=lane,
            path_prefixes=_text_list(value.get("path_prefixes", []), f"{label}.path_prefixes"),
            exact_paths=_text_list(value.get("exact_paths", []), f"{label}.exact_paths"),
            basename_prefixes=_text_list(
                value.get("basename_prefixes", []), f"{label}.basename_prefixes"
            ),
        )
        if result.section_id == "unclassified" and any(
            (result.path_prefixes, result.exact_paths, result.basename_prefixes)
        ):
            raise ManifestError(
                f"{label} unclassified fallback cannot contain path matching rules"
            )
        return result

    def matches(self, path: str) -> bool:
        name = PurePosixPath(path).name
        return (
            path in self.exact_paths
            or any(path == prefix or path.startswith(prefix.rstrip("/") + "/") for prefix in self.path_prefixes)
            or any(name.startswith(prefix) for prefix in self.basename_prefixes)
        )


@dataclass(frozen=True)
class ModuleArea:
    area_id: str
    order: int
    path_prefixes: tuple[str, ...]
    exact_paths: tuple[str, ...]
    basename_prefixes: tuple[str, ...]
    label: str
    description: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.area_id,
            "order": self.order,
            "path_prefixes": list(self.path_prefixes),
            "exact_paths": list(self.exact_paths),
            "basename_prefixes": list(self.basename_prefixes),
            "label": self.label,
            "description": self.description,
        }

    def matches(self, path: str) -> bool:
        name = PurePosixPath(path).name
        return (
            path in self.exact_paths
            or any(path == prefix or path.startswith(prefix.rstrip("/") + "/") for prefix in self.path_prefixes)
            or any(name.startswith(prefix) for prefix in self.basename_prefixes)
        )

    @classmethod
    def from_dict(cls, value: Any, index: int, label: str) -> "ModuleArea":
        item_label = f"{label}.module_areas[{index}]"
        allowed = {
            "id",
            "order",
            "path_prefixes",
            "exact_paths",
            "basename_prefixes",
            "label",
            "description",
        }
        if not isinstance(value, Mapping) or set(value) - allowed:
            raise ManifestError(
                f"{item_label} contains unsupported fields"
            )
        order = value.get("order")
        if not isinstance(order, int) or isinstance(order, bool) or order < 0:
            raise ManifestError(f"{item_label}.order must be a non-negative integer")
        prefixes = _text_list(value.get("path_prefixes", []), f"{item_label}.path_prefixes")
        exact_paths = _text_list(value.get("exact_paths", []), f"{item_label}.exact_paths")
        basename_prefixes = _text_list(value.get("basename_prefixes", []), f"{item_label}.basename_prefixes")
        if not any((prefixes, exact_paths, basename_prefixes)):
            raise ManifestError(
                f"{item_label} must contain at least one path_prefixes, exact_paths, or basename_prefixes rule"
            )
        return cls(
            area_id=_id(value.get("id"), f"{item_label}.id"),
            order=order,
            path_prefixes=prefixes,
            exact_paths=exact_paths,
            basename_prefixes=basename_prefixes,
            label=_text(value.get("label"), f"{item_label}.label"),
            description=_text(value.get("description"), f"{item_label}.description"),
        )


@dataclass(frozen=True)
class ConceptualComponent:
    component_id: str
    component_type: str
    label: str
    description: str
    grid_column: int
    grid_row: int
    group_ids: tuple[str, ...]
    evidence_status: str | None = None
    evidence_label: str | None = None
    evidence_note: str | None = None
    source_refs: tuple[str, ...] | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "id": self.component_id,
            "type": self.component_type,
            "label": self.label,
            "description": self.description,
            "grid_column": self.grid_column,
            "grid_row": self.grid_row,
            "group_ids": list(self.group_ids),
        }
        if self.evidence_status is not None:
            result.update(
                {
                    "evidence_status": self.evidence_status,
                    "evidence_label": self.evidence_label,
                    "evidence_note": self.evidence_note,
                    "source_refs": list(self.source_refs or ()),
                }
            )
        return result

    @classmethod
    def from_dict(cls, value: Any, index: int, label: str) -> "ConceptualComponent":
        item_label = f"{label}.conceptual_architecture.components[{index}]"
        required = {
            "id",
            "type",
            "label",
            "description",
            "grid_column",
            "grid_row",
            "group_ids",
        }
        optional = {"evidence_status", "evidence_label", "evidence_note", "source_refs"}
        if (
            not isinstance(value, Mapping)
            or not required.issubset(value)
            or set(value) - required - optional
        ):
            raise ManifestError(
                f"{item_label} must contain "
                "id, type, label, description, grid_column, grid_row, and group_ids"
            )
        component_type = _text(value.get("type"), f"{item_label}.type")
        if component_type not in {"input", "process", "output", "human_gate", "state"}:
            raise ManifestError(
                f"{item_label}.type must be input, process, output, human_gate, or state"
            )
        grid_column = value.get("grid_column")
        grid_row = value.get("grid_row")
        if (
            not isinstance(grid_column, int)
            or isinstance(grid_column, bool)
            or grid_column < 1
        ):
            raise ManifestError(f"{item_label}.grid_column must be a positive integer")
        if not isinstance(grid_row, int) or isinstance(grid_row, bool) or grid_row < 1:
            raise ManifestError(f"{item_label}.grid_row must be a positive integer")
        group_ids = _text_list(value.get("group_ids"), f"{item_label}.group_ids")
        if len(group_ids) != len(set(group_ids)):
            raise ManifestError(f"{item_label}.group_ids contains duplicate IDs")
        evidence_status = value.get("evidence_status")
        if evidence_status is not None:
            evidence_status = _text(evidence_status, f"{item_label}.evidence_status")
            if evidence_status not in {
                "declared_and_code_supported",
                "declared_only",
                "code_discovered",
                "generated_candidate",
            }:
                raise ManifestError(f"{item_label}.evidence_status is unsupported")
            evidence_label = _text(value.get("evidence_label"), f"{item_label}.evidence_label")
            evidence_note = _text(value.get("evidence_note"), f"{item_label}.evidence_note")
            source_refs: tuple[str, ...] | None = _text_list(
                value.get("source_refs", []), f"{item_label}.source_refs"
            )
        else:
            if optional & set(value):
                raise ManifestError(
                    f"{item_label} evidence fields require evidence_status"
                )
            evidence_label = None
            evidence_note = None
            source_refs = None
        return cls(
            component_id=_id(value.get("id"), f"{item_label}.id"),
            component_type=component_type,
            label=_text(value.get("label"), f"{item_label}.label"),
            description=_text(value.get("description"), f"{item_label}.description"),
            grid_column=grid_column,
            grid_row=grid_row,
            group_ids=group_ids,
            evidence_status=evidence_status,
            evidence_label=evidence_label,
            evidence_note=evidence_note,
            source_refs=source_refs,
        )


@dataclass(frozen=True)
class ConceptualFlow:
    source_id: str
    target_id: str
    label: str

    def to_dict(self) -> dict[str, str]:
        return {"from": self.source_id, "to": self.target_id, "label": self.label}

    @classmethod
    def from_dict(cls, value: Any, index: int, label: str) -> "ConceptualFlow":
        item_label = f"{label}.conceptual_architecture.flows[{index}]"
        if not isinstance(value, Mapping) or set(value) != {"from", "to", "label"}:
            raise ManifestError(f"{item_label} must contain only from, to, and label")
        source_id = _id(value.get("from"), f"{item_label}.from")
        target_id = _id(value.get("to"), f"{item_label}.to")
        if source_id == target_id:
            raise ManifestError(f"{item_label} cannot connect a component to itself")
        return cls(
            source_id=source_id,
            target_id=target_id,
            label=_text(value.get("label"), f"{item_label}.label"),
        )


@dataclass(frozen=True)
class ConceptualArchitecture:
    title: str
    description: str
    boundary_note: str
    components: tuple[ConceptualComponent, ...]
    flows: tuple[ConceptualFlow, ...]
    purpose_statement_state: str | None = None
    purpose_source_refs: tuple[str, ...] | None = None
    source_refs: tuple[str, ...] | None = None
    workflow_order_status: str | None = None
    workflow_order_label: str | None = None
    workflow_order_note: str | None = None
    workflow_order_source_refs: tuple[str, ...] | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "title": self.title,
            "description": self.description,
            "boundary_note": self.boundary_note,
            "components": [item.to_dict() for item in self.components],
            "flows": [item.to_dict() for item in self.flows],
        }
        if self.purpose_statement_state is not None:
            result.update(
                {
                    "purpose_statement_state": self.purpose_statement_state,
                    "purpose_source_refs": list(self.purpose_source_refs or ()),
                    "source_refs": list(self.source_refs or ()),
                    "workflow_order_status": self.workflow_order_status,
                    "workflow_order_label": self.workflow_order_label,
                    "workflow_order_note": self.workflow_order_note,
                    "workflow_order_source_refs": list(
                        self.workflow_order_source_refs or ()
                    ),
                }
            )
        return result

    @classmethod
    def from_dict(cls, value: Any, label: str) -> "ConceptualArchitecture":
        required = {"title", "description", "boundary_note", "components", "flows"}
        optional = {
            "purpose_statement_state",
            "purpose_source_refs",
            "source_refs",
            "workflow_order_status",
            "workflow_order_label",
            "workflow_order_note",
            "workflow_order_source_refs",
        }
        item_label = f"{label}.conceptual_architecture"
        if (
            not isinstance(value, Mapping)
            or not required.issubset(value)
            or set(value) - required - optional
        ):
            raise ManifestError(
                f"{item_label} must contain title, description, boundary_note, components, and flows"
            )
        raw_components = value.get("components")
        raw_flows = value.get("flows")
        if not isinstance(raw_components, list) or not raw_components:
            raise ManifestError(f"{item_label}.components must be a non-empty array")
        if not isinstance(raw_flows, list) or not raw_flows:
            raise ManifestError(f"{item_label}.flows must be a non-empty array")
        components = tuple(
            ConceptualComponent.from_dict(item, index, label)
            for index, item in enumerate(raw_components)
        )
        component_ids = [item.component_id for item in components]
        if len(component_ids) != len(set(component_ids)):
            raise ManifestError(f"{item_label}.components contains duplicate IDs")
        coordinates = [(item.grid_column, item.grid_row) for item in components]
        if len(coordinates) != len(set(coordinates)):
            raise ManifestError(f"{item_label}.components contains duplicate grid coordinates")
        flows = tuple(
            ConceptualFlow.from_dict(item, index, label)
            for index, item in enumerate(raw_flows)
        )
        flow_ids = [(item.source_id, item.target_id) for item in flows]
        if len(flow_ids) != len(set(flow_ids)):
            raise ManifestError(f"{item_label}.flows contains duplicate relationships")
        unknown_component_ids = {
            component_id
            for flow in flows
            for component_id in (flow.source_id, flow.target_id)
            if component_id not in component_ids
        }
        if unknown_component_ids:
            raise ManifestError(
                f"{item_label}.flows references unknown components: "
                f"{sorted(unknown_component_ids)}"
            )
        purpose_statement_state = value.get("purpose_statement_state")
        if purpose_statement_state is not None:
            purpose_statement_state = _text(
                purpose_statement_state, f"{item_label}.purpose_statement_state"
            )
            if purpose_statement_state not in {"project_declared", "unknown"}:
                raise ManifestError(
                    f"{item_label}.purpose_statement_state must be project_declared or unknown"
                )
            workflow_order_status = _text(
                value.get("workflow_order_status"),
                f"{item_label}.workflow_order_status",
            )
            if workflow_order_status not in {
                "code_supported",
                "partially_supported",
                "conflicting",
                "unverified",
            }:
                raise ManifestError(f"{item_label}.workflow_order_status is unsupported")
            purpose_source_refs: tuple[str, ...] | None = _text_list(
                value.get("purpose_source_refs", []),
                f"{item_label}.purpose_source_refs",
            )
            source_refs: tuple[str, ...] | None = _text_list(
                value.get("source_refs", []), f"{item_label}.source_refs"
            )
            workflow_order_label = _text(
                value.get("workflow_order_label"), f"{item_label}.workflow_order_label"
            )
            workflow_order_note = _text(
                value.get("workflow_order_note"), f"{item_label}.workflow_order_note"
            )
            workflow_order_source_refs: tuple[str, ...] | None = _text_list(
                value.get("workflow_order_source_refs", []),
                f"{item_label}.workflow_order_source_refs",
            )
        else:
            if optional & set(value):
                raise ManifestError(
                    f"{item_label} evidence fields require purpose_statement_state"
                )
            purpose_source_refs = None
            source_refs = None
            workflow_order_status = None
            workflow_order_label = None
            workflow_order_note = None
            workflow_order_source_refs = None
        return cls(
            title=_text(value.get("title"), f"{item_label}.title"),
            description=_text(value.get("description"), f"{item_label}.description"),
            boundary_note=_text(value.get("boundary_note"), f"{item_label}.boundary_note"),
            components=components,
            flows=flows,
            purpose_statement_state=purpose_statement_state,
            purpose_source_refs=purpose_source_refs,
            source_refs=source_refs,
            workflow_order_status=workflow_order_status,
            workflow_order_label=workflow_order_label,
            workflow_order_note=workflow_order_note,
            workflow_order_source_refs=workflow_order_source_refs,
        )

    def validate_group_ids(self, section_ids: set[str], label: str) -> None:
        unknown_group_ids = {
            group_id
            for component in self.components
            for group_id in component.group_ids
            if group_id not in section_ids
        }
        if unknown_group_ids:
            raise ManifestError(
                f"{label}.conceptual_architecture references unknown section IDs: "
                f"{sorted(unknown_group_ids)}"
            )


@dataclass(frozen=True)
class PresentationProfile:
    profile_id: str
    profile_sha256: str
    display_name: str
    brand_mark: str
    node_label_rules: tuple[tuple[str, str], ...]
    term_replacements: tuple[tuple[str, str], ...]
    module_areas: tuple[ModuleArea, ...]
    conceptual_architecture: ConceptualArchitecture | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "profile_sha256": self.profile_sha256,
            "display_name": self.display_name,
            "brand_mark": self.brand_mark,
            "node_label_rules": [
                {"pattern": pattern, "label": label}
                for pattern, label in self.node_label_rules
            ],
            "term_replacements": [
                {"from": source, "to": target}
                for source, target in self.term_replacements
            ],
            "module_areas": [item.to_dict() for item in self.module_areas],
            "conceptual_architecture": (
                self.conceptual_architecture.to_dict()
                if self.conceptual_architecture is not None
                else None
            ),
        }

    @classmethod
    def from_dict(cls, value: Any, label: str = "target_profile") -> "PresentationProfile":
        if not isinstance(value, Mapping):
            raise ManifestError(f"{label} must be an object")
        allowed = {
            "profile_id",
            "profile_sha256",
            "display_name",
            "brand_mark",
            "node_label_rules",
            "term_replacements",
            "module_areas",
            "conceptual_architecture",
        }
        unknown = set(value) - allowed
        if unknown:
            raise ManifestError(f"{label} contains unknown fields: {sorted(unknown)}")
        profile_sha256 = _text(value.get("profile_sha256"), f"{label}.profile_sha256")
        if not _SHA256_PATTERN.fullmatch(profile_sha256):
            raise ManifestError(f"{label}.profile_sha256 must be a lowercase SHA-256")
        brand_mark = _text(value.get("brand_mark"), f"{label}.brand_mark")
        if len(brand_mark) > 4:
            raise ManifestError(f"{label}.brand_mark must contain at most four characters")

        def parse_rules(key: str, source_key: str, target_key: str) -> tuple[tuple[str, str], ...]:
            items = value.get(key, [])
            if not isinstance(items, list):
                raise ManifestError(f"{label}.{key} must be an array")
            result: list[tuple[str, str]] = []
            for index, item in enumerate(items):
                if not isinstance(item, Mapping) or set(item) != {source_key, target_key}:
                    raise ManifestError(
                        f"{label}.{key}[{index}] must contain only {source_key} and {target_key}"
                    )
                result.append(
                    (
                        _text(item.get(source_key), f"{label}.{key}[{index}].{source_key}"),
                        _text(item.get(target_key), f"{label}.{key}[{index}].{target_key}"),
                    )
                )
            return tuple(result)

        module_areas = value.get("module_areas", [])
        if not isinstance(module_areas, list):
            raise ManifestError(f"{label}.module_areas must be an array")
        raw_conceptual_architecture = value.get("conceptual_architecture")
        if raw_conceptual_architecture is not None and not isinstance(
            raw_conceptual_architecture, Mapping
        ):
            raise ManifestError(f"{label}.conceptual_architecture must be an object or null")
        return cls(
            profile_id=_id(value.get("profile_id"), f"{label}.profile_id"),
            profile_sha256=profile_sha256,
            display_name=_text(value.get("display_name"), f"{label}.display_name"),
            brand_mark=brand_mark,
            node_label_rules=parse_rules("node_label_rules", "pattern", "label"),
            term_replacements=parse_rules("term_replacements", "from", "to"),
            module_areas=tuple(
                ModuleArea.from_dict(item, index, label)
                for index, item in enumerate(module_areas)
            ),
            conceptual_architecture=(
                ConceptualArchitecture.from_dict(raw_conceptual_architecture, label)
                if raw_conceptual_architecture is not None
                else None
            ),
        )


@dataclass(frozen=True)
class TargetProfile:
    presentation: PresentationProfile
    sections: tuple[ProfileSection, ...]

    @property
    def profile_id(self) -> str:
        return self.presentation.profile_id

    @property
    def profile_sha256(self) -> str:
        return self.presentation.profile_sha256

    def section_id_for_path(self, path: str) -> str:
        for section in self.sections:
            if section.section_id != "unclassified" and section.matches(path):
                return section.section_id
        return "unclassified"

    def group_source(self, section_id: str) -> str:
        source = f"target-profile:{self.profile_id}:sha256:{self.profile_sha256}"
        return source if section_id != "unclassified" else source + ":unclassified-fallback"

    def snapshot_metadata(self) -> dict[str, Any]:
        return self.presentation.to_dict()


def _parse_profile(raw: bytes, label: str) -> TargetProfile:
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ManifestError(f"{label} is not valid UTF-8 JSON") from exc
    if not isinstance(value, Mapping):
        raise ManifestError(f"{label} must be an object")
    allowed = {
        "schema_version",
        "profile_id",
        "display_name",
        "brand_mark",
        "sections",
        "node_label_rules",
        "term_replacements",
        "module_areas",
        "conceptual_architecture",
    }
    unknown = set(value) - allowed
    if unknown:
        raise ManifestError(f"{label} contains unknown fields: {sorted(unknown)}")
    if value.get("schema_version") != TARGET_PROFILE_SCHEMA:
        raise ManifestError(f"{label}.schema_version must be {TARGET_PROFILE_SCHEMA}")
    sections_value = value.get("sections")
    if not isinstance(sections_value, list) or not sections_value:
        raise ManifestError(f"{label}.sections must be a non-empty array")
    sections = tuple(ProfileSection.from_dict(item, index) for index, item in enumerate(sections_value))
    section_ids = [section.section_id for section in sections]
    if len(section_ids) != len(set(section_ids)):
        raise ManifestError(f"{label}.sections contains duplicate IDs")
    if section_ids.count("unclassified") != 1:
        raise ManifestError(f"{label}.sections must contain exactly one unclassified fallback")
    presentation = PresentationProfile.from_dict(
        {
            "profile_id": value.get("profile_id"),
            "profile_sha256": sha256_bytes(raw),
            "display_name": value.get("display_name"),
            "brand_mark": value.get("brand_mark"),
            "node_label_rules": value.get("node_label_rules", []),
            "term_replacements": value.get("term_replacements", []),
            "module_areas": value.get("module_areas", []),
            "conceptual_architecture": value.get("conceptual_architecture"),
        },
        label,
    )
    if presentation.conceptual_architecture is not None:
        presentation.conceptual_architecture.validate_group_ids(set(section_ids), label)
    return TargetProfile(presentation=presentation, sections=sections)


def load_target_profile(path: Path | None) -> TargetProfile:
    if path is None:
        try:
            raw = (
                resources.files("plainchange")
                .joinpath("assets/default-target-profile.json")
                .read_bytes()
            )
        except (FileNotFoundError, OSError) as exc:
            raise ManifestError("packaged default target profile is missing") from exc
        return _parse_profile(raw, "packaged default target profile")
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise ManifestError(f"target profile cannot be read: {path}") from exc
    if len(raw) > 256_000:
        raise ManifestError("target profile exceeds the 256 KB boundary")
    return _parse_profile(raw, "target profile")


def default_presentation_profile() -> PresentationProfile:
    return load_target_profile(None).presentation
