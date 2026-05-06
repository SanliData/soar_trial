"""
TOOLS: enrichment_tool
PURPOSE: MCP-ready contact/company enrichment — run(input) -> dict
"""
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def run(input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enrich contact or company: email, linkedin, website. MCP-ready interface.
    Later can delegate to Apollo, Clearbit, or MCP enrichment server.
    """
    entity_type = input.get("entity_type", "contact")
    name = input.get("name", "")
    company = input.get("company", "")
    role = input.get("role", "")
    if entity_type == "company":
        return {
            "company_name": company or name,
            "website": f"https://{ (company or name).lower().replace(' ', '') }.com",
            "industry": input.get("industry", ""),
            "enriched": True,
        }
    email = f"contact@{ (company or 'company').lower().replace(' ', '') }.com" if company or name else None
    linkedin = f"https://linkedin.com/in/{ (name or role or 'user').lower().replace(' ', '-') }" if name or role else None
    logger.info("enrichment_tool: entity_type=%s name=%s -> email=%s", entity_type, name, bool(email))
    return {"name": name, "role": role, "email": email, "linkedin": linkedin, "company": company, "enriched": True}
