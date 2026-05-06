"""
MODULE: widget_validation_service
PURPOSE: Validate widget payloads before rendering (H-025)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import re
from typing import Any

from src.intelligence_widgets.widget_contracts import (
    ALLOWED_VISUALIZATION_TYPES,
    ALLOWED_WIDGET_TYPES,
    IntelligenceWidget,
    WidgetRenderRequest,
)
from src.intelligence_widgets.widget_registry import WIDGET_VISUALIZATION_ALLOWLIST


_SCRIPT_PATTERN = re.compile(r"(?i)<\s*script\b")
_INLINE_EVENT_PATTERN = re.compile(r"(?i)\bon\w+\s*=")


def _scan_object_for_script_like_strings(obj: Any, path: str = "") -> None:
    if isinstance(obj, str):
        if _SCRIPT_PATTERN.search(obj) or _INLINE_EVENT_PATTERN.search(obj):
            raise ValueError(f"unsafe pattern in data at {path or 'root'}")
        return
    if isinstance(obj, dict):
        for k, v in obj.items():
            _scan_object_for_script_like_strings(k, f"{path}.{k}[key]")
            _scan_object_for_script_like_strings(v, f"{path}.{k}")
        return
    if isinstance(obj, list):
        for i, v in enumerate(obj):
            _scan_object_for_script_like_strings(v, f"{path}[{i}]")


def validate_render_request(body: WidgetRenderRequest) -> None:
    if body.widget_type not in ALLOWED_WIDGET_TYPES:
        raise ValueError(f"invalid widget_type: {body.widget_type}")
    if body.visualization_type not in ALLOWED_VISUALIZATION_TYPES:
        raise ValueError(f"invalid visualization_type: {body.visualization_type}")
    allowed_viz = WIDGET_VISUALIZATION_ALLOWLIST.get(body.widget_type, frozenset())
    if body.visualization_type not in allowed_viz:
        raise ValueError(
            f"visualization_type {body.visualization_type} not allowed for widget_type {body.widget_type}"
        )
    _scan_object_for_script_like_strings(body.data)


def validate_intelligence_widget(widget: IntelligenceWidget) -> None:
    validate_render_request(
        WidgetRenderRequest(
            widget_type=widget.widget_type,
            title=widget.title,
            description=widget.description,
            authority_level=widget.authority_level,
            freshness_days=widget.freshness_days,
            interactive=widget.interactive,
            visualization_type=widget.visualization_type,
            data=widget.data,
            tags=widget.tags,
        )
    )
