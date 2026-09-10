from __future__ import annotations

import json
import os
import sys
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from .models import canonical_json_bytes


class ProgressRecorder:
    """Durable, machine-readable progress for long local analysis runs."""

    def __init__(self, output_dir: Path, operation: str, sample_id: str) -> None:
        self.path = output_dir / "run-receipt.json"
        self._started = time.perf_counter()
        self._active_stage: dict[str, Any] | None = None
        self.value: dict[str, Any] = {
            "schema_version": "change-passport.run-receipt.v1",
            "operation": operation,
            "sample_id": sample_id,
            "status": "running",
            "started_at": _now(),
            "finished_at": None,
            "elapsed_seconds": 0.0,
            "stages": [],
            "latest_progress": None,
        }
        output_dir.mkdir(parents=True, exist_ok=True)
        self._persist()

    def _persist(self) -> None:
        self.value["elapsed_seconds"] = round(time.perf_counter() - self._started, 3)
        temporary = self.path.with_name(self.path.name + ".tmp")
        temporary.write_bytes(canonical_json_bytes(self.value) + b"\n")
        os.replace(temporary, self.path)

    def _emit(self, event: str, **fields: Any) -> None:
        print(
            json.dumps(
                {"progress": event, "sample_id": self.value["sample_id"], **fields},
                ensure_ascii=False,
                separators=(",", ":"),
            ),
            file=sys.stderr,
            flush=True,
        )

    @contextmanager
    def stage(self, name: str, label: str) -> Iterator[dict[str, Any]]:
        started = time.perf_counter()
        item: dict[str, Any] = {
            "name": name,
            "label": label,
            "status": "running",
            "started_at": _now(),
            "finished_at": None,
            "duration_seconds": None,
            "details": {},
        }
        self.value["stages"].append(item)
        self._active_stage = item
        self._persist()
        self._emit("stage_started", stage=name, label=label)
        try:
            yield item["details"]
        except BaseException as exc:
            item["status"] = "failed"
            item["error_type"] = type(exc).__name__
            raise
        else:
            item["status"] = "succeeded"
        finally:
            item["finished_at"] = _now()
            item["duration_seconds"] = round(time.perf_counter() - started, 3)
            self._active_stage = None
            self._persist()
            self._emit(
                "stage_finished",
                stage=name,
                status=item["status"],
                duration_seconds=item["duration_seconds"],
            )

    def update(self, current: int, total: int, message: str, **details: Any) -> None:
        stage = self._active_stage["name"] if self._active_stage else None
        progress = {
            "stage": stage,
            "current": current,
            "total": total,
            "percent": round((current / total) * 100, 1) if total else 100.0,
            "message": message,
            "details": details,
        }
        self.value["latest_progress"] = progress
        self._persist()
        self._emit("stage_progress", **progress)

    def finish(self, *, status: str, error: BaseException | None = None) -> None:
        self.value["status"] = status
        self.value["finished_at"] = _now()
        if error is not None:
            self.value["error"] = {
                "type": type(error).__name__,
                "message": str(error),
            }
        self._persist()
        self._emit("run_finished", status=status, elapsed_seconds=self.value["elapsed_seconds"])


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
