"""
SALES_SKILLS: skill_executor
PURPOSE: Run a sequence of skills with a shared workflow context
"""
import logging
from typing import Any, Dict, List

from src.sales_skills.skill_registry import get_skill

logger = logging.getLogger(__name__)


class SkillExecutor:
    """Runs a sequence of skills; merges each skill result into shared context."""

    def __init__(self, skill_names: List[str]):
        self.skill_names = skill_names

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute skills in order; merge each result into context; return final context."""
        ctx = dict(context)
        for name in self.skill_names:
            skill = get_skill(name)
            if not skill:
                logger.warning("skill_executor: unknown skill %s, skipping", name)
                continue
            try:
                result = skill.run(ctx)
                if result:
                    ctx.update(result)
            except Exception as e:
                logger.exception("skill_executor: %s failed: %s", name, e)
                ctx.setdefault("_errors", []).append({"skill": name, "error": str(e)})
        return ctx


def run_skill_sequence(skill_names: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience: run a sequence of skills with the given context."""
    return SkillExecutor(skill_names).run(context)
