"""
ROUTER: runtime_clustering_router
PURPOSE: HTTP facade for runtime clustering abstractions (H-042)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

from src.runtime_clustering.dynamic_index_grouping_service import export_dynamic_index_grouping_manifest
from src.runtime_clustering.embedding_cluster_service import export_embedding_cluster_manifest
from src.runtime_clustering.retrieval_partition_service import export_retrieval_partition_manifest
from src.runtime_clustering.semantic_batching_service import export_semantic_batching_manifest

router = APIRouter(tags=["runtime-clustering"])


def _envelope(payload: Dict[str, Any]) -> Dict[str, Any]:
    merged: Dict[str, Any] = {
        "runtime_clustering_foundation": True,
        "giant_clustering_infra_required": False,
        "unbounded_semantic_partitions": False,
    }
    merged.update(payload)
    return merged


@router.get("/system/clustering/groups")
async def get_cluster_groups() -> Dict[str, Any]:
    return _envelope(
        {
            "embedding_clusters": export_embedding_cluster_manifest(),
            "retrieval_partitions": export_retrieval_partition_manifest(),
            "dynamic_index_groups": export_dynamic_index_grouping_manifest(),
        }
    )


@router.get("/system/clustering/semantic-batches")
async def get_semantic_batches() -> Dict[str, Any]:
    return _envelope({"semantic_batches": export_semantic_batching_manifest()})
