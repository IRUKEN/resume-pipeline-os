from __future__ import annotations

from pathlib import Path

from .normalize import normalize_text


def read_job_description(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Job description not found: {path}")
    return normalize_text(path.read_text(encoding="utf-8"))
