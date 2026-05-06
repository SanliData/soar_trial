"""
MONITORING: log_ingestor
PURPOSE: Read logs from configurable sources; parse into structured events (timestamp, module, endpoint, error, traceback, request_id)
"""
import logging
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

***REMOVED*** SOARB2B-known incident type patterns (module/error -> normalized type); order matters (first match)
INCIDENT_TYPE_PATTERNS = [
    (r"auth.*fail|OAuth|oauth|JWT|jwt.*invalid|token.*expired", "authentication_flow_failure"),
    (r"oauth.*callback|callback.*fail", "oauth_callback_failure"),
    (r"jwt.*valid|validation.*jwt", "jwt_validation_failure"),
    (r"lead_generation_workflow|lead_generation_workflow\.py|workflows/lead_generation", "lead_generation_workflow_failure"),
    (r"company_discovery|company_discovery_skill", "company_discovery_failure"),
    (r"decision_maker_detection|decision_maker_detection_skill|persona_detection", "decision_maker_detection_failure"),
    (r"contact_enrichment|contact_enrichment_skill", "contact_enrichment_failure"),
    (r"email_generation|email_generation_skill|outreach.*email", "email_generation_failure"),
    (r"campaign_creation|campaign_creation\.py", "campaign_creation_failure"),
    (r"campaign_dispatch|outreach_queue|automation:campaign|enqueue_outreach", "campaign_dispatch_failure"),
    (r"response_classification|response_classifier", "response_classification_failure"),
    (r"learning_engine|learning_engine\.py", "learning_engine_failure"),
    (r"redis|Redis|queue.*fail|get_redis_client|ConnectionRefusedError.*6379", "redis_queue_failure"),
    (r"openai.*timeout|Timeout.*openai|OpenAI.*timeout|timed out.*openai", "openai_timeout"),
    (r"openai\.RateLimitError|rate.?limit|RateLimitError", "openai_rate_limit"),
    (r"openai.*invalid|invalid.*response|OpenAI.*error|APIError|JSONDecodeError.*openai", "openai_invalid_response"),
    (r"malformed.*context|workflow.*context|context.*missing|KeyError.*context", "malformed_workflow_context"),
    (r"db_write|database.*error|sqlalchemy|IntegrityError|SessionLocal|OperationalError", "db_write_failure"),
    (r"rate.?limit|rate_limit|429", "rate_limit_issue"),
    (r"validation.*error|RequestValidationError|422", "malformed_payload_issue"),
    (r"external.*api|integration.*fail|requests\.(get|post).*Error", "external_api_integration_issue"),
    (r"analytics.*query|analytics_query_failure|/analytics/query", "analytics_query_failure"),
    (r"graph_builder|graph_generation|intelligence_graph.*fail", "graph_generation_failure"),
    (r"invalid_sql_generation|query_validator|Only SELECT", "invalid_sql_generation"),
    (r"query_timeout|analytics.*timeout|statement_timeout", "query_timeout"),
    (r"nl_query_parsing|question_parser|ParsedIntent", "nl_query_parsing_error"),
    (r"opportunity_scoring_anomaly|score.*0\.95.*signals_count", "opportunity_scoring_anomaly"),
]

***REMOVED*** Regex for common log formats (Python logging, uvicorn, PM2)
RE_TIMESTAMP = re.compile(r"(\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)")
RE_REQUEST_ID = re.compile(r"(?:request[_-]?id|X-Request-ID)[=:\s]+([a-zA-Z0-9\-]+)", re.I)
RE_MODULE = re.compile(r"(?:File \"[^\"]*\"|[\w/\\]+/)([\w/\\]+\.py)")
RE_ENDPOINT = re.compile(r"(?:GET|POST|PUT|PATCH|DELETE)\s+([^\s]+)|(?:path=|route[=:])\s*[\"']?([^\"'\s]+)")
RE_ERROR = re.compile(r"(?:Error|Exception|Traceback|error):\s*(.+)", re.I)
RE_EXCEPTION_TYPE = re.compile(r"(\w+(?:\.\w+)*Error|\w+(?:\.\w+)*Exception)")


def _normalize_error_type(message: str, module: Optional[str] = None) -> str:
    text = f"{message or ''} {module or ''}"
    for pattern, inc_type in INCIDENT_TYPE_PATTERNS:
        if re.search(pattern, text, re.I):
            return inc_type
    return "unknown_error"


def _parse_timestamp(s: str) -> Optional[datetime]:
    if not s:
        return None
    try:
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%fZ"):
            try:
                return datetime.strptime(s.strip()[:26], fmt.replace(".%f", ".%f")[:26]).replace(tzinfo=timezone.utc)
            except ValueError:
                continue
    except Exception:
        pass
    return None


def parse_log_line(line: str, source: str = "app") -> Optional[Dict[str, Any]]:
    """
    Parse a raw log line into a structured event.
    Returns dict with timestamp, module, endpoint, error_message, traceback, request_id, source, raw.
    """
    if not line or not line.strip():
        return None
    event = {"source": source, "raw": line.strip()[:2000], "error_message": None, "traceback": None}
    ts = RE_TIMESTAMP.search(line)
    if ts:
        event["timestamp"] = _parse_timestamp(ts.group(1)) or datetime.now(timezone.utc)
    else:
        event["timestamp"] = datetime.now(timezone.utc)
    rid = RE_REQUEST_ID.search(line)
    if rid:
        event["request_id"] = rid.group(1)
    mod = RE_MODULE.search(line)
    if mod:
        event["module"] = mod.group(1).replace("\\", "/")
    ep = RE_ENDPOINT.search(line)
    if ep:
        event["endpoint"] = ep.group(1)
    err = RE_ERROR.search(line)
    if err:
        event["error_message"] = err.group(1).strip()[:500]
    if "Error" in line or "Exception" in line or "Traceback" in line:
        event["error_message"] = event.get("error_message") or line.strip()[:500]
    exc_type = RE_EXCEPTION_TYPE.search(line)
    if exc_type:
        event["exception_type"] = exc_type.group(1)
    ep_m = RE_ENDPOINT.search(line)
    if ep_m:
        event["endpoint"] = event.get("endpoint") or (ep_m.group(1) or ep_m.group(2) or "").strip()
    event["error_type"] = _normalize_error_type(event.get("error_message", ""), event.get("module"))
    return event


def read_log_file(path: str, max_lines: int = 500, tail: bool = True) -> List[str]:
    """Read recent lines from a file (tail by default)."""
    try:
        p = Path(path)
        if not p.exists():
            return []
        with open(p, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        if tail and len(lines) > max_lines:
            lines = lines[-max_lines:]
        elif not tail:
            lines = lines[:max_lines]
        return [ln.strip() for ln in lines if ln.strip()]
    except Exception as e:
        logger.debug("read_log_file %s: %s", path, e)
        return []


def _ingest_agent_run_logs(max_events: int) -> List[Dict[str, Any]]:
    """Ingest workflow/skill failures from agent_run_logs table (error_message not null)."""
    events = []
    try:
        from src.db.base import SessionLocal
        from src.models.agent_run_log import AgentRunLog
        db = SessionLocal()
        try:
            rows = (
                db.query(AgentRunLog)
                .filter(AgentRunLog.error_message.isnot(None), AgentRunLog.error_message != "")
                .order_by(AgentRunLog.created_at.desc())
                .limit(max_events)
                .all()
            )
            for r in rows:
                ts = r.created_at
                if ts and getattr(ts, "tzinfo", None) is None:
                    ts = ts.replace(tzinfo=timezone.utc)
                events.append({
                    "timestamp": ts,
                    "module": r.workflow_step,
                    "error_message": (r.error_message or "")[:500],
                    "source": "agent_run_logs",
                    "raw": r.error_message,
                    "request_id": r.agent_run_id,
                    "workflow_step": r.workflow_step,
                    "error_type": _normalize_error_type(r.error_message or "", r.workflow_step),
                })
        finally:
            db.close()
    except Exception as e:
        logger.debug("_ingest_agent_run_logs: %s", e)
    return events


async def ingest_logs(
    log_paths: Optional[List[str]] = None,
    max_events: int = 1000,
    ingest_from_db: bool = True,
) -> List[Dict[str, Any]]:
    """
    Ingest from configurable sources. Default: PM2 logs (soarb2b-error.log, soarb2b-out.log),
    then backend/logs/*.log. If ingest_from_db, also pull workflow failures from agent_run_logs.
    Returns list of structured events (timestamp, module, endpoint, error_message, request_id, error_type, workflow_step).
    """
    paths = log_paths or []
    if not paths:
        backend = Path(__file__).resolve().parent.parent.parent.parent  ***REMOVED*** backend/
        for name in (
            "logs/soarb2b-error.log",
            "logs/soarb2b-out.log",
            "logs/error.log",
            "logs/combined.log",
            "logs/app.log",
            "error.log",
            "app.log",
        ):
            candidate = backend / name
            if candidate.exists():
                paths.append(str(candidate))
    events = []
    seen = set()
    for path in paths[:20]:
        for line in read_log_file(path, max_lines=300):
            ev = parse_log_line(line, source=path)
            if ev and (ev.get("error_message") or "Error" in (ev.get("raw") or "") or "Exception" in (ev.get("raw") or "")):
                key = (ev.get("error_message", "")[:100], ev.get("module", ""), ev.get("error_type", ""))
                if key not in seen:
                    seen.add(key)
                    events.append(ev)
            if len(events) >= max_events:
                break
        if len(events) >= max_events:
            break
    if ingest_from_db:
        db_events = _ingest_agent_run_logs(max(100, max_events - len(events)))
        for ev in db_events:
            key = (ev.get("error_message", "")[:100], ev.get("module", ""), ev.get("error_type", ""))
            if key not in seen:
                seen.add(key)
                events.append(ev)
            if len(events) >= max_events:
                break
    if not events and os.getenv("MONITORING_DEMO_EVENTS"):
        events = [
            {
                "timestamp": datetime.now(timezone.utc),
                "module": "src/skills/outreach/email_generation_skill.py",
                "error_message": "OpenAI API timeout",
                "error_type": "openai_timeout",
                "source": "demo",
                "raw": "OpenAI API timeout during email generation",
            }
        ]
    logger.info("log_ingestor: ingested %s events from %s paths (+ db=%s)", len(events), len(paths), ingest_from_db)
    return events
