"""
INTELLIGENCE_GRAPH: graph edge model
PURPOSE: Represents a foreign key relationship (for join path planning)
"""
from typing import Optional

from pydantic import BaseModel, Field


class GraphEdge(BaseModel):
    """Foreign key as edge: from_table -> to_table."""
    from_table: str = Field(..., description="Table containing the FK")
    to_table: str = Field(..., description="Referenced table")
    from_column: str = Field(..., description="FK column in from_table")
    to_column: str = Field(..., description="Referenced column (usually PK) in to_table")
    edge_name: Optional[str] = Field(None, description="Optional relationship name")
