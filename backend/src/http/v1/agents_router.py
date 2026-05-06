"""
ROUTER: agents_router
PURPOSE: Autonomous Lead Generation + Sales Engine agents
"""
import json
import logging
import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.agents.models.agent_run import (
    LeadGenerationRequest,
    SalesEngineRunRequest,
    SalesEngineRunResponse,
)
from src.agents.models.lead_result import (
    CompanyResult,
    ContactResult,
    LeadGenerationResponse,
)
from src.agents.workflows.lead_generation_workflow import run_lead_generation_workflow
from src.agents.workflows.sales_engine_workflow import run_sales_engine_workflow
from src.agents.skills.response_classification import run_response_classification
from src.agents.skills.followup_generation import run_followup_generation
from src.db.base import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agents", tags=["agents"])

***REMOVED*** Redis key TTL for job result (1 hour)
AGENTS_JOB_TTL = 3600


def _get_redis():
    try:
        from src.core.cache import get_redis_client
        return get_redis_client()
    except Exception:
        return None


def _companies_to_response(companies: List[Dict[str, Any]]) -> List[CompanyResult]:
    out = []
    for c in companies:
        contacts = [
            ContactResult(
                name=co.get("name", ""),
                role=co.get("role", ""),
                email=co.get("email"),
                linkedin=co.get("linkedin"),
                generated_email=co.get("generated_email"),
            )
            for co in c.get("contacts", [])
        ]
        out.append(
            CompanyResult(
                company=c.get("name", c.get("company", "Unknown")),
                website=c.get("website"),
                contacts=contacts,
            )
        )
    return out


@router.post("/lead-generation", response_model=LeadGenerationResponse)
async def post_lead_generation(request: LeadGenerationRequest):
    """
    Run lead generation workflow: company discovery -> persona extraction
    -> lead enrichment -> email generation. Returns result in response.
    Result is also stored in Redis (when available) for later retrieval by job_id.
    """
    job_id = str(uuid.uuid4())
    redis = _get_redis()

    async def run_and_store():
        try:
            result = await run_lead_generation_workflow(
                industry=request.industry,
                location=request.location,
                decision_roles=request.decision_roles,
                keywords=request.keywords,
            )
            companies = _companies_to_response(result.get("companies", []))
            payload = LeadGenerationResponse(companies=companies, job_id=job_id, status="completed")
            if redis:
                redis.setex(
                    f"agents:job:{job_id}",
                    AGENTS_JOB_TTL,
                    payload.model_dump_json(),
                )
            return payload
        except Exception as e:
            logger.exception("lead_generation workflow failed: %s", e)
            err_payload = LeadGenerationResponse(
                companies=[],
                job_id=job_id,
                status="failed",
                error=str(e),
            )
            if redis:
                redis.setex(
                    f"agents:job:{job_id}",
                    AGENTS_JOB_TTL,
                    err_payload.model_dump_json(),
                )
            return err_payload

    response = await run_and_store()
    if response.status == "failed" and response.error:
        raise HTTPException(status_code=500, detail=response.error)
    return response


@router.get("/lead-generation/jobs/{job_id}", response_model=LeadGenerationResponse)
async def get_lead_generation_job(job_id: str):
    """Poll job result from Redis (when using background queue)."""
    redis = _get_redis()
    if not redis:
        raise HTTPException(status_code=503, detail="Redis not available for job storage")
    raw = redis.get(f"agents:job:{job_id}")
    if not raw:
        raise HTTPException(status_code=404, detail="Job not found or expired")
    try:
        data = json.loads(raw)
        return LeadGenerationResponse(**data)
    except Exception as e:
        logger.warning("Failed to parse job result: %s", e)
        raise HTTPException(status_code=500, detail="Invalid job result")


***REMOVED*** ---------- Sales Engine ----------


@router.post("/sales-engine/run", response_model=SalesEngineRunResponse)
async def post_sales_engine_run(request: SalesEngineRunRequest):
    """
    Run Autonomous Sales Agent: company_discovery -> company_analysis -> persona_detection
    -> contact_enrichment -> email_generation -> outreach_queue. Returns summary.
    """
    agent_run_id = f"run_{uuid.uuid4().hex[:12]}"
    input_payload = request.model_dump()
    try:
        result = await run_sales_engine_workflow(
            agent_run_id=agent_run_id,
            industry=request.industry,
            location=request.location,
            target_roles=request.target_roles,
            campaign_goal=request.campaign_goal,
            keywords=request.keywords,
            company_size=request.company_size,
            input_payload=input_payload,
        )
        if result.get("status") == "failed":
            raise HTTPException(status_code=500, detail=result.get("error", "Workflow failed"))
        return SalesEngineRunResponse(
            companies_found=result.get("companies_found", 0),
            leads_generated=result.get("leads_generated", 0),
            emails_generated=result.get("emails_generated", 0),
            agent_run_id=result.get("agent_run_id", agent_run_id),
            status=result.get("status", "completed"),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("sales_engine run failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/runs")
async def get_agents_runs(
    limit: int = 50,
    workflow_type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List agent runs from PostgreSQL."""
    try:
        from src.models.agent_run_log import AgentRun
        q = db.query(AgentRun).order_by(AgentRun.created_at.desc()).limit(limit)
        if workflow_type:
            q = q.filter(AgentRun.workflow_type == workflow_type)
        runs = q.all()
        return [
            {
                "agent_run_id": r.agent_run_id,
                "workflow_type": r.workflow_type,
                "status": r.status,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in runs
        ]
    except Exception as e:
        logger.warning("get_agents_runs failed: %s", e)
        raise HTTPException(status_code=503, detail="Run storage unavailable")


@router.get("/runs/{run_id}")
async def get_agents_run(run_id: str, db: Session = Depends(get_db)):
    """Get one agent run and its step logs."""
    try:
        from src.models.agent_run_log import AgentRun, AgentRunLog
        run = db.query(AgentRun).filter(AgentRun.agent_run_id == run_id).first()
        if not run:
            raise HTTPException(status_code=404, detail="Run not found")
        logs = db.query(AgentRunLog).filter(AgentRunLog.agent_run_id == run_id).order_by(AgentRunLog.created_at).all()
        return {
            "agent_run_id": run.agent_run_id,
            "workflow_type": run.workflow_type,
            "status": run.status,
            "input_payload": run.input_payload,
            "output_payload": run.output_payload,
            "created_at": run.created_at.isoformat() if run.created_at else None,
            "steps": [
                {
                    "workflow_step": l.workflow_step,
                    "token_usage": l.token_usage,
                    "latency_ms": l.latency_ms,
                    "error_message": l.error_message,
                    "created_at": l.created_at.isoformat() if l.created_at else None,
                }
                for l in logs
            ],
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.warning("get_agents_run failed: %s", e)
        raise HTTPException(status_code=503, detail="Run storage unavailable")


class ClassifyResponseRequest(BaseModel):
    reply_email_body: str = Field(..., description="Reply email body to classify")


class ClassifyResponseResponse(BaseModel):
    classification: str = Field(..., description="positive_interest | neutral | not_now | not_interested")
    reasoning: str = Field(..., description="Short reasoning")
    followup_subject: Optional[str] = Field(None, description="Suggested follow-up subject")
    followup_body: Optional[str] = Field(None, description="Suggested follow-up body")
    suggested_action: Optional[str] = Field(None, description="e.g. Schedule meeting, reminder in 3 weeks")


@router.post("/classify-response", response_model=ClassifyResponseResponse)
async def post_classify_response(request: ClassifyResponseRequest):
    """
    Classify a reply email (positive_interest | neutral | not_now | not_interested) and generate follow-up.
    """
    classification_result = await run_response_classification(request.reply_email_body)
    classification = classification_result.get("classification", "neutral")
    reasoning = classification_result.get("reasoning", "")
    followup = await run_followup_generation(classification, reasoning)
    return ClassifyResponseResponse(
        classification=classification,
        reasoning=reasoning,
        followup_subject=followup.get("subject"),
        followup_body=followup.get("body"),
        suggested_action=followup.get("suggested_action"),
    )


@router.get("/trace/{trace_id}")
async def get_agents_trace(trace_id: str):
    """
    Debug endpoint: GET /agents/trace/{trace_id}.
    Returns execution trace (skill_calls, tool_outputs, decision_steps) from Redis.
    """
    try:
        from src.agents.execution_trace import get_trace
        trace = get_trace(trace_id)
        if not trace:
            raise HTTPException(status_code=404, detail="Trace not found or expired")
        return trace
    except HTTPException:
        raise
    except Exception as e:
        logger.warning("get_agents_trace failed: %s", e)
        raise HTTPException(status_code=503, detail="Trace storage unavailable")


@router.get("/health")
async def agents_health():
    return {"status": "ok", "service": "agents"}
