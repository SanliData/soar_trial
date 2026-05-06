"""
MODULE: safe_component_projection
PURPOSE: Whitelist-only component projection (no executable injection) (H-048)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.generative_operational_ui.ui_component_registry import ALLOWED_COMPONENT_TYPES
from src.generative_operational_ui.ui_policy_validation import enforce_registry_component_type, reject_executable_payload


def project_safe_component(*, component_type: str, component_id: str, props: dict[str, Any]) -> dict[str, Any]:
    ct = (component_type or "").strip()
    enforce_registry_component_type(ct, ALLOWED_COMPONENT_TYPES)
    out = {
        "component_type": ct,
        "component_id": (component_id or "").strip() or f"{ct}:default",
        "props": {k: v for k, v in (props or {}).items() if k not in {"raw_html", "raw_js", "executable_payload"}},
        "sanitized": True,
        "deterministic": True,
        "executable_payload": False,
    }
    reject_executable_payload(out)
    return out

