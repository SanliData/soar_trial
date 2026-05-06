import logging
from typing import Optional

logger = logging.getLogger(__name__)

TASK_MODEL = {
    "classification": "gpt-3.5-turbo",
    "parsing": "gpt-3.5-turbo",
    "email_generation": "gpt-4",
    "strategy_generation": "gpt-4",
    "default": "gpt-3.5-turbo",
}


def get_model_for_task(task_type: str) -> str:
    """Map task to model: classification/parsing -> cheap; email_generation/strategy -> high quality."""
    return TASK_MODEL.get(task_type, TASK_MODEL["default"])
