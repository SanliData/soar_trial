"""
SKILLS: skill_registry (unified)
PURPOSE: Register and retrieve skills by name; list available skills; auto-register on import
"""
import logging
from typing import Any, Dict, List, Optional, Type

from src.skills.base_skill import BaseSkill

logger = logging.getLogger(__name__)

_registry: Dict[str, BaseSkill] = {}


def register_skill(name: str, skill_class: Type[BaseSkill]) -> None:
    """Register a skill class; instantiated on first use."""
    if not issubclass(skill_class, BaseSkill):
        raise TypeError(f"{skill_class} must extend BaseSkill")
    _registry[name] = skill_class()
    logger.debug("skills: registered %s", name)


def get_skill(name: str) -> Optional[BaseSkill]:
    """Lookup skill by name."""
    return _registry.get(name)


def list_skills() -> List[Dict[str, Any]]:
    """Return specs for all registered skills (for workflow authoring)."""
    return [s.to_spec() for s in _registry.values()]


def get_skill_names() -> List[str]:
    """Return registered skill names."""
    return list(_registry.keys())
