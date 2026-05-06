"""
MONITORING: root_cause_analyzer
PURPOSE: Infer root cause, affected module/route/workflow; optional OpenAI summary
"""
import logging
import os
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_OPENAI_AVAILABLE = False
try:
    import openai
    _OPENAI_AVAILABLE = True
except ImportError:
    openai = None

***REMOVED*** Map error_type -> default root cause and suggested next step
DEFAULT_ROOT_CAUSES = {
    "lead_generation_workflow_failure": ("Workflow execution failed in lead generation pipeline", "lead_generation_workflow", "Check skill_executor logs and workflow context", "Verify input context and skill order"),
    "decision_maker_detection_failure": ("Decision maker detection skill failed", "decision_maker_detection_skill", "Check OpenAI and company context", "Validate persona prompt and token limits"),
    "contact_enrichment_failure": ("Contact enrichment failed", "contact_enrichment_skill", "Enrichment API or fallback failed", "Add retries and validate enrichment provider"),
    "email_generation_failure": ("Email generation skill failed", "email_generation_skill", "OpenAI or template error", "Check OPENAI_API_KEY and prompt"),
    "campaign_creation_failure": ("Campaign creation failed", "campaign_creation_skill", "DB or Redis write failed", "Check intel_companies/contacts and Redis"),
    "campaign_dispatch_failure": ("Campaign dispatch/queue failed", "outreach_queue", "Redis or worker unavailable", "Verify Redis and automation workers"),
    "response_classification_failure": ("Response classification failed", "response_classifier", "OpenAI or input format", "Validate reply body and model"),
    "learning_engine_failure": ("Learning engine error", "learning_engine", "Cache or analysis failed", "Check Redis and campaign_metrics"),
    "redis_queue_failure": ("Redis or queue failure", "redis", "Connection or command failed", "Check REDIS_URL and connectivity"),
    "openai_timeout": ("OpenAI API timeout", "openai", "Timeout during API call", "Add retry/backoff and monitor token latency"),
    "openai_invalid_response": ("OpenAI returned invalid response", "openai", "Parse or schema error", "Validate response format and fallbacks"),
    "malformed_workflow_context": ("Malformed workflow context", "skill_executor", "Missing or invalid context field", "Validate context between skills"),
    "db_write_failure": ("Database write failed", "database", "Constraint or connection error", "Check migrations and DB health"),
    "authentication_flow_failure": ("Authentication flow failed", "auth", "OAuth/JWT or session error", "Check GOOGLE_CLIENT_* and JWT_SECRET"),
    "oauth_callback_failure": ("OAuth callback failed", "auth", "Callback or redirect error", "Verify BASE_URL and OAuth redirect URI"),
    "jwt_validation_failure": ("JWT validation failed", "auth", "Invalid or expired token", "Check JWT_SECRET and token expiry"),
    "company_discovery_failure": ("Company discovery failed", "company_discovery_skill", "Discovery step error", "Check discovery skill and inputs"),
    "openai_rate_limit": ("OpenAI rate limit hit", "openai", "429 from API", "Add backoff or reduce request rate"),
    "rate_limit_issue": ("Rate limit exceeded", "middleware", "Redis or in-memory limit", "Adjust rate limits or Redis"),
    "malformed_payload_issue": ("Malformed request payload", "route", "Validation error 422", "Check request body and Pydantic models"),
    "external_api_integration_issue": ("External API integration failed", "integration", "Third-party API error", "Check external service and retries"),
    "analytics_query_failure": ("Analytics NL query execution failed", "nl_query", "SQL execution or pipeline error", "Check nl_query pipeline and DB connectivity"),
    "graph_generation_failure": ("Intelligence graph build failed", "intelligence_graph", "Schema introspection or Redis cache error", "Check db/base and graph_builder"),
    "invalid_sql_generation": ("Generated SQL rejected by validator", "nl_query/query_validator", "Disallowed table or dangerous token", "Review query_validator whitelist and sql_generator"),
    "query_timeout": ("Analytics query timed out", "nl_query", "Query exceeded timeout", "Reduce limit or add indexes"),
    "nl_query_parsing_error": ("NL question parsing failed", "nl_query/question_parser", "Intent extraction error", "Check question_parser and allowed tables"),
    "opportunity_scoring_anomaly": ("Opportunity score anomaly: high score with few signals", "opportunity_engine", "score > 0.95 and signals < 1", "Review scoring weights and signal inputs"),
}


async def analyze_root_cause(
    cluster: Dict[str, Any],
    use_openai: bool = False,
) -> Dict[str, Any]:
    """
    Analyze clustered incident. Infer root_cause, likely_component, technical_summary, suggested_next_step.
    Optionally use OpenAI to summarize.
    """
    etype = cluster.get("error_type", "unknown_error")
    sample = (cluster.get("sample_errors") or [{}])[0]
    msg = sample.get("error_message", "") or sample.get("raw", "")[:300]
    comps = cluster.get("affected_components", [])
    root_cause, likely_component, technical_summary, suggested_next_step = DEFAULT_ROOT_CAUSES.get(
        etype, ("Unknown error", "unknown", msg or "See sample_errors", "Inspect logs and stack traces")
    )
    if comps:
        likely_component = comps[0] if isinstance(comps[0], str) else str(comps[0])

    if use_openai and os.getenv("OPENAI_API_KEY") and _OPENAI_AVAILABLE:
        try:
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            prompt = (
                f"Error type: {etype}. Message: {msg}. Components: {comps}. "
                "In one sentence each: (1) root cause, (2) technical summary, (3) suggested next step. "
                'Return JSON: {"root_cause":"...","technical_summary":"...","suggested_next_step":"..."}'
            )
            resp = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=200,
            )
            import json
            text = (resp.choices[0].message.content or "{}").strip()
            if "```" in text:
                text = text.split("```")[1].replace("json", "").strip()
            data = json.loads(text)
            root_cause = data.get("root_cause", root_cause)
            technical_summary = data.get("technical_summary", technical_summary)
            suggested_next_step = data.get("suggested_next_step", suggested_next_step)
        except Exception as e:
            logger.debug("root_cause OpenAI: %s", e)

    return {
        "root_cause": root_cause,
        "likely_component": likely_component,
        "technical_summary": technical_summary,
        "suggested_next_step": suggested_next_step,
    }
