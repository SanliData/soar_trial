from enum import Enum
from typing import Any, Dict
from pydantic import BaseModel, Field


class NodeType(str, Enum):
    company = "company"
    contact = "contact"
    industry = "industry"
    campaign = "campaign"
    message = "message"
    technology = "technology"
    geography = "geography"


class GraphNode(BaseModel):
    id: str
    type: NodeType
    label: str = ""
    properties: Dict[str, Any] = Field(default_factory=dict)
