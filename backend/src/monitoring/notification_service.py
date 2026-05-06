"""
MONITORING: notification_service
PURPOSE: Send structured alerts (Slack-style); log if Slack not wired; suppress duplicates; notify on new or escalation
"""
import logging
import os
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def _format_alert(incident: Dict[str, Any], likely_files: List[str]) -> str:
    affected_area = incident.get("affected_endpoint") or incident.get("affected_workflow") or "general"
    if incident.get("affected_workflow") and incident.get("affected_endpoint"):
        affected_area = f"{incident['affected_workflow']} / {incident['affected_endpoint']}"
    time_start = incident.get("first_seen_at") or incident.get("time_window_start", "")
    time_end = incident.get("last_seen_at") or incident.get("time_window_end", "")
    time_window = f"{time_start} → {time_end}" if time_start or time_end else "N/A"
    status = incident.get("alert_status", "new")
    lines = [
        "[SOARB2B Incident Alert]",
        f"Severity: {incident.get('severity', 'S3')}",
        f"Incident Title: {incident.get('title', 'Unknown')}",
        f"Affected Area: {affected_area}",
        f"Occurrences: {incident.get('occurrence_count', 0)}",
        f"Time Window: {time_window}",
        "Impacted Components:",
    ]
    for c in (incident.get("affected_components") or [])[:10]:
        lines.append(f"  - {c}")
    lines.append("Likely Root Cause:")
    lines.append(f"  {incident.get('root_cause', '')}")
    lines.append("Suggested Immediate Action:")
    lines.append(f"  {incident.get('suggested_next_step', '')}")
    if likely_files:
        lines.append("Likely Source Files:")
        for f in likely_files[:8]:
            lines.append(f"  - {f}")
    lines.append(f"Status: {status}")
    return "\n".join(lines)


async def send_alert(
    incident: Dict[str, Any],
    likely_files: Optional[List[str]] = None,
    suppress_duplicate: bool = True,
    previous_severity: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Send formatted alert. If Slack webhook configured, post there; else log.
    Only send if not suppress_duplicate or severity escalated.
    """
    severity = incident.get("severity", "S3")
    if suppress_duplicate and previous_severity == severity:
        logger.info("notification_service: suppressing duplicate alert for same severity")
        return {"sent": False, "reason": "duplicate_suppressed"}
    body = _format_alert(incident, likely_files or incident.get("likely_files") or [])
    webhook = os.getenv("SLACK_WEBHOOK_URL") or os.getenv("MONITORING_SLACK_WEBHOOK")
    if webhook:
        try:
            import urllib.request
            import json as _json
            req = urllib.request.Request(
                webhook,
                data=_json.dumps({"text": body}).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=10) as r:
                pass
            logger.info("notification_service: Slack alert sent")
            return {"sent": True, "channel": "slack"}
        except Exception as e:
            logger.warning("notification_service: Slack failed %s, falling back to log", e)
    logger.warning("MONITORING ALERT:\n%s", body)
    return {"sent": True, "channel": "log"}


async def should_notify(
    incident_id: str,
    severity: str,
    existing_incident: Optional[Dict[str, Any]],
) -> bool:
    """Decide if we should send notification: new incident or severity escalation."""
    if not existing_incident:
        return True
    prev = existing_incident.get("severity", "S4")
    order = {"S1": 0, "S2": 1, "S3": 2, "S4": 3}
    return order.get(severity, 3) < order.get(prev, 3)
