"""
MONITORING: severity_classifier
PURPOSE: S1=critical, S2=major, S3=isolated, S4=low; consider frequency, affected workflows, user-facing, campaigns blocked
"""
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

***REMOVED*** Components that imply user-facing or critical path
USER_FACING_OR_CRITICAL = {
    "lead_generation_workflow", "sales_engine", "agents", "campaign_engine",
    "email_generation_skill", "contact_enrichment_skill", "decision_maker_detection_skill",
}
CAMPAIGN_BLOCKING = {"campaign_creation_failure", "campaign_dispatch_failure", "redis_queue_failure", "outreach_queue"}


def _severity_reason(severity: str, cluster: Dict[str, Any]) -> str:
    count = cluster.get("count", 0)
    comps = cluster.get("affected_components", [])
    etype = cluster.get("error_type", "")
    if severity == "S1":
        return "Critical production outage: high frequency and critical path affected"
    if severity == "S2":
        return f"Major feature degradation: {count} occurrences affecting {comps[:3]}"
    if severity == "S3":
        return f"Isolated functionality issue: {etype} ({count} occurrences)"
    return f"Low-priority or noisy: {etype}"


async def classify_severity(
    cluster: Dict[str, Any],
    clusters: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Classify severity from cluster. Consider error frequency, affected workflows, user-facing, campaign blocking.
    Returns { severity: S1|S2|S3|S4, reason: str }.
    """
    count = cluster.get("count", 0)
    etype = cluster.get("error_type", "unknown_error")
    comps = set(c.lower() for c in (cluster.get("affected_components") or []))
    is_user_facing = bool(comps & USER_FACING_OR_CRITICAL) or any(
        u in str(cluster.get("sample_errors", [{}])[0]).lower() for u in USER_FACING_OR_CRITICAL
    )
    is_campaign_blocking = etype in CAMPAIGN_BLOCKING or bool(comps & CAMPAIGN_BLOCKING)
    total_cluster_events = count
    if isinstance(clusters, list):
        total_cluster_events = sum(c.get("count", 0) for c in clusters)

    ***REMOVED*** S1: critical
    if (count >= 50 and is_user_facing) or (is_campaign_blocking and count >= 20) or (count >= 100):
        severity = "S1"
    ***REMOVED*** S2: major
    elif (count >= 10 and is_user_facing) or is_campaign_blocking or (count >= 30):
        severity = "S2"
    ***REMOVED*** S3: isolated
    elif count >= 3 or is_user_facing:
        severity = "S3"
    else:
        severity = "S4"

    reason = _severity_reason(severity, cluster)
    return {"severity": severity, "reason": reason}
