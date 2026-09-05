from __future__ import annotations

import subprocess

import pytest

from change_passport.git_evidence import (
    GitEvidenceError,
    collect_git_evidence,
    read_git_blobs,
)
from change_passport.models import Limits, RepositorySpec


def _status(repo) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), "status", "--porcelain"],
        check=True,
        capture_output=True,
        shell=False,
        text=True,
    ).stdout


def test_collects_reproducible_read_only_git_evidence(sample_repo):
    repo, base, head = sample_repo
    spec = RepositorySpec(path=repo, base=base, head=head)
    before = _status(repo)

    first = collect_git_evidence(spec, Limits())
    second = collect_git_evidence(spec, Limits())

    assert first == second
    assert first.base_commit == base
    assert first.head_commit == head
    assert [item.path for item in first.files] == ["app.py", "feature.py"]
    assert first.patch_sha256
    assert "greeting(name" in first.patch_excerpt
    assert _status(repo) == before


def test_invalid_ref_fails_closed(sample_repo):
    repo, _, head = sample_repo
    spec = RepositorySpec(path=repo, base="does-not-exist", head=head)

    with pytest.raises(GitEvidenceError, match="rev-parse failed"):
        collect_git_evidence(spec, Limits())


def test_same_commit_range_is_rejected(sample_repo):
    repo, _, head = sample_repo
    spec = RepositorySpec(path=repo, base=head, head=head)

    with pytest.raises(GitEvidenceError, match="same commit"):
        collect_git_evidence(spec, Limits())


def test_patch_truncation_is_explicit(sample_repo):
    repo, base, head = sample_repo
    spec = RepositorySpec(path=repo, base=base, head=head)

    evidence = collect_git_evidence(spec, Limits(max_patch_bytes=32))

    assert evidence.patch_truncated is True
    assert "PATCH TRUNCATED" in evidence.patch_excerpt


def test_reads_multiple_immutable_blobs_in_one_batch(sample_repo):
    repo, _, head = sample_repo

    blobs = read_git_blobs(repo, head, ["app.py", "feature.py"], 15)

    assert set(blobs) == {"app.py", "feature.py"}
    assert b"greeting(name" in blobs["app.py"]
    assert blobs["feature.py"] == b"ENABLED = True\n"
