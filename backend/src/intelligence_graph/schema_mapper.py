"""
INTELLIGENCE_GRAPH: schema_mapper
PURPOSE: Map SQLAlchemy metadata to graph nodes (tables) and column lists
"""
import logging
from typing import Any, Dict, List

from src.intelligence_graph.models.graph_node import GraphNode

logger = logging.getLogger(__name__)


def get_tables_from_metadata() -> List[GraphNode]:
    """Build graph nodes from SQLAlchemy Base.metadata (all registered tables)."""
    from src.db.base import Base
    nodes = []
    for table_name, table in Base.metadata.tables.items():
        columns = [c.name for c in table.c]
        pk = None
        for c in table.primary_key:
            pk = c.name
            break
        nodes.append(GraphNode(
            table_name=table_name,
            primary_key=pk,
            columns=columns,
            description=f"Table {table_name}",
        ))
    logger.info("schema_mapper: mapped %s tables to nodes", len(nodes))
    return nodes
