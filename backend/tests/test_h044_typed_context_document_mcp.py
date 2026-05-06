"""
TEST: H-044 typed context + document intelligence + MCP runtime compatibility
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import json
import os

import pytest
from fastapi.testclient import TestClient

from src.app import create_app
from src.context_compression.duplicate_context_detector import detect_duplicates
from src.context_compression.retrieval_relevance_service import score_retrieval_relevance
from src.context_compression.semantic_context_summarizer import summarize_context
from src.context_isolation.context_boundary_service import validate_context_boundary_access
from src.context_isolation.cross_context_validation import validate_no_unrestricted_shared_context
from src.context_orchestration.guardrail_context_service import build_guardrail_context
from src.context_orchestration.instruction_context_service import build_instruction_context
from src.context_orchestration.context_validation_service import validate_context_item
from src.document_intelligence.document_validation_service import validate_document_extraction
from src.document_intelligence.ocr_pipeline_service import placeholder_extract
from src.mcp_runtime.mcp_runtime_validation import validate_mcp_tool_projection
from src.mcp_runtime.mcp_tool_projection_service import project_mcp_tools

os.environ.setdefault("JWT_SECRET", "test-h044-jwt-secret-32characters-required!")
os.environ.setdefault("SOARB2B_API_KEYS", "test-h044-key")

app = create_app()
client = TestClient(app)


def test_valid_context_type_accepted():
    item = build_instruction_context(
        context_id="t1",
        workflow_scope="procurement_analysis",
        instructions="Do a deterministic summary.",
    )
    validate_context_item(item)


def test_invalid_context_type_rejected():
    bad = build_instruction_context(
        context_id="t2",
        workflow_scope="procurement_analysis",
        instructions="x",
    )
    bad["context_type"] = "invalid_type"
    with pytest.raises(ValueError, match="invalid context_type rejected"):
        validate_context_item(bad)


def test_guardrail_context_not_compressed_away():
    gr = build_guardrail_context(
        context_id="g1",
        workflow_scope="procurement_analysis",
        guardrails="No external execution.",
    )
    s = summarize_context(gr, max_tokens=5, allow_guardrail_compression=False)
    assert s["preserved"] is True
    assert s["marker"] is None
    assert s["compression_ratio"] == 1.0


def test_duplicate_context_detection_deterministic():
    a = build_instruction_context(
        context_id="d1",
        workflow_scope="executive_reporting",
        instructions="Same summary string.",
    )
    b = dict(a)
    b["context_id"] = "d2"
    out1 = detect_duplicates([a, b])
    out2 = detect_duplicates([a, b])
    assert json.dumps(out1, sort_keys=True) == json.dumps(out2, sort_keys=True)
    assert out1["automatic_deletion"] is False
    assert out1["estimated_token_waste"] >= 0


def test_relevance_scoring_deterministic():
    a = score_retrieval_relevance(
        source_type="uploaded_documents",
        freshness_days=10,
        workflow_scope="procurement_analysis",
        geographic_scope="TX",
        commercial_relevance=0.7,
    )
    b = score_retrieval_relevance(
        source_type="uploaded_documents",
        freshness_days=10,
        workflow_scope="procurement_analysis",
        geographic_scope="TX",
        commercial_relevance=0.7,
    )
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def test_isolated_workflow_context_enforced():
    it = build_instruction_context(
        context_id="iso1",
        workflow_scope="procurement_analysis",
        instructions="x",
    )
    blocked = validate_context_boundary_access(
        requesting_workflow_scope="executive_reporting",
        requested_item=it,
        explicit_cross_workflow_allow=False,
    )
    assert blocked["allowed"] is False
    allowed = validate_context_boundary_access(
        requesting_workflow_scope="executive_reporting",
        requested_item=it,
        explicit_cross_workflow_allow=True,
    )
    assert allowed["allowed"] is True


def test_document_extraction_metadata_valid_and_unsafe_rejected():
    extraction = placeholder_extract(
        document_id="doc-1",
        document_type="bid_document",
        source_lineage={"source_type": "ocr_document", "source_record_id": "upload-1"},
    )
    validate_document_extraction(extraction)
    bad = dict(extraction)
    bad["file_metadata"] = {"Authorization": "Bearer abc"}
    with pytest.raises(ValueError, match="unsafe file metadata rejected"):
        validate_document_extraction(bad)


def test_mcp_tool_projection_deterministic_and_unsafe_rejected():
    a = project_mcp_tools(policy_scope="internal_operator")
    b = project_mcp_tools(policy_scope="internal_operator")
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
    assert a["policy_scoped"] is True
    with pytest.raises(ValueError, match="unrestricted MCP execution rejected"):
        validate_mcp_tool_projection(
            {
                "tool_id": "bad",
                "name": "bad",
                "capability_id": "bad",
                "policy_scope": "internal_operator",
                "unrestricted_execution": True,
            }
        )


def test_global_context_dumping_rejected():
    with pytest.raises(ValueError, match="global context blob rejected"):
        validate_no_unrestricted_shared_context({"shared_global_context_blob": True})


def test_endpoints_smoke():
    r = client.get("/api/v1/system/context/types")
    assert r.status_code == 200
    assert r.json()["typed_context_orchestration_foundation"] is True

    r2 = client.get("/api/v1/system/context/compression")
    assert r2.status_code == 200
    assert r2.json()["llm_calls_for_compression"] is False

    r3 = client.get("/api/v1/system/documents/ocr-pipeline")
    assert r3.status_code == 200
    assert r3.json()["gpu_ocr_infrastructure"] is False

    r4 = client.get("/api/v1/system/mcp/tools")
    assert r4.status_code == 200
    assert r4.json()["unrestricted_mcp_execution"] is False

