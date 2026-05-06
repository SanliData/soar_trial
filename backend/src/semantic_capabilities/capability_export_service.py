"""
MODULE: capability_export_service
PURPOSE: Build sanitized capability catalog payloads for operators and planners (H-020)
ENCODING: UTF-8 WITHOUT BOM

No secrets, runtime env blobs, tokens, connection strings—only declarative semantic metadata.
"""

from typing import Any

from src.config.settings import get_settings
from src.semantic_capabilities.capability_loader import load_capabilities
from src.semantic_capabilities.capability_validation import audit_export_json_for_secret_material
from src.semantic_capability_graph.capability_context_service import build_h020_semantic_graph_extension

_SYSTEM_LABEL = "FinderOS / SOAR B2B"


def build_capabilities_catalog() -> dict[str, Any]:
    """
    Deterministic merged JSON-safe structure for orchestration tooling.
    """
    settings = get_settings()
    version = (settings.FINDEROS_VERSION or "0.1.0").strip() or "0.1.0"
    caps = load_capabilities()
    payload = {
        "system": _SYSTEM_LABEL,
        "version": version,
        "capabilities": [c.model_dump(mode="json") for c in caps],
        "semantic_capability_graph": build_h020_semantic_graph_extension(),
    }
    audit_export_json_for_secret_material(payload)
    return payload
