"""
MODULE: runtime_telemetry_service
PURPOSE: In-memory ring buffer of recent runtime profiles (H-021 foundation)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import List

from src.ai_runtime.runtime_schema import AIRuntimeProfile

_MAX_STORE = 500
_store: list[AIRuntimeProfile] = []


def record_profile(profile: AIRuntimeProfile) -> None:
    _store.append(profile)
    overflow = len(_store) - _MAX_STORE
    if overflow > 0:
        del _store[0:overflow]


def list_recent_profiles(limit: int = 20) -> list[AIRuntimeProfile]:
    if limit < 1:
        limit = 1
    return list(_store[-limit:])


def clear_profiles_for_tests() -> None:
    _store.clear()
