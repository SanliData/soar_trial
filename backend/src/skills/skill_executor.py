"""
SKILLS: skill_executor (unified)
PURPOSE: Execute skills sequentially with shared context; async run
"""
import asyncio
import logging
import time
import uuid
from typing import Any, Dict, List, Optional

from src.skills.skill_registry import get_skill

logger = logging.getLogger(__name__)


def _log_skill_run(
    run_id: str,
    skill_name: str,
    execution_time_ms: int,
    token_usage: Optional[Dict[str, Any]] = None,
    error_message: Optional[str] = None,
    workflow_id: Optional[str] = None,
) -> None:
    try:
        from src.models.skill_execution_log import SkillExecutionLog
        from src.db.base import SessionLocal
        db = SessionLocal()
        try:
            db.add(SkillExecutionLog(
                workflow_id=workflow_id,
                run_id=run_id,
                skill_name=skill_name,
                execution_time_ms=execution_time_ms,
                token_usage=token_usage,
                error_message=error_message,
            ))
            db.commit()
        finally:
            db.close()
    except Exception as e:
        logger.debug("skill_executor log failed: %s", e)


async def run_sequence(
    skill_names: List[str],
    context: Dict[str, Any],
    run_id: Optional[str] = None,
    workflow_id: Optional[str] = None,
    trace_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Execute skills in order; merge each result into context; return final context.
    Each skill must implement async run(context) -> dict.
    If trace_id is set, each skill call is appended to the execution trace (Redis).
    """
    run_id = run_id or f"skill_run_{uuid.uuid4().hex[:12]}"
    workflow_id = workflow_id or run_id
    ctx = dict(context)
    for name in skill_names:
        skill = get_skill(name)
        if not skill:
            logger.warning("skill_executor: unknown skill %s, skipping", name)
            _log_skill_run(run_id, name, 0, error_message="skill not found", workflow_id=workflow_id)
            continue
        t0 = time.perf_counter()
        token_usage = None
        error_message = None
        result = None
        try:
            result = await skill.run(ctx)
            if isinstance(result, dict):
                ctx.update(result)
            token_usage = result.get("token_usage") if isinstance(result, dict) else None
        except Exception as e:
            logger.exception("skill_executor: %s failed: %s", name, e)
            error_message = str(e)
            ctx.setdefault("_errors", []).append({"skill": name, "error": str(e)})
        execution_time_ms = int((time.perf_counter() - t0) * 1000)
        _log_skill_run(run_id, name, execution_time_ms, token_usage=token_usage, error_message=error_message, workflow_id=workflow_id)
        if trace_id:
            try:
                from src.agents.execution_trace import append_skill_call
                inputs_summary = {k: v for k, v in ctx.items() if k not in ("_errors", "run_id") and not k.startswith("_")}
                if len(str(inputs_summary)) > 1500:
                    inputs_summary = {"_keys": list(inputs_summary.keys()), "_truncated": True}
                out_summary = {}
                if isinstance(result, dict):
                    out_summary = {k: v for k, v in result.items() if k != "token_usage"}
                    if len(str(out_summary)) > 1000:
                        out_summary = {"_keys": list(out_summary.keys()), "_truncated": True}
                append_skill_call(trace_id, name, inputs_summary, out_summary, execution_time_ms)
            except Exception as te:
                logger.debug("execution_trace append_skill_call: %s", te)
    ctx["run_id"] = run_id
    return ctx


async def run_pipeline(
    skill_names: List[str],
    initial_context: Dict[str, Any],
    run_id: Optional[str] = None,
    workflow_id: Optional[str] = None,
    trace_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Alias for run_sequence (backward compatibility)."""
    return await run_sequence(
        skill_names, initial_context, run_id=run_id, workflow_id=workflow_id, trace_id=trace_id
    )
