"""
AGENTS: agent_run models
PURPOSE: Pydantic models for agent run input and status
"""
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class AgentRunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class LeadGenerationRequest(BaseModel):
    """Input for POST /agents/lead-generation."""

    industry: str = Field(..., description="Industry or vertical (e.g. fiber infrastructure)")
    location: str = Field(..., description="Location (e.g. Texas)")
    decision_roles: List[str] = Field(
        default_factory=lambda: ["CEO", "CTO", "Founder", "Procurement", "Director"],
        description="Roles to target (CEO, CTO, Founder, Procurement, Director)",
    )
    keywords: Optional[List[str]] = Field(default=None, description="Optional keywords for company discovery")


class SalesEngineRunRequest(BaseModel):
    """Input for POST /agents/sales-engine/run."""

    industry: str = Field(..., description="Industry (e.g. fiber infrastructure)")
    location: str = Field(..., description="Location (e.g. Texas)")
    target_roles: List[str] = Field(
        default_factory=lambda: ["CEO", "CTO", "Founder", "Procurement Director", "VP Operations"],
        description="Decision maker roles to target",
    )
    campaign_goal: str = Field(
        default="introduce services",
        description="Goal of the outreach campaign (e.g. introduce fiber subcontracting services)",
    )
    keywords: Optional[List[str]] = Field(default=None, description="Optional keywords for company discovery")
    company_size: Optional[str] = Field(default=None, description="Optional company size filter (e.g. 11-50)")


class SalesEngineRunResponse(BaseModel):
    """Output for POST /agents/sales-engine/run."""

    companies_found: int = Field(0, description="Number of companies discovered")
    leads_generated: int = Field(0, description="Number of leads (contacts) generated")
    emails_generated: int = Field(0, description="Number of outreach emails generated")
    agent_run_id: str = Field(..., description="Unique run ID")
    status: str = Field(default="completed", description="Run status")
    error: Optional[str] = Field(None, description="Error message if failed")
