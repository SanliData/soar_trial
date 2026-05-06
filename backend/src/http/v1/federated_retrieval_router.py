"""
ROUTER: federated_retrieval_router
PURPOSE: HTTP facade for federated retrieval fabric (H-045)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

from src.federated_retrieval.connector_registry_service import export_connector_registry
from src.federated_retrieval.federated_search_service import federated_search
from src.federated_retrieval.incremental_sync_service import export_incremental_sync_status
from src.federated_retrieval.retrieval_observability_service import export_retrieval_observability
from src.federated_retrieval.source_lineage_service import build_source_lineage

router = APIRouter(tags=["federated-retrieval"])


def _envelope(payload: Dict[str, Any]) -> Dict[str, Any]:
    merged: Dict[str, Any] = {
        "federated_retrieval_foundation": True,
        "connector_execution_enabled": False,
        "uncontrolled_retrieval_expansion": False,
        "lineage_required": True,
    }
    merged.update(payload)
    return merged


@router.get("/system/retrieval/connectors")
async def get_connectors() -> Dict[str, Any]:
    return _envelope({"connectors": export_connector_registry()})


@router.get("/system/retrieval/sync")
async def get_sync_status() -> Dict[str, Any]:
    return _envelope({"sync": export_incremental_sync_status()})


@router.get("/system/retrieval/search")
async def get_search() -> Dict[str, Any]:
    return _envelope({"search": federated_search(query="telecom bid", mode="hybrid", limit=5)})


@router.get("/system/retrieval/lineage")
async def get_lineage() -> Dict[str, Any]:
    lineage = build_source_lineage(
        source_name="uploaded_documents",
        source_type="internal_repository",
        original_reference="upload://doc-ud-001",
        authority_score=0.6,
        freshness_days=14,
    )
    return _envelope({"lineage": lineage})


@router.get("/system/retrieval/observability")
async def get_retrieval_observability() -> Dict[str, Any]:
    return _envelope({"observability": export_retrieval_observability()})

