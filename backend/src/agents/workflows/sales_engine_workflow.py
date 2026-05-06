"""
AGENTS: sales_engine_workflow
PURPOSE: company_discovery -> company_analysis -> persona_detection -> contact_enrichment -> email_generation -> outreach_queue
"""
import logging
import time
from typing import Any, Dict, List, Optional

from src.agents.run_logger import log_step, upsert_run
from src.agents.skills.company_discovery import run_company_discovery
from src.agents.skills.company_analysis import run_company_analysis
from src.agents.skills.persona_detection import run_persona_detection
from src.agents.skills.contact_enrichment import run_contact_enrichment
from src.agents.skills.email_generation import run_outreach_email_generation
from src.agents.skills.outreach_queue import run_outreach_queue
from src.agents.skills.campaign_creation import run_campaign_creation
from src.learning.learning_engine import get_targeting_recommendations, get_email_strategy

logger = logging.getLogger(__name__)


async def run_sales_engine_workflow(
    agent_run_id: str,
    industry: str,
    location: str,
    target_roles: List[str],
    campaign_goal: str,
    keywords: Optional[List[str]] = None,
    company_size: Optional[str] = None,
    input_payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Execute full sales engine pipeline; log each step to PostgreSQL.
    Returns summary: companies_found, leads_generated, emails_generated, agent_run_id, status.
    """
    logger.info("workflow: sales_engine start run_id=%s industry=%s location=%s", agent_run_id, industry, location)
    upsert_run(agent_run_id, "sales_engine", "running", input_payload=input_payload)
    t0 = time.perf_counter()
    companies = []

    try:
        ***REMOVED*** 0. Learning: get targeting recommendations (roles, company_size) from past campaigns
        targeting = await get_targeting_recommendations(industry=industry, location=location, roles=target_roles)
        effective_roles = targeting.get("recommended_roles") or target_roles
        effective_company_size = company_size or targeting.get("recommended_company_size")

        ***REMOVED*** 1. company_discovery
        step_start = time.perf_counter()
        step1 = await run_company_discovery(
            industry=industry,
            location=location,
            keywords=keywords,
            company_size=effective_company_size,
        )
        companies = step1.get("companies", [])
        log_step(agent_run_id, "company_discovery", latency_ms=int((time.perf_counter() - step_start) * 1000))
        if not companies:
            logger.warning("workflow: no companies from discovery")
            upsert_run(agent_run_id, "sales_engine", "completed", output_payload={"companies_found": 0, "leads_generated": 0, "emails_generated": 0, "contacts_identified": 0, "campaign_created": False})
            return {"companies_found": 0, "leads_generated": 0, "emails_generated": 0, "contacts_identified": 0, "campaign_created": False, "agent_run_id": agent_run_id, "status": "completed"}

        ***REMOVED*** 2. company_analysis
        step_start = time.perf_counter()
        step2 = await run_company_analysis(companies)
        companies = step2.get("companies", [])
        log_step(
            agent_run_id,
            "company_analysis",
            token_usage=step2.get("token_usage"),
            latency_ms=step2.get("latency_ms") or int((time.perf_counter() - step_start) * 1000),
        )

        ***REMOVED*** 3. persona_detection (use learning-recommended roles)
        step_start = time.perf_counter()
        step3 = await run_persona_detection(companies, effective_roles)
        companies = step3.get("companies", [])
        log_step(
            agent_run_id,
            "persona_detection",
            token_usage=step3.get("token_usage"),
            latency_ms=step3.get("latency_ms") or int((time.perf_counter() - step_start) * 1000),
        )

        ***REMOVED*** 4. contact_enrichment
        step_start = time.perf_counter()
        step4 = await run_contact_enrichment(companies)
        companies = step4.get("companies", [])
        log_step(agent_run_id, "contact_enrichment", latency_ms=step4.get("latency_ms"))

        ***REMOVED*** 5. email_generation (outreach subject + body; use learning email strategy)
        email_strategy = await get_email_strategy(campaign_goal=campaign_goal, industry=industry)
        step_start = time.perf_counter()
        step5 = await run_outreach_email_generation(companies, campaign_goal, email_strategy=email_strategy)
        companies = step5.get("companies", [])
        log_step(
            agent_run_id,
            "email_generation",
            token_usage=step5.get("token_usage"),
            latency_ms=step5.get("latency_ms") or int((time.perf_counter() - step_start) * 1000),
        )

        ***REMOVED*** 6. outreach_queue
        step_start = time.perf_counter()
        step6 = await run_outreach_queue(companies, campaign_goal, agent_run_id)
        companies = step6.get("companies", [])
        log_step(agent_run_id, "outreach_queue", latency_ms=step6.get("latency_ms"))

        ***REMOVED*** 7. campaign_creation (intel graph + automation queue)
        step_start = time.perf_counter()
        step7 = await run_campaign_creation(companies, campaign_goal, agent_run_id)
        companies = step7.get("companies", companies)
        log_step(agent_run_id, "campaign_creation", latency_ms=step7.get("latency_ms"))

        leads = sum(len(c.get("contacts", [])) for c in companies)
        emails = sum(len(c.get("contacts", [])) for c in companies)
        summary = {
            "companies_found": len(companies),
            "leads_generated": leads,
            "emails_generated": emails,
            "contacts_identified": leads,
            "campaign_created": step7.get("campaign_created", False),
            "campaign_id": step7.get("campaign_id"),
            "agent_run_id": agent_run_id,
            "status": "completed",
        }
        upsert_run(agent_run_id, "sales_engine", "completed", output_payload=summary)
        logger.info("workflow: sales_engine done run_id=%s companies=%s leads=%s", agent_run_id, len(companies), leads)
        return summary
    except Exception as e:
        logger.exception("workflow: sales_engine failed run_id=%s error=%s", agent_run_id, e)
        log_step(agent_run_id, "workflow_error", error_message=str(e))
        upsert_run(agent_run_id, "sales_engine", "failed", output_payload={"error": str(e)})
        return {
            "companies_found": 0,
            "leads_generated": 0,
            "emails_generated": 0,
            "contacts_identified": 0,
            "campaign_created": False,
            "agent_run_id": agent_run_id,
            "status": "failed",
            "error": str(e),
        }
