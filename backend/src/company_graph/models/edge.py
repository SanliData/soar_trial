from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class EdgeType(str, Enum):
    company_has_contact = "company_has_contact"
    company_belongs_to_industry = "company_belongs_to_industry"
    contact_replied_to_campaign = "contact_replied_to_campaign"
    campaign_used_message = "campaign_used_message"
    company_similar_to_company = "company_similar_to_company"


class GraphEdge(BaseModel):
    id: Optional[str] = None
    type: EdgeType
    source_id: str
    target_id: str
    properties: Dict[str, Any] = Field(default_factory=dict)
