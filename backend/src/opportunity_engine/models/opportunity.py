"""
OPPORTUNITY_ENGINE: opportunity model
PURPOSE: Pydantic model for a candidate opportunity (company, industry, region, signals)
"""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Opportunity(BaseModel):
    """A detected candidate opportunity."""
    company: str = Field(..., description="Company name")
    company_id: Optional[int] = Field(None, description="Primary key when from DB")
    industry: Optional[str] = Field(None, description="Industry tag")
    region: Optional[str] = Field(None, description="Geography/region")
    signals: List[str] = Field(default_factory=list, description="e.g. hiring_spike, similar_company_response")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Extra: contacts, technology_stack, etc.")
