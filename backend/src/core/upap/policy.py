"""
CORE: upap/policy
PURPOSE: UPAP limits, thresholds, and region filters. Single source of truth.
ENCODING: UTF-8 WITHOUT BOM
"""

from typing import Any, Dict

# Hard filters (ENFORCED at discovery, enrichment, export)
COMPANY_LIMIT_DEFAULT = 100
COMPANY_SIZE_MAX_DEFAULT = 50
MIN_READY_LEADS_DEFAULT = 5

# Decision maker: only claim "decision_maker" when confidence >= threshold
DECISION_MAKER_CONFIDENCE_THRESHOLD = 0.65

# Region filters: optional allow/deny list (empty = no region filter)
REGION_FILTER_ALLOW_LIST: list = []    # e.g. ["US", "DE"]
REGION_FILTER_DENY_LIST: list = []     # e.g. []


def get_limits_from_plan(plan_params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Resolve enforced limits from plan (onboarding_data).
    Falls back to policy defaults if not set. Explicit 0 is respected for min_ready_leads.
    """
    def _int_or(key: str, default: int) -> int:
        val = plan_params.get(key)
        if val is None:
            return default
        try:
            return int(val)
        except (TypeError, ValueError):
            return default

    return {
        "company_limit": _int_or("company_limit", COMPANY_LIMIT_DEFAULT),
        "company_size_max": _int_or("company_size_max", COMPANY_SIZE_MAX_DEFAULT),
        "min_ready_leads": _int_or("min_ready_leads", MIN_READY_LEADS_DEFAULT),
        "region_allow_list": plan_params.get("region_allow_list") or REGION_FILTER_ALLOW_LIST,
        "region_deny_list": plan_params.get("region_deny_list") or REGION_FILTER_DENY_LIST,
    }
