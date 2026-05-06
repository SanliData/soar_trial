"""
AGENTS: outreach_email model
PURPOSE: Pydantic model for generated outreach email
"""
from typing import Optional

from pydantic import BaseModel, Field


class OutreachEmail(BaseModel):
    """Generated outreach email (subject + body)."""

    subject: str = Field(..., description="Email subject line")
    email_body: str = Field(..., description="Email body (plain text)")
    contact_name: Optional[str] = Field(None, description="Recipient name")
    contact_role: Optional[str] = Field(None, description="Recipient role")
