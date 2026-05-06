"""
INTELLIGENCE_GRAPH: semantic edge model
PURPOSE: Relationship edges in the relational intelligence graph
"""
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class EdgeType(str, Enum):
    company_has_contact = "company_has_contact"
    contact_replied_to_campaign = "contact_replied_to_campaign"
    campaign_used_template = "campaign_used_template"
    company_belongs_to_industry = "company_belongs_to_industry"
    company_similar_to_company = "company_similar_to_company"
    contact_opened_message = "contact_opened_message"
    contact_replied = "contact_replied"
    company_engaged_with_campaign = "company_engaged_with_campaign"


class Edge(BaseModel):
    """Semantic edge between two nodes."""
    id: Optional[str] = Field(None, description="Optional edge id")
    type: EdgeType = Field(..., description="Relationship type")
    source_id: str = Field(..., description="Source node id")
    target_id: str = Field(..., description="Target node id")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Edge attributes (e.g. reply_rate)")
