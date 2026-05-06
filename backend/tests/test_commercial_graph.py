"""
TEST: commercial_graph (H-026)
PURPOSE: Deterministic entities, relationships, traversal, confidence
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

from src.app import create_app

os.environ.setdefault("JWT_SECRET", "test-h026-jwt-secret-32characters-required!")
os.environ["SOARB2B_API_KEYS"] = "test-h026-graph-key"

from src.commercial_graph.commercial_graph_builder import (
    clear_graph_for_tests,
    create_entity,
    create_relationship,
)
from src.commercial_graph.entity_schema import (
    CreateCommercialEntityRequest,
    CreateCommercialRelationshipRequest,
)
from src.commercial_graph.graph_confidence_service import compute_relationship_confidence
from src.commercial_graph.graph_reasoning_service import explain_relationship
from src.commercial_graph.graph_traversal_service import get_relationship_path
from src.commercial_graph.relationship_registry import validate_relationship_type

clear_graph_for_tests()
app = create_app()
client = TestClient(app)

BASE = "/api/v1/system/graph"


@pytest.fixture(autouse=True)
def _reset_graph():
    clear_graph_for_tests()
    yield


def test_valid_entity_accepted():
    r = client.post(
        f"{BASE}/entity",
        json={
            "entity_type": "company",
            "name": "Acme",
            "authority_score": 0.8,
            "freshness_days": 10,
        },
    )
    assert r.status_code == 200
    assert r.json()["deterministic_graph"] is True
    assert r.json()["entity"]["entity_type"] == "company"


def test_invalid_entity_type_rejected():
    r = client.post(
        f"{BASE}/entity",
        json={
            "entity_type": "unknown_kind",
            "name": "x",
            "authority_score": 0.5,
            "freshness_days": 1,
        },
    )
    assert r.status_code == 422


def test_valid_relationship_accepted():
    a = client.post(
        f"{BASE}/entity",
        json={
            "entity_type": "company",
            "name": "A",
            "authority_score": 0.9,
            "freshness_days": 5,
            "tags": ["x"],
        },
    ).json()["entity"]
    b = client.post(
        f"{BASE}/entity",
        json={
            "entity_type": "contractor",
            "name": "B",
            "authority_score": 0.85,
            "freshness_days": 6,
            "tags": ["x"],
        },
    ).json()["entity"]
    r = client.post(
        f"{BASE}/relationship",
        json={
            "source_entity_id": a["entity_id"],
            "target_entity_id": b["entity_id"],
            "relationship_type": "partners_with",
            "evidence_sources": ["annual_report", "registry"],
        },
    )
    assert r.status_code == 200
    assert r.json()["relationship"]["confidence_score"] >= 0.0


def test_invalid_relationship_type_rejected():
    u1 = client.post(
        f"{BASE}/entity",
        json={
            "entity_type": "utility",
            "name": "U1",
            "authority_score": 0.7,
            "freshness_days": 2,
        },
    ).json()["entity"]
    u2 = client.post(
        f"{BASE}/entity",
        json={
            "entity_type": "utility",
            "name": "U2",
            "authority_score": 0.71,
            "freshness_days": 2,
        },
    ).json()["entity"]
    r = client.post(
        f"{BASE}/relationship",
        json={
            "source_entity_id": u1["entity_id"],
            "target_entity_id": u2["entity_id"],
            "relationship_type": "ghost_link",
            "evidence_sources": [],
        },
    )
    assert r.status_code == 422


def test_traversal_deterministic():
    ids = []
    for name, et in [("N1", "municipality"), ("N2", "company"), ("N3", "utility")]:
        ent = client.post(
            f"{BASE}/entity",
            json={"entity_type": et, "name": name, "authority_score": 0.8, "freshness_days": 3},
        ).json()["entity"]
        ids.append(ent["entity_id"])
    client.post(
        f"{BASE}/relationship",
        json={
            "source_entity_id": ids[0],
            "target_entity_id": ids[1],
            "relationship_type": "operates_in",
            "evidence_sources": ["a"],
        },
    )
    client.post(
        f"{BASE}/relationship",
        json={
            "source_entity_id": ids[1],
            "target_entity_id": ids[2],
            "relationship_type": "supplies",
            "evidence_sources": ["b"],
        },
    )
    r1 = client.get(f"{BASE}/traverse?entity_id={ids[0]}&depth=3")
    r2 = client.get(f"{BASE}/traverse?entity_id={ids[0]}&depth=3")
    assert r1.status_code == 200
    assert r1.json()["connected"]["visited_entity_ids"] == r2.json()["connected"]["visited_entity_ids"]


def test_confidence_scoring_deterministic():
    clear_graph_for_tests()
    ea = create_entity(
        CreateCommercialEntityRequest(
            entity_type="company",
            name="C1",
            authority_score=0.8,
            freshness_days=10,
        )
    )
    eb = create_entity(
        CreateCommercialEntityRequest(
            entity_type="company",
            name="C2",
            authority_score=0.8,
            freshness_days=10,
            tags=["t"],
        )
    )
    c1 = compute_relationship_confidence(
        source=ea,
        target=eb,
        relationship_type="related_to",
        evidence_sources=["e1"],
        repetition_count=0,
    )
    c2 = compute_relationship_confidence(
        source=ea,
        target=eb,
        relationship_type="related_to",
        evidence_sources=["e1"],
        repetition_count=0,
    )
    assert c1 == c2


def test_registry_validation():
    validate_relationship_type("supplies")
    with pytest.raises(ValueError):
        validate_relationship_type("unknown")


def test_explain_relationship_works():
    a = client.post(
        f"{BASE}/entity",
        json={"entity_type": "company", "name": "X", "authority_score": 0.9, "freshness_days": 1},
    ).json()["entity"]
    b = client.post(
        f"{BASE}/entity",
        json={"entity_type": "procurement_project", "name": "P", "authority_score": 0.85, "freshness_days": 2},
    ).json()["entity"]
    rel = client.post(
        f"{BASE}/relationship",
        json={
            "source_entity_id": a["entity_id"],
            "target_entity_id": b["entity_id"],
            "relationship_type": "funds_project",
            "evidence_sources": ["budget_doc"],
        },
    ).json()["relationship"]
    exp = explain_relationship(rel["relationship_id"])
    assert exp["relationship_type"] == "funds_project"
    assert "registry_semantics" in exp
    assert exp["confidence_factors"]["authority_blend"] >= 0.0


def test_path_finding():
    clear_graph_for_tests()
    e1 = create_entity(
        CreateCommercialEntityRequest(entity_type="company", name="a", authority_score=0.7, freshness_days=1)
    )
    e2 = create_entity(
        CreateCommercialEntityRequest(entity_type="company", name="b", authority_score=0.7, freshness_days=1)
    )
    e3 = create_entity(
        CreateCommercialEntityRequest(entity_type="company", name="c", authority_score=0.7, freshness_days=1)
    )
    create_relationship(
        CreateCommercialRelationshipRequest(
            source_entity_id=e1.entity_id,
            target_entity_id=e2.entity_id,
            relationship_type="related_to",
            evidence_sources=["x"],
        )
    )
    create_relationship(
        CreateCommercialRelationshipRequest(
            source_entity_id=e2.entity_id,
            target_entity_id=e3.entity_id,
            relationship_type="related_to",
            evidence_sources=["y"],
        )
    )
    p = get_relationship_path(e1.entity_id, e3.entity_id)
    assert p["path_found"] is True
    assert p["entity_ids"] == [e1.entity_id, e2.entity_id, e3.entity_id]
