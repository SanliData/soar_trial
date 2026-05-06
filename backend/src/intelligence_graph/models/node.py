"""
INTELLIGENCE_GRAPH: semantic node model
PURPOSE: Entity nodes in the relational intelligence graph (company, contact, industry, campaign, message, geography)
"""
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class NodeType(str, Enum):
    company = "company"
    contact = "contact"
    industry = "industry"
    campaign = "campaign"
    message = "message"
    geography = "geography"
    engagement = "engagement"


class Node(BaseModel):
    """Semantic node in the intelligence graph."""
    id: str = Field(..., description="Unique node id (e.g. company_123)")
    type: NodeType = Field(..., description="Entity type")
    label: Optional[str] = Field(None, description="Display label")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Attributes (industry, location, etc.)")
