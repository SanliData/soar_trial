"""
MODULE: runtime_context_validation_service
PURPOSE: Validate snapshot payloads and context budget requests (H-030)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from pydantic import BaseModel, Field

***REMOVED*** Prevent uncontrolled context expansion via oversized POST bodies.
MAX_LARGE_TEXT_CHARS = 256_000
MAX_ESTIMATED_CHARS_FIELD = 10_000_000


class ContextBudgetRequest(BaseModel):
    estimated_chars: int = Field(default=0, ge=0, le=MAX_ESTIMATED_CHARS_FIELD)
    requested_layers: list[str] = Field(default_factory=list)
    large_text_sample: str = Field(default="", max_length=MAX_LARGE_TEXT_CHARS)
