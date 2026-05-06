"""
MODULE: harness_validation_service
PURPOSE: Validate harness-bound requests (H-031)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

from src.agent_harness.memory_registry import MEMORY_TYPES


class HarnessCompressRequest(BaseModel):
    mode: Literal["context", "trajectory", "memory"] = "context"
    payload: str = Field(default="", max_length=512_000)
    memory_type: Optional[str] = None
    trajectory_steps: Optional[list[str]] = None


def validate_memory_type(memory_type: str) -> None:
    if memory_type not in MEMORY_TYPES:
        raise ValueError(f"invalid memory_type: {memory_type}")


def validate_harness_topology(nodes: list[str]) -> None:
    allowed = {"memory", "skills", "protocols", "evaluation", "compression"}
    for n in nodes:
        if n not in allowed:
            raise ValueError(f"invalid harness topology node: {n}")
