"""
TEST: knowledge_ingestion (H-024)
PURPOSE: Deterministic ingestion, validation, chunking, retrieval policy
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import os
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from src.app import create_app

os.environ.setdefault("JWT_SECRET", "test-h024-jwt-secret-32characters-required!")
os.environ["SOARB2B_API_KEYS"] = "test-h024-knowledge-ingestion-key"

from src.knowledge_ingestion.knowledge_block_schema import KnowledgeBlock, SourceLineage
from src.knowledge_ingestion.knowledge_repository import clear_blocks_for_tests
from src.knowledge_ingestion.retrieval_policy_service import rank_blocks, retrieval_score
from src.knowledge_ingestion.semantic_chunk_service import create_semantic_chunks

clear_blocks_for_tests()
app = create_app()
client = TestClient(app)

BASE = "/api/v1/system/knowledge"


@pytest.fixture(autouse=True)
def _reset_repo():
    clear_blocks_for_tests()
    yield


def test_valid_knowledge_block_accepted():
    body = {
        "block_type": "market_signal",
        "title": "EU sector momentum",
        "content": "Structured summary of verified indicators.",
        "source_lineage": {"source_type": "verified_partner_dataset", "source_record_id": "vp-001"},
        "freshness_days": 14,
        "geographic_scope": "EU",
        "industry": "Manufacturing",
        "tags": ["signal", "eu"],
    }
    r = client.post(f"{BASE}/block", json=body)
    assert r.status_code == 200
    data = r.json()
    assert data["deterministic_ingestion"] is True
    assert data["scraping_executed"] is False
    b = data["block"]
    assert b["block_id"]
    assert 0.0 <= b["authority_score"] <= 1.0


def test_invalid_authority_rejected_at_schema_level():
    with pytest.raises(ValidationError):
        KnowledgeBlock(
            block_id="x",
            block_type="market_signal",
            title="t",
            content="c",
            authority_score=1.4,
            freshness_days=1,
            commercial_relevance=0.5,
            source_lineage=SourceLineage(
                source_type="public_procurement_feed",
                source_record_id="p1",
            ),
            created_at=datetime.now(timezone.utc),
        )


def test_freshness_scoring_monotonic():
    from src.knowledge_ingestion.freshness_scoring_service import freshness_confidence_score

    assert freshness_confidence_score(0) >= freshness_confidence_score(30)
    assert freshness_confidence_score(400) < freshness_confidence_score(10)


def test_semantic_chunking_preserves_sections():
    text = "Section A intro.\n\nSection B details.\nMore B.\n\nSection C wrap."
    chunks = create_semantic_chunks(text, max_chunk_chars=500)
    joined = "\n\n".join(chunks)
    assert "Section A" in joined
    assert "Section B" in joined
    assert "Section C" in joined


def test_retrieval_policy_ranking_deterministic():
    b1 = KnowledgeBlock(
        block_id="a",
        block_type="procurement_notice",
        title="t1",
        content="c",
        authority_score=0.9,
        freshness_days=10,
        geographic_scope="EU",
        industry="Tech",
        commercial_relevance=0.9,
        source_lineage=SourceLineage(source_type="public_procurement_feed", source_record_id="x"),
        created_at=datetime.now(timezone.utc),
    )
    b2 = KnowledgeBlock(
        block_id="b",
        block_type="procurement_notice",
        title="t2",
        content="c",
        authority_score=0.4,
        freshness_days=400,
        geographic_scope="US",
        industry="Retail",
        commercial_relevance=0.3,
        source_lineage=SourceLineage(source_type="uploaded_documents", source_record_id="y"),
        created_at=datetime.now(timezone.utc),
    )
    r1, _ = rank_blocks([b1, b2], query_geo="EU", query_industry="Tech")
    r2, _ = rank_blocks([b2, b1], query_geo="EU", query_industry="Tech")
    assert [x.block_id for x in r1] == [x.block_id for x in r2]
    assert r1[0].block_id == "a"


def test_retrieval_score_stable():
    b = KnowledgeBlock(
        block_id="z",
        block_type="market_signal",
        title="t",
        content="c",
        authority_score=0.8,
        freshness_days=20,
        commercial_relevance=0.8,
        source_lineage=SourceLineage(source_type="approved_public_registry", source_record_id="z"),
        created_at=datetime.now(timezone.utc),
    )
    s1, _ = retrieval_score(b)
    s2, _ = retrieval_score(b)
    assert s1 == s2


def test_invalid_source_rejected():
    body = {
        "block_type": "market_signal",
        "title": "bad",
        "content": "bad",
        "source_lineage": {"source_type": "unverified_anonymous_scraping_source", "source_record_id": "r"},
        "freshness_days": 1,
    }
    r = client.post(f"{BASE}/block", json=body)
    assert r.status_code == 422


def test_invalid_block_type_rejected():
    body = {
        "block_type": "unknown_block",
        "title": "bad",
        "content": "bad",
        "source_lineage": {"source_type": "uploaded_documents", "source_record_id": "u1"},
        "freshness_days": 1,
    }
    r = client.post(f"{BASE}/block", json=body)
    assert r.status_code == 422


def test_policies_endpoint():
    r = client.get(f"{BASE}/policies")
    assert r.status_code == 200
    j = r.json()
    assert j["deterministic_ingestion"] is True
    assert "weights" in j["policies"]
