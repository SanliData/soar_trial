"""
TEST: prompt_orchestration (H-027)
PURPOSE: Deterministic strategy registry, policies, evaluation
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import json
import os

import pytest
from fastapi.testclient import TestClient

from src.app import create_app

os.environ.setdefault("JWT_SECRET", "test-h027-jwt-secret-32characters-required!")
os.environ["SOARB2B_API_KEYS"] = "test-h027-prompt-key"

from src.prompt_orchestration.arq_template_service import export_arq_manifest
from src.prompt_orchestration.json_contract_service import export_contracts_manifest
from src.prompt_orchestration.prompt_evaluation_service import evaluate_prompt_configuration
from src.prompt_orchestration.prompt_strategy_registry import export_strategies_manifest
from src.prompt_orchestration.prompt_validation_service import EvaluatePromptRequest
from src.prompt_orchestration.reasoning_policy_service import select_strategy_for_task

app = create_app()
client = TestClient(app)

BASE = "/api/v1/system/prompts"


def test_invalid_strategy_rejected():
    r = client.post(
        f"{BASE}/evaluate",
        json={
            "task_type": "graph_reasoning",
            "strategy_override": "unknown_strategy",
        },
    )
    assert r.status_code == 422


def test_invalid_persona_rejected():
    r = client.post(
        f"{BASE}/evaluate",
        json={"task_type": "general_qa", "persona": "hacker_persona"},
    )
    assert r.status_code == 422


def test_arq_templates_deterministic():
    a = json.dumps(export_arq_manifest(), sort_keys=True)
    b = json.dumps(export_arq_manifest(), sort_keys=True)
    assert a == b


def test_json_contracts_export():
    m = export_contracts_manifest()
    ids = [c["contract_id"] for c in m["contracts"]]
    assert "results_hub_v1" in ids


def test_reasoning_policy_deterministic():
    p1 = select_strategy_for_task("graph_reasoning")
    p2 = select_strategy_for_task("graph_reasoning")
    assert p1 == p2
    assert p1["recommended_strategy"] == "arq_reasoning"


def test_evaluation_works():
    body = EvaluatePromptRequest(
        task_type="opportunity_ranking",
        contract_id="opportunity_rank_v1",
        persona="commercial_intelligence_officer",
        include_negative_constraints=True,
        arq_template_id="opportunity_evaluation",
    )
    out = evaluate_prompt_configuration(body)
    assert out["evaluation_score"] >= 0
    assert out["effective_strategy"] == "json_prompting"


def test_registry_endpoints():
    assert client.get(f"{BASE}/strategies").status_code == 200
    assert client.get(f"{BASE}/personas").status_code == 200
    assert client.get(f"{BASE}/arq-templates").status_code == 200
    j = client.get(f"{BASE}/strategies").json()
    assert j["deterministic_prompt_orchestration"] is True
    assert j["chain_of_thought_exposure"] == "none"


def test_strategies_manifest_stable():
    a = json.dumps(export_strategies_manifest(), sort_keys=True)
    b = json.dumps(export_strategies_manifest(), sort_keys=True)
    assert a == b
