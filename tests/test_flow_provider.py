from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from plainchange.flow_provider import CodexFlowProvider, CompatibleFlowProvider
from plainchange.model_adapter import ModelGenerationError


@pytest.mark.parametrize("mode", ["success", "missing_completion", "failed", "timeout", "invalid_json"])
def test_codex_completion_requires_exit_and_completed_event_and_keeps_receipts(tmp_path, monkeypatch, mode):
    monkeypatch.setattr("plainchange.flow_provider.codex_status", lambda: {"chatgpt": True, "path": "codex.exe"})
    monkeypatch.setenv("OPENAI_API_KEY", "must-not-inherit")
    monkeypatch.setenv("OPENAI_BASE_URL", "must-not-inherit")
    class Process:
        returncode = 1 if mode == "failed" else 0
        def __init__(self, args, **kwargs):
            assert "--ignore-user-config" in args
            assert args[args.index("--sandbox")+1] == "read-only"
            assert "shell_tool" in args and "unified_exec" in args
            assert "--output-schema" in args
            assert "OPENAI_API_KEY" not in kwargs["env"]
            assert "OPENAI_BASE_URL" not in kwargs["env"]
            self.events = kwargs["stdout"]
            self.output = Path(args[args.index("-o")+1])
        def communicate(self, data=None, timeout=None):
            if mode == "timeout" and timeout:
                raise subprocess.TimeoutExpired("codex", timeout)
            event = {"type": "turn.started"} if mode == "missing_completion" else {"type": "turn.completed", "usage": {"input_tokens": 10}}
            self.events.write((json.dumps(event) + "\n").encode())
            self.events.flush()
            self.output.write_text("invalid" if mode == "invalid_json" else '{"reads":[]}', encoding="utf-8")
        def kill(self):
            self.returncode = -1
    monkeypatch.setattr("plainchange.flow_provider.subprocess.Popen", Process)
    folder = tmp_path / "attempt"
    provider = CodexFlowProvider(timeout=1)
    if mode == "success":
        assert provider.complete("instructions", {"source": "content"}, {}, folder) == {"reads": []}
    else:
        with pytest.raises(ModelGenerationError):
            provider.complete("instructions", {"source": "content"}, {}, folder)
    receipt = json.loads((folder / "receipt.json").read_text(encoding="utf-8"))
    assert receipt["status"] == ("succeeded" if mode == "success" else "uncertain" if mode == "timeout" else "failed")
    assert (folder / "request.json").is_file()
    assert "must-not-inherit" not in (folder / "request.json").read_text(encoding="utf-8")


def test_api_alternative_sends_schema_and_does_not_accept_truncation(tmp_path, monkeypatch):
    config = tmp_path / "config.json"
    config.write_text(json.dumps({"schema_version": "change-passport.model-provider.v1", "provider_id": "test", "base_url": "http://localhost:1234/v1", "model": "test", "api_key_env": None, "timeout_seconds": 10, "response_format": "json_schema"}))
    def respond(url, payload, timeout, headers):
        assert payload["response_format"]["json_schema"]["strict"] is True
        return {"choices": [{"finish_reason": "length", "message": {"content": '{"reads":[]}'}}]}
    monkeypatch.setattr("plainchange.flow_provider._post_json", respond)
    with pytest.raises(ModelGenerationError, match="完整"):
        CompatibleFlowProvider(config).complete("test", {}, {}, tmp_path / "attempt")
    assert json.loads((tmp_path / "attempt/receipt.json").read_text(encoding="utf-8"))["status"] == "failed"
