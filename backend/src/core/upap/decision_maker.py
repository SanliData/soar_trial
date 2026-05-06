"""
CORE: upap/decision_maker
PURPOSE: Deterministic decision-maker role inference (no LLM).
ENCODING: UTF-8 WITHOUT BOM

- infer_role(title, dept, keyword_intent) -> (role, confidence)
- infer_decision_maker_persona() -> role, authority_level, department, decision_type,
  accessibility_score, decision_maker_confidence; is_decision_maker only when confidence >= threshold.
"""

import re
from typing import Any, Dict, Optional, Tuple

from src.core.upap.policy import DECISION_MAKER_CONFIDENCE_THRESHOLD

ALLOWED_ROLES = frozenset({"Procurement", "QA", "Ops"})


def infer_role(
    title: Optional[str] = None,
    dept: Optional[str] = None,
    keyword_intent: Optional[str] = None,
) -> Tuple[str, float]:
    """
    Deterministic inference: map title/dept/keywords to role and confidence.
    Returns (role, confidence). role in {Procurement, QA, Ops}; confidence in [0.0, 1.0].
    """
    title = (title or "").strip().lower()
    dept = (dept or "").strip().lower()
    keyword_intent = (keyword_intent or "").strip().lower()
    combined = " ".join([title, dept, keyword_intent])

    ***REMOVED*** Procurement signals
    proc_keywords = ["procurement", "purchasing", "buyer", "sourcing", "supply", "purchase", "vendor"]
    ***REMOVED*** QA signals
    qa_keywords = ["quality", "qa", "qc", "compliance", "regulatory", "audit", "inspection"]
    ***REMOVED*** Ops signals
    ops_keywords = ["operations", "ops", "production", "manufacturing", "plant", "facility", "logistics"]

    scores = {"Procurement": 0.0, "QA": 0.0, "Ops": 0.0}
    for w in proc_keywords:
        if w in combined:
            scores["Procurement"] += 0.35
    for w in qa_keywords:
        if w in combined:
            scores["QA"] += 0.35
    for w in ops_keywords:
        if w in combined:
            scores["Ops"] += 0.35

    ***REMOVED*** Title hints (stronger)
    if any(t in title for t in ["procurement", "purchasing", "buyer", "sourcing"]):
        scores["Procurement"] += 0.4
    if any(t in title for t in ["quality", "qa", "qc", "compliance", "regulatory"]):
        scores["QA"] += 0.4
    if any(t in title for t in ["operations", "ops", "production", "manufacturing", "plant"]):
        scores["Ops"] += 0.4

    best_role = max(scores, key=scores.get)
    raw_score = scores[best_role]
    confidence = min(1.0, max(0.0, raw_score))
    if confidence < 0.1:
        best_role = "Ops"  ***REMOVED*** default when no signal
        confidence = 0.3
    return (best_role, round(confidence, 2))


def _authority_level(title: str) -> str:
    """Heuristic: director/head/vp -> high, manager -> medium, else low."""
    t = title.lower()
    if any(x in t for x in ["director", "head", "vp", "vice president", "chief", "c-level"]):
        return "high"
    if any(x in t for x in ["manager", "lead", "senior", "principal"]):
        return "medium"
    return "low"


def _accessibility_score(title: str, role: str) -> float:
    """Heuristic: public-facing roles/seniority -> higher accessibility (0-1)."""
    score = 0.5
    t = title.lower()
    if "linkedin" in t or "contact" in t or "sales" in t:
        score += 0.2
    if _authority_level(title) == "high":
        score += 0.15
    if role == "Procurement":
        score += 0.1
    return round(min(1.0, score), 2)


def infer_decision_maker_persona(
    title: Optional[str] = None,
    dept: Optional[str] = None,
    keyword_intent: Optional[str] = None,
    confidence_threshold: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Full persona fields: role, authority_level, department, decision_type,
    accessibility_score, decision_maker_confidence. is_decision_maker True only when
    decision_maker_confidence >= confidence_threshold (default DECISION_MAKER_CONFIDENCE_THRESHOLD).
    """
    role, confidence = infer_role(title=title, dept=dept, keyword_intent=keyword_intent)
    title_s = (title or "").strip()
    dept_s = (dept or "").strip() or "General"
    thresh = confidence_threshold if confidence_threshold is not None else DECISION_MAKER_CONFIDENCE_THRESHOLD
    return {
        "role": role,
        "authority_level": _authority_level(title_s),
        "department": dept_s,
        "decision_type": role,  ***REMOVED*** align with role for now
        "accessibility_score": _accessibility_score(title_s, role),
        "decision_maker_confidence": confidence,
        "is_decision_maker": confidence >= thresh,
    }
