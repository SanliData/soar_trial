"""
MODULE: backend_metadata_service
PURPOSE: Deterministic backend metadata snapshot (H-030)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.config.settings import get_settings
from src.semantic_capabilities.capability_loader import load_capabilities

***REMOVED*** Curated module tags — visibility only, not live filesystem walk.
_ACTIVE_MODULES: tuple[str, ...] = (
    "semantic_capabilities",
    "commercial_graph",
    "knowledge_ingestion",
    "intelligence_widget",
    "prompt_orchestration",
    "trajectory_evaluation",
    "agent_security",
    "runtime_context",
    "context_orchestration",
    "context_compression",
    "context_isolation",
    "document_intelligence",
    "mcp_runtime",
    "agent_operating_system",
    "natural_language_control_plane",
    "federated_retrieval",
    "selective_context_runtime",
)


def build_backend_metadata_snapshot() -> dict[str, Any]:
    settings = get_settings()
    caps = load_capabilities()
    return {
        "active_modules": list(_ACTIVE_MODULES),
        "enabled_capabilities": len(caps),
        "graph_status": "available",
        "ingestion_status": "enabled",
        "security_status": "foundation_active",
        "widget_status": "enabled",
        "orchestration_status": "deterministic_hints_only",
        "runtime_version": (settings.FINDEROS_VERSION or "0.1.0").strip(),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "progressive_context": {
            "recommended_layer_order": ["metadata", "capabilities", "topology", "hints", "context_budget"],
            "default_capability_depth": "summary",
        },
    }
