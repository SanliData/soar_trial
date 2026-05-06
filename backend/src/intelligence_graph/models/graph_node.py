"""
INTELLIGENCE_GRAPH: graph node model
PURPOSE: Represents a table in the schema graph (for join path planning)
"""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class GraphNode(BaseModel):
    """Table as node in the schema graph."""
    table_name: str = Field(..., description="Database table name")
    primary_key: Optional[str] = Field(None, description="Primary key column name")
    columns: List[str] = Field(default_factory=list, description="Column names")
    description: Optional[str] = Field(None, description="Human-readable description")
    metadata: Dict[str, Any] = Field(default_factory=dict)
