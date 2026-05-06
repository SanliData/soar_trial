"""
MODULE: model_routing_service
PURPOSE: Deterministic placeholder routing by task type + quality tier (H-021)
ENCODING: UTF-8 WITHOUT BOM
"""

from typing import TypedDict

from src.ai_runtime.runtime_schema import AIRuntimeTask, QualityTierLiteral, TaskTypeLiteral


class RoutedModel(TypedDict):
    selected_model: str
    model_family: str
    quality_tier: QualityTierLiteral


_TIER_DEFAULTS: dict[QualityTierLiteral, RoutedModel] = {
    "economy": {"selected_model": "economy-reasoner", "model_family": "placeholder-economy", "quality_tier": "economy"},
    "standard": {"selected_model": "standard-reasoner", "model_family": "placeholder-standard", "quality_tier": "standard"},
    "premium": {"selected_model": "premium-reasoner", "model_family": "placeholder-premium", "quality_tier": "premium"},
}


def route_model(task: AIRuntimeTask) -> RoutedModel:
    """
    Choose placeholder model metadata without contacting external APIs.
    Explicit mapping rules override tier defaults when applicable.
    """
    pref = (task.preferred_model or "").strip()
    if pref:
        return {
            "selected_model": pref,
            "model_family": "custom-preference",
            "quality_tier": task.requested_quality_tier,
        }

    tt: TaskTypeLiteral = task.task_type
    tier: QualityTierLiteral = task.requested_quality_tier

    if tt == "graph_reasoning" and tier == "premium":
        return {
            "selected_model": "premium-reasoner",
            "model_family": "placeholder-premium",
            "quality_tier": "premium",
        }
    if tt == "generative_ui_widget" and tier == "standard":
        return {
            "selected_model": "standard-reasoner",
            "model_family": "placeholder-standard",
            "quality_tier": "standard",
        }
    if tt == "analytics_summary" and tier == "economy":
        return {
            "selected_model": "economy-reasoner",
            "model_family": "placeholder-economy",
            "quality_tier": "economy",
        }

    base = _TIER_DEFAULTS[tier]
    return dict(base)
