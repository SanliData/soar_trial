"""
MODULE: skill_registry
PURPOSE: Static reusable intelligence skills catalog (H-031)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

SKILL_REGISTRY: dict[str, dict[str, Any]] = {
    "procurement_analysis": {
        "category": "commercial",
        "risk_tier": "medium",
        "inputs": ["notice_payload"],
        "outputs": ["structured_summary"],
    },
    "opportunity_evaluation": {
        "category": "ranking",
        "risk_tier": "medium",
        "inputs": ["entity_bundle"],
        "outputs": ["score_vector"],
    },
    "graph_investigation": {
        "category": "graph",
        "risk_tier": "low",
        "inputs": ["seed_entity"],
        "outputs": ["path_hints"],
    },
    "onboarding_planning": {
        "category": "workflow",
        "risk_tier": "low",
        "inputs": ["user_answers"],
        "outputs": ["plan_draft"],
    },
    "executive_summarization": {
        "category": "briefing",
        "risk_tier": "low",
        "inputs": ["evidence_pack"],
        "outputs": ["brief_md"],
    },
    "market_signal_review": {
        "category": "signals",
        "risk_tier": "medium",
        "inputs": ["signal_digest"],
        "outputs": ["ranked_signals"],
    },
}


def export_skills_manifest() -> dict[str, Any]:
    skills = sorted(SKILL_REGISTRY.keys())
    return {
        "skills": [{"skill_id": k, **SKILL_REGISTRY[k]} for k in skills],
        "count": len(skills),
    }


def get_skill(skill_id: str) -> dict[str, Any] | None:
    if skill_id not in SKILL_REGISTRY:
        return None
    return {"skill_id": skill_id, **SKILL_REGISTRY[skill_id]}
