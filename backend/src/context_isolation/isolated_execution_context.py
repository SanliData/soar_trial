"""
MODULE: isolated_execution_context
PURPOSE: Minimal isolated execution context schema (H-044)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class IsolatedExecutionContext:
    workflow_scope: str
    subagent_id: str
    allowed_context_types: tuple[str, ...]
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    auditable: bool = True
    shared_memory_allowed: bool = False

