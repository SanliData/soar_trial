"""
INTELLIGENCE_GRAPH: relationship_extractor
PURPOSE: Extract foreign key relationships (edges) from SQLAlchemy metadata
"""
import logging
from typing import List

from src.db.base import Base
from src.intelligence_graph.models.graph_edge import GraphEdge

logger = logging.getLogger(__name__)


def extract_foreign_keys() -> List[GraphEdge]:
    """Extract all FK relationships from registered models; return as GraphEdge list."""
    edges = []
    try:
        for table_name, table in Base.metadata.tables.items():
            for fk in table.foreign_keys:
                try:
                    to_table = fk.column.table.name
                    to_column = fk.column.name
                    from_column = fk.parent.name
                    if table_name != to_table:
                        edges.append(GraphEdge(
                            from_table=table_name,
                            to_table=to_table,
                            from_column=from_column,
                            to_column=to_column,
                            edge_name=f"{table_name}.{from_column} -> {to_table}.{to_column}",
                        ))
                except Exception as e:
                    logger.debug("relationship_extractor skip FK: %s", e)
        logger.info("relationship_extractor: extracted %s edges", len(edges))
    except Exception as e:
        logger.warning("relationship_extractor failed: %s", e)
    return edges
