import logging
import os
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def route_and_call(task_type: str, messages: List[Dict[str, str]], **kwargs: Any) -> Optional[str]:
    """Select model by task and call OpenAI (or other provider)."""
    from src.llm_router.model_registry import get_model_for_task
    model = get_model_for_task(task_type)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning("OPENAI_API_KEY not set")
        return None
    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        r = client.chat.completions.create(model=model, messages=messages, **kwargs)
        return (r.choices[0].message.content or "").strip()
    except Exception as e:
        logger.exception("route_and_call: %s", e)
        return None
