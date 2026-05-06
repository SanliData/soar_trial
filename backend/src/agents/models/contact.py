"""
AGENTS: contact model
PURPOSE: Pydantic model for enriched contact in sales engine
"""
from typing import Optional

from pydantic import BaseModel, Field


class Contact(BaseModel):
    """Enriched contact (decision maker)."""

    name: str = Field(..., description="Full name or title")
    role: str = Field(..., description="Job role (e.g. CEO, CTO, Procurement Director)")
    email: Optional[str] = Field(None, description="Email if found")
    linkedin: Optional[str] = Field(None, description="LinkedIn profile URL")
    company_website: Optional[str] = Field(None, description="Company website")
