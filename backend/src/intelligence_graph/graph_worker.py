"""
INTELLIGENCE_GRAPH: graph_worker
PURPOSE: Background graph rebuild via Redis queue — startup enqueues job, worker processes it
"""
import asyncio
import json
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

QUEUE_KEY = "intelligence_graph:rebuild_queue"
QUEUE_BLOCK_TIMEOUT = 5  ***REMOVED*** seconds for BRPOP


def _redis():
    try:
        from src.core.cache import get_redis_client
        return get_redis_client()
    except Exception:
        return None


def enqueue_graph_rebuild(payload: Optional[Dict[str, Any]] = None) -> bool:
    """
    Enqueue a graph rebuild job. Call at startup instead of running refresh synchronously.
    """
    r = _redis()
    if not r:
        logger.debug("graph_worker: Redis not available, skip enqueue")
        return False
    try:
        job = {"action": "rebuild", "payload": payload or {}}
        r.lpush(QUEUE_KEY, json.dumps(job))
        logger.info("graph_worker: enqueued graph rebuild")
        return True
    except Exception as e:
        logger.warning("graph_worker: enqueue failed %s", e)
        return False


def process_one_rebuild_job() -> bool:
    """
    Pop one job from the queue and run graph rebuild. Returns True if a job was processed.
    """
    r = _redis()
    if not r:
        return False
    try:
        raw = r.rpop(QUEUE_KEY)
        if not raw:
            return False
        job = json.loads(raw) if isinstance(raw, str) else raw
        if job.get("action") != "rebuild":
            return True
        from src.intelligence_graph.graph_builder import refresh_graph_cache
        refresh_graph_cache()
        logger.info("graph_worker: processed rebuild job")
        return True
    except Exception as e:
        logger.exception("graph_worker: process job failed %s", e)
        return False


async def run_graph_worker_loop(interval_seconds: float = 10.0) -> None:
    """
    Background loop: wait for jobs on Redis queue and process rebuilds.
    Run with asyncio.create_task(run_graph_worker_loop()) after startup.
    """
    while True:
        try:
            process_one_rebuild_job()
        except Exception as e:
            logger.debug("graph_worker loop: %s", e)
        await asyncio.sleep(interval_seconds)


def run_graph_worker_once() -> bool:
    """Process a single rebuild job if one is queued (sync helper for tests or one-shot)."""
    return process_one_rebuild_job()
