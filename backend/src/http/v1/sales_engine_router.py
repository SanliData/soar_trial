"""
ROUTER: sales_engine_router (Self-Learning AI Sales Engine)
PURPOSE: POST /sales/run-lead-workflow — skill-first pipeline; non-blocking via optional background
"""
import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.skills.bootstrap import bootstrap_skills
from src.workflows.lead_generation_workflow import run_lead_generation_workflow

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sales", tags=["sales-engine"])


# ---------- Example request ----------
# POST /sales/run-lead-workflow
# {
# "industry": "fiber infrastructure",
# "location": "Texas",
# "target_roles": ["CEO","CTO","Procurement Director"],
# "campaign_goal": "introduce subcontracting services"
# }


class RunLeadWorkflowRequest(BaseModel):
    industry: str = Field(..., description="Target industry")
    location: str = Field(..., description="Target location")
    target_roles: List[str] = Field(default_factory=lambda: ["CEO", "CTO", "Procurement Director"])
    campaign_goal: str = Field(..., description="Campaign goal")
    keywords: Optional[List[str]] = None
    company_size: Optional[str] = None


# ---------- Example response ----------
# {
# "companies_found": 40,
# "contacts_identified": 120,
# "emails_generated": 120
# }


class RunLeadWorkflowResponse(BaseModel):
    companies_found: int = Field(..., description="Number of companies found")
    contacts_identified: int = Field(..., description="Number of contacts identified")
    emails_generated: int = Field(..., description="Number of emails generated")
    run_id: Optional[str] = None
    workflow_id: Optional[str] = None


@router.post("/run-lead-workflow", response_model=RunLeadWorkflowResponse)
async def post_run_lead_workflow(request: RunLeadWorkflowRequest):
    """
    Run the skill-first lead generation pipeline:
    company_discovery -> company_analysis -> company_filter -> decision_maker_detection
    -> contact_enrichment -> email_generation.
    Returns structured counts. For very long runs, consider background task + Redis queue.
    """
    bootstrap_skills()
    try:
        result = await run_lead_generation_workflow(
            industry=request.industry,
            location=request.location,
            campaign_goal=request.campaign_goal,
            keywords=request.keywords,
            target_roles=request.target_roles,
            company_size=request.company_size,
        )
        return RunLeadWorkflowResponse(
            companies_found=result.get("companies_found", 0),
            contacts_identified=result.get("contacts_identified", 0),
            emails_generated=result.get("emails_generated", 0),
            run_id=result.get("run_id"),
            workflow_id=result.get("workflow_id"),
        )
    except Exception as e:
        logger.exception("sales run-lead-workflow failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def sales_health():
    return {"status": "ok", "service": "sales-engine"}
