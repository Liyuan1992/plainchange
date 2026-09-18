"""Bounded retries for Windows readers briefly holding a destination open."""
from __future__ import annotations

import os
import time
from pathlib import Path


def replace_with_retry(source: Path, destination: Path) -> None:
    for attempt in range(6):
        try:
            os.replace(source, destination)
            return
        except PermissionError as exc:
            if getattr(exc, "winerror", None) not in {5, 32, 33} or attempt == 5:
                raise
            time.sleep(.02 * 2 ** attempt)
