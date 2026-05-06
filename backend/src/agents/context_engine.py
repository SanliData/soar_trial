# Context Engine: build enriched context from user request for Agent Reasoning
# Flow: User Request -> Context Engine -> Agent Reasoning -> Skill Execution -> Tool Results -> Updated Context -> LLM Response
# Phase 2: execution_trace layer for skill calls, tool outputs, decision steps (stored in Redis)
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def build_context_from_request(
    user_request: Dict[str, Any],
    *,
    available_skills: Optional[List[Dict[str, Any]]] = None,
    session_id: Optional[str] = None,
    history: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Transform user request into structured context for the agent."""
    context = {
        "user_request": user_request,
        "intent": _infer_intent(user_request),
        "entities": _extract_entities(user_request),
        "session_id": session_id,
        "history": history or [],
        "execution_trace": None,   # Set by agent_pipeline when trace_id is created
    }
    if available_skills is not None:
        context["available_skills"] = available_skills
    else:
        try:
            from src.skills.registry import list_skills
            context["available_skills"] = list_skills()
        except Exception as e:
            logger.debug("context_engine: list_skills: %s", e)
            context["available_skills"] = []
    return context


def _infer_intent(request: Dict[str, Any]) -> str:
    intent = request.get("intent") or request.get("action")
    if intent:
        return str(intent).strip().lower()
    if request.get("industry") or request.get("location"):
        return "lead_generation"
    if request.get("question") or request.get("query"):
        return "analytics_query"
    return "unknown"


def _extract_entities(request: Dict[str, Any]) -> Dict[str, Any]:
    entities = {}
    for key in ("industry", "location", "keywords", "target_roles", "decision_roles", "campaign_goal", "company_size", "limit", "question"):
        if key in request and request[key] is not None:
            entities[key] = request[key]
    return entities


def build_layered_context(
    user_request: Dict[str, Any],
    *,
    instructions: Optional[List[str]] = None,
    examples: Optional[List[Dict[str, Any]]] = None,
    knowledge: Optional[Dict[str, Any]] = None,
    memory: Optional[List[Dict[str, Any]]] = None,
    tools: Optional[List[Dict[str, Any]]] = None,
    tool_results: Optional[List[Dict[str, Any]]] = None,
    market_intelligence: Optional[Dict[str, Any]] = None,
    session_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Build agent context with structured layers (order: instructions, examples, knowledge, memory, tools, tool_results, market_intelligence).
    Agents receive context in this order for consistent reasoning.
    """
    base = build_context_from_request(user_request, session_id=session_id)
    layers = {
        "instructions": instructions or [],
        "examples": examples or [],
        "knowledge": knowledge or {},
        "memory": memory or [],
        "tools": tools or base.get("available_skills", []),
        "tool_results": tool_results or [],
        "market_intelligence": market_intelligence or {},
        "execution_trace": base.get("execution_trace"),
    }
    if not layers["market_intelligence"]:
        try:
            from src.market_signals.signal_detector import detect_signals
            entities = base.get("entities", {})
            layers["market_intelligence"] = {"signals": detect_signals(industry=entities.get("industry"), region=entities.get("location"))}
        except Exception:
            pass
    base["context_layers"] = layers
    return base
