from __future__ import annotations

import json
import os
import re
import secrets
import subprocess
import threading
import webbrowser
from dataclasses import dataclass, field
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib import resources
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from . import __version__
from .models import ManifestError, canonical_json_bytes
from .pipeline import analyze_sample

LOOPBACK_HOSTS = {"127.0.0.1", "localhost"}
OID_PATTERN = re.compile(r"^[0-9a-fA-F]{7,64}$")
SAFE_ID_PATTERN = re.compile(r"[^a-z0-9._-]+")
MAX_REQUEST_BYTES = 64_000
MAX_EPHEMERAL_API_KEY_BYTES = 8_192


class OnboardingError(ValueError):
    """Raised when the guided local workflow receives unsafe or invalid input."""


def _run_git(repo: Path, args: list[str], timeout: int = 15) -> subprocess.CompletedProcess[bytes]:
    env = os.environ.copy()
    env.update(
        {
            "GIT_OPTIONAL_LOCKS": "0",
            "GIT_PAGER": "cat",
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_NO_LAZY_FETCH": "1",
        }
    )
    try:
        return subprocess.run(
            ["git", "-C", str(repo), "--no-pager", *args],
            check=False,
            capture_output=True,
            shell=False,
            timeout=timeout,
            env=env,
        )
    except subprocess.TimeoutExpired as exc:
        raise OnboardingError("读取项目版本超时，请确认这是一个可用的本地 Git 项目。") from exc
    except OSError as exc:
        raise OnboardingError("没有找到 Git，请先安装 Git 后重试。") from exc


def _git(repo: Path, args: list[str], timeout: int = 15) -> str:
    completed = _run_git(repo, args, timeout)
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise OnboardingError(detail or "无法读取这个 Git 项目。")
    return completed.stdout.decode("utf-8", errors="replace")


def resolve_repository(value: str | Path) -> Path:
    if not isinstance(value, (str, Path)):
        raise OnboardingError("项目路径格式无效。")
    raw = str(value).strip()
    if not raw:
        raise OnboardingError("请先选择一个项目文件夹。")
    try:
        repo = Path(raw).expanduser().resolve(strict=True)
    except OSError as exc:
        raise OnboardingError("这个项目文件夹不存在。") from exc
    if not repo.is_dir():
        raise OnboardingError("请选择项目文件夹，而不是单个文件。")
    root_text = _git(repo, ["rev-parse", "--show-toplevel"]).strip()
    try:
        root = Path(root_text).resolve(strict=True)
    except OSError as exc:
        raise OnboardingError("无法确定这个 Git 项目的根目录。") from exc
    if not root.is_dir():
        raise OnboardingError("无法确定这个 Git 项目的根目录。")
    return root


def inspect_repository(value: str | Path, *, limit: int = 20) -> dict[str, Any]:
    repo = resolve_repository(value)
    limit = max(2, min(limit, 50))
    branch = _git(repo, ["branch", "--show-current"]).strip() or "当前分支"
    head_check = _run_git(repo, ["rev-parse", "--verify", "HEAD"])
    if head_check.returncode != 0:
        raise OnboardingError(
            f"“{branch}”还没有保存过任何版本，所以现在没有改动前后可以比较。"
            "请先保存一个初始版本，再完成一次修改并保存新版本后重试。"
        )
    raw = _git(
        repo,
        [
            "log",
            f"--max-count={limit}",
            "--date=iso-strict",
            "--format=%H%x1f%h%x1f%cI%x1f%s",
        ],
    )
    commits: list[dict[str, str]] = []
    for line in raw.splitlines():
        parts = line.split("\x1f", 3)
        if len(parts) == 4:
            commits.append(
                {"id": parts[0], "short_id": parts[1], "date": parts[2], "message": parts[3]}
            )
    if len(commits) < 2:
        raise OnboardingError(
            "这个项目目前只有一个已保存版本，还没有“改动前”和“改动后”可以比较。"
            "请完成一次修改并再保存一个版本后重试。"
        )
    return {
        "path": str(repo),
        "name": repo.name,
        "branch": branch,
        "commits": commits,
        "default_head": commits[0]["id"],
        "default_base": commits[1]["id"],
        "default_output": str(_default_output(repo, commits[1]["id"], commits[0]["id"])),
        "output_root": str(repo.parent / "plainchange-reports"),
        "output_stem": _safe_sample_id(repo, "0000000", "0000000").rsplit("-0000000-to-0000000", 1)[0],
        "read_only": True,
    }


def _safe_sample_id(repo: Path, base: str, head: str) -> str:
    stem = SAFE_ID_PATTERN.sub("-", repo.name.casefold()).strip("-._") or "project"
    if not stem[0].isalpha():
        stem = f"project-{stem}"
    return f"{stem[:48]}-{base[:7].lower()}-to-{head[:7].lower()}"[:80]


def _default_output(repo: Path, base: str, head: str) -> Path:
    return repo.parent / "plainchange-reports" / _safe_sample_id(repo, base, head)


def _verified_oid(repo: Path, value: str, label: str) -> str:
    if not isinstance(value, str):
        raise OnboardingError(f"{label}格式无效。")
    revision = value.strip()
    if not OID_PATTERN.fullmatch(revision):
        raise OnboardingError(f"{label}不是由本工具列出的固定版本。")
    resolved = _git(repo, ["rev-parse", "--verify", f"{revision}^{{commit}}"]).strip()
    if not re.fullmatch(r"[0-9a-f]{40,64}", resolved):
        raise OnboardingError(f"无法固定{label}。")
    return resolved


def build_guided_manifest(
    repository: str | Path,
    base: str,
    head: str,
    *,
    task: str = "",
    output: str | Path | None = None,
) -> tuple[Path, Path, dict[str, Any]]:
    repo = resolve_repository(repository)
    base_oid = _verified_oid(repo, base, "较早版本")
    head_oid = _verified_oid(repo, head, "较新版本")
    if base_oid == head_oid:
        raise OnboardingError("较早版本和较新版本不能相同。")
    if output is not None and not isinstance(output, (str, Path)):
        raise OnboardingError("报告目录格式无效。")
    destination = (
        Path(output).expanduser().resolve(strict=False)
        if output and str(output).strip()
        else _default_output(repo, base_oid, head_oid).resolve(strict=False)
    )
    repo_resolved = repo.resolve(strict=True)
    if destination == repo_resolved or destination.is_relative_to(repo_resolved):
        raise OnboardingError("报告必须保存在被分析项目之外，以免修改目标项目。")
    if destination == Path(destination.anchor) or destination.parent == destination:
        raise OnboardingError("不能把磁盘根目录作为报告目录。")
    sample_id = _safe_sample_id(repo, base_oid, head_oid)
    marker = destination / ".plainchange-owned.json"
    if destination.exists():
        entries = list(destination.iterdir())
        if entries and not marker.is_file():
            raise OnboardingError("报告目录已有其他文件，请换一个空目录。")
        if marker.is_file():
            try:
                existing_marker = json.loads(marker.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                raise OnboardingError("报告目录的归属标记已损坏，请换一个目录。") from exc
            if existing_marker.get("sample_id") != sample_id:
                raise OnboardingError("这个报告目录属于另一组版本，请使用建议的新目录。")
    destination.mkdir(parents=True, exist_ok=True)
    evidence_inputs: list[dict[str, Any]] = []
    if not isinstance(task, str):
        raise OnboardingError("需求说明格式无效。")
    task_text = task.strip()
    if task_text:
        if len(task_text.encode("utf-8")) > 32_000:
            raise OnboardingError("需求说明过长，请控制在 32 KB 以内。")
        evidence_inputs.append(
            {
                "id": "task.original",
                "kind": "task",
                "authority": "original_task",
                "source": {"type": "inline", "text": task_text},
            }
        )
    manifest = {
        "schema_version": "change-passport.sample.v1",
        "sample_id": sample_id,
        "repository": {"path": str(repo), "base": base_oid, "head": head_oid},
        "evidence_inputs": evidence_inputs,
        "hidden_ground_truth": [],
        "limits": {
            "max_patch_bytes": 200_000,
            "max_input_bytes": 64_000,
            "git_timeout_seconds": 15,
        },
    }
    marker.write_bytes(
        canonical_json_bytes(
            {"schema_version": "plainchange.output-owner.v1", "sample_id": sample_id}
        )
        + b"\n"
    )
    manifest_path = destination / "guided-manifest.json"
    manifest_path.write_bytes(canonical_json_bytes(manifest) + b"\n")
    return manifest_path, destination, manifest


def choose_directory() -> str | None:
    try:
        import tkinter
        from tkinter import filedialog
    except (ImportError, RuntimeError) as exc:
        raise OnboardingError("当前环境无法打开文件夹选择器，请直接粘贴项目路径。") from exc
    root = tkinter.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    try:
        selected = filedialog.askdirectory(title="选择要理解的软件项目")
    finally:
        root.destroy()
    return selected or None


@dataclass
class GuidedJob:
    job_id: str
    output: Path
    status: str = "queued"
    error: str | None = None
    result: dict[str, Any] | None = None
    analysis_mode: str = "basic_evidence"

    def public(self) -> dict[str, Any]:
        receipt: dict[str, Any] | None = None
        receipt_path = self.output / "run-receipt.json"
        if receipt_path.is_file():
            try:
                receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                receipt = None
        value: dict[str, Any] = {
            "id": self.job_id,
            "status": self.status,
            "error": self.error,
            "receipt": receipt,
            "analysis_mode": self.analysis_mode,
        }
        if self.status == "succeeded":
            value["report_url"] = f"/reports/{self.job_id}/review.html"
            value["output"] = str(self.output)
        return value


@dataclass
class OnboardingState:
    token: str = field(default_factory=lambda: secrets.token_urlsafe(32))
    jobs: dict[str, GuidedJob] = field(default_factory=dict)
    lock: threading.Lock = field(default_factory=threading.Lock)

    def start_job(self, payload: dict[str, Any]) -> GuidedJob:
        manifest_path, output, _manifest = build_guided_manifest(
            payload.get("repository", ""),
            payload.get("base", ""),
            payload.get("head", ""),
            task=payload.get("task", ""),
            output=payload.get("output"),
        )
        # Older API clients did not send a mode; keep those requests local and
        # conservative. The packaged browser explicitly selects full_model.
        requested_mode = payload.get("analysis_mode", "basic_evidence")
        if requested_mode not in {"full_model", "basic_evidence"}:
            raise OnboardingError("分析方式无效。")
        provider_config = payload.get("model_config")
        model_api_key = payload.get("model_api_key")
        human_language = payload.get("human_language", "zh-CN")
        if human_language not in {"zh-CN", "en"}:
            raise OnboardingError("模型说明语言只能是中文或英文。")
        if requested_mode == "full_model" and not isinstance(provider_config, dict):
            raise OnboardingError("完整理解需要先填写模型接口设置。")
        if model_api_key is not None:
            if not isinstance(model_api_key, str) or not model_api_key.strip():
                raise OnboardingError("模型密钥格式无效。")
            if len(model_api_key.encode("utf-8")) > MAX_EPHEMERAL_API_KEY_BYTES:
                raise OnboardingError("模型密钥过长。")
        if requested_mode == "basic_evidence":
            provider_config = None
            model_api_key = None
        job = GuidedJob(
            secrets.token_hex(12),
            output,
            analysis_mode=requested_mode,
        )
        with self.lock:
            self.jobs[job.job_id] = job

        def run() -> None:
            job.status = "running"
            try:
                job.result = analyze_sample(
                    manifest_path,
                    output,
                    generator="model" if requested_mode == "full_model" else "deterministic",
                    model_config=provider_config,
                    model_api_key=model_api_key,
                    human_language=human_language,
                )
            except (ManifestError, OSError, RuntimeError, ValueError) as exc:
                job.status = "failed"
                job.error = str(exc)
            except Exception:
                job.status = "failed"
                job.error = "分析意外中断，请查看终端中的错误信息。"
            else:
                job.status = "succeeded"

        threading.Thread(target=run, name=f"plainchange-{job.job_id}", daemon=True).start()
        return job


def _asset_text(name: str) -> str:
    return resources.files("plainchange").joinpath("templates", name).read_text(encoding="utf-8")


class OnboardingServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address: tuple[str, int], state: OnboardingState | None = None):
        host = address[0]
        if host not in LOOPBACK_HOSTS:
            raise OnboardingError("首次使用页面只能监听本机地址。")
        self.state = state or OnboardingState()
        super().__init__(address, OnboardingHandler)


class OnboardingHandler(BaseHTTPRequestHandler):
    server: OnboardingServer

    def log_message(self, format: str, *args: object) -> None:
        return

    def _headers(
        self, status: HTTPStatus, content_type: str, length: int, *, browser_shell: bool = True
    ) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(length))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Cache-Control", "no-store")
        if browser_shell and content_type.startswith(("text/html", "text/css", "text/javascript")):
            self.send_header(
                "Content-Security-Policy",
                "default-src 'self'; script-src 'self'; style-src 'self'; "
                "img-src 'self' data:; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'",
            )
        self.end_headers()

    def _send_bytes(
        self,
        value: bytes,
        content_type: str,
        status: HTTPStatus = HTTPStatus.OK,
        *,
        browser_shell: bool = True,
    ) -> None:
        self._headers(status, content_type, len(value), browser_shell=browser_shell)
        self.wfile.write(value)

    def _json(self, value: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        self._send_bytes(canonical_json_bytes(value), "application/json; charset=utf-8", status)

    def _authorized(self) -> bool:
        token = self.headers.get("X-PlainChange-Token", "")
        if not secrets.compare_digest(token, self.server.state.token):
            self._json({"ok": False, "error": "本地会话已失效，请刷新页面。"}, HTTPStatus.FORBIDDEN)
            return False
        origin = self.headers.get("Origin")
        if origin:
            allowed = {f"http://{self.headers.get('Host', '')}"}
            if origin not in allowed:
                self._json({"ok": False, "error": "拒绝来自其他网页的请求。"}, HTTPStatus.FORBIDDEN)
                return False
        return True

    def _read_json(self) -> dict[str, Any]:
        if self.headers.get_content_type() != "application/json":
            raise OnboardingError("请求必须使用 JSON。")
        raw_length = self.headers.get("Content-Length", "0")
        try:
            length = int(raw_length)
        except ValueError as exc:
            raise OnboardingError("请求大小无效。") from exc
        if length <= 0 or length > MAX_REQUEST_BYTES:
            raise OnboardingError("请求为空或过大。")
        try:
            value = json.loads(self.rfile.read(length))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise OnboardingError("请求不是有效 JSON。") from exc
        if not isinstance(value, dict):
            raise OnboardingError("请求必须是一个对象。")
        return value

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/":
            html = _asset_text("onboarding.html")
            html = html.replace("__SESSION_TOKEN__", self.server.state.token)
            html = html.replace("__APP_VERSION__", __version__)
            self._send_bytes(html.encode("utf-8"), "text/html; charset=utf-8")
            return
        if parsed.path in {"/onboarding.css", "/onboarding.js"}:
            name = parsed.path.removeprefix("/")
            kind = "text/css" if name.endswith(".css") else "text/javascript"
            self._send_bytes(_asset_text(name).encode("utf-8"), f"{kind}; charset=utf-8")
            return
        if parsed.path.startswith("/api/jobs/"):
            if not self._authorized():
                return
            job_id = parsed.path.removeprefix("/api/jobs/")
            job = self.server.state.jobs.get(job_id)
            if job is None:
                self._json({"ok": False, "error": "没有找到这次分析。"}, HTTPStatus.NOT_FOUND)
            else:
                self._json({"ok": True, "job": job.public()})
            return
        match = re.fullmatch(r"/reports/([0-9a-f]{24})/review\.html", parsed.path)
        if match:
            query_token = parse_qs(parsed.query).get("token", [""])[0]
            if not secrets.compare_digest(query_token, self.server.state.token):
                self._json({"ok": False, "error": "报告链接已失效。"}, HTTPStatus.FORBIDDEN)
                return
            job = self.server.state.jobs.get(match.group(1))
            report = job.output / "review.html" if job and job.status == "succeeded" else None
            if report is None or not report.is_file():
                self._json({"ok": False, "error": "报告尚未生成。"}, HTTPStatus.NOT_FOUND)
                return
            self._send_bytes(
                report.read_bytes(), "text/html; charset=utf-8", browser_shell=False
            )
            return
        self._json({"ok": False, "error": "页面不存在。"}, HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        if not self._authorized():
            return
        try:
            payload = self._read_json()
            if self.path == "/api/pick-directory":
                self._json({"ok": True, "path": choose_directory()})
            elif self.path == "/api/repository":
                self._json({"ok": True, "repository": inspect_repository(payload.get("path", ""))})
            elif self.path == "/api/analyze":
                job = self.server.state.start_job(payload)
                self._json({"ok": True, "job": job.public()}, HTTPStatus.ACCEPTED)
            else:
                self._json({"ok": False, "error": "接口不存在。"}, HTTPStatus.NOT_FOUND)
        except (OnboardingError, ManifestError, OSError) as exc:
            self._json({"ok": False, "error": str(exc)}, HTTPStatus.BAD_REQUEST)


def serve_onboarding(host: str = "127.0.0.1", port: int = 8765, *, open_browser: bool = True) -> None:
    if not isinstance(port, int) or isinstance(port, bool) or not 0 <= port <= 65_535:
        raise OnboardingError("端口必须是 0 到 65535 之间的整数。")
    server = OnboardingServer((host, port))
    actual_host, actual_port = server.server_address[:2]
    url = f"http://{actual_host}:{actual_port}/"
    print(json.dumps({"ok": True, "url": url, "version": __version__}, ensure_ascii=False))
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever(poll_interval=0.25)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
