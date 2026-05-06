"""
AGENTS: lead_enrichment skill
PURPOSE: Enrich leads with website, LinkedIn, email when possible; returns structured JSON
"""
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


async def run_lead_enrichment(
    companies: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Enrich each company/persona with website, LinkedIn, email.
    Returns JSON: same structure with added email/linkedin per persona; fail gracefully per-contact.
    """
    logger.info("agent skill: lead_enrichment start companies=%s", len(companies))
    enriched = []
    for c in companies:
        personas = c.get("personas", [])
        contacts = []
        for p in personas:
            # Placeholder: real impl would call enrichment APIs (Clearbit, Apollo, etc.)
            contacts.append({
                "name": p.get("name", "Unknown"),
                "role": p.get("role", ""),
                "email": f"contact@{c.get('name', 'company').lower().replace(' ', '')}.com" if c.get("website") else None,
                "linkedin": f"https://linkedin.com/in/placeholder-{p.get('role', 'user').lower()}",
            })
        enriched.append({
            "name": c.get("name", "Unknown"),
            "website": c.get("website"),
            "contacts": contacts,
        })
    logger.info("agent skill: lead_enrichment done")
    return {"companies": enriched}
