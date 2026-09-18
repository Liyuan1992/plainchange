from __future__ import annotations

import json
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from plainchange.onboarding import (
    OnboardingError,
    OnboardingServer,
    OnboardingState,
    build_guided_manifest,
    inspect_repository,
)
from conftest import run_git


def _status(repo: Path) -> str:
    return run_git(repo, "status", "--porcelain")


def test_inspect_repository_uses_plain_language_defaults(sample_repo) -> None:
    repo, base, head = sample_repo

    result = inspect_repository(repo)

    assert result["path"] == str(repo.resolve())
    assert result["read_only"] is True
    assert result["default_base"] == base
    assert result["default_head"] == head
    assert result["commits"][0]["message"] == "add named greeting"
    assert result["default_output"].startswith(str(repo.parent))
    assert _status(repo) == ""


def test_repository_subdirectory_is_normalized_to_git_root(sample_repo) -> None:
    repo, _base, _head = sample_repo
    subdirectory = repo / "nested"
    subdirectory.mkdir()

    result = inspect_repository(subdirectory)

    assert result["path"] == str(repo.resolve())
    assert Path(result["default_output"]).parent.parent == repo.parent


def test_inspect_repository_explains_empty_history_without_git_jargon(tmp_path) -> None:
    repo = tmp_path / "empty-repo"
    repo.mkdir()
    run_git(repo, "init", "-b", "main")

    with pytest.raises(OnboardingError) as caught:
        inspect_repository(repo)

    message = str(caught.value)
    assert "还没有保存过任何版本" in message
    assert "没有改动前后可以比较" in message
    assert "fatal:" not in message
    assert "commit" not in message.casefold()


def test_inspect_repository_explains_single_saved_version(tmp_path) -> None:
    repo = tmp_path / "single-version-repo"
    repo.mkdir()
    run_git(repo, "init", "-b", "main")
    run_git(repo, "config", "user.email", "tests@example.invalid")
    run_git(repo, "config", "user.name", "PlainChange Tests")
    (repo / "README.md").write_text("# Example\n", encoding="utf-8")
    run_git(repo, "add", "README.md")
    run_git(repo, "commit", "-m", "initial")

    with pytest.raises(OnboardingError) as caught:
        inspect_repository(repo)

    message = str(caught.value)
    assert "只有一个已保存版本" in message
    assert "再保存一个版本" in message
    assert "fatal:" not in message
    assert "commit" not in message.casefold()


def test_guided_manifest_stays_outside_target_and_preserves_task(sample_repo) -> None:
    repo, base, head = sample_repo

    manifest_path, output, manifest = build_guided_manifest(
        repo, base, head, task="让问候支持姓名。"
    )

    assert not output.is_relative_to(repo)
    assert manifest_path.parent == output
    assert manifest["repository"]["base"] == base
    assert manifest["repository"]["head"] == head
    assert manifest["evidence_inputs"][0]["source"]["text"] == "让问候支持姓名。"
    assert (output / ".plainchange-owned.json").is_file()
    assert _status(repo) == ""


def test_guided_manifest_rejects_same_commit_and_unmanaged_output(sample_repo, tmp_path) -> None:
    repo, base, head = sample_repo
    with pytest.raises(OnboardingError, match="不能相同"):
        build_guided_manifest(repo, head, head)

    occupied = tmp_path / "occupied"
    occupied.mkdir()
    (occupied / "keep.txt").write_text("mine", encoding="utf-8")
    with pytest.raises(OnboardingError, match="已有其他文件"):
        build_guided_manifest(repo, base, head, output=occupied)


def test_server_refuses_non_public_to_bind_publicly() -> None:
    with pytest.raises(OnboardingError, match="只能监听本机"):
        OnboardingServer(("0.0.0.0", 0))


@pytest.fixture
def onboarding_server():
    state = OnboardingState(token="test-session-token")
    server = OnboardingServer(("127.0.0.1", 0), state)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_port}"
    try:
        yield server, state, base_url
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def _request(
    url: str,
    *,
    token: str | None = None,
    payload: dict | None = None,
    extra_headers: dict[str, str] | None = None,
) -> tuple[int, bytes, dict[str, str]]:
    headers = {}
    data = None
    method = "GET"
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
        method = "POST"
    if token:
        headers["X-PlainChange-Token"] = token
    if extra_headers:
        headers.update(extra_headers)
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.status, response.read(), dict(response.headers)
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read(), dict(exc.headers)


def test_browser_shell_is_packaged_and_api_requires_session(onboarding_server) -> None:
    _server, state, base_url = onboarding_server
    status, body, headers = _request(base_url + "/")
    assert status == 200
    html = body.decode("utf-8")
    assert "选一个项目，看看 AI 到底改了什么" in html
    assert "完整理解（推荐）" in html
    assert "基础证据模式" in html
    assert 'id="model-base-url"' in html
    assert 'id="model-api-key"' in html
    assert "密钥只保存在当前 PlainChange 进程的内存中" in html
    assert 'rel="icon" href="data:,"' in html
    assert state.token in html
    assert "default-src 'self'" in headers["Content-Security-Policy"]

    status, body, _headers = _request(
        base_url + "/api/repository", payload={"path": "C:\\missing"}
    )
    assert status == 403
    assert "会话" in body.decode("utf-8")

    status, body, _headers = _request(
        base_url + "/api/repository",
        token=state.token,
        payload={"path": "C:\\missing"},
        extra_headers={"Origin": "http://example.invalid"},
    )
    assert status == 403
    assert "其他网页" in body.decode("utf-8")


def test_full_model_guided_request_requires_provider_settings(sample_repo, onboarding_server) -> None:
    repo, base, head = sample_repo
    _server, state, base_url = onboarding_server
    status, body, _headers = _request(
        base_url + "/api/analyze",
        token=state.token,
        payload={
            "repository": str(repo),
            "base": base,
            "head": head,
            "analysis_mode": "full_model",
        },
    )
    assert status == 400
    assert "模型接口设置" in json.loads(body)["error"]


def test_guided_direct_key_is_memory_only(sample_repo, tmp_path: Path, monkeypatch) -> None:
    repo, base, head = sample_repo
    state = OnboardingState(token="test-session-token")
    captured: dict[str, object] = {}

    def fake_analyze(_manifest, output, **kwargs):
        captured.update(kwargs)
        return {"review_html": str(Path(output) / "review.html")}

    monkeypatch.setattr("plainchange.onboarding.analyze_sample", fake_analyze)
    secret = "direct-key-that-must-not-leak"
    job = state.start_job(
        {
            "repository": str(repo),
            "base": base,
            "head": head,
            "output": str(tmp_path / "report"),
            "analysis_mode": "full_model",
            "model_api_key": secret,
            "model_config": {
                "schema_version": "change-passport.model-provider.v1",
                "provider_id": "guided-provider",
                "base_url": "https://models.example.com/v1",
                "model": "owner-selected-model",
                "api_key_env": None,
                "timeout_seconds": 120,
                "response_format": "json_schema",
            },
        }
    )
    deadline = time.monotonic() + 5
    while job.status not in {"succeeded", "failed"} and time.monotonic() < deadline:
        time.sleep(0.01)

    assert job.status == "succeeded"
    assert captured["model_api_key"] == secret
    assert secret not in json.dumps(job.public())
    assert secret not in (Path(job.output) / "guided-manifest.json").read_text(encoding="utf-8")


def test_http_guided_flow_generates_and_serves_report(sample_repo, onboarding_server) -> None:
    repo, base, head = sample_repo
    _server, state, base_url = onboarding_server

    status, body, _headers = _request(
        base_url + "/api/repository", token=state.token, payload={"path": str(repo)}
    )
    assert status == 200
    inspected = json.loads(body)["repository"]
    assert inspected["default_base"] == base
    assert inspected["default_head"] == head

    status, body, _headers = _request(
        base_url + "/api/analyze",
        token=state.token,
        payload={
            "repository": str(repo),
            "base": base,
            "head": head,
            "task": "让问候支持姓名。",
            "output": inspected["default_output"],
        },
    )
    assert status == 202
    job_id = json.loads(body)["job"]["id"]

    deadline = time.monotonic() + 45
    job = None
    while time.monotonic() < deadline:
        status, body, _headers = _request(
            base_url + f"/api/jobs/{job_id}", token=state.token
        )
        assert status == 200
        job = json.loads(body)["job"]
        if job["status"] in {"succeeded", "failed"}:
            break
        time.sleep(0.1)
    assert job is not None
    assert job["status"] == "succeeded", job
    assert job["receipt"]["status"] == "succeeded"
    assert Path(job["output"], "review.html").is_file()
    assert _status(repo) == ""

    status, report, report_headers = _request(
        base_url + f"{job['report_url']}?token={state.token}"
    )
    assert status == 200
    assert report.startswith(b"<!doctype html>")
    assert b'id="review-data"' in report
    assert "Content-Security-Policy" not in report_headers
