from __future__ import annotations

from typing import Any


def require_keys(payload: dict[str, Any], keys: list[str], label: str) -> None:
    missing = [key for key in keys if key not in payload]
    if missing:
        joined = ", ".join(missing)
        raise ValueError(f"{label} missing required keys: {joined}")
