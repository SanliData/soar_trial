"""
FILE: backend/src/growth_activation/__init__.py
PURPOSE: Public exports for Growth & Activation core
ENCODING: UTF-8 WITHOUT BOM
"""

from .supply_sources import Supplier, SupplierCategory
from .geo_targeting_rules import GeoTargetingConfig, GeoTargetingRule, meters_between
from .activation_events import LeadCandidate, ActivationDecision, decide_activation

__all__ = [
    "Supplier",
    "SupplierCategory",
    "GeoTargetingConfig",
    "GeoTargetingRule",
    "meters_between",
    "LeadCandidate",
    "ActivationDecision",
    "decide_activation",
]
