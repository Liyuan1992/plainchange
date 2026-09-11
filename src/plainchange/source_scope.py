from __future__ import annotations

from pathlib import PurePosixPath


SUPPORTED_SOURCE_SUFFIXES = {
    ".py",
    ".js",
    ".jsx",
    ".mjs",
    ".cjs",
    ".ts",
    ".tsx",
    ".vue",
}

# Repository-owned source can still contain vendored dependency or generated
# trees. Their presence in Git does not make them part of the product's own
# architecture. Keep this list ecosystem-neutral and segment based.
IGNORED_SOURCE_SEGMENTS = {
    ".git",
    ".next",
    ".nuxt",
    ".output",
    ".venv",
    "bower_components",
    "coverage",
    "dist",
    "node_modules",
    "site-packages",
    "vendor",
    "vendors",
}


def is_vendored_or_generated_path(path: str) -> bool:
    return any(part.casefold() in IGNORED_SOURCE_SEGMENTS for part in PurePosixPath(path).parts)


def is_supported_source_path(path: str) -> bool:
    return (
        PurePosixPath(path).suffix.casefold() in SUPPORTED_SOURCE_SUFFIXES
        and not is_vendored_or_generated_path(path)
    )
