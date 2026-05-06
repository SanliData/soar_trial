"""
AGENTS: lead model
PURPOSE: Pydantic model for sales engine lead (company + contacts + outreach)
"""
from typing import List, Optional

from pydantic import BaseModel, Field

from src.agents.models.contact import Contact
from src.agents.models.outreach_email import OutreachEmail


class CompanyContext(BaseModel):
    """Company discovery result."""

    name: str = Field(..., description="Company name")
    website: Optional[str] = Field(None, description="Company website")
    location: Optional[str] = Field(None, description="Location")
    industry: Optional[str] = Field(None, description="Industry")
    company_size: Optional[str] = Field(None, description="e.g. 1-10, 11-50")


class CompanyInsight(BaseModel):
    """LLM-generated company analysis."""

    what_company_does: Optional[str] = Field(None, description="What the company does")
    pain_points: Optional[str] = Field(None, description="Potential pain points")
    outreach_relevance: Optional[str] = Field(None, description="Why outreach is relevant")


class Lead(BaseModel):
    """Full lead: company + contacts + generated email."""

    company: CompanyContext = Field(..., description="Company context")
    company_insight: Optional[CompanyInsight] = Field(None, description="LLM analysis")
    contacts: List[Contact] = Field(default_factory=list, description="Decision makers")
    outreach_email: Optional[OutreachEmail] = Field(None, description="Generated outreach email")
