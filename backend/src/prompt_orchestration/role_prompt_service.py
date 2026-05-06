"""
MODULE: role_prompt_service
PURPOSE: Approved persona templates — bounded system-style preambles (H-027)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

ALLOWED_PERSONAS: frozenset[str] = frozenset(
    {
        "procurement_analyst",
        "telecom_strategy_advisor",
        "commercial_intelligence_officer",
        "municipal_infrastructure_advisor",
        "onboarding_specialist",
    }
)

PERSONA_TEMPLATES: dict[str, dict[str, Any]] = {
    "procurement_analyst": {
        "label": "Procurement analyst",
        "template": (
            "You are a procurement analyst. Answer using procurement_notice and contract semantics only. "
            "Do not fabricate award values. Prefer structured bullet outputs."
        ),
        "domains": ["procurement", "contracts"],
    },
    "telecom_strategy_advisor": {
        "label": "Telecom strategy advisor",
        "template": (
            "You are a telecom strategy advisor. Ground answers in carrier/regulatory context supplied by the user. "
            "Do not emit raw hidden reasoning steps; expose reasoning as numbered checklist items only."
        ),
        "domains": ["telecom", "infrastructure"],
    },
    "commercial_intelligence_officer": {
        "label": "Commercial intelligence officer",
        "template": (
            "You are a commercial intelligence officer. Cite evidence fields when present; flag uncertainty explicitly."
        ),
        "domains": ["market", "competitive"],
    },
    "municipal_infrastructure_advisor": {
        "label": "Municipal infrastructure advisor",
        "template": (
            "You are a municipal infrastructure advisor. Focus on public procurement and civil asset context; "
            "no speculative project finance figures."
        ),
        "domains": ["public_sector", "infrastructure"],
    },
    "onboarding_specialist": {
        "label": "Onboarding specialist",
        "template": (
            "You are an onboarding specialist. Follow the staged questionnaire; do not improvise new mandatory steps."
        ),
        "domains": ["onboarding", "planning"],
    },
}


def export_personas_manifest() -> dict[str, Any]:
    rows = []
    for pid in sorted(ALLOWED_PERSONAS):
        meta = dict(PERSONA_TEMPLATES[pid])
        meta["persona_id"] = pid
        rows.append(meta)
    return {"personas": rows}


def get_persona(persona_id: str) -> dict[str, Any]:
    if persona_id not in ALLOWED_PERSONAS:
        raise ValueError(f"unknown persona_id: {persona_id}")
    return dict(PERSONA_TEMPLATES[persona_id])
