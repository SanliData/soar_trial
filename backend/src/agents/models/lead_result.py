"""
AGENTS: lead_result models
PURPOSE: Structured output for lead generation workflow
"""
from typing import List, Optional

from pydantic import BaseModel, Field


class ContactResult(BaseModel):
    """Enriched contact with optional generated email."""

    name: str = Field(..., description="Full name or title")
    role: str = Field(..., description="Job role (e.g. CTO, Director)")
    email: Optional[str] = Field(None, description="Email if found")
    linkedin: Optional[str] = Field(None, description="LinkedIn profile URL if found")
    generated_email: Optional[str] = Field(None, description="AI-generated outreach email body")


class CompanyResult(BaseModel):
    """Company with contacts and optional website."""

    company: str = Field(..., description="Company name")
    website: Optional[str] = Field(None, description="Company website URL")
    contacts: List[ContactResult] = Field(default_factory=list, description="Decision makers / contacts")


class LeadGenerationResponse(BaseModel):
    """Response for lead-generation workflow."""

    companies: List[CompanyResult] = Field(default_factory=list, description="Discovered companies with contacts")
    job_id: Optional[str] = Field(None, description="Job ID when run async")
    status: Optional[str] = Field(None, description="Status when polled (pending/running/completed/failed)")
    error: Optional[str] = Field(None, description="Error message if failed")
