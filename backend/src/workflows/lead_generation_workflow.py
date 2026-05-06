"""
WORKFLOWS: lead_generation_workflow (skill-first)
PURPOSE: Pipeline via skill executor: company_discovery -> company_analysis -> company_filter -> decision_maker_detection -> contact_enrichment -> email_generation
"""
import asyncio
import logging
import uuid
from typing import Any, Dict, List, Optional

from src.skills.bootstrap import bootstrap_skills
from src.skills.skill_executor import run_pipeline

logger = logging.getLogger(__name__)

LEAD_PIPELINE = [
    "company_discovery",
    "company_analysis",
    "company_filter",
    "decision_maker_detection",
    "contact_enrichment",
    "email_generation",
]


async def run_lead_generation_workflow(
    industry: str,
    location: str,
    campaign_goal: str,
    keywords: Optional[List[str]] = None,
    target_roles: Optional[List[str]] = None,
    company_size: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Run the lead-generation pipeline using the skill executor.
    Returns context with companies_found, contacts_identified, emails_generated (and run_id).
    """
    bootstrap_skills()
    initial_context = {
        "industry": industry,
        "location": location,
        "campaign_goal": campaign_goal,
        "keywords": keywords or [],
        "target_roles": target_roles,
        "company_size": company_size,
    }
    workflow_id = f"wf_lead_{uuid.uuid4().hex[:12]}"
    context = await run_pipeline(LEAD_PIPELINE, initial_context, workflow_id=workflow_id)
    companies = context.get("companies", [])
    contacts_count = sum(len(c.get("contacts", [])) for c in companies)
    emails_count = contacts_count  ***REMOVED*** one email per contact
    return {
        "companies_found": len(companies),
        "contacts_identified": contacts_count,
        "emails_generated": emails_count,
        "companies": companies,
        "run_id": context.get("run_id"),
        "workflow_id": workflow_id,
    }


def run_lead_generation_workflow_async(
    industry: str,
    location: str,
    campaign_goal: str,
    keywords: Optional[List[str]] = None,
    target_roles: Optional[List[str]] = None,
    company_size: Optional[str] = None,
) -> asyncio.Task:
    """Start workflow in background; returns asyncio Task (do not block FastAPI)."""
    return asyncio.create_task(
        run_lead_generation_workflow(
            industry=industry,
            location=location,
            campaign_goal=campaign_goal,
            keywords=keywords,
            target_roles=target_roles,
            company_size=company_size,
        )
    )
