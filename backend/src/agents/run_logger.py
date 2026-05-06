"""
AGENTS: run_logger
PURPOSE: Log workflow steps to PostgreSQL (agent_run_id, workflow_step, token_usage, latency, errors)
"""
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def log_step(
    agent_run_id: str,
    workflow_step: str,
    token_usage: Optional[Dict[str, Any]] = None,
    latency_ms: Optional[int] = None,
    error_message: Optional[str] = None,
) -> None:
    """Write one step log to PostgreSQL. Fail silently if DB unavailable."""
    try:
        from src.db.base import SessionLocal
        from src.models.agent_run_log import AgentRunLog
        db = SessionLocal()
        try:
            log = AgentRunLog(
                agent_run_id=agent_run_id,
                workflow_step=workflow_step,
                token_usage=token_usage,
                latency_ms=latency_ms,
                error_message=error_message,
            )
            db.add(log)
            db.commit()
        finally:
            db.close()
    except Exception as e:
        logger.warning("agent run_logger: could not persist step to DB: %s", e)


def upsert_run(
    agent_run_id: str,
    workflow_type: str,
    status: str,
    input_payload: Optional[Dict[str, Any]] = None,
    output_payload: Optional[Dict[str, Any]] = None,
) -> None:
    """Create or update AgentRun row."""
    try:
        from src.db.base import SessionLocal
        from src.models.agent_run_log import AgentRun
        db = SessionLocal()
        try:
            run = db.query(AgentRun).filter(AgentRun.agent_run_id == agent_run_id).first()
            if run:
                run.status = status
                run.output_payload = output_payload
            else:
                run = AgentRun(
                    agent_run_id=agent_run_id,
                    workflow_type=workflow_type,
                    status=status,
                    input_payload=input_payload,
                    output_payload=output_payload,
                )
                db.add(run)
            db.commit()
        finally:
            db.close()
    except Exception as e:
        logger.warning("agent run_logger: could not upsert run to DB: %s", e)
