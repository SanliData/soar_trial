"""
MODULE: entity_schema
PURPOSE: Commercial entity and relationship models (H-026)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator

ALLOWED_ENTITY_TYPES: frozenset[str] = frozenset(
    {
        "company",
        "municipality",
        "utility",
        "procurement_project",
        "contractor",
        "infrastructure_asset",
        "opportunity_cluster",
        "market_signal",
    }
)

ALLOWED_RELATIONSHIP_TYPES: frozenset[str] = frozenset(
    {
        "contracts_with",
        "funds_project",
        "operates_in",
        "competes_with",
        "partners_with",
        "related_to",
        "supplies",
        "influences",
    }
)


class CommercialEntity(BaseModel):
    entity_id: str
    entity_type: str
    name: str = Field(..., min_length=1)
    description: str = ""
    geographic_scope: Optional[str] = None
    authority_score: float = Field(..., ge=0.0, le=1.0)
    freshness_days: int = Field(..., ge=0, le=3650)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    tags: list[str] = Field(default_factory=list)

    @field_validator("entity_type")
    @classmethod
    def entity_type_ok(cls, v: str) -> str:
        if v not in ALLOWED_ENTITY_TYPES:
            raise ValueError(f"invalid entity_type: {v}")
        return v


class CommercialRelationship(BaseModel):
    relationship_id: str
    source_entity_id: str
    target_entity_id: str
    relationship_type: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    evidence_sources: list[str] = Field(default_factory=list)
    created_at: datetime

    @field_validator("relationship_type")
    @classmethod
    def rel_type_ok(cls, v: str) -> str:
        if v not in ALLOWED_RELATIONSHIP_TYPES:
            raise ValueError(f"invalid relationship_type: {v}")
        return v


class CreateCommercialEntityRequest(BaseModel):
    entity_type: str
    name: str = Field(..., min_length=1)
    description: str = ""
    geographic_scope: Optional[str] = None
    authority_score: float = Field(..., ge=0.0, le=1.0)
    freshness_days: int = Field(..., ge=0, le=3650)
    metadata: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)


class CreateCommercialRelationshipRequest(BaseModel):
    source_entity_id: str = Field(..., min_length=1)
    target_entity_id: str = Field(..., min_length=1)
    relationship_type: str
    evidence_sources: list[str] = Field(default_factory=list)
