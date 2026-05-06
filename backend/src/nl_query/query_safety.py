"""
NL_QUERY: query_safety
PURPOSE: SQL safeguards — max join depth, max result size, query timeout; complexity validator and timeout handling
"""
import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Production stability limits
MAX_JOIN_DEPTH = 4
MAX_RESULT_SIZE = 500
QUERY_TIMEOUT_SEC = 2


def validate_query_complexity(
    plan: Any,
    max_join_depth: int = MAX_JOIN_DEPTH,
    max_result_size: int = MAX_RESULT_SIZE,
) -> Tuple[bool, str]:
    """
    Validate query plan complexity. Returns (ok, error_message).
    Rejects if join depth > max_join_depth or limit > max_result_size.
    """
    if plan is None:
        return False, "No query plan"
    joins = getattr(plan, "joins", None) or []
    if len(joins) > max_join_depth:
        return False, f"Join depth {len(joins)} exceeds maximum {max_join_depth}"
    limit = getattr(plan, "limit", None)
    if limit is not None and int(limit) > max_result_size:
        return False, f"Requested limit {limit} exceeds maximum {max_result_size}"
    return True, ""


def limit_join_depth(
    plan: Any,
    max_join_depth: int = MAX_JOIN_DEPTH,
) -> Any:
    """
    Return a plan with joins truncated to max_join_depth (in-place if possible, else copy).
    """
    if plan is None:
        return plan
    joins = getattr(plan, "joins", None) or []
    if len(joins) <= max_join_depth:
        return plan
    try:
        plan.joins = joins[:max_join_depth]
        logger.info("query_safety: limited join depth from %s to %s", len(joins), max_join_depth)
    except AttributeError:
        pass
    return plan


def apply_result_limit(
    rows: List[Dict[str, Any]],
    max_size: int = MAX_RESULT_SIZE,
) -> List[Dict[str, Any]]:
    """Cap result list to max_size. Returns truncated list."""
    if not rows or len(rows) <= max_size:
        return rows
    logger.info("query_safety: truncated result from %s to %s rows", len(rows), max_size)
    return rows[:max_size]


def get_query_timeout_seconds() -> int:
    """Return configured query timeout (seconds) for NL/analytics queries."""
    return QUERY_TIMEOUT_SEC


def enforce_plan_limits(plan: Any) -> Any:
    """
    Enforce max result size on plan.limit (in-place). Call after plan_sql before generate_sql.
    """
    if plan is None:
        return plan
    limit = getattr(plan, "limit", None)
    if limit is not None and int(limit) > MAX_RESULT_SIZE:
        try:
            plan.limit = MAX_RESULT_SIZE
            logger.info("query_safety: capped plan limit to %s", MAX_RESULT_SIZE)
        except AttributeError:
            pass
    return plan
