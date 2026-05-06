"""
AGENTS: agent_pipeline
PURPOSE: Orchestrate full flow: User Request -> Context Engine -> Agent Reasoning -> Skill Execution -> Tool Results -> Updated Context -> LLM Response
"""
import logging
from typing import Any, Dict, List, Optional

from src.agents.context_engine import build_context_from_request

logger = logging.getLogger(__name__)


async def run_agent_pipeline(
    user_request: Dict[str, Any],
    *,
    skill_sequence: Optional[List[str]] = None,
    session_id: Optional[str] = None,
    history: Optional[List[Dict[str, Any]]] = None,
    include_llm_response: bool = True,
    trace_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Run the full pipeline:
    1. Context Engine: build context from user request
    2. Agent Reasoning: decide skill sequence (or use provided)
    3. Skill Execution: run skills, merge tool results into context
    4. Updated Context: final context after skills
    5. LLM Response: optional summary/response from updated context
    If trace_id is None, a new execution trace is created and stored in Redis (context["trace_id"]).
    """
    # 1. Context Engine
    context = build_context_from_request(
        user_request,
        session_id=session_id,
        history=history,
    )
    intent = context.get("intent", "unknown")
    entities = context.get("entities", {})

    # Execution trace: create or use provided
    if trace_id is None:
        try:
            from src.agents.execution_trace import create_trace
            trace_id = create_trace(session_id=session_id)
        except Exception:
            trace_id = None
    context["trace_id"] = trace_id
    context["execution_trace"] = {"trace_id": trace_id} if trace_id else None

    # 2. Agent Reasoning: pick skill sequence from intent (or use provided)
    if skill_sequence is None:
        skill_sequence = _reason_skill_sequence(intent, entities, context.get("available_skills", []))
    if trace_id and skill_sequence:
        try:
            from src.agents.execution_trace import append_decision_step
            append_decision_step(trace_id, "skill_sequence", f"intent={intent}", {"skill_sequence": skill_sequence})
        except Exception:
            pass

    # 3. Skill Execution (async pipeline) + 4. Tool Results -> Updated Context
    if not skill_sequence:
        if trace_id:
            try:
                from src.agents.execution_trace import finish_trace
                finish_trace(trace_id, {"intent": intent, "skill_sequence": []})
            except Exception:
                pass
        context["llm_response"] = _build_llm_response(context, user_request) if include_llm_response else None
        return context
    try:
        from src.skills.bootstrap import bootstrap_skills
        bootstrap_skills()
        from src.skills.skill_executor import run_pipeline
        context = await run_pipeline(
            skill_sequence,
            {**entities, **context},
            workflow_id=session_id or "pipeline",
            trace_id=trace_id,
        )
        if trace_id:
            try:
                from src.agents.execution_trace import append_tool_output, finish_trace
                append_tool_output(trace_id, "pipeline", {"companies_count": len(context.get("companies", [])), "run_id": context.get("run_id")}, success=True)
                finish_trace(trace_id, {"intent": intent, "companies_count": len(context.get("companies", []))})
            except Exception:
                pass
    except ImportError:
        try:
            from src.sales_skills.skill_executor import run_skill_sequence
            sync_ctx = run_skill_sequence(skill_sequence, {**entities, **context})
            context.update(sync_ctx)
        except Exception as e:
            logger.warning("agent_pipeline skill execution: %s", e)
            context.setdefault("_errors", []).append(str(e))
        if trace_id:
            try:
                from src.agents.execution_trace import finish_trace
                finish_trace(trace_id, {"intent": intent, "fallback": "sync_skill_sequence"})
            except Exception:
                pass

    # 5. LLM Response (optional)
    if include_llm_response:
        context["llm_response"] = _build_llm_response(context, user_request)

    return context


def _reason_skill_sequence(
    intent: str,
    entities: Dict[str, Any],
    available_skills: List[Dict[str, Any]],
) -> List[str]:
    """Map intent + entities to a list of skill names (agent reasoning)."""
    skill_names = [s.get("name") for s in available_skills if s.get("name")]
    if intent == "lead_generation":
        preferred = [
            "company_discovery",
            "company_analysis",
            "company_filter",
            "decision_maker_detection",
            "contact_enrichment",
            "email_generation",
        ]
        return [s for s in preferred if s in skill_names][:6] or ["company_discovery", "email_generation"]
    if intent == "analytics_query":
        return []   # handled by NL query route
    return []


def _build_llm_response(context: Dict[str, Any], user_request: Dict[str, Any]) -> str:
    """Produce a short natural-language response from updated context (can be replaced by real LLM call)."""
    companies = context.get("companies", [])
    errors = context.get("errors", context.get("_errors", []))
    if errors:
        return f"Completed with issues: {len(errors)} error(s). Results may be partial."
    if companies:
        n = len(companies)
        contacts = sum(len(c.get("contacts", [])) for c in companies)
        return f"Found {n} companies and {contacts} contacts. Outreach content generated."
    return "Pipeline completed. No companies in result."
