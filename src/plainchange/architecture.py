from __future__ import annotations

import ast
import html
import json
import os
import posixpath
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Iterable, Mapping

from .analysis_cache import AnalysisCache, cache_key
from .git_evidence import (
    GitEvidence,
    GitTreeEntry,
    list_git_tree,
    read_git_blob,
    read_git_blobs,
)
from .models import ManifestError, SampleManifest, canonical_json_bytes, sha256_bytes
from .source_scope import (
    SUPPORTED_SOURCE_SUFFIXES,
    is_supported_source_path,
    is_vendored_or_generated_path,
)
from .target_profile import PresentationProfile, TargetProfile, load_target_profile

BASELINE_SCHEMA = "change-passport.architecture-baseline.v1"
DELTA_SCHEMA = "change-passport.architecture-delta.v1"
PROPOSAL_SCHEMA = "change-passport.baseline-proposal.v1"
DECISION_SCHEMA = "change-passport.baseline-decision.v1"
SYSTEM_ARCHITECTURE_SCHEMA = "change-passport.system-architecture.v1"
SUPPORTED_SUFFIXES = SUPPORTED_SOURCE_SUFFIXES
MAX_ARCHITECTURE_BLOB_BYTES = 300_000
MAX_DISPLAY_NODES = 14

class ArchitectureError(ManifestError):
    """Raised when an architecture baseline or deterministic delta fails closed."""


def _text(value: Any, label: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str):
        raise ArchitectureError(f"{label} must be a string")
    result = value.strip()
    if not result and not allow_empty:
        raise ArchitectureError(f"{label} must not be empty")
    return result


def _string_tuple(value: Any, label: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise ArchitectureError(f"{label} must be an array")
    return tuple(_text(item, f"{label}[{index}]") for index, item in enumerate(value))


def _repository_id(path: Path) -> str:
    identity = os.path.normcase(str(path.resolve(strict=True))).casefold()
    return "repo." + sha256_bytes(identity.encode("utf-8"))[:20]


def _node_id(path: str) -> str:
    return "module." + sha256_bytes(path.encode("utf-8"))[:20]


def _edge_id(source: str, relation: str, target: str) -> str:
    return "edge." + sha256_bytes(f"{source}:{relation}:{target}".encode("utf-8"))[:20]


@dataclass(frozen=True)
class ArchitectureNode:
    node_id: str
    kind: str
    label: str
    owned_paths: tuple[str, ...]
    responsibilities: tuple[str, ...]
    interfaces: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    last_verified_commit: str
    content_identity: str
    verification_status: str = "verified"

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "kind": self.kind,
            "label": self.label,
            "owned_paths": list(self.owned_paths),
            "responsibilities": list(self.responsibilities),
            "interfaces": list(self.interfaces),
            "invariants": [],
            "evidence_refs": list(self.evidence_refs),
            "last_verified_commit": self.last_verified_commit,
            "content_identity": self.content_identity,
            "verification_status": self.verification_status,
        }

    @classmethod
    def from_dict(cls, value: Any, label: str) -> "ArchitectureNode":
        if not isinstance(value, Mapping):
            raise ArchitectureError(f"{label} must be an object")
        return cls(
            node_id=_text(value.get("node_id"), f"{label}.node_id"),
            kind=_text(value.get("kind"), f"{label}.kind"),
            label=_text(value.get("label"), f"{label}.label"),
            owned_paths=_string_tuple(value.get("owned_paths"), f"{label}.owned_paths"),
            responsibilities=_string_tuple(
                value.get("responsibilities", []), f"{label}.responsibilities"
            ),
            interfaces=_string_tuple(value.get("interfaces", []), f"{label}.interfaces"),
            evidence_refs=_string_tuple(
                value.get("evidence_refs", []), f"{label}.evidence_refs"
            ),
            last_verified_commit=_text(
                value.get("last_verified_commit"), f"{label}.last_verified_commit"
            ),
            content_identity=_text(
                value.get("content_identity"), f"{label}.content_identity"
            ),
            verification_status=_text(
                value.get("verification_status"), f"{label}.verification_status"
            ),
        )


@dataclass(frozen=True)
class ArchitectureEdge:
    edge_id: str
    source_node_id: str
    target_node_id: str
    relation: str
    evidence_refs: tuple[str, ...]
    last_verified_commit: str
    verification_status: str = "verified"

    def to_dict(self) -> dict[str, Any]:
        return {
            "edge_id": self.edge_id,
            "source_node_id": self.source_node_id,
            "target_node_id": self.target_node_id,
            "relation": self.relation,
            "evidence_refs": list(self.evidence_refs),
            "last_verified_commit": self.last_verified_commit,
            "verification_status": self.verification_status,
        }

    @classmethod
    def from_dict(cls, value: Any, label: str) -> "ArchitectureEdge":
        if not isinstance(value, Mapping):
            raise ArchitectureError(f"{label} must be an object")
        return cls(
            edge_id=_text(value.get("edge_id"), f"{label}.edge_id"),
            source_node_id=_text(
                value.get("source_node_id"), f"{label}.source_node_id"
            ),
            target_node_id=_text(
                value.get("target_node_id"), f"{label}.target_node_id"
            ),
            relation=_text(value.get("relation"), f"{label}.relation"),
            evidence_refs=_string_tuple(
                value.get("evidence_refs", []), f"{label}.evidence_refs"
            ),
            last_verified_commit=_text(
                value.get("last_verified_commit"), f"{label}.last_verified_commit"
            ),
            verification_status=_text(
                value.get("verification_status"), f"{label}.verification_status"
            ),
        )


@dataclass(frozen=True)
class ArchitectureBaseline:
    baseline_id: str
    repository_id: str
    commit_identity: str
    nodes: tuple[ArchitectureNode, ...]
    edges: tuple[ArchitectureEdge, ...]
    tracked_path_hashes: Mapping[str, str]
    status: str
    source_refs: tuple[str, ...]
    approved_by: str | None = None
    approved_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": BASELINE_SCHEMA,
            "baseline_id": self.baseline_id,
            "repository_id": self.repository_id,
            "commit_identity": self.commit_identity,
            "scope": "bounded-module-neighborhood",
            "nodes": [item.to_dict() for item in self.nodes],
            "edges": [item.to_dict() for item in self.edges],
            "tracked_path_hashes": dict(sorted(self.tracked_path_hashes.items())),
            "status": self.status,
            "source_refs": list(self.source_refs),
            "approved_by": self.approved_by,
            "approved_at": self.approved_at,
        }

    @classmethod
    def from_dict(cls, value: Any) -> "ArchitectureBaseline":
        if not isinstance(value, Mapping):
            raise ArchitectureError("baseline_invalid: baseline must be an object")
        if value.get("schema_version") != BASELINE_SCHEMA:
            raise ArchitectureError(f"baseline_invalid: schema must be {BASELINE_SCHEMA}")
        nodes_raw = value.get("nodes")
        edges_raw = value.get("edges")
        hashes_raw = value.get("tracked_path_hashes")
        if not isinstance(nodes_raw, list) or not isinstance(edges_raw, list):
            raise ArchitectureError("baseline_invalid: nodes and edges must be arrays")
        if not isinstance(hashes_raw, Mapping):
            raise ArchitectureError("baseline_invalid: tracked_path_hashes must be an object")
        nodes = tuple(
            ArchitectureNode.from_dict(item, f"nodes[{index}]")
            for index, item in enumerate(nodes_raw)
        )
        edges = tuple(
            ArchitectureEdge.from_dict(item, f"edges[{index}]")
            for index, item in enumerate(edges_raw)
        )
        node_ids = {item.node_id for item in nodes}
        if len(node_ids) != len(nodes):
            raise ArchitectureError("baseline_invalid: duplicate node IDs")
        if any(
            item.source_node_id not in node_ids or item.target_node_id not in node_ids
            for item in edges
        ):
            raise ArchitectureError("baseline_invalid: edge references an unknown node")
        result = cls(
            baseline_id=_text(value.get("baseline_id"), "baseline_id"),
            repository_id=_text(value.get("repository_id"), "repository_id"),
            commit_identity=_text(value.get("commit_identity"), "commit_identity"),
            nodes=nodes,
            edges=edges,
            tracked_path_hashes={
                _text(key, "tracked_path_hashes key"): _text(
                    item, f"tracked_path_hashes.{key}"
                )
                for key, item in hashes_raw.items()
            },
            status=_text(value.get("status"), "status"),
            source_refs=_string_tuple(value.get("source_refs", []), "source_refs"),
            approved_by=(
                None if value.get("approved_by") is None else _text(value["approved_by"], "approved_by")
            ),
            approved_at=(
                None if value.get("approved_at") is None else _text(value["approved_at"], "approved_at")
            ),
        )
        if result.status not in {"candidate", "approved"}:
            raise ArchitectureError("baseline_invalid: status must be candidate or approved")
        if result.status == "approved" and (
            not result.approved_by
            or not result.approved_at
            or not any(ref.startswith("decision:") for ref in result.source_refs)
        ):
            raise ArchitectureError(
                "baseline_invalid: approved baseline lacks attributable decision evidence"
            )
        if result.status == "candidate" and (
            result.approved_by is not None or result.approved_at is not None
        ):
            raise ArchitectureError(
                "baseline_invalid: candidate baseline cannot carry approval fields"
            )
        identity_payload = {
            "repository_id": result.repository_id,
            "commit_identity": result.commit_identity,
            "nodes": [item.to_dict() for item in result.nodes],
            "edges": [item.to_dict() for item in result.edges],
            "tracked_path_hashes": dict(sorted(result.tracked_path_hashes.items())),
        }
        expected_id = "baseline." + sha256_bytes(
            canonical_json_bytes(identity_payload)
        )[:20]
        if result.baseline_id != expected_id:
            raise ArchitectureError(
                "baseline_invalid: baseline identity does not match its content"
            )
        return result


@dataclass(frozen=True)
class ImportRef:
    module: str
    level: int
    imported_names: tuple[str, ...]
    line: int
    relative_specifier: str | None = None


@dataclass(frozen=True)
class ParsedModule:
    node: ArchitectureNode
    imports: tuple[ImportRef, ...]


@dataclass(frozen=True)
class Snapshot:
    nodes: Mapping[str, ArchitectureNode]
    edges: Mapping[str, ArchitectureEdge]
    parsed_files: int
    supported_files: int
    unknowns: tuple[str, ...]
    oversize_files: int = 0
    cache_hits: int = 0
    cache_misses: int = 0


def _aliases_for_path(path: str) -> tuple[str, ...]:
    pure = PurePosixPath(path)
    parts = list(pure.parts)
    suffix = pure.suffix
    if suffix:
        parts[-1] = parts[-1][: -len(suffix)]
    if parts and parts[-1] == "__init__":
        parts.pop()
    aliases: set[str] = set()
    if parts:
        aliases.add(".".join(parts))
    if len(parts) > 1 and parts[0] in {"src", "lib", "app"}:
        aliases.add(".".join(parts[1:]))
    return tuple(sorted(value for value in aliases if value))


def _alias_index(tree: Mapping[str, GitTreeEntry]) -> dict[str, str]:
    index: dict[str, str] = {}
    for path in sorted(tree):
        if not is_supported_source_path(path):
            continue
        for alias in _aliases_for_path(path):
            index.setdefault(alias, path)
    return index


def _parse_python(path: str, text: str, entry: GitTreeEntry, commit: str) -> ParsedModule:
    tree = ast.parse(text, filename=path)
    module_doc = ast.get_docstring(tree, clean=True)
    responsibilities = ()
    if module_doc:
        responsibilities = (module_doc.splitlines()[0][:240],)
    interfaces: list[str] = []
    imports: list[ImportRef] = []
    for item in tree.body:
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and not item.name.startswith("_"):
            interfaces.append(f"function:{item.name}")
        elif isinstance(item, ast.ClassDef) and not item.name.startswith("_"):
            interfaces.append(f"class:{item.name}")
            for child in item.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and not child.name.startswith("_"):
                    interfaces.append(f"method:{item.name}.{child.name}")
        elif isinstance(item, ast.Import):
            for alias in item.names:
                imports.append(
                    ImportRef(
                        module=alias.name,
                        level=0,
                        imported_names=(),
                        line=item.lineno,
                    )
                )
        elif isinstance(item, ast.ImportFrom):
            imports.append(
                ImportRef(
                    module=item.module or "",
                    level=item.level,
                    imported_names=tuple(alias.name for alias in item.names if alias.name != "*"),
                    line=item.lineno,
                )
            )
    aliases = _aliases_for_path(path)
    label = min(aliases, key=lambda item: (item.count("."), len(item))) if aliases else path
    node = ArchitectureNode(
        node_id=_node_id(path),
        kind="module",
        label=label,
        owned_paths=(path,),
        responsibilities=responsibilities,
        interfaces=tuple(interfaces[:40]),
        evidence_refs=(f"git:{commit}:{path}",),
        last_verified_commit=commit,
        content_identity=entry.object_id,
    )
    return ParsedModule(node=node, imports=tuple(imports))


JS_IMPORT_PATTERN = re.compile(
    r"(?:\b(?:import|export)\b[^\n;]*?\bfrom\s*|\brequire\s*\()"
    r"[\"'](?P<module>[^\"']+)[\"']"
)
JS_EXPORT_PATTERN = re.compile(
    r"^\s*export\s+(?:default\s+)?(?:async\s+)?(?:class|function|const|let|var|interface|type)\s+([A-Za-z_$][\w$]*)",
    re.MULTILINE,
)


def _parse_javascript(path: str, text: str, entry: GitTreeEntry, commit: str) -> ParsedModule:
    imports = tuple(
        ImportRef(
            module="",
            level=0,
            imported_names=(),
            line=text.count("\n", 0, match.start()) + 1,
            relative_specifier=match.group("module"),
        )
        for match in JS_IMPORT_PATTERN.finditer(text)
    )
    interfaces = tuple(f"export:{value}" for value in JS_EXPORT_PATTERN.findall(text)[:40])
    aliases = _aliases_for_path(path)
    label = min(aliases, key=lambda item: (item.count("."), len(item))) if aliases else path
    return ParsedModule(
        node=ArchitectureNode(
            node_id=_node_id(path),
            kind="module",
            label=label,
            owned_paths=(path,),
            responsibilities=(),
            interfaces=interfaces,
            evidence_refs=(f"git:{commit}:{path}",),
            last_verified_commit=commit,
            content_identity=entry.object_id,
        ),
        imports=imports,
    )


def _parse_module(
    repo: Path,
    commit: str,
    path: str,
    entry: GitTreeEntry,
    timeout: int,
    raw: bytes | None = None,
) -> ParsedModule:
    if entry.size > MAX_ARCHITECTURE_BLOB_BYTES:
        raise ArchitectureError(
            f"architecture source exceeds {MAX_ARCHITECTURE_BLOB_BYTES} bytes: {path}"
        )
    content = raw if raw is not None else read_git_blob(repo, commit, path, timeout)
    text = content.decode("utf-8", errors="replace")
    if PurePosixPath(path).suffix == ".py":
        return _parse_python(path, text, entry, commit)
    return _parse_javascript(path, text, entry, commit)


def _cache_payload(item: ParsedModule) -> dict[str, Any]:
    return {
        "responsibilities": list(item.node.responsibilities),
        "interfaces": list(item.node.interfaces),
        "imports": [
            {
                "module": ref.module,
                "level": ref.level,
                "imported_names": list(ref.imported_names),
                "line": ref.line,
                "relative_specifier": ref.relative_specifier,
            }
            for ref in item.imports
        ],
    }


def _parsed_from_cache(
    path: str,
    entry: GitTreeEntry,
    commit: str,
    value: Mapping[str, Any],
) -> ParsedModule:
    aliases = _aliases_for_path(path)
    label = min(aliases, key=lambda item: (item.count("."), len(item))) if aliases else path
    responsibilities = tuple(str(item) for item in value.get("responsibilities", []))
    interfaces = tuple(str(item) for item in value.get("interfaces", []))
    imports = tuple(
        ImportRef(
            module=str(item.get("module", "")),
            level=int(item.get("level", 0)),
            imported_names=tuple(str(name) for name in item.get("imported_names", [])),
            line=int(item.get("line", 0)),
            relative_specifier=(
                str(item["relative_specifier"])
                if item.get("relative_specifier") is not None
                else None
            ),
        )
        for item in value.get("imports", [])
        if isinstance(item, Mapping)
    )
    return ParsedModule(
        node=ArchitectureNode(
            node_id=_node_id(path),
            kind="module",
            label=label,
            owned_paths=(path,),
            responsibilities=responsibilities,
            interfaces=interfaces,
            evidence_refs=(f"git:{commit}:{path}",),
            last_verified_commit=commit,
            content_identity=entry.object_id,
        ),
        imports=imports,
    )


def _resolve_python_import(
    current_path: str,
    ref: ImportRef,
    aliases: Mapping[str, str],
) -> str | None:
    candidates: list[str] = []
    if ref.level:
        current_aliases = _aliases_for_path(current_path)
        if not current_aliases:
            return None
        current = min(current_aliases, key=lambda item: (item.startswith("src."), len(item)))
        package = current.split(".")[:-1]
        keep = max(0, len(package) - (ref.level - 1))
        prefix = package[:keep]
        if ref.module:
            prefix.extend(ref.module.split("."))
        base = ".".join(prefix)
    else:
        base = ref.module
    if base:
        candidates.append(base)
        candidates.extend(f"{base}.{name}" for name in ref.imported_names)
    else:
        candidates.extend(ref.imported_names)
    for candidate in candidates:
        if candidate in aliases:
            return aliases[candidate]
    return None


def _resolve_javascript_import(
    current_path: str,
    specifier: str,
    tree: Mapping[str, GitTreeEntry],
) -> str | None:
    if not specifier.startswith("."):
        return None
    base = PurePosixPath(current_path).parent.joinpath(specifier)
    normalized = posixpath.normpath(str(base))
    candidates = [normalized]
    candidates.extend(normalized + suffix for suffix in sorted(SUPPORTED_SUFFIXES))
    candidates.extend(
        f"{normalized}/index{suffix}" for suffix in sorted(SUPPORTED_SUFFIXES)
    )
    for candidate in candidates:
        if candidate in tree:
            return candidate
    return None


def _resolve_import(
    current_path: str,
    ref: ImportRef,
    aliases: Mapping[str, str],
    tree: Mapping[str, GitTreeEntry],
) -> str | None:
    if ref.relative_specifier is not None:
        return _resolve_javascript_import(current_path, ref.relative_specifier, tree)
    return _resolve_python_import(current_path, ref, aliases)


def _edge_for_import(
    source: ArchitectureNode,
    target: ArchitectureNode,
    ref: ImportRef,
    commit: str,
) -> ArchitectureEdge:
    source_path = source.owned_paths[0]
    return ArchitectureEdge(
        edge_id=_edge_id(source.node_id, "imports", target.node_id),
        source_node_id=source.node_id,
        target_node_id=target.node_id,
        relation="imports",
        evidence_refs=(f"git:{commit}:{source_path}:L{ref.line}",),
        last_verified_commit=commit,
    )


def _parse_full_snapshot(
    repo: Path,
    commit: str,
    timeout: int,
    analysis_cache: AnalysisCache | None = None,
    progress: Callable[[int, int, str], None] | None = None,
) -> Snapshot:
    tree = list_git_tree(repo, commit, timeout)
    supported = {
        path: entry
        for path, entry in tree.items()
        if is_supported_source_path(path)
    }
    parsed: dict[str, ParsedModule] = {}
    excluded_count = sum(
        PurePosixPath(path).suffix.casefold() in SUPPORTED_SUFFIXES
        and is_vendored_or_generated_path(path)
        for path in tree
    )
    unknowns: list[str] = (
        [f"excluded vendored/generated source files: {excluded_count}"]
        if excluded_count
        else []
    )
    readable_paths = [
        path
        for path, entry in sorted(supported.items())
        if entry.size <= MAX_ARCHITECTURE_BLOB_BYTES
    ]
    cached = analysis_cache.get_many(
        (path, supported[path].object_id) for path in readable_paths
    ) if analysis_cache is not None else {}
    missed_paths = [
        path for path in readable_paths
        if cache_key(path, supported[path].object_id) not in cached
    ]
    if progress is not None:
        progress(
            0,
            len(readable_paths),
            f"快照 {commit[:8]}：缓存命中 {len(readable_paths) - len(missed_paths)} 个模块",
        )
    blobs = read_git_blobs(repo, commit, missed_paths, timeout)
    cache_writes: list[tuple[str, str, Mapping[str, Any]]] = []
    supported_items = sorted(supported.items())
    for index, (path, entry) in enumerate(supported_items, start=1):
        try:
            cached_value = cached.get(cache_key(path, entry.object_id))
            if cached_value is not None:
                parsed[path] = _parsed_from_cache(path, entry, commit, cached_value)
            else:
                parsed[path] = _parse_module(
                    repo, commit, path, entry, timeout, raw=blobs.get(path)
                )
                cache_writes.append((path, entry.object_id, _cache_payload(parsed[path])))
        except (ArchitectureError, SyntaxError) as exc:
            unknowns.append(f"{path}: {type(exc).__name__}: {exc}")
        if progress is not None and (index % 250 == 0 or index == len(supported_items)):
            progress(
                min(index, len(readable_paths)),
                len(readable_paths),
                f"快照 {commit[:8]}：建立静态模块索引",
            )
    if analysis_cache is not None:
        analysis_cache.put_many(cache_writes)
    aliases = _alias_index(tree)
    all_nodes = {item.node.node_id: item.node for item in parsed.values()}
    path_nodes = {path: item.node for path, item in parsed.items()}
    all_edges: dict[str, ArchitectureEdge] = {}
    for source_path, item in parsed.items():
        for ref in item.imports:
            target_path = _resolve_import(source_path, ref, aliases, tree)
            target = path_nodes.get(target_path or "")
            if target is None:
                continue
            edge = _edge_for_import(item.node, target, ref, commit)
            all_edges[edge.edge_id] = edge

    return Snapshot(
        nodes=dict(sorted(all_nodes.items())),
        edges=dict(sorted(all_edges.items())),
        parsed_files=len(parsed),
        supported_files=len(supported),
        unknowns=tuple(unknowns),
        oversize_files=sum(
            entry.size > MAX_ARCHITECTURE_BLOB_BYTES
            for entry in supported.values()
        ),
        cache_hits=len(readable_paths) - len(missed_paths),
        cache_misses=len(missed_paths),
    )


def _bounded_snapshot(
    full: Snapshot,
    changed_paths: set[str],
) -> Snapshot:
    path_nodes = {
        item.owned_paths[0]: item
        for item in full.nodes.values()
        if item.owned_paths
    }
    seeds = {
        path_nodes[path].node_id for path in changed_paths if path in path_nodes
    }
    selected = set(seeds)
    for edge in full.edges.values():
        if edge.source_node_id in seeds or edge.target_node_id in seeds:
            selected.update({edge.source_node_id, edge.target_node_id})
    nodes = {
        node_id: full.nodes[node_id]
        for node_id in sorted(selected)
    }
    edges = {
        edge_id: edge
        for edge_id, edge in sorted(full.edges.items())
        if edge.source_node_id in selected and edge.target_node_id in selected
    }
    return Snapshot(
        nodes=nodes,
        edges=edges,
        parsed_files=full.parsed_files,
        supported_files=full.supported_files,
        unknowns=tuple(
            [
                *full.unknowns,
                *(
                    f"unsupported changed file: {path}"
                    for path in sorted(changed_paths)
                    if not is_supported_source_path(path)
                ),
            ]
        ),
        oversize_files=full.oversize_files,
        cache_hits=full.cache_hits,
        cache_misses=full.cache_misses,
    )


def _incremental_head_snapshot(
    repo: Path,
    commit: str,
    changed_paths: set[str],
    baseline: ArchitectureBaseline,
    timeout: int,
    analysis_cache: AnalysisCache | None = None,
) -> Snapshot:
    tree = list_git_tree(repo, commit, timeout)
    aliases = _alias_index(tree)
    baseline_path_nodes = {
        item.owned_paths[0]: item for item in baseline.nodes if item.owned_paths
    }
    nodes: dict[str, ArchitectureNode] = {
        item.node_id: item
        for item in baseline.nodes
        if item.owned_paths[0] in tree and item.owned_paths[0] not in changed_paths
    }
    edges: dict[str, ArchitectureEdge] = {
        item.edge_id: item
        for item in baseline.edges
        if item.source_node_id in nodes and item.target_node_id in nodes
    }
    parsed_by_path: dict[str, ParsedModule] = {}
    unknowns: list[str] = []
    cache_hits = 0
    cache_misses = 0

    def parse_path(path: str) -> ParsedModule | None:
        nonlocal cache_hits, cache_misses
        if path in parsed_by_path:
            return parsed_by_path[path]
        entry = tree.get(path)
        if entry is None or not is_supported_source_path(path):
            return None
        try:
            cached = analysis_cache.get_many([(path, entry.object_id)]) if analysis_cache is not None else {}
            cached_value = cached.get(cache_key(path, entry.object_id))
            if cached_value is not None:
                cache_hits += 1
                parsed_by_path[path] = _parsed_from_cache(path, entry, commit, cached_value)
            else:
                cache_misses += 1
                parsed_by_path[path] = _parse_module(repo, commit, path, entry, timeout)
                if analysis_cache is not None:
                    analysis_cache.put_many([(path, entry.object_id, _cache_payload(parsed_by_path[path]))])
        except (ArchitectureError, SyntaxError) as exc:
            unknowns.append(f"{path}: {type(exc).__name__}: {exc}")
            return None
        return parsed_by_path[path]

    changed_modules = [
        item
        for path in sorted(changed_paths)
        if (item := parse_path(path)) is not None
    ]
    for item in changed_modules:
        nodes[item.node.node_id] = item.node
    for item in changed_modules:
        source_path = item.node.owned_paths[0]
        for ref in item.imports:
            target_path = _resolve_import(source_path, ref, aliases, tree)
            if target_path is None:
                continue
            target = nodes.get(_node_id(target_path))
            if target is None:
                parsed_target = parse_path(target_path)
                if parsed_target is None:
                    continue
                target = parsed_target.node
                nodes[target.node_id] = target
            edge = _edge_for_import(item.node, target, ref, commit)
            edges[edge.edge_id] = edge
    baseline_paths = set(baseline_path_nodes)
    for path in sorted(changed_paths):
        if path in tree and not is_supported_source_path(path):
            unknowns.append(
                f"excluded changed vendored/generated source file: {path}"
                if is_vendored_or_generated_path(path)
                else f"unsupported changed file: {path}"
            )
        if path not in baseline_paths and path in tree:
            unknowns.append(f"baseline expanded for newly tracked path: {path}")
    return Snapshot(
        nodes=nodes,
        edges=edges,
        parsed_files=len(parsed_by_path),
        supported_files=sum(
            is_supported_source_path(path) for path in tree
        ),
        unknowns=tuple(unknowns),
        cache_hits=cache_hits,
        cache_misses=cache_misses,
    )


def _load_approved_baseline(
    manifest: SampleManifest,
    git: GitEvidence,
    repository_path: Path | None = None,
) -> ArchitectureBaseline | None:
    path = manifest.architecture_baseline_path
    if path is None:
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ArchitectureError("baseline_invalid: baseline is not valid UTF-8 JSON") from exc
    baseline = ArchitectureBaseline.from_dict(raw)
    if baseline.status != "approved" or not baseline.approved_by or not baseline.approved_at:
        raise ArchitectureError("baseline_invalid: only an attributable approved baseline may be reused")
    if baseline.repository_id != _repository_id(manifest.repository.path):
        raise ArchitectureError("baseline_invalid: repository identity does not match")
    if baseline.commit_identity != git.base_commit:
        raise ArchitectureError("baseline_stale: baseline commit does not match base commit")
    tree = list_git_tree(
        repository_path or manifest.repository.path,
        git.base_commit,
        manifest.limits.git_timeout_seconds,
    )
    for tracked_path, object_id in baseline.tracked_path_hashes.items():
        entry = tree.get(tracked_path)
        if entry is None or entry.object_id != object_id:
            raise ArchitectureError(
                f"baseline_stale: tracked path identity changed: {tracked_path}"
            )
    return baseline


def _baseline_from_snapshot(
    repository_id: str,
    commit: str,
    snapshot: Snapshot,
    *,
    status: str,
    source_refs: Iterable[str],
) -> ArchitectureBaseline:
    tracked = {
        node.owned_paths[0]: node.content_identity
        for node in snapshot.nodes.values()
        if node.owned_paths
    }
    ordered_nodes = tuple(sorted(snapshot.nodes.values(), key=lambda item: item.node_id))
    ordered_edges = tuple(sorted(snapshot.edges.values(), key=lambda item: item.edge_id))
    payload = {
        "repository_id": repository_id,
        "commit_identity": commit,
        "nodes": [item.to_dict() for item in ordered_nodes],
        "edges": [item.to_dict() for item in ordered_edges],
        "tracked_path_hashes": dict(sorted(tracked.items())),
    }
    baseline_id = "baseline." + sha256_bytes(canonical_json_bytes(payload))[:20]
    return ArchitectureBaseline(
        baseline_id=baseline_id,
        repository_id=repository_id,
        commit_identity=commit,
        nodes=ordered_nodes,
        edges=ordered_edges,
        tracked_path_hashes=tracked,
        status=status,
        source_refs=tuple(source_refs),
    )


def _node_changed(before: ArchitectureNode, after: ArchitectureNode) -> bool:
    return (
        before.content_identity != after.content_identity
        or before.interfaces != after.interfaces
        or before.responsibilities != after.responsibilities
    )


def _edge_evidence_location_signature(edge: ArchitectureEdge) -> tuple[str, ...]:
    """Compare retained-edge evidence locations without treating revalidation as change."""

    return tuple(
        re.sub(
            r"^git:[0-9a-fA-F]{40}:",
            "git:<commit>:",
            evidence_ref,
        )
        for evidence_ref in edge.evidence_refs
    )


def _build_delta(
    git: GitEvidence,
    baseline_status: str,
    source_baseline_id: str | None,
    before: Snapshot,
    after: Snapshot,
    *,
    reused_nodes: int,
) -> dict[str, Any]:
    before_nodes = dict(before.nodes)
    after_nodes = dict(after.nodes)
    before_edges = dict(before.edges)
    after_edges = dict(after.edges)
    before_ids = set(before_nodes)
    after_ids = set(after_nodes)
    added = after_ids - before_ids
    removed = before_ids - after_ids
    modified = {
        node_id
        for node_id in before_ids & after_ids
        if _node_changed(before_nodes[node_id], after_nodes[node_id])
    }
    changed = added | removed | modified
    added_edges = set(after_edges) - set(before_edges)
    removed_edges = set(before_edges) - set(after_edges)
    modified_edges = {
        edge_id
        for edge_id in set(before_edges) & set(after_edges)
        if _edge_evidence_location_signature(before_edges[edge_id])
        != _edge_evidence_location_signature(after_edges[edge_id])
    }

    impacted: set[str] = set()
    impact_index: dict[tuple[str, str, str], set[str]] = {}
    for edge in list(before_edges.values()) + list(after_edges.values()):
        if edge.target_node_id in changed and edge.source_node_id not in changed:
            impacted.add(edge.source_node_id)
            key = (edge.target_node_id, edge.source_node_id, "imported_by")
            impact_index.setdefault(key, set()).update(edge.evidence_refs)
    impact_paths = [
        {
            "changed_node_id": changed_node_id,
            "impacted_node_id": impacted_node_id,
            "relation": relation,
            "depth": 1,
            "evidence_refs": sorted(evidence_refs),
        }
        for (changed_node_id, impacted_node_id, relation), evidence_refs in impact_index.items()
    ]

    relevant = set(changed) | impacted
    for edge in list(before_edges.values()) + list(after_edges.values()):
        if edge.source_node_id in changed or edge.target_node_id in changed:
            relevant.update({edge.source_node_id, edge.target_node_id})

    context = relevant - changed - impacted

    def display_key(node_id: str) -> tuple[int, str]:
        node = after_nodes.get(node_id) or before_nodes[node_id]
        path = node.owned_paths[0] if node.owned_paths else ""
        non_production = path.startswith(("tests/", "test/", "scripts/"))
        return (1 if non_production else 0, path)

    changed_order = sorted(changed, key=display_key)
    impacted_order = sorted(impacted - changed, key=display_key)
    context_order = sorted(context, key=display_key)
    display_budget = max(MAX_DISPLAY_NODES, len(changed_order))
    ordered_relevant = [
        *changed_order,
        *impacted_order,
        *context_order,
    ]
    displayed = set(ordered_relevant[:display_budget])
    omitted = set(ordered_relevant[display_budget:])

    def node_row(node: ArchitectureNode, status: str) -> dict[str, Any]:
        row = node.to_dict()
        row["change_status"] = status
        before_node = before_nodes.get(node.node_id)
        after_node = after_nodes.get(node.node_id)
        if status == "added":
            detail = "new module"
            if node.interfaces:
                detail += "; +" + ", +".join(node.interfaces[:3])
        elif status == "removed":
            detail = "removed module"
            if node.interfaces:
                detail += "; -" + ", -".join(node.interfaces[:3])
        elif status == "modified" and before_node and after_node:
            added_interfaces = sorted(set(after_node.interfaces) - set(before_node.interfaces))
            removed_interfaces = sorted(set(before_node.interfaces) - set(after_node.interfaces))
            details = [*(f"+{item}" for item in added_interfaces[:3]), *(f"-{item}" for item in removed_interfaces[:3])]
            if before_node.responsibilities != after_node.responsibilities:
                details.append("responsibility text changed")
            detail = "; ".join(details) if details else "module content changed"
        elif status == "impacted":
            detail = "direct consumer of a changed module"
        else:
            detail = "dependency context"
        row["change_detail"] = detail
        return row

    before_rows = []
    for node_id in sorted(displayed & before_ids):
        status = "removed" if node_id in removed else "modified" if node_id in modified else "impacted" if node_id in impacted else "unchanged_context"
        before_rows.append(node_row(before_nodes[node_id], status))
    after_rows = []
    for node_id in sorted(displayed & after_ids):
        status = "added" if node_id in added else "modified" if node_id in modified else "impacted" if node_id in impacted else "unchanged_context"
        after_rows.append(node_row(after_nodes[node_id], status))

    before_edge_rows = [
        edge.to_dict()
        for edge in sorted(before_edges.values(), key=lambda item: item.edge_id)
        if edge.source_node_id in displayed and edge.target_node_id in displayed
    ]
    after_edge_rows = [
        edge.to_dict()
        for edge in sorted(after_edges.values(), key=lambda item: item.edge_id)
        if edge.source_node_id in displayed and edge.target_node_id in displayed
    ]
    unknowns = sorted(set(before.unknowns + after.unknowns))
    if omitted:
        unknowns.append(
            f"display budget folded {len(omitted)} one-hop/context nodes; full IDs remain in display_omissions"
        )
    return {
        "schema_version": DELTA_SCHEMA,
        "baseline_validation": {
            "status": baseline_status,
            "source_baseline_id": source_baseline_id,
            "base_commit": git.base_commit,
        },
        "change_identity": {
            "base_ref": git.base_commit,
            "head_ref": git.head_commit,
            "patch_sha256": git.patch_sha256,
        },
        "before": {"nodes": before_rows, "edges": before_edge_rows},
        "after": {"nodes": after_rows, "edges": after_edge_rows},
        "added_node_ids": sorted(added),
        "removed_node_ids": sorted(removed),
        "modified_node_ids": sorted(modified),
        "impacted_node_ids": sorted(impacted),
        "added_edge_ids": sorted(added_edges),
        "removed_edge_ids": sorted(removed_edges),
        "modified_edge_ids": sorted(modified_edges),
        "impact_paths": sorted(
            impact_paths,
            key=lambda item: (item["changed_node_id"], item["impacted_node_id"]),
        ),
        "display_omissions": {
            "max_display_nodes": display_budget,
            "omitted_node_ids": sorted(omitted),
            "omitted_impacted_node_ids": sorted(omitted & impacted),
            "omitted_context_node_ids": sorted(omitted & context),
        },
        "unknowns": unknowns,
        "limitations": [
            "module-level Python/JavaScript static imports only",
            "impact paths are limited to one verified incoming import edge",
            "dynamic imports, reflection, runtime routing, and configuration injection remain unknown",
        ],
        "analysis_stats": {
            "supported_files_total": max(before.supported_files, after.supported_files),
            "parsed_base_files": before.parsed_files,
            "parsed_head_files": after.parsed_files,
            "reused_nodes": reused_nodes,
            "invalidated_nodes": len(modified | removed),
            "displayed_nodes": len(displayed),
            "omitted_nodes": len(omitted),
        },
    }


def _section_edge_id(source_group_id: str, target_group_id: str) -> str:
    return "section-edge." + sha256_bytes(
        f"{source_group_id}:imports:{target_group_id}".encode("utf-8")
    )[:20]


def build_system_architecture_snapshot(
    repository_id: str,
    commit: str,
    snapshot: Snapshot,
    delta: Mapping[str, Any],
    target_profile: TargetProfile,
) -> dict[str, Any]:
    """Build a complete supported static Head snapshot plus a human overview."""

    node_rows: list[dict[str, Any]] = []
    node_groups: dict[str, str] = {}
    group_node_ids: dict[str, list[str]] = {}
    for node in sorted(snapshot.nodes.values(), key=lambda item: item.node_id):
        path = node.owned_paths[0] if node.owned_paths else ""
        group_id = target_profile.section_id_for_path(path)
        node_groups[node.node_id] = group_id
        group_node_ids.setdefault(group_id, []).append(node.node_id)
        row = node.to_dict()
        row["group_id"] = group_id
        node_rows.append(row)

    edge_rows = [
        item.to_dict()
        for item in sorted(snapshot.edges.values(), key=lambda item: item.edge_id)
    ]
    internal_edge_ids: dict[str, list[str]] = {}
    bundle_edge_ids: dict[tuple[str, str], list[str]] = {}
    for edge in sorted(snapshot.edges.values(), key=lambda item: item.edge_id):
        source_group = node_groups[edge.source_node_id]
        target_group = node_groups[edge.target_node_id]
        if source_group == target_group:
            internal_edge_ids.setdefault(source_group, []).append(edge.edge_id)
        else:
            bundle_edge_ids.setdefault((source_group, target_group), []).append(
                edge.edge_id
            )

    group_edges = []
    for (source_group, target_group), source_edge_ids in sorted(
        bundle_edge_ids.items()
    ):
        group_edges.append(
            {
                "group_edge_id": _section_edge_id(source_group, target_group),
                "source_group_id": source_group,
                "target_group_id": target_group,
                "relation": "imports",
                "relation_label": "静态依赖",
                "source_edge_ids": sorted(source_edge_ids),
                "edge_count": len(source_edge_ids),
            }
        )
    group_edge_ids = {
        (item["source_group_id"], item["target_group_id"]): item["group_edge_id"]
        for item in group_edges
    }

    status_node_ids = {
        "added": sorted(str(item) for item in delta.get("added_node_ids", [])),
        "modified": sorted(str(item) for item in delta.get("modified_node_ids", [])),
        "removed": sorted(str(item) for item in delta.get("removed_node_ids", [])),
        "impacted": sorted(str(item) for item in delta.get("impacted_node_ids", [])),
    }
    delta_nodes = {
        str(item.get("node_id")): item
        for side in ("before", "after")
        for item in delta.get(side, {}).get("nodes", [])
        if isinstance(item, Mapping) and isinstance(item.get("node_id"), str)
    }
    group_status_ids: dict[str, dict[str, list[str]]] = {}
    for status, node_ids in status_node_ids.items():
        for node_id in node_ids:
            group_id = node_groups.get(node_id)
            if group_id is None:
                row = delta_nodes.get(node_id, {})
                owned_paths = row.get("owned_paths", [])
                if isinstance(owned_paths, list) and owned_paths:
                    group_id = target_profile.section_id_for_path(str(owned_paths[0]))
            if group_id is None:
                group_id = "unclassified"
            group_status_ids.setdefault(group_id, {}).setdefault(status, []).append(
                node_id
            )

    groups = []
    for definition in target_profile.sections:
        group_id = definition.section_id
        node_ids = sorted(group_node_ids.get(group_id, []))
        changes = group_status_ids.get(group_id, {})
        if not node_ids and not any(changes.values()):
            continue
        incoming = sorted(
            group_edge_id
            for (source, target), group_edge_id in group_edge_ids.items()
            if target == group_id
        )
        outgoing = sorted(
            group_edge_id
            for (source, target), group_edge_id in group_edge_ids.items()
            if source == group_id
        )
        groups.append(
            {
                "group_id": group_id,
                "label": definition.label,
                "responsibility": definition.responsibility,
                "lane": definition.lane,
                "group_source": target_profile.group_source(group_id),
                "node_ids": node_ids,
                "module_count": len(node_ids),
                "internal_edge_ids": sorted(internal_edge_ids.get(group_id, [])),
                "internal_edge_count": len(internal_edge_ids.get(group_id, [])),
                "incoming_group_edge_ids": incoming,
                "outgoing_group_edge_ids": outgoing,
                "incoming_relation_count": len(incoming),
                "outgoing_relation_count": len(outgoing),
                "change": {
                    status: sorted(changes.get(status, []))
                    for status in ("added", "modified", "removed", "impacted")
                },
                "changed_count": len(
                    set(
                        changes.get("added", [])
                        + changes.get("modified", [])
                        + changes.get("removed", [])
                    )
                ),
            }
        )

    unclassified_paths = sorted(
        row["owned_paths"][0]
        for row in node_rows
        if row["group_id"] == "unclassified" and row.get("owned_paths")
    )
    model: dict[str, Any] = {
        "schema_version": SYSTEM_ARCHITECTURE_SCHEMA,
        "repository_id": repository_id,
        "commit_identity": commit,
        "target_profile": target_profile.snapshot_metadata(),
        "scope": "all-successfully-parsed-supported-modules",
        "status": "candidate_static_snapshot",
        "status_label": "候选静态快照，尚未批准为长期基线",
        "nodes": node_rows,
        "edges": edge_rows,
        "groups": groups,
        "group_edges": group_edges,
        "change_overlay": {
            **status_node_ids,
            "group_ids": sorted(
                group_id
                for group_id, statuses in group_status_ids.items()
                if any(statuses.values())
            ),
        },
        "coverage": {
            "supported_files": snapshot.supported_files,
            "parsed_files": snapshot.parsed_files,
            "parse_failures": max(
                0,
                snapshot.supported_files
                - snapshot.parsed_files
                - snapshot.oversize_files,
            ),
            "oversize_skipped": snapshot.oversize_files,
            "node_count": len(node_rows),
            "edge_count": len(edge_rows),
            "group_count": len(groups),
            "group_edge_count": len(group_edges),
            "unclassified_node_count": len(unclassified_paths),
            "unclassified_paths": unclassified_paths,
            "all_nodes_assigned_once": sum(len(item["node_ids"]) for item in groups)
            == len(node_rows),
        },
        "limitations": sorted(
            {
                *delta.get("limitations", []),
                "this is a static supported-code snapshot, not a complete runtime architecture",
                "database access, network calls, deployment topology, and external-service state are not proven",
                *snapshot.unknowns,
            }
        ),
    }
    model["snapshot_identity"] = sha256_bytes(canonical_json_bytes(model))
    return validate_system_architecture_snapshot(model)


def validate_system_architecture_snapshot(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ArchitectureError("system architecture snapshot must be an object")
    model = dict(value)
    if model.get("schema_version") != SYSTEM_ARCHITECTURE_SCHEMA:
        raise ArchitectureError("system architecture snapshot schema is invalid")
    claimed_identity = model.pop("snapshot_identity", None)
    actual_identity = sha256_bytes(canonical_json_bytes(model))
    if claimed_identity != actual_identity:
        raise ArchitectureError("system architecture snapshot identity does not match")

    nodes = model.get("nodes")
    edges = model.get("edges")
    groups = model.get("groups")
    group_edges = model.get("group_edges")
    coverage = model.get("coverage")
    if not all(isinstance(item, list) for item in (nodes, edges, groups, group_edges)):
        raise ArchitectureError("system architecture collections must be arrays")
    if not isinstance(coverage, Mapping):
        raise ArchitectureError("system architecture coverage must be an object")
    try:
        presentation = PresentationProfile.from_dict(
            model.get("target_profile"), "system architecture target_profile"
        )
    except ManifestError as exc:
        raise ArchitectureError(str(exc)) from exc
    profile_source = (
        f"target-profile:{presentation.profile_id}:sha256:"
        f"{presentation.profile_sha256}"
    )

    node_index = {
        str(item.get("node_id")): item
        for item in nodes
        if isinstance(item, Mapping) and isinstance(item.get("node_id"), str)
    }
    if len(node_index) != len(nodes):
        raise ArchitectureError("system architecture contains duplicate or invalid nodes")
    group_index = {
        str(item.get("group_id")): item
        for item in groups
        if isinstance(item, Mapping) and isinstance(item.get("group_id"), str)
    }
    if len(group_index) != len(groups):
        raise ArchitectureError("system architecture contains duplicate or invalid groups")
    assigned: list[str] = []
    for group_id, group in group_index.items():
        expected_group_source = (
            profile_source
            if group_id != "unclassified"
            else profile_source + ":unclassified-fallback"
        )
        if group.get("group_source") != expected_group_source:
            raise ArchitectureError(
                "system architecture group source does not match target profile"
            )
        node_ids = group.get("node_ids")
        if not isinstance(node_ids, list):
            raise ArchitectureError("system architecture group node_ids must be an array")
        if group.get("module_count") != len(node_ids):
            raise ArchitectureError("system architecture group module count does not match")
        assigned.extend(str(item) for item in node_ids)
        if any(node_index.get(str(item), {}).get("group_id") != group_id for item in node_ids):
            raise ArchitectureError("system architecture group assignment does not match node")
    if len(assigned) != len(set(assigned)) or set(assigned) != set(node_index):
        raise ArchitectureError("system architecture must assign every node exactly once")

    edge_index = {
        str(item.get("edge_id")): item
        for item in edges
        if isinstance(item, Mapping) and isinstance(item.get("edge_id"), str)
    }
    if len(edge_index) != len(edges):
        raise ArchitectureError("system architecture contains duplicate or invalid edges")
    if any(
        edge.get("source_node_id") not in node_index
        or edge.get("target_node_id") not in node_index
        for edge in edge_index.values()
    ):
        raise ArchitectureError("system architecture edge references an unknown node")

    group_edge_index = {
        str(item.get("group_edge_id")): item
        for item in group_edges
        if isinstance(item, Mapping) and isinstance(item.get("group_edge_id"), str)
    }
    if len(group_edge_index) != len(group_edges):
        raise ArchitectureError(
            "system architecture contains duplicate or invalid group edges"
        )
    bundled: list[str] = []
    for group_edge in group_edge_index.values():
        source_group = group_edge.get("source_group_id")
        target_group = group_edge.get("target_group_id")
        if source_group not in group_index or target_group not in group_index:
            raise ArchitectureError("system architecture group edge references an unknown group")
        source_edge_ids = group_edge.get("source_edge_ids")
        if not isinstance(source_edge_ids, list):
            raise ArchitectureError("system architecture source_edge_ids must be an array")
        if group_edge.get("edge_count") != len(source_edge_ids):
            raise ArchitectureError(
                "system architecture group edge count does not match"
            )
        for edge_id in source_edge_ids:
            edge = edge_index.get(str(edge_id))
            if edge is None:
                raise ArchitectureError("system architecture group edge references an unknown edge")
            if (
                node_index[str(edge["source_node_id"])]["group_id"] != source_group
                or node_index[str(edge["target_node_id"])]["group_id"] != target_group
            ):
                raise ArchitectureError("system architecture group edge source mapping is invalid")
            bundled.append(str(edge_id))
    expected_cross_edges = {
        edge_id
        for edge_id, edge in edge_index.items()
        if node_index[str(edge["source_node_id"])]["group_id"]
        != node_index[str(edge["target_node_id"])]["group_id"]
    }
    if len(bundled) != len(set(bundled)) or set(bundled) != expected_cross_edges:
        raise ArchitectureError("system architecture group edges must cover each cross-group edge once")

    for group_id, group in group_index.items():
        internal_edge_ids = group.get("internal_edge_ids")
        incoming_ids = group.get("incoming_group_edge_ids")
        outgoing_ids = group.get("outgoing_group_edge_ids")
        if not all(
            isinstance(item, list)
            for item in (internal_edge_ids, incoming_ids, outgoing_ids)
        ):
            raise ArchitectureError("system architecture group relation IDs must be arrays")
        expected_internal = {
            edge_id
            for edge_id, edge in edge_index.items()
            if node_index[str(edge["source_node_id"])]["group_id"] == group_id
            and node_index[str(edge["target_node_id"])]["group_id"] == group_id
        }
        expected_incoming = {
            edge_id
            for edge_id, edge in group_edge_index.items()
            if edge["target_group_id"] == group_id
        }
        expected_outgoing = {
            edge_id
            for edge_id, edge in group_edge_index.items()
            if edge["source_group_id"] == group_id
        }
        if set(str(item) for item in internal_edge_ids) != expected_internal:
            raise ArchitectureError(
                "system architecture group internal edges do not match"
            )
        if set(str(item) for item in incoming_ids) != expected_incoming:
            raise ArchitectureError(
                "system architecture group incoming relations do not match"
            )
        if set(str(item) for item in outgoing_ids) != expected_outgoing:
            raise ArchitectureError(
                "system architecture group outgoing relations do not match"
            )
        if group.get("internal_edge_count") != len(expected_internal):
            raise ArchitectureError(
                "system architecture group internal edge count does not match"
            )
        if group.get("incoming_relation_count") != len(expected_incoming):
            raise ArchitectureError(
                "system architecture group incoming relation count does not match"
            )
        if group.get("outgoing_relation_count") != len(expected_outgoing):
            raise ArchitectureError(
                "system architecture group outgoing relation count does not match"
            )

    count_contract = {
        "parsed_files": len(nodes),
        "node_count": len(nodes),
        "edge_count": len(edges),
        "group_count": len(groups),
        "group_edge_count": len(group_edges),
    }
    if any(coverage.get(key) != expected for key, expected in count_contract.items()):
        raise ArchitectureError("system architecture parsed-file coverage does not match nodes")
    if coverage.get("all_nodes_assigned_once") is not True:
        raise ArchitectureError("system architecture coverage is not complete")
    model["snapshot_identity"] = claimed_identity
    return model


def build_architecture_bundle(
    manifest: SampleManifest,
    git: GitEvidence,
    *,
    analysis_repo_path: Path | None = None,
    analysis_cache: AnalysisCache | None = None,
    progress: Callable[[int, int, str], None] | None = None,
) -> dict[str, Any]:
    changed_paths = {item.path for item in git.files if not item.binary}
    repo = analysis_repo_path or manifest.repository.path
    baseline = _load_approved_baseline(manifest, git, repo)
    repository_id = _repository_id(manifest.repository.path)
    target_profile = load_target_profile(manifest.target_profile_path)
    full_head = _parse_full_snapshot(
        repo,
        git.head_commit,
        manifest.limits.git_timeout_seconds,
        analysis_cache,
        progress,
    )
    if baseline is None:
        baseline_status = "bootstrap_unapproved"
        full_before = _parse_full_snapshot(
            repo,
            git.base_commit,
            manifest.limits.git_timeout_seconds,
            analysis_cache,
            progress,
        )
        before = _bounded_snapshot(full_before, changed_paths)
        after = _bounded_snapshot(full_head, changed_paths)
        source_baseline_id = None
        reused_nodes = 0
        cache_stats = {
            "hits": full_head.cache_hits + full_before.cache_hits,
            "misses": full_head.cache_misses + full_before.cache_misses,
        }
    else:
        baseline_status = "approved"
        source_baseline_id = baseline.baseline_id
        before = Snapshot(
            nodes={item.node_id: item for item in baseline.nodes},
            edges={item.edge_id: item for item in baseline.edges},
            parsed_files=0,
            supported_files=len(baseline.nodes),
            unknowns=(),
        )
        baseline_paths = {
            path for item in baseline.nodes for path in item.owned_paths
        }
        existing_untracked = {
            path
            for path in changed_paths
            if path not in baseline_paths
            and is_supported_source_path(path)
            and not any(change.path == path and change.status == "A" for change in git.files)
        }
        if existing_untracked:
            after = _bounded_snapshot(full_head, changed_paths)
            baseline_status = "approved_with_bounded_expansion"
            reused_nodes = 0
        else:
            after = _incremental_head_snapshot(
                repo,
                git.head_commit,
                changed_paths,
                baseline,
                manifest.limits.git_timeout_seconds,
                analysis_cache,
            )
            reused_nodes = sum(
                item.node_id in after.nodes
                and item.content_identity == after.nodes[item.node_id].content_identity
                for item in baseline.nodes
            )
        cache_stats = {
            "hits": full_head.cache_hits + after.cache_hits,
            "misses": full_head.cache_misses + after.cache_misses,
        }

    delta = _build_delta(
        git,
        baseline_status,
        source_baseline_id,
        before,
        after,
        reused_nodes=reused_nodes,
    )
    system_architecture = build_system_architecture_snapshot(
        repository_id,
        git.head_commit,
        full_head,
        delta,
        target_profile,
    )
    candidate_baseline = _baseline_from_snapshot(
        repository_id,
        git.head_commit,
        after,
        status="candidate",
        source_refs=(
            f"git:commit:{git.head_commit}",
            f"git:patch:{git.patch_sha256}",
        ),
    )
    proposal_payload = {
        "source_baseline_id": source_baseline_id,
        "change_identity": delta["change_identity"],
        "candidate_baseline": candidate_baseline.to_dict(),
    }
    proposal_id = "proposal." + sha256_bytes(canonical_json_bytes(proposal_payload))[:20]
    proposal = {
        "schema_version": PROPOSAL_SCHEMA,
        "proposal_id": proposal_id,
        **proposal_payload,
        "evidence_refs": [
            f"git:commit:{git.head_commit}",
            f"git:patch:{git.patch_sha256}",
        ],
        "limitations": list(delta["limitations"]),
        "decision": "pending",
    }
    proposal["proposal_sha256"] = sha256_bytes(canonical_json_bytes(proposal))
    decision_template = {
        "schema_version": DECISION_SCHEMA,
        "proposal_id": proposal_id,
        "proposal_sha256": proposal["proposal_sha256"],
        "decision": None,
        "actor": None,
        "decided_at": None,
        "notes": "",
    }
    return {
        "delta": delta,
        "system_architecture": system_architecture,
        "proposal": proposal,
        "decision_template": decision_template,
        "cache_stats": cache_stats,
    }


def _mermaid_id(prefix: str, node_id: str) -> str:
    return prefix + "_" + re.sub(r"[^A-Za-z0-9_]", "_", node_id)


def _render_interface_name(value: str) -> str:
    kind, separator, name = value.partition(":")
    kind_label = {"function": "函数", "class": "类", "method": "方法"}.get(kind)
    if separator and kind_label:
        return f"{kind_label} {name}"
    return value


def _render_change_detail(item: Mapping[str, Any]) -> str:
    status = str(item["change_status"])
    raw_detail = str(item.get("change_detail", status))
    if status == "added":
        interface_text = raw_detail.partition("; ")[2]
        interfaces = [
            _render_interface_name(part.removeprefix("+"))
            for part in interface_text.split(", +")
            if part
        ]
        return "新增模块" + (f"；新增接口：{'、'.join(interfaces)}" if interfaces else "")
    if status == "removed":
        interface_text = raw_detail.partition("; ")[2]
        interfaces = [
            _render_interface_name(part.removeprefix("-"))
            for part in interface_text.split(", -")
            if part
        ]
        return "移除模块" + (f"；移除接口：{'、'.join(interfaces)}" if interfaces else "")
    if status == "modified":
        details: list[str] = []
        for part in raw_detail.split("; "):
            if part.startswith("+"):
                details.append(f"新增接口：{_render_interface_name(part[1:])}")
            elif part.startswith("-"):
                details.append(f"移除接口：{_render_interface_name(part[1:])}")
            elif part == "responsibility text changed":
                details.append("职责说明已变化")
            elif part == "module content changed":
                details.append("模块内容已修改")
            else:
                details.append(part)
        return "；".join(details)
    if status == "impacted":
        return "直接依赖已变更模块"
    if status == "unchanged_context":
        return "依赖关系上下文"
    return raw_detail


def render_mermaid(delta: Mapping[str, Any]) -> str:
    if delta.get("schema_version") != DELTA_SCHEMA:
        raise ArchitectureError("architecture delta schema is invalid")
    lines = [
        "flowchart LR",
        "  classDef added fill:#d1fae5,stroke:#059669,color:#064e3b;",
        "  classDef removed fill:#fee2e2,stroke:#dc2626,color:#7f1d1d;",
        "  classDef modified fill:#fef3c7,stroke:#d97706,color:#78350f;",
        "  classDef impacted fill:#dbeafe,stroke:#2563eb,color:#1e3a8a;",
        "  classDef context fill:#f3f4f6,stroke:#6b7280,color:#111827;",
    ]
    for side, prefix in (("before", "B"), ("after", "A")):
        title = "变更前" if side == "before" else "变更后"
        lines.extend([f"  subgraph {prefix}[{title}]", "    direction TB"])
        nodes = delta[side]["nodes"]
        node_ids = {item["node_id"] for item in nodes}
        for item in nodes:
            mermaid_id = _mermaid_id(prefix, item["node_id"])
            label = html.escape(item["label"], quote=True)
            status = item["change_status"]
            detail = html.escape(_render_change_detail(item), quote=True)
            compact_path = "/".join(item["owned_paths"][0].split("/")[-3:])
            path = html.escape(compact_path, quote=True)
            lines.append(f"    %% node:{item['node_id']}")
            lines.append(f'    {mermaid_id}["{label}<br/>{detail}<br/>{path}"]')
            css = "context" if status == "unchanged_context" else status
            lines.append(f"    class {mermaid_id} {css};")
        for edge in delta[side]["edges"]:
            if edge["source_node_id"] not in node_ids or edge["target_node_id"] not in node_ids:
                continue
            source = _mermaid_id(prefix, edge["source_node_id"])
            target = _mermaid_id(prefix, edge["target_node_id"])
            relation = {"imports": "静态导入"}.get(edge["relation"], edge["relation"])
            lines.append(f"    {source} -->|{relation}| {target}")
        omitted_count = len(delta.get("display_omissions", {}).get("omitted_node_ids", []))
        if omitted_count:
            folded_id = f"{prefix}_folded"
            lines.append(
                f'    {folded_id}["… 其余 {omitted_count} 个一跳依赖/上下文模块<br/>完整 ID 保留在 JSON"]'
            )
            lines.append(f"    class {folded_id} context;")
        lines.append("  end")
    return "\n".join(lines) + "\n"


def architecture_evidence_bindings(delta: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Return stable structured subjects for deterministic architecture evidence IDs."""
    if delta.get("schema_version") != DELTA_SCHEMA:
        raise ArchitectureError("architecture delta schema is invalid")
    changed_ids = (
        list(delta["added_node_ids"])
        + list(delta["removed_node_ids"])
        + list(delta["modified_node_ids"])
    )
    bindings = [
        {
            "evidence_id": f"arch.node.{index:03d}",
            "subject_type": "node",
            "node_ids": [node_id],
            "edge_ids": [],
            "impact_path_index": None,
        }
        for index, node_id in enumerate(dict.fromkeys(changed_ids), start=1)
    ]
    bindings.extend(
        {
            "evidence_id": f"arch.impact.{index:03d}",
            "subject_type": "impact_path",
            "node_ids": [item["changed_node_id"], item["impacted_node_id"]],
            "edge_ids": [],
            "impact_path_index": index - 1,
        }
        for index, item in enumerate(delta.get("impact_paths", []), start=1)
    )
    return bindings


def architecture_evidence_entries(delta: Mapping[str, Any]) -> list[dict[str, Any]]:
    node_index = {
        item["node_id"]: item
        for side in ("before", "after")
        for item in delta[side]["nodes"]
    }
    entries: list[dict[str, Any]] = []
    bindings = architecture_evidence_bindings(delta)
    for binding in bindings:
        if binding["subject_type"] != "node":
            continue
        node_id = binding["node_ids"][0]
        node = node_index[node_id]
        entries.append(
            {
                "id": binding["evidence_id"],
                "kind": "architecture",
                "authority": "architecture_fact",
                "content": (
                    f"status={node['change_status']}; node_id={node_id}; label={node['label']}; "
                    f"paths={','.join(node['owned_paths'])}; interfaces={','.join(node['interfaces']) or 'none'}"
                ),
                "source_ref": node["evidence_refs"][0],
                "limitations": [],
            }
        )
    impact_paths = delta.get("impact_paths", [])
    for binding in bindings:
        if binding["subject_type"] != "impact_path":
            continue
        item = impact_paths[binding["impact_path_index"]]
        entries.append(
            {
                "id": binding["evidence_id"],
                "kind": "architecture",
                "authority": "architecture_fact",
                "content": (
                    f"changed_node_id={item['changed_node_id']}; "
                    f"impacted_node_id={item['impacted_node_id']}; "
                    f"relation={item['relation']}; depth={item['depth']}"
                ),
                "source_ref": item["evidence_refs"][0],
                "limitations": ["bounded_one_hop_impact"],
            }
        )
    return entries


def approve_baseline_proposal(proposal_value: Any, decision_value: Any) -> dict[str, Any]:
    if not isinstance(proposal_value, Mapping) or proposal_value.get("schema_version") != PROPOSAL_SCHEMA:
        raise ArchitectureError("baseline proposal schema is invalid")
    if not isinstance(decision_value, Mapping) or decision_value.get("schema_version") != DECISION_SCHEMA:
        raise ArchitectureError("baseline decision schema is invalid")
    proposal_id = _text(proposal_value.get("proposal_id"), "proposal_id")
    claimed_proposal_hash = _text(
        proposal_value.get("proposal_sha256"), "proposal_sha256"
    )
    proposal_without_hash = dict(proposal_value)
    proposal_without_hash.pop("proposal_sha256", None)
    actual_proposal_hash = sha256_bytes(canonical_json_bytes(proposal_without_hash))
    if claimed_proposal_hash != actual_proposal_hash:
        raise ArchitectureError("baseline proposal hash does not match its content")
    if decision_value.get("proposal_id") != proposal_id:
        raise ArchitectureError("baseline decision proposal_id does not match")
    if decision_value.get("proposal_sha256") != claimed_proposal_hash:
        raise ArchitectureError("baseline decision proposal hash does not match")
    if decision_value.get("decision") != "approved":
        raise ArchitectureError("baseline decision must be explicitly approved")
    actor = _text(decision_value.get("actor"), "actor")
    decided_at = _text(decision_value.get("decided_at"), "decided_at")
    baseline = ArchitectureBaseline.from_dict(proposal_value.get("candidate_baseline"))
    if baseline.status != "candidate":
        raise ArchitectureError("proposal candidate baseline is not candidate status")
    approved = ArchitectureBaseline(
        baseline_id=baseline.baseline_id,
        repository_id=baseline.repository_id,
        commit_identity=baseline.commit_identity,
        nodes=baseline.nodes,
        edges=baseline.edges,
        tracked_path_hashes=baseline.tracked_path_hashes,
        status="approved",
        source_refs=baseline.source_refs
        + (f"decision:{proposal_id}:{claimed_proposal_hash}",),
        approved_by=actor,
        approved_at=decided_at,
    )
    return approved.to_dict()
