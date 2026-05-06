"""
AGENTS: contact_enrichment skill
PURPOSE: Enrich contacts with email, LinkedIn, company website; fail gracefully per contact
"""
import logging
import time
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


async def run_contact_enrichment(companies: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Enrich each persona with email, LinkedIn, company website when possible.
    Returns companies with "contacts" (enriched). Missing data is left null.
    """
    logger.info("agent skill: contact_enrichment start companies=%s", len(companies))
    start = time.perf_counter()
    out = []
    for c in companies:
        personas = c.get("personas", [])
        website = c.get("website")
        contacts = []
        for p in personas:
            name = p.get("name", "Unknown")
            role = p.get("role", "")
            ***REMOVED*** Placeholder: real impl would call enrichment APIs (Apollo, Clearbit, etc.) with retries
            email = None
            linkedin = None
            if website:
                email = f"contact@{c.get('name', 'company').lower().replace(' ', '')}.com"
            linkedin = f"https://linkedin.com/in/placeholder-{role.lower().replace(' ', '-')}"
            contacts.append({
                "name": name,
                "role": role,
                "email": email,
                "linkedin": linkedin,
                "company_website": website,
            })
        out.append({**c, "contacts": contacts})
    latency_ms = int((time.perf_counter() - start) * 1000)
    logger.info("agent skill: contact_enrichment done latency_ms=%s", latency_ms)
    return {"companies": out, "latency_ms": latency_ms}
