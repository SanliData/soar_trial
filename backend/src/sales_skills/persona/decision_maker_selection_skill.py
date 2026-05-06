"""
SALES_SKILLS: decision_maker_selection_skill
PURPOSE: Select or rank decision-maker contacts for companies (roles: CEO, CTO, etc.)
"""
import logging
from typing import Any, Dict, List

from src.sales_skills.base_skill import BaseSkill

logger = logging.getLogger(__name__)

DEFAULT_TARGET_ROLES = ["CEO", "CTO", "Founder", "Procurement Director", "VP Operations"]


class DecisionMakerSelectionSkill(BaseSkill):
    name = "decision_maker_selection"
    description = "Select or rank decision-maker contacts per company by target roles"
    inputs = ["companies", "target_roles"]
    outputs = ["companies_with_contacts", "selected_contacts"]

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        companies = context.get("companies", [])
        target_roles = context.get("target_roles") or DEFAULT_TARGET_ROLES
        companies_with_contacts: List[Dict[str, Any]] = []
        selected_contacts: List[Dict[str, Any]] = []
        try:
            from src.db.base import SessionLocal
            from src.models.intel_company import IntelCompany
            from src.models.intel_contact import IntelContact
            db = SessionLocal()
            try:
                for c in companies:
                    company_id = c.get("id") if isinstance(c.get("id"), int) else None
                    name = c.get("name") or c.get("company_name")
                    if not company_id and name:
                        rec = db.query(IntelCompany).filter(IntelCompany.company_name.ilike(f"%{name}%")).first()
                        company_id = rec.id if rec else None
                    contacts: List[Dict[str, Any]] = []
                    if company_id:
                        rows = db.query(IntelContact).filter(IntelContact.company_id == company_id).all()
                        for r in rows:
                            role = (r.role or "").upper()
                            for tr in target_roles:
                                if tr.upper() in role or role in tr.upper():
                                    contacts.append({
                                        "id": r.id,
                                        "name": r.name,
                                        "role": r.role,
                                        "email": r.email,
                                        "company_id": company_id,
                                    })
                                    selected_contacts.append({"company": name, "name": r.name, "role": r.role})
                                    break
                    companies_with_contacts.append({**c, "selected_contacts": contacts})
            finally:
                db.close()
        except Exception as e:
            logger.debug("decision_maker_selection: %s", e)
        if not companies_with_contacts:
            for c in companies:
                companies_with_contacts.append({
                    **c,
                    "selected_contacts": [{"name": f"{r} (placeholder)", "role": r} for r in target_roles[:3]],
                })
        logger.info("decision_maker_selection: %s companies, %s contacts", len(companies_with_contacts), len(selected_contacts))
        return {"companies_with_contacts": companies_with_contacts, "selected_contacts": selected_contacts}
