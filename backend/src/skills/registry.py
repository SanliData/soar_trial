"""
SKILLS: registry (backward compatibility)
PURPOSE: Re-export from unified skill_registry
"""
from src.skills.skill_registry import (
    get_skill,
    get_skill_names,
    list_skills,
    register_skill,
)

__all__ = ["register_skill", "get_skill", "list_skills", "get_skill_names"]
