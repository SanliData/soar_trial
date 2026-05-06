"""
CORE: query_limits
PURPOSE: Global query limits enforcement
ENCODING: UTF-8 WITHOUT BOM

Every query MAX 100 results.
Applies separately to businesses, personas, contacts.
"""

# Global query limits (non-negotiable)
MAX_RESULTS_PER_QUERY = 100
MAX_VISIT_STOPS_PER_ROUTE = 20

# Admin override capability (requires admin key)
ADMIN_MAX_RESULTS_OVERRIDE = 1000   # Admin can request up to 1000 (still capped)


def enforce_query_limit(count: int, is_admin: bool = False) -> int:
    """
    Enforce query limit.
    Returns the capped count.
    """
    max_results = ADMIN_MAX_RESULTS_OVERRIDE if is_admin else MAX_RESULTS_PER_QUERY
    return min(count, max_results)


def validate_query_params(limit: int = None, offset: int = 0, is_admin: bool = False) -> dict:
    """
    Validate and enforce query parameters.
    Returns validated limit and offset.
    """
    max_results = ADMIN_MAX_RESULTS_OVERRIDE if is_admin else MAX_RESULTS_PER_QUERY
    
    # If limit not provided, default to max
    if limit is None:
        limit = max_results
    else:
        # Enforce cap even if user requests more
        limit = min(limit, max_results)
    
    # Ensure offset is non-negative
    offset = max(0, offset)
    
    return {
        "limit": limit,
        "offset": offset,
        "capped": limit == max_results   # True if limit was capped
    }


def should_show_capped_warning(estimated_total: int, requested_limit: int = None) -> bool:
    """
    Determine if user should see capped sample warning.
    """
    max_results = MAX_RESULTS_PER_QUERY
    effective_limit = requested_limit if requested_limit else max_results
    
    return estimated_total > effective_limit
