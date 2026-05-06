"""
CORE: upap/regulated
PURPOSE: Regulated domain and simulation mode gate.
ENCODING: UTF-8 WITHOUT BOM

- is_regulated_domain(query_params) -> bool
- require_simulation_mode(is_regulated, simulation_mode) -> GateResult
- Block real company names when regulated + simulation required.
"""

import re
from typing import Any, Dict, List, Optional
from dataclasses import dataclass


@dataclass
class GateResult:
    passed: bool
    reason: str
    regulated_domain: bool
    simulation_mode: Optional[bool]
    blocked_reason: Optional[str] = None
    blocked_count: int = 0


# Industries/domains considered regulated (pharma, healthcare, finance, etc.)
REGULATED_KEYWORDS = [
    "pharma", "pharmaceutical", "healthcare", "medical", "clinical",
    "finance", "banking", "insurance", "legal", "defense",
    "regulated", "compliance", "gdpr", "hipaa", "fda",
]
REGULATED_HS_PREFIXES = ["30", "29", "28", "30", "25"]   # HS chapters often used for pharma/chemicals


def is_regulated_domain(query_params: Dict[str, Any]) -> bool:
    """
    Determine if the query targets a regulated domain.
    Explicit plan.regulated_domain overrides; else uses target_type, product_service, industry, hs_code.
    """
    if not query_params:
        return False
    if "regulated_domain" in query_params and isinstance(query_params.get("regulated_domain"), bool):
        return query_params["regulated_domain"]
    text_parts = []
    for key in ("target_type", "product_service", "industry", "geography", "hs_code"):
        val = query_params.get(key)
        if val and isinstance(val, str):
            text_parts.append(val.lower())
    if not text_parts:
        return False
    combined = " ".join(text_parts)
    for kw in REGULATED_KEYWORDS:
        if kw in combined:
            return True
    hs = (query_params.get("hs_code") or "").strip()
    if hs:
        for prefix in REGULATED_HS_PREFIXES:
            if hs.startswith(prefix):
                return True
    return False


def _looks_like_real_company_name(name: Optional[str]) -> bool:
    """
    Heuristic: non-empty, not a placeholder, not "Company A" style.
    Real names usually have mixed case, spaces, possibly Inc/LLC.
    """
    if not name or not isinstance(name, str):
        return False
    s = name.strip()
    if len(s) < 2:
        return False
    # Placeholders / test data
    if re.match(r"^(Company\s+[A-Z]|Test\s+Co|Mock\s+|Sample\s+|N/A|—|-$)", s, re.I):
        return False
    if re.match(r"^[A-Za-z]+\s*\d+$", s):   # "Company1", "Biz123"
        return False
    # Likely real: has space, or Inc/LLC/GmbH, or mixed words
    if " " in s or re.search(r"\b(Inc|LLC|Ltd|GmbH|Corp|Co\.)\b", s, re.I):
        return True
    # Single word but long and mixed case
    if len(s) > 4 and s[1:].lower() != s[1:]:
        return True
    return True


def require_simulation_mode(
    is_regulated: bool,
    simulation_mode: Optional[bool],
    leads: Optional[List[Dict[str, Any]]] = None,
) -> GateResult:
    """
    If regulated_domain == True and simulation_mode missing or False → FAIL.
    If regulated + simulation required and real company name detected → FAIL (block).
    """
    blocked_reason = None
    blocked_count = 0
    sim = simulation_mode if isinstance(simulation_mode, bool) else None
    if simulation_mode is not None and not isinstance(simulation_mode, bool):
        try:
            sim = bool(simulation_mode)
        except Exception:
            sim = None

    if not is_regulated:
        return GateResult(
            passed=True,
            reason="ok",
            regulated_domain=False,
            simulation_mode=sim,
            blocked_reason=None,
            blocked_count=0,
        )

    # Regulated: simulation_mode must be True
    if sim is not True:
        return GateResult(
            passed=False,
            reason="regulated_domain_requires_simulation_mode",
            regulated_domain=True,
            simulation_mode=sim,
            blocked_reason="simulation_mode missing or false for regulated domain",
            blocked_count=0,
        )

    # Regulated + simulation required: block real company names
    if leads:
        allowed = []
        for lead in leads:
            name = lead.get("company_name") or lead.get("Company Name") or lead.get("name")
            if _looks_like_real_company_name(name):
                blocked_count += 1
                continue
            allowed.append(lead)
        if blocked_count > 0:
            return GateResult(
                passed=False,
                reason="regulated_simulation_real_company_names_blocked",
                regulated_domain=True,
                simulation_mode=True,
                blocked_reason="real company name detected in regulated simulation",
                blocked_count=blocked_count,
            )

    return GateResult(
        passed=True,
        reason="ok",
        regulated_domain=True,
        simulation_mode=True,
        blocked_reason=None,
        blocked_count=0,
    )
