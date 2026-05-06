"""
MODULE: capability_loader
PURPOSE: Load and validate deterministic capability bundles (H-020)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Optional

from src.semantic_capabilities.capability_registry import CAPABILITY_DEFINITIONS
from src.semantic_capabilities.capability_schema import CapabilityDefinition
from src.semantic_capabilities.capability_validation import validate_capability_definitions

_sorted_cache: Optional[list[CapabilityDefinition]] = None


def load_capabilities() -> list[CapabilityDefinition]:
    """
    Validate registry once per process then return deterministic sorted view.
    """
    global _sorted_cache  ***REMOVED*** noqa: PLW0603 process-level memo for hot exporter path
    if _sorted_cache is None:
        validate_capability_definitions(list(CAPABILITY_DEFINITIONS))
        _sorted_cache = sorted(CAPABILITY_DEFINITIONS, key=lambda c: c.capability_id)
    return list(_sorted_cache)


def invalidate_capability_cache_for_tests() -> None:
    global _sorted_cache  ***REMOVED*** noqa: PLW0603
    _sorted_cache = None
