import logging
from typing import Any, Dict
from src.skills.base_skill import BaseSkill

logger = logging.getLogger(__name__)


class ContactEnrichmentSalesSkill(BaseSkill):
    name = "contact_enrichment_skill"
    description = "Enrich contact data"
    inputs = ["companies", "selected_contacts"]
    outputs = ["companies", "enriched_contacts"]

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        contacts = context.get("selected_contacts", [])
        return {"companies": context.get("companies", []), "enriched_contacts": list(contacts)}
