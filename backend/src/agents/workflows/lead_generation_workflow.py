"""
AGENTS: lead_generation_workflow
PURPOSE: Run company_discovery -> persona_extraction -> lead_enrichment -> email_generation
"""
import logging
from typing import Any, Dict, List, Optional

from src.agents.skills.company_discovery import run_company_discovery
from src.agents.skills.persona_extraction import run_persona_extraction
from src.agents.skills.lead_enrichment import run_lead_enrichment
from src.agents.skills.email_generation import run_email_generation

logger = logging.getLogger(__name__)


async def run_lead_generation_workflow(
    industry: str,
    location: str,
    decision_roles: List[str],
    keywords: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Execute: company_discovery -> persona_extraction -> lead_enrichment -> email_generation.
    Each step returns structured data; failures in enrichment/email are handled gracefully.
    """
    keywords = keywords or []
    logger.info("workflow: lead_generation start industry=%s location=%s roles=%s", industry, location, decision_roles)

    step1 = await run_company_discovery(industry=industry, location=location, keywords=keywords)
    companies = step1.get("companies", [])
    if not companies:
        logger.warning("workflow: no companies from discovery")
        return {"companies": []}

    step2 = await run_persona_extraction(companies=companies, decision_roles=decision_roles)
    companies_with_personas = step2.get("companies", [])

    step3 = await run_lead_enrichment(companies=companies_with_personas)
    companies_enriched = step3.get("companies", [])

    step4 = await run_email_generation(
        companies=companies_enriched,
        context={"industry": industry, "location": location},
    )
    final = step4.get("companies", [])

    logger.info("workflow: lead_generation done companies=%s", len(final))
    return {"companies": final}
