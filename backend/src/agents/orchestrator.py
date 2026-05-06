"""
AGENTS: orchestrator
PURPOSE: Run agent skills sequentially with logging; extensible for future workflows
"""
import logging
from typing import Any, Awaitable, Callable, Dict, List

logger = logging.getLogger(__name__)


async def run_sequence(
    initial_context: Dict[str, Any],
    steps: List[tuple[str, Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]],
) -> Dict[str, Any]:
    """
    Run each step sequentially; each step receives context and returns updated context.
    Logs each step; on exception logs and re-raises so caller can fail gracefully.
    """
    context = dict(initial_context)
    for name, step_fn in steps:
        logger.info("orchestrator: step start name=%s", name)
        try:
            context = await step_fn(context)
            logger.info("orchestrator: step done name=%s", name)
        except Exception as e:
            logger.exception("orchestrator: step failed name=%s error=%s", name, e)
            raise
    return context
