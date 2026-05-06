"""
CORE: upap/cross_channel
PURPOSE: Deterministic cross-channel recommendation.
ENCODING: UTF-8 WITHOUT BOM

- recommend(keyword_intent, geo_confidence, role_score) -> { channel_recommendation, sequence?, rule_id }
- Allowed: linkedin_only, google_only, both_with_sequence.
"""

from typing import Any, Dict, Optional

ALLOWED_CHANNELS = frozenset({"linkedin_only", "google_only", "both_with_sequence"})


def recommend(
    keyword_intent: Optional[str] = None,
    geo_confidence: Optional[float] = None,
    role_score: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Deterministic rules for channel recommendation.
    Returns dict with channel_recommendation, optional sequence, rule_id.
    """
    keyword_intent = (keyword_intent or "").strip().lower()
    geo_confidence = geo_confidence if isinstance(geo_confidence, (int, float)) else 0.5
    role_score = role_score if isinstance(role_score, (int, float)) else 0.5

    # B2B / professional intent -> LinkedIn
    if any(k in keyword_intent for k in ["b2b", "linkedin", "professional", "decision maker", "executive", "procurement"]):
        return {
            "channel_recommendation": "linkedin_only",
            "sequence": None,
            "rule_id": "upap_rule_b2b_linkedin",
        }
    # Local / geo / store -> Google
    if any(k in keyword_intent for k in ["local", "store", "near me", "location", "retail", "foot traffic"]):
        return {
            "channel_recommendation": "google_only",
            "sequence": None,
            "rule_id": "upap_rule_geo_google",
        }
    # High geo confidence + high role score -> both with sequence
    if geo_confidence >= 0.6 and role_score >= 0.5:
        return {
            "channel_recommendation": "both_with_sequence",
            "sequence": ["linkedin", "google"],
            "rule_id": "upap_rule_both_sequence",
        }
    # Default: both with sequence
    return {
        "channel_recommendation": "both_with_sequence",
        "sequence": ["linkedin", "google"],
        "rule_id": "upap_rule_default",
    }
