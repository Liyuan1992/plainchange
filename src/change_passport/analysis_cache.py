from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Any, Iterable, Mapping

from .models import canonical_json_bytes, sha256_bytes


PARSER_CACHE_VERSION = "static-module-parser.v1"


def default_cache_root() -> Path:
    configured = os.environ.get("CHANGE_PASSPORT_CACHE_DIR")
    if configured:
        return Path(configured).expanduser().resolve(strict=False)
    external = Path("E:/DevCache")
    if external.is_dir():
        return external / "change-passport"
    return Path.home() / ".cache" / "change-passport"


def cache_key(path: str, object_id: str) -> str:
    return sha256_bytes(f"{PARSER_CACHE_VERSION}\0{path}\0{object_id}".encode("utf-8"))


class AnalysisCache:
    """Content-addressed parse cache; values contain no commit-specific claims."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = (root or default_cache_root()).resolve(strict=False)
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / "analysis-cache.sqlite3"
        self.connection = sqlite3.connect(self.path, timeout=30)
        self.connection.execute("PRAGMA journal_mode=WAL")
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS parsed_modules (
                cache_key TEXT PRIMARY KEY,
                parser_version TEXT NOT NULL,
                path TEXT NOT NULL,
                object_id TEXT NOT NULL,
                payload_json BLOB NOT NULL
            )
            """
        )

    def close(self) -> None:
        self.connection.close()

    def get_many(self, identities: Iterable[tuple[str, str]]) -> dict[str, dict[str, Any]]:
        pairs = list(identities)
        if not pairs:
            return {}
        keys = [cache_key(path, object_id) for path, object_id in pairs]
        result: dict[str, dict[str, Any]] = {}
        chunk_size = 800
        for index in range(0, len(keys), chunk_size):
            chunk = keys[index : index + chunk_size]
            placeholders = ",".join("?" for _ in chunk)
            rows = self.connection.execute(
                f"SELECT cache_key, payload_json FROM parsed_modules WHERE cache_key IN ({placeholders})",
                chunk,
            )
            for key, raw in rows:
                try:
                    value = json.loads(bytes(raw).decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError, TypeError):
                    continue
                if isinstance(value, dict):
                    result[str(key)] = value
        return result

    def put_many(self, values: Iterable[tuple[str, str, Mapping[str, Any]]]) -> None:
        rows = [
            (
                cache_key(path, object_id),
                PARSER_CACHE_VERSION,
                path,
                object_id,
                canonical_json_bytes(payload),
            )
            for path, object_id, payload in values
        ]
        if not rows:
            return
        with self.connection:
            self.connection.executemany(
                "INSERT OR REPLACE INTO parsed_modules VALUES (?, ?, ?, ?, ?)",
                rows,
            )
