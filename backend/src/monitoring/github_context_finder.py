"""
MONITORING: github_context_finder
PURPOSE: Infer likely source files from stack traces, module names, endpoints, workflow names (no GitHub API)
"""
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

***REMOVED*** Known app structure for SOARB2B (real paths under backend/src/)
PREFIX = "backend/src/"
MODULE_TO_PATH = {
    "lead_generation_workflow": "workflows/lead_generation_workflow.py",
    "company_discovery": "skills/discovery/company_discovery_skill.py",
    "company_discovery_skill": "skills/discovery/company_discovery_skill.py",
    "company_analysis": "skills/discovery/company_analysis_skill.py",
    "company_analysis_skill": "skills/discovery/company_analysis_skill.py",
    "company_filter": "skills/discovery/company_filter_skill.py",
    "company_filter_skill": "skills/discovery/company_filter_skill.py",
    "decision_maker_detection": "skills/persona/decision_maker_detection_skill.py",
    "decision_maker_detection_skill": "skills/persona/decision_maker_detection_skill.py",
    "persona_detection": "agents/skills/persona_detection.py",
    "contact_enrichment": "skills/enrichment/contact_enrichment_skill.py",
    "contact_enrichment_skill": "skills/enrichment/contact_enrichment_skill.py",
    "email_generation": "skills/outreach/email_generation_skill.py",
    "email_generation_skill": "skills/outreach/email_generation_skill.py",
    "followup_generation": "skills/outreach/followup_generation_skill.py",
    "followup_generation_skill": "skills/outreach/followup_generation_skill.py",
    "campaign_creation": "agents/skills/campaign_creation.py",
    "outreach_queue": "automation/outreach_queue.py",
    "agents/skills/outreach_queue": "agents/skills/outreach_queue.py",
    "campaign_engine": "automation/campaign_engine.py",
    "response_classifier": "automation/response_classifier.py",
    "response_engine": "automation/response_engine.py",
    "followup_engine": "automation/followup_engine.py",
    "learning_engine": "learning/learning_engine.py",
    "skill_executor": "skills/skill_executor.py",
    "sales_engine_workflow": "agents/workflows/sales_engine_workflow.py",
    "run_logger": "agents/run_logger.py",
    "app": "app.py",
    "nl_query": "nl_query/question_parser.py",
    "question_parser": "nl_query/question_parser.py",
    "graph_sql_planner": "nl_query/graph_sql_planner.py",
    "sql_generator": "nl_query/sql_generator.py",
    "query_validator": "nl_query/query_validator.py",
    "graph_builder": "intelligence_graph/graph_builder.py",
    "intelligence_graph": "intelligence_graph/graph_query_engine.py",
}
***REMOVED*** Real FastAPI route prefixes (for affected_endpoint context)
ENDPOINT_TO_ROUTE = {
    "/agents/lead-generation": "agents_router",
    "/agents/sales-engine/run": "agents_router",
    "/agents/runs": "agents_router",
    "/ai-sales/run-agent": "ai_sales_router",
    "/sales/run-lead-workflow": "sales_engine_router",
    "/skills/run-lead-workflow": "skills_router",
    "/learning/insights": "learning_router",
    "/learning/recommendations": "learning_router",
    "/learning/analyze-campaign": "learning_router",
    "/monitoring/run": "monitoring_router",
    "/admin": "admin_router",
    "/analytics/query": "analytics_router",
}
RE_FILE = re.compile(r"[\w/\\]+\.py")


def find_likely_files(
    cluster: Dict[str, Any],
    sample_events: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Infer likely source files from module names, affected_components, and raw stack traces.
    Returns { likely_files: [ "backend/src/...", ... ] }.
    """
    files = set()
    comps = cluster.get("affected_components") or []
    for c in comps:
        name = (c if isinstance(c, str) else str(c)).replace(".py", "")
        path = MODULE_TO_PATH.get(name)
        if path:
            files.add(PREFIX + path)
        if ".py" in str(c):
            files.add(PREFIX + c.replace("\\", "/"))
    samples = sample_events or cluster.get("sample_errors", [])
    for s in samples:
        raw = s.get("raw") or s.get("error_message") or ""
        for m in RE_FILE.findall(raw):
            if "src" in m or ".py" in m:
                p = m.replace("\\", "/")
                if not p.startswith("backend/"):
                    p = PREFIX + p.split("src/")[-1] if "src/" in p else PREFIX + p
                files.add(p)
        mod = s.get("module")
        if mod:
            if not mod.startswith("backend/"):
                mod = PREFIX + mod
            files.add(mod.replace("\\", "/"))
    etype = cluster.get("error_type", "")
    for key, path in MODULE_TO_PATH.items():
        if key in etype or key in str(comps):
            files.add(PREFIX + path)
    result = sorted(files)[:15]
    return {"likely_files": result}
