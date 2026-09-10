from __future__ import annotations

import hashlib
import os
import re
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Sequence

from .models import Limits, RepositorySpec
from .analysis_cache import default_cache_root


class GitEvidenceError(RuntimeError):
    """Raised when immutable Git evidence cannot be collected."""


@dataclass(frozen=True)
class GitTreeEntry:
    path: str
    object_id: str
    size: int


@dataclass(frozen=True)
class FileChange:
    path: str
    status: str
    added_lines: int | None
    deleted_lines: int | None
    binary: bool


@dataclass(frozen=True)
class GitEvidence:
    repository_name: str
    base_commit: str
    head_commit: str
    files: tuple[FileChange, ...]
    added_lines: int
    deleted_lines: int
    patch_sha256: str
    patch_excerpt: str
    patch_bytes: int
    patch_truncated: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "repository_name": self.repository_name,
            "base_commit": self.base_commit,
            "head_commit": self.head_commit,
            "files": [asdict(item) for item in self.files],
            "added_lines": self.added_lines,
            "deleted_lines": self.deleted_lines,
            "patch_sha256": self.patch_sha256,
            "patch_excerpt": self.patch_excerpt,
            "patch_bytes": self.patch_bytes,
            "patch_truncated": self.patch_truncated,
        }


def _run_git(
    repo: Path,
    args: Sequence[str],
    timeout: int,
    *,
    no_lazy_fetch: bool = False,
) -> bytes:
    env = os.environ.copy()
    env.update(
        {
            "GIT_OPTIONAL_LOCKS": "0",
            "GIT_PAGER": "cat",
            "GIT_TERMINAL_PROMPT": "0",
        }
    )
    if no_lazy_fetch:
        env["GIT_NO_LAZY_FETCH"] = "1"
    try:
        completed = subprocess.run(
            ["git", "-C", str(repo), "--no-pager", *args],
            check=False,
            capture_output=True,
            shell=False,
            timeout=timeout,
            env=env,
        )
    except subprocess.TimeoutExpired as exc:
        raise GitEvidenceError(f"git command timed out: {args[0]}") from exc
    except OSError as exc:
        raise GitEvidenceError("git executable is unavailable") from exc
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise GitEvidenceError(f"git {args[0]} failed: {detail or completed.returncode}")
    return completed.stdout


@dataclass(frozen=True)
class RepositoryMaterialization:
    repository: RepositorySpec
    object_status: str
    missing_object_count: int
    used_managed_copy: bool
    managed_copy_path: str | None

    def to_dict(self) -> dict[str, object]:
        return {
            "repository": {
                "path": str(self.repository.path),
                "base": self.repository.base,
                "head": self.repository.head,
            },
            "object_status": self.object_status,
            "missing_object_count": self.missing_object_count,
            "used_managed_copy": self.used_managed_copy,
            "managed_copy_path": self.managed_copy_path,
        }


def _missing_objects(repo: Path, base: str, head: str, timeout: int) -> tuple[str, ...]:
    raw = _run_git(
        repo,
        ["rev-list", "--objects", "--missing=print", base, head, "--"],
        timeout,
        no_lazy_fetch=True,
    )
    return tuple(
        line[1:].decode("ascii", errors="replace").strip()
        for line in raw.splitlines()
        if line.startswith(b"?")
    )


def _run_git_program(args: Sequence[str], timeout: int) -> None:
    env = os.environ.copy()
    env.update({"GIT_TERMINAL_PROMPT": "0", "GIT_PAGER": "cat"})
    try:
        completed = subprocess.run(
            ["git", *args],
            check=False,
            capture_output=True,
            shell=False,
            timeout=timeout,
            env=env,
        )
    except subprocess.TimeoutExpired as exc:
        raise GitEvidenceError("managed Git materialization timed out") from exc
    except OSError as exc:
        raise GitEvidenceError("git executable is unavailable") from exc
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise GitEvidenceError(f"managed Git materialization failed: {detail or completed.returncode}")


def materialize_repository(
    repository: RepositorySpec,
    limits: Limits,
    *,
    cache_root: Path | None = None,
    progress: Callable[[int, int, str], None] | None = None,
) -> RepositoryMaterialization:
    """Use the target read-only when complete; hydrate missing objects in managed cache."""

    timeout = limits.git_timeout_seconds
    if progress is not None:
        progress(0, 2, "检查固定版本所需的 Git 对象")
    try:
        base = _resolve_commit(repository.path, repository.base, timeout, no_lazy_fetch=True)
        head = _resolve_commit(repository.path, repository.head, timeout, no_lazy_fetch=True)
        missing = _missing_objects(repository.path, base, head, timeout)
    except GitEvidenceError:
        base = head = ""
        missing = ("unresolved-required-commit",)
    if not missing:
        if progress is not None:
            progress(2, 2, "固定版本所需对象已经完整")
        return RepositoryMaterialization(
            repository=RepositorySpec(repository.path, base, head),
            object_status="complete",
            missing_object_count=0,
            used_managed_copy=False,
            managed_copy_path=None,
        )

    try:
        remote = _run_git(
            repository.path,
            ["remote", "get-url", "origin"],
            timeout,
            no_lazy_fetch=True,
        ).decode("utf-8", errors="strict").strip()
    except (GitEvidenceError, UnicodeDecodeError) as exc:
        raise GitEvidenceError(
            "required Git objects are missing and the target has no usable origin; "
            "configure origin or provide a complete local repository"
        ) from exc
    if not remote:
        raise GitEvidenceError("required Git objects are missing and origin is empty")

    root = (cache_root or default_cache_root()) / "git"
    root.mkdir(parents=True, exist_ok=True)
    safe_name = re.sub(r"[^A-Za-z0-9._-]+", "-", repository.path.name)[:48] or "repository"
    identity = hashlib.sha256(str(repository.path).casefold().encode("utf-8")).hexdigest()[:16]
    managed = root / f"{safe_name}-{identity}.git"
    if not managed.is_dir():
        _run_git_program(["init", "--bare", str(managed)], timeout)
    remotes = _run_git(managed, ["remote"], timeout).decode("utf-8", errors="replace").splitlines()
    if "origin" in remotes:
        _run_git(managed, ["remote", "set-url", "origin", remote], timeout)
    else:
        _run_git(managed, ["remote", "add", "origin", remote], timeout)

    resolved: list[str] = []
    for index, ref in enumerate((repository.base, repository.head), start=1):
        if progress is not None:
            progress(index - 1, 2, f"在受管缓存中补齐第 {index} 个固定版本")
        _run_git(
            managed,
            ["fetch", "--no-tags", "--force", "origin", ref],
            max(timeout, 120),
        )
        resolved.append(_resolve_commit(managed, "FETCH_HEAD", timeout, no_lazy_fetch=True))
        if progress is not None:
            progress(index, 2, f"已补齐第 {index} 个固定版本")
    materialized = RepositorySpec(managed, resolved[0], resolved[1])
    remaining = _missing_objects(managed, resolved[0], resolved[1], timeout)
    if remaining:
        raise GitEvidenceError(
            f"managed Git copy is still missing {len(remaining)} required objects"
        )
    return RepositoryMaterialization(
        repository=materialized,
        object_status="hydrated_in_managed_cache",
        missing_object_count=len(missing),
        used_managed_copy=True,
        managed_copy_path=str(managed),
    )


def _resolve_commit(
    repo: Path,
    ref: str,
    timeout: int,
    *,
    no_lazy_fetch: bool = False,
) -> str:
    raw = _run_git(
        repo,
        ["rev-parse", "--verify", "--end-of-options", f"{ref}^{{commit}}"],
        timeout,
        no_lazy_fetch=no_lazy_fetch,
    )
    commit = raw.decode("ascii", errors="strict").strip()
    if len(commit) != 40 or any(char not in "0123456789abcdef" for char in commit.lower()):
        raise GitEvidenceError(f"git returned an invalid commit identity for {ref}")
    return commit.lower()


def list_git_tree(repo: Path, commit: str, timeout: int) -> dict[str, GitTreeEntry]:
    """Return immutable blob identities without checking out or touching the worktree."""

    raw = _run_git(
        repo,
        ["ls-tree", "-r", "-z", "--long", "--full-tree", commit, "--"],
        timeout,
    )
    result: dict[str, GitTreeEntry] = {}
    for record in raw.split(b"\0"):
        if not record:
            continue
        try:
            metadata, raw_path = record.split(b"\t", 1)
            _mode, object_type, object_id, raw_size = metadata.split(b" ", 3)
        except ValueError as exc:
            raise GitEvidenceError("unexpected git ls-tree output") from exc
        if object_type != b"blob":
            continue
        path = raw_path.decode("utf-8", errors="replace")
        try:
            size = int(raw_size)
        except ValueError as exc:
            raise GitEvidenceError("git ls-tree returned an invalid blob size") from exc
        result[path] = GitTreeEntry(
            path=path,
            object_id=object_id.decode("ascii", errors="strict"),
            size=size,
        )
    return result


def read_git_blob(repo: Path, commit: str, path: str, timeout: int) -> bytes:
    """Read one tree-owned blob by immutable commit/path identity."""

    if "\x00" in path or path.startswith("-"):
        raise GitEvidenceError("git blob path is invalid")
    return _run_git(repo, ["show", "--no-textconv", f"{commit}:{path}"], timeout)


def read_git_blobs(
    repo: Path,
    commit: str,
    paths: Sequence[str],
    timeout: int,
) -> dict[str, bytes]:
    """Read many immutable blobs through one cat-file process."""

    ordered = list(dict.fromkeys(paths))
    if any("\x00" in path or "\n" in path or "\r" in path for path in ordered):
        raise GitEvidenceError("git blob path contains an unsupported control character")
    if not ordered:
        return {}
    env = os.environ.copy()
    env.update(
        {
            "GIT_OPTIONAL_LOCKS": "0",
            "GIT_PAGER": "cat",
            "GIT_TERMINAL_PROMPT": "0",
        }
    )
    query = "".join(f"{commit}:{path}\n" for path in ordered).encode("utf-8")
    try:
        completed = subprocess.run(
            ["git", "-C", str(repo), "--no-pager", "cat-file", "--batch"],
            input=query,
            check=False,
            capture_output=True,
            shell=False,
            timeout=timeout,
            env=env,
        )
    except subprocess.TimeoutExpired as exc:
        raise GitEvidenceError("git cat-file batch timed out") from exc
    except OSError as exc:
        raise GitEvidenceError("git executable is unavailable") from exc
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise GitEvidenceError(f"git cat-file failed: {detail or completed.returncode}")

    result: dict[str, bytes] = {}
    output = completed.stdout
    offset = 0
    for path in ordered:
        line_end = output.find(b"\n", offset)
        if line_end < 0:
            raise GitEvidenceError("unexpected git cat-file batch output")
        header = output[offset:line_end].split()
        offset = line_end + 1
        if len(header) != 3 or header[1] != b"blob":
            raise GitEvidenceError(f"git cat-file could not read blob: {path}")
        try:
            size = int(header[2])
        except ValueError as exc:
            raise GitEvidenceError("git cat-file returned an invalid blob size") from exc
        end = offset + size
        if end > len(output):
            raise GitEvidenceError("git cat-file batch output was truncated")
        result[path] = output[offset:end]
        offset = end + 1
    return result


def _parse_name_status(raw: bytes) -> dict[str, str]:
    tokens = [token for token in raw.split(b"\0") if token]
    if len(tokens) % 2:
        raise GitEvidenceError("unexpected git name-status output")
    result: dict[str, str] = {}
    for index in range(0, len(tokens), 2):
        status = tokens[index].decode("utf-8", errors="replace")
        path = tokens[index + 1].decode("utf-8", errors="replace")
        result[path] = status
    return result


def _parse_numstat(raw: bytes) -> dict[str, tuple[int | None, int | None, bool]]:
    result: dict[str, tuple[int | None, int | None, bool]] = {}
    for record in raw.split(b"\0"):
        if not record:
            continue
        fields = record.split(b"\t", 2)
        if len(fields) != 3:
            raise GitEvidenceError("unexpected git numstat output")
        added_raw, deleted_raw, path_raw = fields
        path = path_raw.decode("utf-8", errors="replace")
        binary = added_raw == b"-" or deleted_raw == b"-"
        added = None if binary else int(added_raw)
        deleted = None if binary else int(deleted_raw)
        result[path] = (added, deleted, binary)
    return result


def collect_git_evidence(repository: RepositorySpec, limits: Limits) -> GitEvidence:
    base_commit = _resolve_commit(repository.path, repository.base, limits.git_timeout_seconds)
    head_commit = _resolve_commit(repository.path, repository.head, limits.git_timeout_seconds)
    if base_commit == head_commit:
        raise GitEvidenceError("base and head resolve to the same commit")

    name_status = _parse_name_status(
        _run_git(
            repository.path,
            ["diff", "--no-ext-diff", "--no-renames", "--name-status", "-z", base_commit, head_commit, "--"],
            limits.git_timeout_seconds,
        )
    )
    numstat = _parse_numstat(
        _run_git(
            repository.path,
            ["diff", "--no-ext-diff", "--no-renames", "--numstat", "-z", base_commit, head_commit, "--"],
            limits.git_timeout_seconds,
        )
    )
    if not name_status:
        raise GitEvidenceError("the immutable change range has no changed files")

    changes: list[FileChange] = []
    for path in sorted(name_status):
        added, deleted, binary = numstat.get(path, (None, None, True))
        changes.append(
            FileChange(
                path=path,
                status=name_status[path],
                added_lines=added,
                deleted_lines=deleted,
                binary=binary,
            )
        )

    patch_raw = _run_git(
        repository.path,
        ["diff", "--no-ext-diff", "--no-renames", "--unified=3", base_commit, head_commit, "--"],
        limits.git_timeout_seconds,
    )
    patch_sha256 = hashlib.sha256(patch_raw).hexdigest()
    truncated = len(patch_raw) > limits.max_patch_bytes
    excerpt_raw = patch_raw[: limits.max_patch_bytes]
    excerpt = excerpt_raw.decode("utf-8", errors="replace")
    if truncated:
        excerpt += "\n[PATCH TRUNCATED BY CHANGE PASSPORT]\n"

    return GitEvidence(
        repository_name=repository.path.name,
        base_commit=base_commit,
        head_commit=head_commit,
        files=tuple(changes),
        added_lines=sum(item.added_lines or 0 for item in changes),
        deleted_lines=sum(item.deleted_lines or 0 for item in changes),
        patch_sha256=patch_sha256,
        patch_excerpt=excerpt,
        patch_bytes=len(patch_raw),
        patch_truncated=truncated,
    )
