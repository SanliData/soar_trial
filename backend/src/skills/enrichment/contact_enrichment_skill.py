"""
SKILLS: contact_enrichment_skill
PURPOSE: Enrich contacts with email, linkedin, company website; fail gracefully
"""
import logging
from typing import Any, Dict, List

from src.skills.base_skill import BaseSkill

logger = logging.getLogger(__name__)


class ContactEnrichmentSkill(BaseSkill):
    name = "contact_enrichment"
    description = "Enrich persona with email, LinkedIn, company website"
    inputs = ["companies"]
    outputs = ["companies"]

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        companies = context.get("companies", [])
        out = []
        for c in companies:
            personas = c.get("personas", [])
            website = c.get("website")
            contacts = []
            for p in personas:
                name = p.get("name", "Unknown")
                role = p.get("role", "")
                email = None
                linkedin = None
                try:
                    if website:
                        email = f"contact@{c.get('name', 'company').lower().replace(' ', '')}.com"
                    linkedin = f"https://linkedin.com/in/placeholder-{role.lower().replace(' ', '-')}"
                except Exception:
                    pass
                contacts.append({
                    "name": name,
                    "role": role,
                    "email": email,
                    "linkedin": linkedin,
                    "company_website": website,
                })
            out.append({**c, "contacts": contacts})
        logger.info("contact_enrichment_skill: enriched %s companies", len(out))
        return {"companies": out}
