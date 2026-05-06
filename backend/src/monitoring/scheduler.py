"""
MONITORING: scheduler
PURPOSE: Run monitoring agent every 5 minutes via background task; non-blocking; callable manually
"""
import asyncio
import logging
import os
from typing import Optional

from src.monitoring.monitoring_agent import run_monitoring_agent

logger = logging.getLogger(__name__)

INTERVAL_SECONDS = 60 * 5   # 5 minutes
_task: Optional[asyncio.Task] = None


async def _run_loop() -> None:
    while True:
        try:
            await asyncio.sleep(INTERVAL_SECONDS)
            if not os.getenv("MONITORING_AGENT_ENABLED", "").lower() in ("1", "true", "yes"):
                continue
            logger.info("monitoring scheduler: running agent")
            await run_monitoring_agent()
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.exception("monitoring scheduler loop: %s", e)


def start_scheduler() -> None:
    """Start background scheduler (call from app startup if MONITORING_AGENT_ENABLED)."""
    global _task
    if os.getenv("MONITORING_AGENT_ENABLED", "").lower() not in ("1", "true", "yes"):
        return
    if _task is not None and not _task.done():
        return
    _task = asyncio.create_task(_run_loop())
    logger.info("monitoring scheduler started (interval=%ss)", INTERVAL_SECONDS)


def stop_scheduler() -> None:
    """Cancel background scheduler."""
    global _task
    if _task and not _task.done():
        _task.cancel()
    _task = None
