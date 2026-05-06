"""
LEARNING: performance_analyzer
PURPOSE: analyze_campaign_success, identify_best_industries, identify_best_roles; output top_industries, top_roles, best_email_length, best_subject_style
"""
import json
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def _get_db():
    from src.db.base import SessionLocal
    return SessionLocal()


async def analyze_campaign_success(limit: int = 100) -> Dict[str, Any]:
    """
    Analyze historical campaign metrics and return aggregated insights.
    Returns top_industries, top_roles, best_email_length, best_subject_style (placeholders if no data).
    """
    db = _get_db()
    try:
        from src.learning.models.campaign_metrics import CampaignMetrics
        rows = db.query(CampaignMetrics).order_by(CampaignMetrics.created_at.desc()).limit(limit * 2).all()
    finally:
        db.close()

    ***REMOVED*** Aggregate by industry (reply_rate, positive_rate)
    industry_stats = {}
    role_stats = {}
    for r in rows:
        sent = r.emails_sent or 1
        reply_rate = (r.replies_received or 0) / sent
        pos_rate = (r.positive_responses or 0) / sent
        if r.industry:
            industry_stats[r.industry] = industry_stats.get(r.industry, {"replies": 0, "positive": 0, "sent": 0})
            industry_stats[r.industry]["replies"] += r.replies_received or 0
            industry_stats[r.industry]["positive"] += r.positive_responses or 0
            industry_stats[r.industry]["sent"] += r.emails_sent or 0
        if r.roles_snapshot:
            try:
                roles = json.loads(r.roles_snapshot) if isinstance(r.roles_snapshot, str) else r.roles_snapshot
                if not isinstance(roles, list):
                    roles = [r.roles_snapshot]
                for role in roles:
                    role_stats[role] = role_stats.get(role, {"replies": 0, "positive": 0, "sent": 0})
                    role_stats[role]["replies"] += r.replies_received or 0
                    role_stats[role]["positive"] += r.positive_responses or 0
                    role_stats[role]["sent"] += r.emails_sent or 0
            except Exception:
                pass

    ***REMOVED*** Top industries by positive rate (min 10 sent)
    industry_sorted = [
        (ind, (s["positive"] / s["sent"]) if s["sent"] else 0, s["sent"])
        for ind, s in industry_stats.items()
        if s["sent"] >= 5
    ]
    industry_sorted.sort(key=lambda x: -x[1])
    top_industries = [x[0] for x in industry_sorted[:10]]

    ***REMOVED*** Top roles
    role_sorted = [
        (role, (s["positive"] / s["sent"]) if s["sent"] else 0, s["sent"])
        for role, s in role_stats.items()
        if s["sent"] >= 5
    ]
    role_sorted.sort(key=lambda x: -x[1])
    top_roles = [x[0] for x in role_sorted[:10]]

    return {
        "top_industries": top_industries or ["fiber infrastructure", "construction"],
        "top_roles": top_roles or ["CTO", "Procurement Director"],
        "best_email_length": "short",
        "best_subject_style": "problem-solution",
        "campaigns_analyzed": len(rows),
    }


async def identify_best_industries(limit: int = 50) -> List[str]:
    """Return industries with highest positive_interest_rate (min volume)."""
    result = await analyze_campaign_success(limit=limit)
    return result.get("top_industries", [])


async def identify_best_roles(limit: int = 50) -> List[str]:
    """Return roles with highest positive_interest_rate (min volume)."""
    result = await analyze_campaign_success(limit=limit)
    return result.get("top_roles", [])
