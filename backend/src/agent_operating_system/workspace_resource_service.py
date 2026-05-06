"""
MODULE: workspace_resource_service
PURPOSE: Workspace resource metadata (permission-aware) (H-045)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

RESOURCE_EPOCH = "2026-01-01T00:00:00Z"

RESOURCES: list[dict[str, Any]] = [
    {
        "resource_id": "knowledge_base",
        "resource_type": "knowledge",
        "access_scope": "read_only",
        "created_at": RESOURCE_EPOCH,
    },
    {
        "resource_id": "document_repository",
        "resource_type": "documents",
        "access_scope": "read_only",
        "created_at": RESOURCE_EPOCH,
    },
    {
        "resource_id": "procurement_feed",
        "resource_type": "feed",
        "access_scope": "read_only",
        "created_at": RESOURCE_EPOCH,
    },
    {
        "resource_id": "graph_store",
        "resource_type": "graph",
        "access_scope": "read_only_projection",
        "created_at": RESOURCE_EPOCH,
    },
    {
        "resource_id": "evaluation_registry",
        "resource_type": "governance",
        "access_scope": "read_only",
        "created_at": RESOURCE_EPOCH,
    },
    {
        "resource_id": "capability_gateway",
        "resource_type": "execution_policy",
        "access_scope": "policy_read",
        "created_at": RESOURCE_EPOCH,
    },
]


def export_workspace_resources() -> dict[str, Any]:
    return {
        "resources": list(RESOURCES),
        "metadata_only": True,
        "permission_aware": True,
        "deterministic": True,
    }

"""
MODULE: workspace_resource_service
PURPOSE: Workspace resource metadata (permission-aware) (H-045)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

RESOURCE_EPOCH = "2026-01-01T00:00:00Z"

RESOURCES: list[dict[str, Any]] = [
    {"resource_id": "knowledge_base", "resource_type": "knowledge", "access_scope": "read_only", "created_at": RESOURCE_EPOCH},
    {"resource_id": "document_repository", "resource_type": "documents", "access_scope": "read_only", "created_at": RESOURCE_EPOCH},
    {"resource_id": "procurement_feed", "resource_type": "feed", "access_scope": "read_only", "created_at": RESOURCE_EPOCH},
    {"resource_id": "graph_store", "resource_type": "graph", "access_scope": "read_only_projection", "created_at": RESOURCE_EPOCH},
    {"resource_id": "evaluation_registry", "resource_type": "governance", "access_scope": "read_only", "created_at": RESOURCE_EPOCH},
    {"resource_id": "capability_gateway", "resource_type": "execution_policy", "access_scope": "policy_read", "created_at": RESOURCE_EPOCH},
]


def export_workspace_resources() -> dict[str, Any]:
    return {
        "resources": list(RESOURCES),
        "metadata_only": True,
        "permission_aware": True,
        "deterministic": True,
    }

