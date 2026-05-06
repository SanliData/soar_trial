"""
PACKAGE: runtime_context
PURPOSE: Backend context engineering & structured runtime metadata (H-030)
ENCODING: UTF-8 WITHOUT BOM
"""

from src.runtime_context.context_trace_service import get_context_trace_store, reset_context_trace_store_for_tests

__all__ = [
    "get_context_trace_store",
    "reset_context_trace_store_for_tests",
]
