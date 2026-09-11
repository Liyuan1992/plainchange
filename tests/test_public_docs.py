from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_public_readmes_have_reciprocal_language_navigation_and_matching_boundaries():
    english = (ROOT / "README.md").read_text(encoding="utf-8")
    chinese = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")

    assert "English | [简体中文](README.zh-CN.md)" in english
    assert "[English](README.md) | 简体中文" in chinese
    assert "PlainChange turns AI-made software changes" in english
    assert "PlainChange 是 AI 生成代码与人类决策之间的理解和控制层" in chinese
    assert "target repository is always read-only" in english
    assert "目标仓库必须保持只读" in chinese
    assert "supports English and Simplified Chinese" in english
    assert "只支持英文和简体中文" in chinese
    assert "Original quotations, code paths, identifiers, and technical evidence remain unchanged" in english
    assert "引用原话、代码路径、标识符和技术证据保留原文" in chinese
    assert "localize-report" in english and "localize-report" in chinese


def test_sdist_manifest_includes_both_public_readmes():
    manifest = (ROOT / "MANIFEST.in").read_text(encoding="utf-8")

    assert "include README.md" in manifest
    assert "include README.zh-CN.md" in manifest
