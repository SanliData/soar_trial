"""
MODULE: knowledge_block_schema
PURPOSE: Structured knowledge block models for commercial intelligence ingestion (H-024)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

ALLOWED_BLOCK_TYPES: frozenset[str] = frozenset(
    {
        "opportunity_signal",
        "procurement_notice",
        "market_signal",
        "executive_summary",
        "graph_relationship",
        "exposure_pattern",
        "onboarding_guidance",
    }
)


class SourceLineage(BaseModel):
    """Provenance for audit and authority scoring."""

    source_type: str = Field(..., description="Registered ingestion source key.")
    source_record_id: str = Field(..., min_length=1)
    parent_document_id: Optional[str] = None


class KnowledgeBlock(BaseModel):
    """Semantic intelligence unit with governance metadata."""

    block_id: str
    block_type: str
    title: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    authority_score: float = Field(..., ge=0.0, le=1.0)
    freshness_days: int = Field(..., ge=0)
    geographic_scope: Optional[str] = None
    industry: Optional[str] = None
    commercial_relevance: float = Field(..., ge=0.0, le=1.0)
    source_lineage: SourceLineage
    created_at: datetime
    tags: list[str] = Field(default_factory=list)

    @field_validator("block_type")
    @classmethod
    def block_type_ok(cls, v: str) -> str:
        if v not in ALLOWED_BLOCK_TYPES:
            raise ValueError(f"invalid block_type: {v}")
        return v


class CreateKnowledgeBlockRequest(BaseModel):
    """Inbound payload for deterministic ingestion (no scraping execution)."""

    block_type: str
    title: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    source_lineage: SourceLineage
    freshness_days: int = Field(..., ge=0)
    geographic_scope: Optional[str] = None
    industry: Optional[str] = None
    commercial_relevance: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    tags: list[str] = Field(default_factory=list)
