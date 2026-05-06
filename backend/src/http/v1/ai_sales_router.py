"""
ROUTER: ai_sales_router
PURPOSE: POST /ai-sales/run-agent — trigger AI Sales Agent workflow (async), return agent_run_id
         Full result: GET /agents/runs/{agent_run_id}
"""
import asyncio
import logging
import uuid
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.agents.workflows.sales_engine_workflow import run_sales_engine_workflow

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai-sales", tags=["ai-sales"])


***REMOVED*** ---------- Example request ----------
***REMOVED*** POST /ai-sales/run-agent
***REMOVED*** {
***REMOVED***   "industry": "fiber infrastructure",
***REMOVED***   "location": "Texas",
***REMOVED***   "target_roles": ["CEO", "CTO", "Procurement Director"],
***REMOVED***   "campaign_goal": "introduce subcontracting services"
***REMOVED*** }


class RunAgentRequest(BaseModel):
    industry: str = Field(..., description="Target industry")
    location: str = Field(..., description="Target location (e.g. Texas)")
    target_roles: List[str] = Field(..., description="Roles to target (e.g. CEO, CTO)")
    campaign_goal: str = Field(..., description="Campaign goal (e.g. introduce subcontracting services)")
    keywords: Optional[List[str]] = Field(None, description="Optional keywords for discovery")
    company_size: Optional[str] = Field(None, description="Optional company size filter")


***REMOVED*** ---------- Example output (full result when workflow completes; from GET /agents/runs/{id} or when polling) ----------
***REMOVED*** {
***REMOVED***   "companies_found": 45,
***REMOVED***   "contacts_identified": 132,
***REMOVED***   "emails_generated": 132,
***REMOVED***   "campaign_created": true,
***REMOVED***   "agent_run_id": "run_12345"
***REMOVED*** }


class RunAgentResponse(BaseModel):
    agent_run_id: str = Field(..., description="Run id; poll GET /agents/runs/{agent_run_id} for full result")
    message: str = Field(default="Workflow started. Poll GET /agents/runs/{agent_run_id} for result.")
    poll_url: Optional[str] = Field(None, description="URL to poll for result (relative)")


@router.post("/run-agent", response_model=RunAgentResponse)
async def post_run_agent(request: RunAgentRequest):
    """
    Trigger the AI Sales Agent workflow asynchronously (non-blocking).
    Workflow: company_discovery → company_analysis → persona_detection → contact_enrichment
    → email_generation → outreach_queue → campaign_creation.
    Returns immediately with agent_run_id. Full result (companies_found, contacts_identified,
    emails_generated, campaign_created) is stored in the run; poll GET /agents/runs/{agent_run_id}.
    """
    agent_run_id = f"run_{uuid.uuid4().hex[:12]}"
    input_payload = request.model_dump()

    async def run_workflow():
        try:
            await run_sales_engine_workflow(
                agent_run_id=agent_run_id,
                industry=request.industry,
                location=request.location,
                target_roles=request.target_roles,
                campaign_goal=request.campaign_goal,
                keywords=request.keywords,
                company_size=request.company_size,
                input_payload=input_payload,
            )
        except Exception as e:
            logger.exception("ai_sales run_agent workflow failed run_id=%s: %s", agent_run_id, e)

    asyncio.create_task(run_workflow())

    return RunAgentResponse(
        agent_run_id=agent_run_id,
        message="Workflow started. Poll GET /agents/runs/{agent_run_id} for result.",
        poll_url=f"/agents/runs/{agent_run_id}",
    )
