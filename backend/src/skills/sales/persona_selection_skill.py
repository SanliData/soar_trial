import logging
from typing import Any, Dict
from src.skills.base_skill import BaseSkill

logger = logging.getLogger(__name__)


class PersonaSelectionSkill(BaseSkill):
    name = "persona_selection_skill"
    description = "Select target personas per company"
    inputs = ["companies", "target_roles"]
    outputs = ["companies", "selected_contacts"]

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        companies = context.get("companies", [])
        roles = context.get("target_roles") or ["CEO", "CTO"]
        selected = []
        try:
            from src.db.base import SessionLocal
            from src.models.intel_contact import IntelContact
            db = SessionLocal()
            try:
                for c in companies:
                    for r in db.query(IntelContact).filter(IntelContact.company_id == c.get("id")).all():
                        if any((ro or "").upper() in (r.role or "").upper() for ro in roles):
                            selected.append({"company_id": c.get("id"), "contact_id": r.id, "name": r.name, "role": r.role})
            finally:
                db.close()
        except Exception as e:
            logger.exception("persona_selection_skill: %s", e)
        return {"companies": companies, "selected_contacts": selected}
