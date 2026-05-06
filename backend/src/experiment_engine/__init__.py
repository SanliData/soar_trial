"""
EXPERIMENT_ENGINE: A/B testing for email templates, subject lines, persona targeting, message tone
"""
from src.experiment_engine.experiment_manager import (
    get_experiment,
    register_experiment,
    list_experiments,
)
from src.experiment_engine.variant_allocator import allocate_variant, get_variant_for_campaign
from src.experiment_engine.performance_tracker import (
    record_event,
    get_metrics,
    get_experiment_metrics,
)

__all__ = [
    "get_experiment",
    "register_experiment",
    "list_experiments",
    "allocate_variant",
    "get_variant_for_campaign",
    "record_event",
    "get_metrics",
    "get_experiment_metrics",
]
