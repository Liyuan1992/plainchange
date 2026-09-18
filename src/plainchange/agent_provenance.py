from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
from collections import defaultdict
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Protocol, Sequence

from .models import canonical_json_bytes, sha256_bytes

PROVENANCE_SCHEMA = "plainchange.agent-provenance.v1"
COMMAND_CONTRACT = "git-ai-diff-json.v1"
MAX_OUTPUT_BYTES = 8 * 1024 * 1024
MAX_HUNKS = 50_000
MAX_FILES = 5_000
MAX_IDENTITIES = 10_000
MAX_CHANGED_LINES = 5_000_000
SAFE_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 ._+:/@-]{0,79}$")


class AgentProvenanceProvider(Protocol):
    """Read-only source for normalized agent authorship attestations."""

    def collect(
        self,
        repository: Path,
        base_commit: str,
        head_commit: str,
        *,
        expected_added_lines: int,
        expected_deleted_lines: int,
    ) -> dict[str, Any]: ...


class _CommandFailure(RuntimeError):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def _base_result(
    base_commit: str,
    head_commit: str,
    status: str,
    reason: str,
    *,
    expected_added_lines: int = 0,
    expected_deleted_lines: int = 0,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "schema_version": PROVENANCE_SCHEMA,
        "provider": "git-ai",
        "source_kind": "authorship_attestation",
        "status": status,
        "status_reason": reason,
        "base_commit": base_commit,
        "head_commit": head_commit,
        "provider_version": None,
        "command_contract": COMMAND_CONTRACT,
        "summary": {
            "added_code_lines": expected_added_lines,
            "deleted_code_lines": expected_deleted_lines,
            "ai_added_lines": 0,
            "human_added_lines": 0,
            "untracked_added_lines": expected_added_lines,
            "recorded_added_lines": 0,
            "coverage_percent": 0,
            "session_count": 0,
            "tools": [],
        },
        "files": [],
        "limitations": [
            "authorship_does_not_prove_correctness",
            "runtime_behavior_not_verified",
            "prompts_and_transcripts_not_collected",
        ],
    }
    result["normalized_sha256"] = sha256_bytes(canonical_json_bytes(result))
    return result


def _finalize(result: dict[str, Any]) -> dict[str, Any]:
    result.pop("normalized_sha256", None)
    result["normalized_sha256"] = sha256_bytes(canonical_json_bytes(result))
    return result


def validate_agent_provenance(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping) or value.get("schema_version") != PROVENANCE_SCHEMA:
        raise ValueError("agent provenance schema is invalid")
    result = dict(value)
    claimed = result.pop("normalized_sha256", None)
    if claimed != sha256_bytes(canonical_json_bytes(result)):
        raise ValueError("agent provenance hash does not match its content")
    result["normalized_sha256"] = claimed
    if result.get("status") not in {
        "available",
        "partial",
        "no_record",
        "not_installed",
        "invalid",
    }:
        raise ValueError("agent provenance status is invalid")
    expected_keys = {
        "schema_version", "provider", "source_kind", "status", "status_reason",
        "base_commit", "head_commit", "provider_version", "command_contract",
        "summary", "files", "limitations", "normalized_sha256",
    }
    if set(result) != expected_keys:
        raise ValueError("agent provenance fields are invalid")
    if result["provider"] != "git-ai" or result["source_kind"] != "authorship_attestation":
        raise ValueError("agent provenance authority is invalid")
    if result["command_contract"] != COMMAND_CONTRACT:
        raise ValueError("agent provenance command contract is invalid")
    commit_pattern = re.compile(r"^[0-9a-f]{40,64}$")
    if not commit_pattern.fullmatch(str(result["base_commit"])) or not commit_pattern.fullmatch(str(result["head_commit"])):
        raise ValueError("agent provenance commit binding is invalid")
    version = result["provider_version"]
    if version is not None and _bounded_text(version, fallback="") != version:
        raise ValueError("agent provenance version is invalid")
    summary = result.get("summary")
    expected_summary_keys = {
        "added_code_lines", "deleted_code_lines", "ai_added_lines",
        "human_added_lines", "untracked_added_lines", "recorded_added_lines",
        "coverage_percent", "session_count", "tools",
    }
    if not isinstance(summary, Mapping) or set(summary) != expected_summary_keys:
        raise ValueError("agent provenance summary is invalid")
    for key in expected_summary_keys - {"tools"}:
        _bounded_int(summary[key], f"invalid_{key}")
    if summary["recorded_added_lines"] != summary["ai_added_lines"] + summary["human_added_lines"]:
        raise ValueError("agent provenance recorded total is invalid")
    if summary["recorded_added_lines"] + summary["untracked_added_lines"] != summary["added_code_lines"]:
        raise ValueError("agent provenance addition total is invalid")
    expected_coverage = round(summary["recorded_added_lines"] * 100 / summary["added_code_lines"]) if summary["added_code_lines"] else 0
    if summary["coverage_percent"] != expected_coverage:
        raise ValueError("agent provenance coverage is invalid")
    tools = summary["tools"]
    if not isinstance(tools, list) or len(tools) > 32:
        raise ValueError("agent provenance tools are invalid")
    for item in tools:
        if not isinstance(item, Mapping) or set(item) != {"tool", "model"}:
            raise ValueError("agent provenance tool identity is invalid")
        if _bounded_text(item["tool"], fallback="") != item["tool"] or _bounded_text(item["model"], fallback="") != item["model"]:
            raise ValueError("agent provenance tool identity is unsafe")
    files = result.get("files")
    if not isinstance(files, list) or len(files) > MAX_FILES:
        raise ValueError("agent provenance files are invalid")
    file_keys = {"path", "ai_added_lines", "human_added_lines", "untracked_added_lines", "deleted_lines"}
    for item in files:
        if not isinstance(item, Mapping) or set(item) != file_keys or _safe_path(item["path"]) != item["path"]:
            raise ValueError("agent provenance file summary is invalid")
        for key in file_keys - {"path"}:
            _bounded_int(item[key], f"invalid_file_{key}")
    limitations = result.get("limitations")
    if not isinstance(limitations, list) or not limitations or len(limitations) > 8:
        raise ValueError("agent provenance limitations are invalid")
    if any(not isinstance(item, str) or not re.fullmatch(r"[a-z0-9_]{1,80}", item) for item in limitations):
        raise ValueError("agent provenance limitation is invalid")
    return result


def _bounded_text(value: Any, *, fallback: str) -> str:
    if not isinstance(value, str):
        return fallback
    candidate = " ".join(value.split())
    if not candidate or len(candidate) > 80 or not SAFE_IDENTITY.fullmatch(candidate):
        return fallback
    return candidate


def _safe_path(value: Any) -> str:
    if not isinstance(value, str) or not value or len(value) > 500:
        raise ValueError("invalid_path")
    normalized = value.replace("\\", "/")
    path = PurePosixPath(normalized)
    if (
        path.is_absolute()
        or ".." in path.parts
        or re.match(r"^[A-Za-z]:", normalized)
        or any(ord(character) < 32 for character in normalized)
    ):
        raise ValueError("invalid_path")
    return path.as_posix()


def _bounded_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= MAX_CHANGED_LINES:
        raise ValueError(label)
    return value


def _run_bounded(
    command: Sequence[str],
    *,
    cwd: Path,
    timeout_seconds: int,
    max_output_bytes: int,
) -> bytes:
    environment = os.environ.copy()
    environment.update({"GIT_OPTIONAL_LOCKS": "0", "GIT_TERMINAL_PROMPT": "0"})
    with tempfile.TemporaryFile() as stdout_file, tempfile.TemporaryFile() as stderr_file:
        try:
            completed = subprocess.run(
                list(command),
                cwd=cwd,
                env=environment,
                stdin=subprocess.DEVNULL,
                stdout=stdout_file,
                stderr=stderr_file,
                shell=False,
                timeout=timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise _CommandFailure("timeout") from exc
        except OSError as exc:
            raise _CommandFailure("execution_failed") from exc
        stdout_size = stdout_file.tell()
        stderr_size = stderr_file.tell()
        if stdout_size > max_output_bytes or stderr_size > max_output_bytes:
            raise _CommandFailure("oversized_output")
        if completed.returncode != 0:
            raise _CommandFailure("nonzero_exit")
        stdout_file.seek(0)
        return stdout_file.read()


def _normalize_discovered_executable(
    executable: str,
    *,
    platform_name: str | None = None,
) -> str:
    """Preserve the executable identity expected by Git AI on Windows.

    ``shutil.which`` appends the first matching PATHEXT entry and commonly
    returns ``git-ai.EXE``. Git AI v1.7.5 uses its invocation name to decide
    whether to run Git AI commands or proxy regular Git. A capitalized
    extension makes it proxy ``diff`` to Git, so normalize only the extension
    spelling on Windows without changing the discovered location.
    """

    selected_platform = os.name if platform_name is None else platform_name
    if selected_platform == "nt" and executable.lower().endswith(".exe"):
        return executable[:-4] + ".exe"
    return executable


def _agent_identity(record: Any) -> tuple[str, str]:
    if not isinstance(record, Mapping):
        return ("unknown", "unknown")
    agent = record.get("agent_id")
    if not isinstance(agent, Mapping):
        return ("unknown", "unknown")
    return (
        _bounded_text(agent.get("tool"), fallback="unknown"),
        _bounded_text(agent.get("model"), fallback="unknown"),
    )


def _normalize_diff(
    raw: Any,
    *,
    base_commit: str,
    head_commit: str,
    expected_added_lines: int,
    expected_deleted_lines: int,
) -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        raise ValueError("root_not_object")
    hunks = raw.get("hunks")
    sessions = raw.get("sessions", {})
    prompts = raw.get("prompts", {})
    if not isinstance(hunks, list) or len(hunks) > MAX_HUNKS:
        raise ValueError("invalid_hunks")
    if not isinstance(sessions, Mapping) or len(sessions) > MAX_IDENTITIES:
        raise ValueError("invalid_sessions")
    if not isinstance(prompts, Mapping) or len(prompts) > MAX_IDENTITIES:
        raise ValueError("invalid_prompts")
    expected_added_lines = _bounded_int(expected_added_lines, "invalid_expected_additions")
    expected_deleted_lines = _bounded_int(expected_deleted_lines, "invalid_expected_deletions")

    file_counts: dict[str, dict[str, int]] = defaultdict(
        lambda: {"ai_added_lines": 0, "human_added_lines": 0, "untracked_added_lines": 0, "deleted_lines": 0}
    )
    session_keys: set[str] = set()
    tool_models: set[tuple[str, str]] = set()
    observed_additions = 0
    observed_deletions = 0
    for hunk in hunks:
        if not isinstance(hunk, Mapping):
            raise ValueError("invalid_hunk")
        path = _safe_path(hunk.get("file_path"))
        start = _bounded_int(hunk.get("start_line"), "invalid_start_line")
        end = _bounded_int(hunk.get("end_line"), "invalid_end_line")
        if start < 1 or end < start:
            raise ValueError("invalid_line_range")
        count = end - start + 1
        kind = hunk.get("hunk_kind")
        if kind == "deletion":
            observed_deletions += count
            file_counts[path]["deleted_lines"] += count
            continue
        if kind != "addition":
            raise ValueError("invalid_hunk_kind")
        observed_additions += count
        session_id = hunk.get("session_id")
        prompt_id = hunk.get("prompt_id")
        human_id = hunk.get("human_id")
        has_ai = isinstance(session_id, str) or isinstance(prompt_id, str)
        has_human = isinstance(human_id, str)
        if has_ai and has_human:
            raise ValueError("conflicting_attribution")
        if has_ai:
            file_counts[path]["ai_added_lines"] += count
            if isinstance(session_id, str):
                session_keys.add("s:" + session_id)
                tool_models.add(_agent_identity(sessions.get(session_id)))
            elif isinstance(prompt_id, str):
                session_keys.add("p:" + prompt_id)
                tool_models.add(_agent_identity(prompts.get(prompt_id)))
        elif has_human:
            file_counts[path]["human_added_lines"] += count
        else:
            file_counts[path]["untracked_added_lines"] += count

    if len(file_counts) > MAX_FILES or observed_additions > expected_added_lines or observed_deletions > expected_deleted_lines:
        raise ValueError("diff_totals_do_not_match_git")
    missing_additions = expected_added_lines - observed_additions
    ai_lines = sum(item["ai_added_lines"] for item in file_counts.values())
    human_lines = sum(item["human_added_lines"] for item in file_counts.values())
    untracked_lines = sum(item["untracked_added_lines"] for item in file_counts.values()) + missing_additions
    recorded_lines = ai_lines + human_lines
    status = "no_record"
    reason = "no_attribution_for_range"
    if recorded_lines:
        status = "partial" if untracked_lines else "available"
        reason = "partially_attributed" if untracked_lines else "attribution_available"

    result = _base_result(
        base_commit,
        head_commit,
        status,
        reason,
        expected_added_lines=expected_added_lines,
        expected_deleted_lines=expected_deleted_lines,
    )
    result["summary"] = {
        "added_code_lines": expected_added_lines,
        "deleted_code_lines": expected_deleted_lines,
        "ai_added_lines": ai_lines,
        "human_added_lines": human_lines,
        "untracked_added_lines": untracked_lines,
        "recorded_added_lines": recorded_lines,
        "coverage_percent": round(recorded_lines * 100 / expected_added_lines) if expected_added_lines else 0,
        "session_count": len(session_keys),
        "tools": [
            {"tool": tool, "model": model}
            for tool, model in sorted(tool_models)
        ][:32],
    }
    result["files"] = [
        {"path": path, **counts}
        for path, counts in sorted(file_counts.items())
        if any(counts.values())
    ]
    if missing_additions:
        result["limitations"].append("git_ai_output_did_not_cover_all_added_lines")
    return _finalize(result)


class GitAIProvenanceProvider:
    def __init__(
        self,
        *,
        command_prefix: Sequence[str] | None = None,
        timeout_seconds: int = 20,
        max_output_bytes: int = MAX_OUTPUT_BYTES,
    ) -> None:
        self.command_prefix = tuple(command_prefix) if command_prefix is not None else None
        self.timeout_seconds = timeout_seconds
        self.max_output_bytes = max_output_bytes

    def _resolved_command(self) -> tuple[str, ...] | None:
        if self.command_prefix is not None:
            return self.command_prefix
        executable = shutil.which("git-ai")
        return (_normalize_discovered_executable(executable),) if executable else None

    def collect(
        self,
        repository: Path,
        base_commit: str,
        head_commit: str,
        *,
        expected_added_lines: int,
        expected_deleted_lines: int,
    ) -> dict[str, Any]:
        command = self._resolved_command()
        if command is None:
            return _base_result(
                base_commit,
                head_commit,
                "not_installed",
                "git_ai_not_installed",
                expected_added_lines=expected_added_lines,
                expected_deleted_lines=expected_deleted_lines,
            )
        try:
            provider_version = None
            try:
                version_output = _run_bounded(
                    (*command, "--version"),
                    cwd=repository,
                    timeout_seconds=min(self.timeout_seconds, 5),
                    max_output_bytes=4_096,
                )
                provider_version = _bounded_text(
                    version_output.decode("utf-8"), fallback="unknown"
                )
                if provider_version == "unknown":
                    provider_version = None
            except (_CommandFailure, UnicodeDecodeError):
                provider_version = None
            payload = _run_bounded(
                (*command, "diff", f"{base_commit}..{head_commit}", "--json"),
                cwd=repository,
                timeout_seconds=self.timeout_seconds,
                max_output_bytes=self.max_output_bytes,
            )
            raw = json.loads(payload.decode("utf-8"))
            result = _normalize_diff(
                raw,
                base_commit=base_commit,
                head_commit=head_commit,
                expected_added_lines=expected_added_lines,
                expected_deleted_lines=expected_deleted_lines,
            )
            result["provider_version"] = provider_version
            return _finalize(result)
        except _CommandFailure as exc:
            return _base_result(
                base_commit,
                head_commit,
                "invalid",
                exc.code,
                expected_added_lines=expected_added_lines,
                expected_deleted_lines=expected_deleted_lines,
            )
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError, TypeError):
            return _base_result(
                base_commit,
                head_commit,
                "invalid",
                "malformed_or_unsupported_output",
                expected_added_lines=expected_added_lines,
                expected_deleted_lines=expected_deleted_lines,
            )


def collect_agent_provenance(
    repository: Path,
    base_commit: str,
    head_commit: str,
    *,
    expected_added_lines: int,
    expected_deleted_lines: int,
    provider: AgentProvenanceProvider | None = None,
) -> dict[str, Any]:
    selected = provider or GitAIProvenanceProvider()
    result = selected.collect(
        repository,
        base_commit,
        head_commit,
        expected_added_lines=expected_added_lines,
        expected_deleted_lines=expected_deleted_lines,
    )
    return validate_agent_provenance(result)


def provenance_evidence_entry(value: Any) -> dict[str, Any]:
    result = validate_agent_provenance(value)
    summary = result["summary"]
    tools = ", ".join(
        f"{item['tool']}:{item['model']}" for item in summary["tools"]
    ) or "none"
    return {
        "id": "agent.provenance",
        "kind": "agent_provenance",
        "authority": "authorship_attestation",
        "content": (
            f"provider=git-ai; status={result['status']}; "
            f"ai_added_lines={summary['ai_added_lines']}; "
            f"human_added_lines={summary['human_added_lines']}; "
            f"untracked_added_lines={summary['untracked_added_lines']}; "
            f"session_count={summary['session_count']}; tools={tools}"
        ),
        "source_ref": f"git-ai:normalized:{result['normalized_sha256']}",
        "limitations": list(result["limitations"]),
    }
