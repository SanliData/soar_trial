"""
AGENTS: campaign_creation skill
PURPOSE: Persist companies/contacts to IntelCompany/IntelContact, create IntelCampaign, push to Redis for automation
"""
import json
import logging
import time
import uuid
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def _get_redis():
    try:
        from src.core.cache import get_redis_client
        return get_redis_client()
    except Exception:
        return None


def _get_db():
    from src.db.base import SessionLocal
    return SessionLocal()


async def run_campaign_creation(
    companies: List[Dict[str, Any]],
    campaign_goal: str,
    agent_run_id: str,
) -> Dict[str, Any]:
    """
    Persist workflow output to intelligence graph and create campaign.
    - Insert/update IntelCompany per company
    - Insert IntelContact per contact (with company_id, outreach_subject, outreach_body)
    - Create IntelCampaign (campaign_id, agent_run_id, status=active, goal, payload)
    - Push campaign to Redis for automation engine
    Returns { "companies": companies, "campaign_created": bool, "campaign_id", "companies_stored", "contacts_stored", "latency_ms" }
    """
    logger.info("agent skill: campaign_creation start companies=%s run_id=%s", len(companies), agent_run_id)
    start = time.perf_counter()
    campaign_id = f"camp_{uuid.uuid4().hex[:12]}"
    db = _get_db()
    companies_stored = 0
    contacts_stored = 0
    try:
        from src.models.intel_company import IntelCompany
        from src.models.intel_contact import IntelContact
        from src.models.intel_campaign import IntelCampaign

        for c in companies:
            name = c.get("name") or c.get("company_name") or "Unknown"
            comp = IntelCompany(
                company_name=name,
                website=c.get("website"),
                industry=c.get("industry"),
                location=c.get("location"),
                technologies=c.get("technologies"),
                description=(c.get("insight") or {}).get("what_company_does") or c.get("description"),
                agent_run_id=agent_run_id,
            )
            db.add(comp)
            db.flush()
            companies_stored += 1
            for contact in c.get("contacts", []):
                db.add(IntelContact(
                    company_id=comp.id,
                    name=contact.get("name", ""),
                    role=contact.get("role"),
                    linkedin_url=contact.get("linkedin") or contact.get("linkedin_url"),
                    email=contact.get("email"),
                    outreach_subject=contact.get("outreach_subject"),
                    outreach_body=contact.get("outreach_body") or contact.get("generated_email"),
                    agent_run_id=agent_run_id,
                ))
                contacts_stored += 1
        campaign = IntelCampaign(
            campaign_id=campaign_id,
            agent_run_id=agent_run_id,
            status="active",
            goal=campaign_goal,
            payload={"companies_count": companies_stored, "contacts_count": contacts_stored},
        )
        db.add(campaign)
        db.commit()
        campaign_created = True
    except Exception as e:
        logger.exception("campaign_creation DB failed: %s", e)
        db.rollback()
        campaign_created = False
        campaign_id = None
    finally:
        db.close()

    redis = _get_redis()
    if redis and campaign_created:
        try:
            payload = {"campaign_id": campaign_id, "agent_run_id": agent_run_id, "goal": campaign_goal, "companies": companies}
            redis.setex(f"automation:campaign:{campaign_id}", 86400 * 7, json.dumps(payload))
            redis.lpush("automation:campaign:queue", campaign_id)
        except Exception as e:
            logger.warning("campaign_creation Redis push failed: %s", e)

    latency_ms = int((time.perf_counter() - start) * 1000)
    logger.info("agent skill: campaign_creation done campaign_created=%s companies=%s contacts=%s", campaign_created, companies_stored, contacts_stored)
    return {
        "companies": companies,
        "campaign_created": campaign_created,
        "campaign_id": campaign_id,
        "companies_stored": companies_stored,
        "contacts_stored": contacts_stored,
        "latency_ms": latency_ms,
    }
