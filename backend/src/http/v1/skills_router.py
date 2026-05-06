"""
ROUTER: skills_router
PURPOSE: POST /skills/run-lead-workflow — skill-first lead generation (async, non-blocking)
"""
import asyncio
import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.skills.bootstrap import bootstrap_skills
from src.skills.registry import list_skills
from src.workflows.lead_generation_workflow import run_lead_generation_workflow

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/skills", tags=["skills"])


***REMOVED*** ---------- Example request ----------
***REMOVED*** POST /skills/run-lead-workflow
***REMOVED*** {
***REMOVED***   "industry": "fiber infrastructure",
***REMOVED***   "location": "Texas",
***REMOVED***   "campaign_goal": "introduce subcontracting services"
***REMOVED*** }


class RunLeadWorkflowRequest(BaseModel):
    industry: str = Field(..., description="Target industry")
    location: str = Field(..., description="Target location")
    campaign_goal: str = Field(..., description="Campaign goal")
    keywords: Optional[List[str]] = Field(None, description="Optional keywords")
    target_roles: Optional[List[str]] = Field(None, description="Optional roles (default: CEO, CTO, etc.)")
    company_size: Optional[str] = Field(None, description="Optional company size")


***REMOVED*** ---------- Example response ----------
***REMOVED*** {
***REMOVED***   "companies_found": 40,
***REMOVED***   "contacts_identified": 120,
***REMOVED***   "emails_generated": 120
***REMOVED*** }


class RunLeadWorkflowResponse(BaseModel):
    companies_found: int = Field(..., description="Number of companies found")
    contacts_identified: int = Field(..., description="Number of contacts identified")
    emails_generated: int = Field(..., description="Number of emails generated")
    run_id: Optional[str] = Field(None, description="Skill run id for logging")


@router.post("/run-lead-workflow", response_model=RunLeadWorkflowResponse)
async def post_run_lead_workflow(request: RunLeadWorkflowRequest):
    """
    Run the skill-first lead generation pipeline (company_discovery -> company_analysis
    -> decision_maker_detection -> contact_enrichment -> email_generation).
    Executes in the request context but skills are async; for very long runs consider
    moving to a background task and returning run_id for polling.
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
        )
    except Exception as e:
        logger.exception("run-lead-workflow failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def get_skills_list():
    """List all registered skills (name, description, inputs, outputs) for agent workflows."""
    bootstrap_skills()
    return {"skills": list_skills()}
