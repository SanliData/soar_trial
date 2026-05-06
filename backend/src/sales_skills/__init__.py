"""
SALES_SKILLS: Self-Learning Sales Operating System — reusable sales capabilities
PURPOSE: Skills implement run(context) -> dict; executor runs sequences with shared context
"""
from src.sales_skills.base_skill import BaseSkill
from src.sales_skills.skill_registry import register_skill, get_skill, list_skills, get_skill_names
from src.sales_skills.skill_executor import SkillExecutor, run_skill_sequence
from src.sales_skills.register_all import register_all_sales_skills

# Register built-in skills when package is imported
register_all_sales_skills()

__all__ = [
    "BaseSkill",
    "register_skill",
    "get_skill",
    "list_skills",
    "get_skill_names",
    "SkillExecutor",
    "run_skill_sequence",
    "register_all_sales_skills",
]
