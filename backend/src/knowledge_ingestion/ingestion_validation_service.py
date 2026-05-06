"""
MODULE: ingestion_validation_service
PURPOSE: Validate ranges, lineage, and registry gates before persistence (H-024)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from src.knowledge_ingestion.knowledge_block_schema import (
    ALLOWED_BLOCK_TYPES,
    CreateKnowledgeBlockRequest,
)
from src.knowledge_ingestion.source_registry import require_approved_source


def validate_create_request(body: CreateKnowledgeBlockRequest) -> None:
    if body.block_type not in ALLOWED_BLOCK_TYPES:
        raise ValueError(f"invalid block_type: {body.block_type}")
    require_approved_source(body.source_lineage.source_type)
    if body.commercial_relevance is not None and not (0.0 <= body.commercial_relevance <= 1.0):
        raise ValueError("commercial_relevance must be between 0 and 1")
