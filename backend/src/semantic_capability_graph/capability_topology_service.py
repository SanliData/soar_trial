"""
MODULE: capability_topology_service
PURPOSE: Explainable topology derived from static registry + edges (H-034)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from src.semantic_capability_graph.capability_graph_registry import (
    SEMANTIC_CAPABILITY_ENTITIES,
    export_entity_registry,
)
from src.semantic_capability_graph.capability_relationship_service import (
    SEMANTIC_RELATIONSHIPS,
    export_relationships,
)


def get_capability_graph() -> dict[str, Any]:
    reg = export_entity_registry()
    rel = export_relationships()
    return {
        "nodes": reg["entities"],
        "edges": rel["edges"],
        "relationship_types": rel["relationship_types"],
    }


def summarize_topology() -> dict[str, Any]:
    nodes = sorted(SEMANTIC_CAPABILITY_ENTITIES.keys())
    indeg = defaultdict(int)
    outdeg = defaultdict(int)
    for s, _, t in SEMANTIC_RELATIONSHIPS:
        outdeg[s] += 1
        indeg[t] += 1
    return {
        "node_count": len(nodes),
        "edge_count": len(SEMANTIC_RELATIONSHIPS),
        "sources": sorted([n for n in nodes if outdeg[n] > 0]),
        "sinks": sorted([n for n in nodes if indeg[n] > 0 and outdeg[n] == 0]),
        "rule": "degree_summary_v1",
    }


def list_dependency_paths(root: str = "workflow_governance") -> dict[str, Any]:
    if root not in SEMANTIC_CAPABILITY_ENTITIES:
        raise ValueError(f"unknown root capability: {root}")
    paths: list[list[str]] = []
    stack: list[tuple[str, list[str]]] = [(root, [root])]
    seen_path_end: set[tuple[str, ...]] = set()
    while stack:
        node, acc = stack.pop()
        for s, r, t in SEMANTIC_RELATIONSHIPS:
            if s == node and r == "depends_on":
                nxt = acc + [t]
                key = tuple(nxt)
                if key in seen_path_end:
                    continue
                seen_path_end.add(key)
                paths.append(nxt)
                stack.append((t, nxt))
    paths.sort(key=lambda p: (len(p), p))
    return {"root": root, "relationship": "depends_on", "paths": paths[:50]}


def list_trust_paths(root: str = "agent_security") -> dict[str, Any]:
    if root not in SEMANTIC_CAPABILITY_ENTITIES:
        raise ValueError(f"unknown root capability: {root}")
    paths = []
    for s, r, t in SEMANTIC_RELATIONSHIPS:
        if r in ("trusted_by", "secured_by") and (s == root or t == root):
            paths.append([s, r, t])
    paths.sort()
    return {"root": root, "trust_edges": paths, "rule": "static_trust_scan_v1"}
