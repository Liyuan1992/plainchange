from __future__ import annotations

import json
import sys
from pathlib import Path

from plainchange.agent_provenance import (
    GitAIProvenanceProvider,
    _normalize_discovered_executable,
    collect_agent_provenance,
    provenance_evidence_entry,
    validate_agent_provenance,
)


def test_normalizes_windows_pathext_casing_for_git_ai_dispatch() -> None:
    assert _normalize_discovered_executable(
        r"C:\Users\owner\.git-ai\bin\git-ai.EXE",
        platform_name="nt",
    ) == r"C:\Users\owner\.git-ai\bin\git-ai.exe"
    assert _normalize_discovered_executable(
        "/usr/local/bin/git-ai.EXE",
        platform_name="posix",
    ) == "/usr/local/bin/git-ai.EXE"


def _provider(tmp_path: Path, payload: object, *, mode: str = "ok", max_bytes: int = 1_000_000) -> GitAIProvenanceProvider:
    script = tmp_path / f"fake_git_ai_{mode}.py"
    serialized = json.dumps(payload)
    script.write_text(
        "import sys, time\n"
        "if '--version' in sys.argv:\n"
        "    print('git-ai 1.7.0')\n"
        "    raise SystemExit(0)\n"
        + ("time.sleep(2)\n" if mode == "timeout" else "")
        + ("print('{bad json')\n" if mode == "malformed" else f"print({serialized!r})\n")
        + ("raise SystemExit(7)\n" if mode == "nonzero" else ""),
        encoding="utf-8",
    )
    return GitAIProvenanceProvider(
        command_prefix=(sys.executable, str(script)),
        timeout_seconds=1 if mode == "timeout" else 5,
        max_output_bytes=max_bytes,
    )


def _payload() -> dict[str, object]:
    return {
        "files": {"src/app.py": {"diff": "SECRET DIFF", "base_content": "SECRET BASE", "annotations": {}}},
        "prompts": {
            "prompt-secret": {
                "agent_id": {"tool": "codex", "model": "gpt-5.5"},
                "messages_url": "file:///secret/transcript.jsonl",
            }
        },
        "sessions": {
            "session-secret": {
                "agent_id": {"tool": "claude-code", "model": "claude-sonnet"},
                "human_author": {"email": "owner@example.com"},
            }
        },
        "humans": {"human-secret": {"email": "owner@example.com"}},
        "commits": {"deadbeef": {"message": "private commit message"}},
        "hunks": [
            {"commit_sha": "a", "content_hash": "1", "hunk_kind": "addition", "start_line": 1, "end_line": 2, "file_path": "src/app.py", "session_id": "session-secret"},
            {"commit_sha": "a", "content_hash": "2", "hunk_kind": "addition", "start_line": 3, "end_line": 3, "file_path": "src/app.py", "prompt_id": "prompt-secret"},
            {"commit_sha": "a", "content_hash": "3", "hunk_kind": "addition", "start_line": 4, "end_line": 4, "file_path": "src/app.py", "human_id": "human-secret"},
            {"commit_sha": "a", "content_hash": "4", "hunk_kind": "addition", "start_line": 5, "end_line": 5, "file_path": "src/app.py"},
            {"commit_sha": "a", "content_hash": "5", "hunk_kind": "deletion", "start_line": 8, "end_line": 9, "file_path": "src/app.py"},
        ],
    }


def test_normalizes_mixed_attribution_without_private_fields(tmp_path: Path) -> None:
    result = collect_agent_provenance(
        tmp_path,
        "a" * 40,
        "b" * 40,
        expected_added_lines=6,
        expected_deleted_lines=2,
        provider=_provider(tmp_path, _payload()),
    )

    assert result["status"] == "partial"
    assert result["provider_version"] == "git-ai 1.7.0"
    assert result["summary"] == {
        "added_code_lines": 6,
        "deleted_code_lines": 2,
        "ai_added_lines": 3,
        "human_added_lines": 1,
        "untracked_added_lines": 2,
        "recorded_added_lines": 4,
        "coverage_percent": 67,
        "session_count": 2,
        "tools": [
            {"tool": "claude-code", "model": "claude-sonnet"},
            {"tool": "codex", "model": "gpt-5.5"},
        ],
    }
    serialized = json.dumps(result, ensure_ascii=False)
    for forbidden in (
        "session-secret",
        "prompt-secret",
        "owner@example.com",
        "transcript.jsonl",
        "SECRET DIFF",
        "SECRET BASE",
        "private commit message",
    ):
        assert forbidden not in serialized
    validate_agent_provenance(result)
    evidence = json.dumps(provenance_evidence_entry(result), ensure_ascii=False)
    assert "authorship_attestation" in evidence
    assert "session-secret" not in evidence


def test_valid_output_without_attribution_is_no_record(tmp_path: Path) -> None:
    result = collect_agent_provenance(
        tmp_path,
        "a" * 40,
        "b" * 40,
        expected_added_lines=2,
        expected_deleted_lines=0,
        provider=_provider(tmp_path, {"hunks": [], "sessions": {}, "prompts": {}}),
    )
    assert result["status"] == "no_record"
    assert result["summary"]["untracked_added_lines"] == 2


def test_missing_command_is_nonfatal(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("plainchange.agent_provenance.shutil.which", lambda _: None)
    result = collect_agent_provenance(
        tmp_path,
        "a" * 40,
        "b" * 40,
        expected_added_lines=1,
        expected_deleted_lines=0,
    )
    assert result["status"] == "not_installed"


def test_command_failures_and_bad_output_are_sanitized(tmp_path: Path) -> None:
    cases = [
        ("malformed", 1_000_000, "malformed_or_unsupported_output"),
        ("nonzero", 1_000_000, "nonzero_exit"),
        ("timeout", 1_000_000, "timeout"),
        ("ok", 16, "oversized_output"),
    ]
    for mode, max_bytes, reason in cases:
        result = collect_agent_provenance(
            tmp_path,
            "a" * 40,
            "b" * 40,
            expected_added_lines=1,
            expected_deleted_lines=0,
            provider=_provider(tmp_path, _payload(), mode=mode, max_bytes=max_bytes),
        )
        assert result["status"] == "invalid"
        assert result["status_reason"] == reason


def test_unsafe_identity_and_path_never_reach_normalized_output(tmp_path: Path) -> None:
    payload = _payload()
    payload["sessions"]["session-secret"]["agent_id"] = {
        "tool": "</script><script>alert(1)</script>",
        "model": "bad\nmodel",
    }
    result = collect_agent_provenance(
        tmp_path,
        "a" * 40,
        "b" * 40,
        expected_added_lines=5,
        expected_deleted_lines=2,
        provider=_provider(tmp_path, payload),
    )
    assert any(item["tool"] == "unknown" for item in result["summary"]["tools"])
    assert "alert(1)" not in json.dumps(result)

    payload = _payload()
    payload["hunks"][0]["file_path"] = "../secret.txt"
    invalid = collect_agent_provenance(
        tmp_path,
        "a" * 40,
        "b" * 40,
        expected_added_lines=5,
        expected_deleted_lines=2,
        provider=_provider(tmp_path, payload),
    )
    assert invalid["status"] == "invalid"


def test_read_only_adapter_does_not_create_git_ai_notes(tmp_path: Path) -> None:
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    notes = git_dir / "refs" / "notes" / "ai"
    assert not notes.exists()
    collect_agent_provenance(
        tmp_path,
        "a" * 40,
        "b" * 40,
        expected_added_lines=5,
        expected_deleted_lines=2,
        provider=_provider(tmp_path, _payload()),
    )
    assert not notes.exists()
