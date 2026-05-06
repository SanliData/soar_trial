"""
MODULE: widget_state_service
PURPOSE: Lightweight in-memory widget render audit trail (H-025)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from collections import deque
from typing import Deque

_MAX = 200
_recent_widget_ids: Deque[str] = deque(maxlen=_MAX)


def clear_state_for_tests() -> None:
    _recent_widget_ids.clear()


def record_widget_render(widget_id: str) -> None:
    _recent_widget_ids.append(widget_id)


def recent_widget_ids() -> list[str]:
    return list(_recent_widget_ids)

