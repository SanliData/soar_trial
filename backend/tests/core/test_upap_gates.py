"""
Tests: UPAP gates (regulated, decision maker, cross-channel, hard filters, evidence).
PASS/FAIL and evidence file enforcement.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from src.core.upap.gates import run_upap_gates
from src.core.upap.regulated import is_regulated_domain, require_simulation_mode
from src.core.upap.decision_maker import infer_role, ALLOWED_ROLES
from src.core.upap.cross_channel import recommend, ALLOWED_CHANNELS
from src.core.upap.evidence import write_upap_evidence
from src.core.upap.policy import get_limits_from_plan, MIN_READY_LEADS_DEFAULT
from src.core.upap.enforce import enforce, DROP_REASON_SIZE
from src.core.upap.verify import run_verification_gate
from src.core.upap.decision_maker import infer_decision_maker_persona
from src.core.upap_limits import COMPANY_LIMIT, COMPANY_SIZE_MAX


***REMOVED*** --- Regulated gate ---
class TestRegulatedGate:
    def test_regulated_domain_true_for_pharma(self):
        assert is_regulated_domain({"product_service": "pharmaceutical ingredients"}) is True
        assert is_regulated_domain({"industry": "healthcare"}) is True

    def test_regulated_domain_false_for_generic(self):
        assert is_regulated_domain({"product_service": "office supplies"}) is False
        assert is_regulated_domain({}) is False

    def test_regulated_plus_no_simulation_fail(self):
        result = require_simulation_mode(is_regulated=True, simulation_mode=None, leads=[])
        assert result.passed is False
        assert "simulation" in result.reason.lower() or "regulated" in result.reason.lower()

    def test_regulated_plus_simulation_false_fail(self):
        result = require_simulation_mode(is_regulated=True, simulation_mode=False, leads=[])
        assert result.passed is False

    def test_regulated_plus_simulation_true_pass_with_no_leads(self):
        result = require_simulation_mode(is_regulated=True, simulation_mode=True, leads=[])
        assert result.passed is True

    def test_regulated_plus_real_company_name_fail(self):
        leads = [
            {"company_name": "Company A"},
            {"company_name": "Acme Corp Inc"},
        ]
        result = require_simulation_mode(is_regulated=True, simulation_mode=True, leads=leads)
        assert result.passed is False
        assert result.blocked_count >= 1
        assert result.blocked_reason is not None


***REMOVED*** --- run_upap_gates: regulated fail ---
class TestRunUpapGatesRegulatedFail:
    def test_regulated_no_simulation_fail(self):
        query_params = {"product_service": "pharma", "industry": "healthcare"}
        leads = [{"company_name": "Company A", "persona_role": "Buyer"}]
        filtered, evidence, status = run_upap_gates(
            stage="EXPORT",
            trace_id="trace-1",
            run_id="run-1",
            query_id="q1",
            query_params=query_params,
            leads=leads,
        )
        assert status == "FAIL"
        assert evidence["status"] == "FAIL"
        assert evidence["regulated_domain"] is True
        assert "simulation" in (evidence.get("reason") or "").lower() or "regulated" in (evidence.get("reason") or "").lower()

    def test_regulated_real_company_fail(self):
        query_params = {"product_service": "pharma", "simulation_mode": True}
        leads = [{"company_name": "Pfizer Inc", "persona_role": "Procurement"}]
        filtered, evidence, status = run_upap_gates(
            stage="EXPORT",
            trace_id="t",
            run_id="r",
            query_id="q",
            query_params=query_params,
            leads=leads,
        )
        assert status == "FAIL"
        assert evidence["regulated_domain"] is True
        assert evidence.get("blocked_reason") or "real" in (evidence.get("reason") or "").lower()


***REMOVED*** --- Decision maker & cross-channel (missing → FAIL via invalid role) ---
class TestRunUpapGatesDecisionMakerAndChannel:
    @patch("src.core.upap.gates.infer_decision_maker_persona")
    def test_missing_decision_maker_fail(self, mock_persona):
        mock_persona.return_value = {
            "role": "Unknown",
            "authority_level": "low",
            "department": "General",
            "decision_type": "Unknown",
            "accessibility_score": 0.5,
            "decision_maker_confidence": 0.5,
            "is_decision_maker": False,
        }
        query_params = {"min_ready_leads": 0}
        leads = [{"company_name": "Company A", "persona_role": "Manager"}]
        filtered, evidence, status = run_upap_gates(
            stage="EXPORT",
            trace_id="t",
            run_id="r",
            query_id="q",
            query_params=query_params,
            leads=leads,
        )
        assert status == "FAIL"
        assert evidence.get("reason") == "missing_decision_maker"

    @patch("src.core.upap.gates.recommend")
    def test_missing_channel_recommendation_fail(self, mock_recommend):
        mock_recommend.return_value = {"channel_recommendation": "invalid_channel", "rule_id": "x", "sequence": None}
        query_params = {}
        leads = [{"company_name": "Company A", "persona_role": "Procurement"}]
        filtered, evidence, status = run_upap_gates(
            stage="EXPORT",
            trace_id="t",
            run_id="r",
            query_id="q",
            query_params=query_params,
            leads=leads,
        )
        assert status == "FAIL"
        assert evidence.get("reason") == "missing_channel_recommendation"


***REMOVED*** --- PASS path writes evidence file ---
class TestRunUpapGatesPassWritesEvidence:
    def test_export_pass_writes_evidence_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            evidence_dir = Path(tmp)
            query_params = {"min_ready_leads": 0}
            leads = [
                {"company_name": "Company A", "persona_role": "Procurement", "company_size": "1-10"},
                {"company_name": "Company B", "persona_role": "QA", "company_size": "11-50"},
            ]
            filtered, evidence, status = run_upap_gates(
                stage="EXPORT",
                trace_id="trace-pass",
                run_id="run-pass",
                query_id="query-pass",
                query_params=query_params,
                leads=leads,
                evidence_dir=evidence_dir,
            )
            assert status == "PASS"
            path = evidence_dir / "upap_evidence_query-pass_run-pass.json"
            assert path.exists()
            content = json.loads(path.read_text(encoding="utf-8"))
            assert content["trace_id"] == "trace-pass"
            assert content["run_id"] == "run-pass"
            assert content["query_id"] == "query-pass"
            assert content["status"] == "PASS"
            assert "timestamp" in content
            assert content.get("regulated_domain") is False
            assert "limits" in content
            assert content["limits"].get("company_size_max") == COMPANY_SIZE_MAX
            assert content["limits"].get("company_limit") == COMPANY_LIMIT
            assert content["rows_before"] == 2
            assert content["rows_after"] <= 2
            assert "decision_maker_summary" in content
            assert "channel_summary" in content
            assert "rejected_counts" in content

    def test_pass_enriches_leads_with_role_and_channel(self):
        query_params = {"product_service": "B2B procurement", "min_ready_leads": 0}
        leads = [{"company_name": "Company A", "persona_role": "Procurement", "company_size": "1-10"}]
        with tempfile.TemporaryDirectory() as tmp:
            filtered, evidence, status = run_upap_gates(
                stage="EXPORT",
                trace_id="t",
                run_id="r",
                query_id="q",
                query_params=query_params,
                leads=leads,
                evidence_dir=Path(tmp),
            )
        assert status == "PASS"
        assert len(filtered) >= 1
        lead = filtered[0]
        assert lead.get("decision_maker_role") in ALLOWED_ROLES
        assert lead.get("decision_confidence_score") is not None
        assert lead.get("channel_recommendation") in ALLOWED_CHANNELS
        assert lead.get("channel_rule_id")


***REMOVED*** --- Hard filters (all over 50 → 0 rows → FAIL) ---
class TestRunUpapGatesHardFiltersFail:
    def test_all_rows_over_50_fail(self):
        query_params = {"min_ready_leads": 0}
        leads = [
            {"company_name": "Big1", "company_size": "51-200", "persona_role": "Ops"},
            {"company_name": "Big2", "company_size": "201-500", "persona_role": "QA"},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            filtered, evidence, status = run_upap_gates(
                stage="EXPORT",
                trace_id="t",
                run_id="r",
                query_id="q",
                query_params=query_params,
                leads=leads,
                evidence_dir=Path(tmp),
            )
        assert status == "FAIL"
        assert evidence["rows_after"] == 0
        ***REMOVED*** enforce() uses drop_reasons key company_size_exceeds_max
        assert evidence.get("rejected_counts", {}).get("company_size_exceeds_max", 0) >= 2


***REMOVED*** --- Evidence writer ---
class TestEvidenceWriter:
    def test_write_upap_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            evidence = {
                "trace_id": "te",
                "run_id": "re",
                "query_id": "qe",
                "timestamp": "2025-01-01T00:00:00Z",
                "status": "PASS",
                "regulated_domain": False,
                "simulation_mode": None,
                "limits": {"company_size_max": 50, "company_limit": 100},
                "rows_before": 1,
                "rows_after": 1,
                "rejected_counts": {},
                "decision_maker_summary": {"Procurement": 1},
                "channel_summary": {"linkedin_only": 1},
            }
            path = write_upap_evidence("qe", "re", evidence, d)
            assert path.name == "upap_evidence_qe_re.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            assert data["status"] == "PASS"
            assert data["query_id"] == "qe"


***REMOVED*** --- infer_role / recommend (deterministic) ---
class TestDecisionMakerAndCrossChannel:
    def test_infer_role_procurement(self):
        role, conf = infer_role(title="Procurement Manager", dept="", keyword_intent="")
        assert role == "Procurement"
        assert 0 <= conf <= 1.0

    def test_infer_role_qa(self):
        role, conf = infer_role(title="Quality Assurance", dept="QA", keyword_intent="")
        assert role == "QA"
        assert 0 <= conf <= 1.0

    def test_recommend_returns_valid_channel(self):
        rec = recommend(keyword_intent="B2B", geo_confidence=0.5, role_score=0.5)
        assert rec["channel_recommendation"] in ALLOWED_CHANNELS
        assert rec.get("rule_id")

    def test_infer_decision_maker_persona_has_confidence_and_threshold(self):
        persona = infer_decision_maker_persona(title="Procurement Manager", dept="Supply", keyword_intent="")
        assert "decision_maker_confidence" in persona
        assert "is_decision_maker" in persona
        assert persona["decision_maker_confidence"] >= 0
        assert persona["authority_level"] in ("low", "medium", "high")
        assert persona["role"] in ALLOWED_ROLES


***REMOVED*** --- Verification gate min_ready_leads ---
class TestVerificationGateMinReadyLeads:
    def test_min_ready_leads_not_met_fail(self):
        query_params = {"min_ready_leads": 5}
        leads = [
            {"company_name": "A", "persona_role": "Procurement", "company_size": "1-10"},
            {"company_name": "B", "persona_role": "QA", "company_size": "1-10"},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            filtered, evidence, status = run_upap_gates(
                stage="EXPORT",
                trace_id="t",
                run_id="r",
                query_id="q",
                query_params=query_params,
                leads=leads,
                evidence_dir=Path(tmp),
            )
        assert status == "FAIL"
        assert "min_ready" in (evidence.get("reason") or "").lower() or "verification" in (evidence.get("reason") or "").lower()


***REMOVED*** --- Enforce company_size_max drop ---
class TestEnforceCompanySizeMax:
    def test_enforce_drops_company_size_over_max(self):
        leads = [
            {"company_name": "Small", "company_size": "1-10"},
            {"company_name": "Big", "company_size": "51-200"},
        ]
        kept, dropped, hist, audit = enforce(
            leads, "trace-1", "run-1", "plan-1", {}, "EXPORT",
        )
        assert len(kept) == 1
        assert kept[0]["company_name"] == "Small"
        assert hist.get(DROP_REASON_SIZE, 0) == 1
        assert dropped[0]["dropped_reason"] == DROP_REASON_SIZE
