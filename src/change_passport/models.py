from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

MANIFEST_SCHEMA = "change-passport.sample.v1"
ID_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9._-]{0,79}$")

AUTHORITY_BY_KIND: dict[str, set[str]] = {
    "task": {"original_task", "retrospective_claim"},
    "test": {"actual_test_receipt", "self_report"},
    "history": {"approved_history", "candidate_history"},
}


class ManifestError(ValueError):
    """Raised when a sample manifest violates the evidence contract."""


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ManifestError(f"{label} must be an object")
    return value


def _require_string(value: Any, label: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str):
        raise ManifestError(f"{label} must be a string")
    result = value.strip()
    if not allow_empty and not result:
        raise ManifestError(f"{label} must not be empty")
    return result


def _validate_id(value: Any, label: str) -> str:
    result = _require_string(value, label)
    if not ID_PATTERN.fullmatch(result):
        raise ManifestError(f"{label} has an invalid identifier")
    if result.startswith("git.") or result.startswith("system."):
        raise ManifestError(f"{label} uses a reserved identifier prefix")
    return result


def _windows_identity(path: Path) -> str:
    return os.path.normcase(str(path.resolve(strict=True))).casefold()


@dataclass(frozen=True)
class Limits:
    max_patch_bytes: int = 200_000
    max_input_bytes: int = 64_000
    git_timeout_seconds: int = 15

    @classmethod
    def from_dict(cls, value: Any) -> "Limits":
        if value is None:
            return cls()
        data = _require_mapping(value, "limits")
        allowed = {"max_patch_bytes", "max_input_bytes", "git_timeout_seconds"}
        unknown = set(data) - allowed
        if unknown:
            raise ManifestError(f"limits contains unknown fields: {sorted(unknown)}")
        values: dict[str, int] = {}
        for key in allowed:
            if key not in data:
                continue
            raw = data[key]
            if not isinstance(raw, int) or isinstance(raw, bool) or raw <= 0:
                raise ManifestError(f"limits.{key} must be a positive integer")
            values[key] = raw
        result = cls(**values)
        if result.max_patch_bytes > 5_000_000:
            raise ManifestError("limits.max_patch_bytes exceeds the 5 MB spike boundary")
        if result.max_input_bytes > 1_000_000:
            raise ManifestError("limits.max_input_bytes exceeds the 1 MB spike boundary")
        if result.git_timeout_seconds > 120:
            raise ManifestError("limits.git_timeout_seconds exceeds 120 seconds")
        return result


@dataclass(frozen=True)
class Source:
    source_type: str
    text: str | None = None
    path: str | None = None

    @classmethod
    def from_dict(cls, value: Any, label: str) -> "Source":
        data = _require_mapping(value, label)
        source_type = _require_string(data.get("type"), f"{label}.type")
        unknown = set(data) - {"type", "text", "path"}
        if unknown:
            raise ManifestError(f"{label} contains unknown fields: {sorted(unknown)}")
        if source_type == "inline":
            text = _require_string(data.get("text"), f"{label}.text")
            if data.get("path") is not None:
                raise ManifestError(f"{label}.path is not allowed for inline sources")
            return cls(source_type=source_type, text=text)
        if source_type == "file":
            path = _require_string(data.get("path"), f"{label}.path")
            if data.get("text") is not None:
                raise ManifestError(f"{label}.text is not allowed for file sources")
            return cls(source_type=source_type, path=path)
        raise ManifestError(f"{label}.type must be inline or file")

    def resolve_path(self, manifest_dir: Path) -> Path:
        if self.source_type != "file" or self.path is None:
            raise ManifestError("only file sources have a path")
        candidate = Path(self.path)
        if not candidate.is_absolute():
            candidate = manifest_dir / candidate
        try:
            resolved = candidate.resolve(strict=True)
        except OSError as exc:
            raise ManifestError(f"source file does not exist: {candidate}") from exc
        if not resolved.is_file():
            raise ManifestError(f"source path is not a file: {resolved}")
        return resolved

    def identities(self, manifest_dir: Path, max_bytes: int) -> set[str]:
        if self.source_type == "inline":
            assert self.text is not None
            return {f"content:{sha256_bytes(self.text.encode('utf-8'))}"}
        resolved = self.resolve_path(manifest_dir)
        raw = resolved.read_bytes()
        if len(raw) > max_bytes:
            raise ManifestError(
                f"evidence source exceeds max_input_bytes ({len(raw)} > {max_bytes})"
            )
        return {
            f"file:{_windows_identity(resolved)}",
            f"content:{sha256_bytes(raw)}",
        }

    def read_text(self, manifest_dir: Path, max_bytes: int) -> str:
        if self.source_type == "inline":
            assert self.text is not None
            raw = self.text.encode("utf-8")
        else:
            raw = self.resolve_path(manifest_dir).read_bytes()
        if len(raw) > max_bytes:
            raise ManifestError(
                f"evidence source exceeds max_input_bytes ({len(raw)} > {max_bytes})"
            )
        return raw.decode("utf-8", errors="replace")


@dataclass(frozen=True)
class EvidenceInput:
    evidence_id: str
    kind: str
    authority: str
    source: Source

    @classmethod
    def from_dict(cls, value: Any, index: int) -> "EvidenceInput":
        label = f"evidence_inputs[{index}]"
        data = _require_mapping(value, label)
        unknown = set(data) - {"id", "kind", "authority", "source"}
        if unknown:
            raise ManifestError(f"{label} contains unknown fields: {sorted(unknown)}")
        evidence_id = _validate_id(data.get("id"), f"{label}.id")
        kind = _require_string(data.get("kind"), f"{label}.kind")
        authority = _require_string(data.get("authority"), f"{label}.authority")
        if kind not in AUTHORITY_BY_KIND:
            raise ManifestError(f"{label}.kind must be task, test, or history")
        if authority not in AUTHORITY_BY_KIND[kind]:
            raise ManifestError(f"{label}.authority is invalid for kind={kind}")
        source = Source.from_dict(data.get("source"), f"{label}.source")
        return cls(evidence_id=evidence_id, kind=kind, authority=authority, source=source)


@dataclass(frozen=True)
class HiddenGroundTruth:
    ground_truth_id: str
    source: Source

    @classmethod
    def from_dict(cls, value: Any, index: int) -> "HiddenGroundTruth":
        label = f"hidden_ground_truth[{index}]"
        data = _require_mapping(value, label)
        unknown = set(data) - {"id", "source"}
        if unknown:
            raise ManifestError(f"{label} contains unknown fields: {sorted(unknown)}")
        return cls(
            ground_truth_id=_validate_id(data.get("id"), f"{label}.id"),
            source=Source.from_dict(data.get("source"), f"{label}.source"),
        )


@dataclass(frozen=True)
class RepositorySpec:
    path: Path
    base: str
    head: str

    @classmethod
    def from_dict(cls, value: Any, manifest_dir: Path) -> "RepositorySpec":
        data = _require_mapping(value, "repository")
        unknown = set(data) - {"path", "base", "head"}
        if unknown:
            raise ManifestError(f"repository contains unknown fields: {sorted(unknown)}")
        raw_path = Path(_require_string(data.get("path"), "repository.path"))
        candidate = raw_path if raw_path.is_absolute() else manifest_dir / raw_path
        try:
            path = candidate.resolve(strict=True)
        except OSError as exc:
            raise ManifestError(f"repository path does not exist: {candidate}") from exc
        if not path.is_dir():
            raise ManifestError(f"repository path is not a directory: {path}")
        return cls(
            path=path,
            base=_require_string(data.get("base"), "repository.base"),
            head=_require_string(data.get("head"), "repository.head"),
        )


@dataclass(frozen=True)
class SampleManifest:
    manifest_path: Path
    sample_id: str
    repository: RepositorySpec
    evidence_inputs: tuple[EvidenceInput, ...]
    hidden_ground_truth: tuple[HiddenGroundTruth, ...]
    architecture_baseline_path: Path | None
    limits: Limits

    @property
    def manifest_dir(self) -> Path:
        return self.manifest_path.parent

    @classmethod
    def load(cls, manifest_path: str | Path) -> "SampleManifest":
        path = Path(manifest_path).resolve(strict=True)
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ManifestError(f"manifest is not valid UTF-8 JSON: {path}") from exc
        data = _require_mapping(raw, "manifest")
        allowed = {
            "schema_version",
            "sample_id",
            "repository",
            "evidence_inputs",
            "hidden_ground_truth",
            "architecture_baseline",
            "limits",
        }
        unknown = set(data) - allowed
        if unknown:
            raise ManifestError(f"manifest contains unknown fields: {sorted(unknown)}")
        if data.get("schema_version") != MANIFEST_SCHEMA:
            raise ManifestError(f"schema_version must be {MANIFEST_SCHEMA}")
        sample_id = _validate_id(data.get("sample_id"), "sample_id")
        evidence_raw = data.get("evidence_inputs", [])
        hidden_raw = data.get("hidden_ground_truth", [])
        if not isinstance(evidence_raw, list):
            raise ManifestError("evidence_inputs must be an array")
        if not isinstance(hidden_raw, list):
            raise ManifestError("hidden_ground_truth must be an array")
        evidence = tuple(EvidenceInput.from_dict(item, i) for i, item in enumerate(evidence_raw))
        hidden = tuple(HiddenGroundTruth.from_dict(item, i) for i, item in enumerate(hidden_raw))
        ids = [item.evidence_id for item in evidence] + [item.ground_truth_id for item in hidden]
        if len(ids) != len(set(ids)):
            raise ManifestError("all evidence and ground-truth IDs must be unique")
        baseline_path: Path | None = None
        baseline_raw = data.get("architecture_baseline")
        if baseline_raw is not None:
            baseline_data = _require_mapping(baseline_raw, "architecture_baseline")
            if set(baseline_data) != {"path"}:
                raise ManifestError("architecture_baseline must contain only path")
            raw_baseline_path = Path(
                _require_string(baseline_data.get("path"), "architecture_baseline.path")
            )
            candidate = (
                raw_baseline_path
                if raw_baseline_path.is_absolute()
                else path.parent / raw_baseline_path
            )
            try:
                baseline_path = candidate.resolve(strict=True)
            except OSError as exc:
                raise ManifestError(
                    f"architecture baseline does not exist: {candidate}"
                ) from exc
            if not baseline_path.is_file():
                raise ManifestError(
                    f"architecture baseline is not a file: {baseline_path}"
                )
        result = cls(
            manifest_path=path,
            sample_id=sample_id,
            repository=RepositorySpec.from_dict(data.get("repository"), path.parent),
            evidence_inputs=evidence,
            hidden_ground_truth=hidden,
            architecture_baseline_path=baseline_path,
            limits=Limits.from_dict(data.get("limits")),
        )
        result.validate_separation()
        return result

    def validate_separation(self) -> None:
        input_identities = set().union(
            *(
                item.source.identities(self.manifest_dir, self.limits.max_input_bytes)
                for item in self.evidence_inputs
            ),
            set(),
        )
        hidden_identities = set().union(
            *(
                item.source.identities(self.manifest_dir, self.limits.max_input_bytes)
                for item in self.hidden_ground_truth
            ),
            set(),
        )
        overlap = sorted(input_identities & hidden_identities)
        if overlap:
            raise ManifestError(
                "generator evidence overlaps hidden ground truth: " + ", ".join(overlap)
            )

    def validate_output_path(self, output_path: str | Path) -> Path:
        output = Path(output_path).resolve(strict=False)
        repository = self.repository.path.resolve(strict=True)
        if output == repository or output.is_relative_to(repository):
            raise ManifestError("output directory must not be inside the target repository")
        source_paths = {
            item.source.resolve_path(self.manifest_dir)
            for item in (*self.evidence_inputs, *self.hidden_ground_truth)
            if item.source.source_type == "file"
        }
        if output in source_paths:
            raise ManifestError("output path overlaps an evidence source")
        return output
